/**
 * Autoresearch MCP Test Runner v3
 *
 * Fixes:
 * - Each skill gets its OWN group directory (no cross-contamination)
 * - Session cleared between cases (no session reuse)
 * - Reads results from group dir files (not just stdout)
 * - Reports actual file output even on timeout
 */
import { runContainerAgent } from '../src/container-runner.js';
import { RegisteredGroup } from '../src/types.js';
import fs from 'fs';
import path from 'path';

const AUTORESEARCH_DIR = path.resolve('autoresearch');

interface EvalCase {
  id: string;
  input: string;
  [key: string]: unknown;
}

function setupSkillGroup(skill: string) {
  const folder = `autoresearch-${skill}`;
  const groupDir = path.resolve('groups', folder);
  const sessionDir = path.resolve('data/sessions', folder);

  // Clean slate
  fs.mkdirSync(groupDir, { recursive: true });
  for (const f of fs.readdirSync(groupDir)) {
    if (f.endsWith('.md') && f !== 'CLAUDE.md') {
      fs.unlinkSync(path.join(groupDir, f));
    }
  }
  fs.writeFileSync(
    path.join(groupDir, 'CLAUDE.md'),
    `# Autoresearch Test: ${skill}\nEval testing with MCP tools.\n`,
  );

  // Clear session
  const claudeDir = path.join(sessionDir, '.claude');
  if (fs.existsSync(claudeDir)) {
    fs.rmSync(claudeDir, { recursive: true, force: true });
  }

  const group: RegisteredGroup = {
    jid: `autoresearch-${skill}@eval`,
    name: `Eval: ${skill}`,
    folder,
    trigger: '',
    requiresTrigger: false,
    isMain: false,
  };

  return { group, groupDir, sessionDir };
}

function getReportFiles(groupDir: string): Array<{ name: string; content: string; size: number }> {
  const reports: Array<{ name: string; content: string; size: number }> = [];
  for (const f of fs.readdirSync(groupDir)) {
    if (!f.endsWith('.md') || f === 'CLAUDE.md') continue;
    const fp = path.join(groupDir, f);
    const content = fs.readFileSync(fp, 'utf-8');
    reports.push({ name: f, content, size: content.length });
  }
  return reports;
}

async function runEvalCase(
  skill: string,
  evalCase: EvalCase,
  group: RegisteredGroup,
  groupDir: string,
  sessionDir: string,
) {
  const start = Date.now();

  // Clear reports from previous case
  for (const f of fs.readdirSync(groupDir)) {
    if (f.endsWith('.md') && f !== 'CLAUDE.md') {
      fs.unlinkSync(path.join(groupDir, f));
    }
  }

  // Clear session between cases
  const claudeDir = path.join(sessionDir, '.claude');
  if (fs.existsSync(claudeDir)) {
    fs.rmSync(claudeDir, { recursive: true, force: true });
  }

  const prompt = `You are testing the ${skill} skill with MCP tools.

IMPORTANT: You have 25 minutes max. Write your report to a file EARLY, then enhance it.
- Use 3-8 MCP tool calls for real data
- Save report file within first 10 minutes
- A saved report with real data beats nothing

QUERY: ${evalCase.input}

After your analysis, add "## MCP Tools Used" listing every MCP tool call you made.`;

  const output = await runContainerAgent(
    group,
    {
      prompt,
      groupFolder: group.folder,
      chatJid: group.jid,
      isMain: false,
      assistantName: 'autoresearch-eval',
    },
    () => {},
  );

  const duration_ms = Date.now() - start;
  const timedOut = !output.result;
  const reports = getReportFiles(groupDir);

  return {
    id: evalCase.id,
    skill,
    stdout_output: output.result || output.error || 'no stdout',
    file_reports: reports.map(r => ({ name: r.name, size: r.size })),
    file_content: reports.map(r => r.content).join('\n---\n') || 'no files written',
    duration_ms,
    timed_out: timedOut,
    had_file_output: reports.length > 0,
  };
}

async function main() {
  const skills = process.argv.slice(2);
  if (skills.length === 0) {
    console.log('Usage: npx tsx scripts/autoresearch-mcp-test.ts <skill1> [skill2] ...');
    console.log('\nSkills run SEQUENTIALLY (one at a time) to avoid shared-state bugs.');
    console.log('Each skill gets its own isolated group directory.\n');
    const dirs = fs.readdirSync(AUTORESEARCH_DIR).filter(d =>
      fs.existsSync(path.join(AUTORESEARCH_DIR, d, 'eval-cases.json')),
    );
    dirs.forEach(d => console.log(`  ${d}`));
    process.exit(0);
  }

  for (const skill of skills) {
    const evalPath = path.join(AUTORESEARCH_DIR, skill, 'eval-cases.json');
    if (!fs.existsSync(evalPath)) {
      console.error(`No eval cases found for ${skill}`);
      continue;
    }

    const cases: EvalCase[] = JSON.parse(fs.readFileSync(evalPath, 'utf-8'));
    const testCases = cases.slice(0, 3);
    const { group, groupDir, sessionDir } = setupSkillGroup(skill);

    const outputDir = path.join(AUTORESEARCH_DIR, skill, 'logs', 'mcp-round1');
    fs.mkdirSync(outputDir, { recursive: true });

    console.log(`\n=== ${skill} (${testCases.length} cases, isolated group: ${group.folder}) ===`);

    for (const tc of testCases) {
      console.log(`  Running: ${tc.id}...`);
      try {
        const result = await runEvalCase(skill, tc, group, groupDir, sessionDir);
        const mins = (result.duration_ms / 60000).toFixed(1);
        const fileInfo = result.file_reports.map(r => `${r.name}(${r.size}B)`).join(', ') || 'none';

        let status: string;
        if (!result.timed_out) status = 'OK';
        else if (result.had_file_output) status = 'TIMEOUT+FILES';
        else status = 'TIMEOUT-EMPTY';

        fs.writeFileSync(
          path.join(outputDir, `${tc.id}.json`),
          JSON.stringify(result, null, 2),
        );
        console.log(`  ${result.timed_out ? '⏱' : '✓'} ${tc.id} (${mins}m) [${status}] ${fileInfo}`);
      } catch (err) {
        console.error(`  ✗ ${tc.id}: ${err}`);
      }
    }
  }

  console.log('\nDone.');
}

main().catch(console.error);
