/**
 * NanoClaw Agent Runner
 * Runs inside a container, receives config via stdin, outputs result to stdout
 *
 * Input protocol:
 *   Stdin: Full ContainerInput JSON (read until EOF, like before)
 *   IPC:   Follow-up messages written as JSON files to /workspace/ipc/input/
 *          Files: {type:"message", text:"..."}.json — polled and consumed
 *          Sentinel: /workspace/ipc/input/_close — signals session end
 *
 * Stdout protocol:
 *   Each result is wrapped in OUTPUT_START_MARKER / OUTPUT_END_MARKER pairs.
 *   Multiple results may be emitted (one per agent teams result).
 *   Final marker after loop ends signals completion.
 */

import fs from 'fs';
import path from 'path';
import { query, HookCallback, PreCompactHookInput, PreToolUseHookInput } from '@anthropic-ai/claude-agent-sdk';
import { fileURLToPath } from 'url';

interface ContainerInput {
  prompt: string;
  sessionId?: string;
  groupFolder: string;
  chatJid: string;
  isMain: boolean;
  isScheduledTask?: boolean;
  assistantName?: string;
  secrets?: Record<string, string>;
  imageAttachments?: Array<{ relativePath: string; mediaType: string }>;
}

interface ImageContentBlock {
  type: 'image';
  source: { type: 'base64'; media_type: string; data: string };
}
interface TextContentBlock {
  type: 'text';
  text: string;
}
type ContentBlock = ImageContentBlock | TextContentBlock;

interface ContainerOutput {
  status: 'success' | 'error';
  result: string | null;
  newSessionId?: string;
  error?: string;
}

interface SessionEntry {
  sessionId: string;
  fullPath: string;
  summary: string;
  firstPrompt: string;
}

interface SessionsIndex {
  entries: SessionEntry[];
}

interface SDKUserMessage {
  type: 'user';
  message: { role: 'user'; content: string | ContentBlock[] };
  parent_tool_use_id: null;
  session_id: string;
}

const IPC_INPUT_DIR = '/workspace/ipc/input';
const IPC_INPUT_CLOSE_SENTINEL = path.join(IPC_INPUT_DIR, '_close');
const IPC_POLL_MS = 500;

/**
 * Push-based async iterable for streaming user messages to the SDK.
 * Keeps the iterable alive until end() is called, preventing isSingleUserTurn.
 */
class MessageStream {
  private queue: SDKUserMessage[] = [];
  private waiting: (() => void) | null = null;
  private done = false;

  push(text: string): void {
    this.queue.push({
      type: 'user',
      message: { role: 'user', content: text },
      parent_tool_use_id: null,
      session_id: '',
    });
    this.waiting?.();
  }

  pushMultimodal(content: ContentBlock[]): void {
    this.queue.push({
      type: 'user',
      message: { role: 'user', content },
      parent_tool_use_id: null,
      session_id: '',
    });
    this.waiting?.();
  }

  end(): void {
    this.done = true;
    this.waiting?.();
  }

  async *[Symbol.asyncIterator](): AsyncGenerator<SDKUserMessage> {
    while (true) {
      while (this.queue.length > 0) {
        yield this.queue.shift()!;
      }
      if (this.done) return;
      await new Promise<void>(r => { this.waiting = r; });
      this.waiting = null;
    }
  }
}

async function readStdin(): Promise<string> {
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', chunk => { data += chunk; });
    process.stdin.on('end', () => resolve(data));
    process.stdin.on('error', reject);
  });
}

const OUTPUT_START_MARKER = '---NANOCLAW_OUTPUT_START---';
const OUTPUT_END_MARKER = '---NANOCLAW_OUTPUT_END---';

function writeOutput(output: ContainerOutput): void {
  console.log(OUTPUT_START_MARKER);
  console.log(JSON.stringify(output));
  console.log(OUTPUT_END_MARKER);
}

function log(message: string): void {
  console.error(`[agent-runner] ${message}`);
}

function getSessionSummary(sessionId: string, transcriptPath: string): string | null {
  const projectDir = path.dirname(transcriptPath);
  const indexPath = path.join(projectDir, 'sessions-index.json');

  if (!fs.existsSync(indexPath)) {
    log(`Sessions index not found at ${indexPath}`);
    return null;
  }

  try {
    const index: SessionsIndex = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
    const entry = index.entries.find(e => e.sessionId === sessionId);
    if (entry?.summary) {
      return entry.summary;
    }
  } catch (err) {
    log(`Failed to read sessions index: ${err instanceof Error ? err.message : String(err)}`);
  }

  return null;
}

/**
 * Archive the full transcript to conversations/ before compaction.
 */
function createPreCompactHook(assistantName?: string): HookCallback {
  return async (input, _toolUseId, _context) => {
    const preCompact = input as PreCompactHookInput;
    const transcriptPath = preCompact.transcript_path;
    const sessionId = preCompact.session_id;

    if (!transcriptPath || !fs.existsSync(transcriptPath)) {
      log('No transcript found for archiving');
      return {};
    }

    try {
      const content = fs.readFileSync(transcriptPath, 'utf-8');
      const messages = parseTranscript(content);

      if (messages.length === 0) {
        log('No messages to archive');
        return {};
      }

      const summary = getSessionSummary(sessionId, transcriptPath);
      const name = summary ? sanitizeFilename(summary) : generateFallbackName();

      const conversationsDir = '/workspace/group/conversations';
      fs.mkdirSync(conversationsDir, { recursive: true });

      const date = new Date().toISOString().split('T')[0];
      const filename = `${date}-${name}.md`;
      const filePath = path.join(conversationsDir, filename);

      const markdown = formatTranscriptMarkdown(messages, summary, assistantName);
      fs.writeFileSync(filePath, markdown);

      log(`Archived conversation to ${filePath}`);
    } catch (err) {
      log(`Failed to archive transcript: ${err instanceof Error ? err.message : String(err)}`);
    }

    return {};
  };
}

// Secrets to strip from Bash tool subprocess environments.
// These are needed by claude-code for API auth but should never
// be visible to commands Kit runs.
const SECRET_ENV_VARS = ['ANTHROPIC_API_KEY', 'CLAUDE_CODE_OAUTH_TOKEN'];

function createSanitizeBashHook(): HookCallback {
  return async (input, _toolUseId, _context) => {
    const preInput = input as PreToolUseHookInput;
    const command = (preInput.tool_input as { command?: string })?.command;
    if (!command) return {};

    const unsetPrefix = `unset ${SECRET_ENV_VARS.join(' ')} 2>/dev/null; `;
    return {
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        updatedInput: {
          ...(preInput.tool_input as Record<string, unknown>),
          command: unsetPrefix + command,
        },
      },
    };
  };
}

function sanitizeFilename(summary: string): string {
  return summary
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 50);
}

function generateFallbackName(): string {
  const time = new Date();
  return `conversation-${time.getHours().toString().padStart(2, '0')}${time.getMinutes().toString().padStart(2, '0')}`;
}

interface ParsedMessage {
  role: 'user' | 'assistant';
  content: string;
}

function parseTranscript(content: string): ParsedMessage[] {
  const messages: ParsedMessage[] = [];

  for (const line of content.split('\n')) {
    if (!line.trim()) continue;
    try {
      const entry = JSON.parse(line);
      if (entry.type === 'user' && entry.message?.content) {
        const text = typeof entry.message.content === 'string'
          ? entry.message.content
          : entry.message.content.map((c: { text?: string }) => c.text || '').join('');
        if (text) messages.push({ role: 'user', content: text });
      } else if (entry.type === 'assistant' && entry.message?.content) {
        const textParts = entry.message.content
          .filter((c: { type: string }) => c.type === 'text')
          .map((c: { text: string }) => c.text);
        const text = textParts.join('');
        if (text) messages.push({ role: 'assistant', content: text });
      }
    } catch {
    }
  }

  return messages;
}

function formatTranscriptMarkdown(messages: ParsedMessage[], title?: string | null, assistantName?: string): string {
  const now = new Date();
  const formatDateTime = (d: Date) => d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });

  const lines: string[] = [];
  lines.push(`# ${title || 'Conversation'}`);
  lines.push('');
  lines.push(`Archived: ${formatDateTime(now)}`);
  lines.push('');
  lines.push('---');
  lines.push('');

  for (const msg of messages) {
    const sender = msg.role === 'user' ? 'User' : (assistantName || 'Assistant');
    const content = msg.content.length > 2000
      ? msg.content.slice(0, 2000) + '...'
      : msg.content;
    lines.push(`**${sender}**: ${content}`);
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Check for _close sentinel.
 */
function shouldClose(): boolean {
  if (fs.existsSync(IPC_INPUT_CLOSE_SENTINEL)) {
    try { fs.unlinkSync(IPC_INPUT_CLOSE_SENTINEL); } catch { /* ignore */ }
    return true;
  }
  return false;
}

/**
 * Drain all pending IPC input messages.
 * Returns messages found, or empty array.
 */
function drainIpcInput(): string[] {
  try {
    fs.mkdirSync(IPC_INPUT_DIR, { recursive: true });
    const files = fs.readdirSync(IPC_INPUT_DIR)
      .filter(f => f.endsWith('.json'))
      .sort();

    const messages: string[] = [];
    for (const file of files) {
      const filePath = path.join(IPC_INPUT_DIR, file);
      try {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
        fs.unlinkSync(filePath);
        if (data.type === 'message' && data.text) {
          messages.push(data.text);
        }
      } catch (err) {
        log(`Failed to process input file ${file}: ${err instanceof Error ? err.message : String(err)}`);
        try { fs.unlinkSync(filePath); } catch { /* ignore */ }
      }
    }
    return messages;
  } catch (err) {
    log(`IPC drain error: ${err instanceof Error ? err.message : String(err)}`);
    return [];
  }
}

/**
 * Wait for a new IPC message or _close sentinel.
 * Returns the messages as a single string, or null if _close.
 */
function waitForIpcMessage(): Promise<string | null> {
  return new Promise((resolve) => {
    const poll = () => {
      if (shouldClose()) {
        resolve(null);
        return;
      }
      const messages = drainIpcInput();
      if (messages.length > 0) {
        resolve(messages.join('\n'));
        return;
      }
      setTimeout(poll, IPC_POLL_MS);
    };
    poll();
  });
}

/**
 * Run a single query and stream results via writeOutput.
 * Uses MessageStream (AsyncIterable) to keep isSingleUserTurn=false,
 * allowing agent teams subagents to run to completion.
 * Also pipes IPC messages into the stream during the query.
 */
async function runQuery(
  prompt: string,
  sessionId: string | undefined,
  mcpServerPath: string,
  containerInput: ContainerInput,
  sdkEnv: Record<string, string | undefined>,
  resumeAt?: string,
): Promise<{ newSessionId?: string; lastAssistantUuid?: string; closedDuringQuery: boolean }> {
  const stream = new MessageStream();
  stream.push(prompt);

  // Load image attachments and send as multimodal content blocks
  if (containerInput.imageAttachments?.length) {
    const blocks: ContentBlock[] = [];
    for (const img of containerInput.imageAttachments) {
      const imgPath = path.join('/workspace/group', img.relativePath);
      try {
        const data = fs.readFileSync(imgPath).toString('base64');
        blocks.push({ type: 'image', source: { type: 'base64', media_type: img.mediaType, data } });
      } catch (err) {
        log(`Failed to load image: ${imgPath}`);
      }
    }
    if (blocks.length > 0) {
      stream.pushMultimodal(blocks);
    }
  }

  // Poll IPC for follow-up messages and _close sentinel during the query
  let ipcPolling = true;
  let closedDuringQuery = false;
  const pollIpcDuringQuery = () => {
    if (!ipcPolling) return;
    if (shouldClose()) {
      log('Close sentinel detected during query, ending stream');
      closedDuringQuery = true;
      stream.end();
      ipcPolling = false;
      return;
    }
    const messages = drainIpcInput();
    for (const text of messages) {
      log(`Piping IPC message into active query (${text.length} chars)`);
      stream.push(text);
    }
    setTimeout(pollIpcDuringQuery, IPC_POLL_MS);
  };
  setTimeout(pollIpcDuringQuery, IPC_POLL_MS);

  let newSessionId: string | undefined;
  let lastAssistantUuid: string | undefined;
  let messageCount = 0;
  let resultCount = 0;
  let activeTasks = 0; // Track running subagent tasks
  let pushbackCount = 0; // How many times we've pushed back on early results

  // Load global CLAUDE.md as additional system context (shared across all groups)
  const globalClaudeMdPath = '/workspace/global/CLAUDE.md';
  let globalClaudeMd: string | undefined;
  if (!containerInput.isMain && fs.existsSync(globalClaudeMdPath)) {
    globalClaudeMd = fs.readFileSync(globalClaudeMdPath, 'utf-8');
  }

  // Discover additional directories mounted at /workspace/extra/*
  // These are passed to the SDK so their CLAUDE.md files are loaded automatically
  const extraDirs: string[] = [];
  const extraBase = '/workspace/extra';
  if (fs.existsSync(extraBase)) {
    for (const entry of fs.readdirSync(extraBase)) {
      const fullPath = path.join(extraBase, entry);
      if (fs.statSync(fullPath).isDirectory()) {
        extraDirs.push(fullPath);
      }
    }
  }
  if (extraDirs.length > 0) {
    log(`Additional directories: ${extraDirs.join(', ')}`);
  }

  for await (const message of query({
    prompt: stream,
    options: {
      cwd: '/workspace/group',
      additionalDirectories: extraDirs.length > 0 ? extraDirs : undefined,
      resume: sessionId,
      resumeSessionAt: resumeAt,
      systemPrompt: globalClaudeMd
        ? { type: 'preset' as const, preset: 'claude_code' as const, append: globalClaudeMd }
        : undefined,
      allowedTools: [
        'Bash',
        'Read', 'Write', 'Edit', 'Glob', 'Grep',
        'WebSearch', 'WebFetch',
        'Task', 'TaskOutput', 'TaskStop',
        'TeamCreate', 'TeamDelete', 'SendMessage',
        'TodoWrite', 'ToolSearch', 'Skill',
        'NotebookEdit',
        'mcp__nanoclaw__*',
        'mcp__fda__*',
        'mcp__ctgov__*',
        'mcp__pubmed__*',
        'mcp__drugbank__*',
        'mcp__ema__*',
        'mcp__opentargets__*',
        'mcp__chembl__*',
        'mcp__nlm__*',
        'mcp__cdc__*',
        'mcp__pubchem__*',
        'mcp__biorxiv__*',
        'mcp__medicare__*',
        'mcp__medicaid__*',
        'mcp__eu_filings__*',
        'mcp__ensembl__*',
        'mcp__uniprot__*',
        'mcp__stringdb__*',
        'mcp__reactome__*',
        'mcp__kegg__*',
        'mcp__alphafold__*',
        'mcp__pdb__*',
        'mcp__hpo__*',
        'mcp__gtex__*',
        'mcp__geneontology__*',
        'mcp__depmap__*',
        'mcp__gnomad__*',
        'mcp__cbioportal__*',
        'mcp__bindingdb__*',
        'mcp__geo__*',
        'mcp__clinpgx__*',
        'mcp__monarch__*',
        'mcp__jaspar__*',
        'mcp__clinvar__*',
        'mcp__cosmic__*',
        'mcp__gwas__*',
        'mcp__hmdb__*',
        'mcp__openalex__*',
        'mcp__brenda__*',
        'mcp__cellxgene__*',
        'mcp__esm__*',
        'mcp__metabolomics__*'
      ],
      env: sdkEnv,
      permissionMode: 'bypassPermissions',
      allowDangerouslySkipPermissions: true,
      settingSources: ['project', 'user'],
      mcpServers: {
        nanoclaw: {
          command: 'node',
          args: [mcpServerPath],
          env: {
            NANOCLAW_CHAT_JID: containerInput.chatJid,
            NANOCLAW_GROUP_FOLDER: containerInput.groupFolder,
            NANOCLAW_IS_MAIN: containerInput.isMain ? '1' : '0',
          },
        },
        // Pharma MCP Servers (mounted read-only, symlinked by entrypoint)
        ...(fs.existsSync('/tmp/fda-mcp-server/build/index.js') ? {
          fda: {
            command: 'node',
            args: ['/tmp/fda-mcp-server/build/index.js'],
            env: {
              FDA_API_KEY: process.env.FDA_API_KEY || '',
            },
          },
        } : {}),
        ...(fs.existsSync('/tmp/ctgov-mcp-server/build/index.js') ? {
          ctgov: {
            command: 'node',
            args: ['/tmp/ctgov-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/pubmed-mcp-server/build/index.js') ? {
          pubmed: {
            command: 'node',
            args: ['/tmp/pubmed-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/drugbank-mcp-server/build/index.js') ? {
          drugbank: {
            command: 'node',
            args: ['/tmp/drugbank-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/ema-mcp-server/build/index.js') ? {
          ema: {
            command: 'node',
            args: ['/tmp/ema-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/opentargets-mcp-server/build/index.js') ? {
          opentargets: {
            command: 'node',
            args: ['/tmp/opentargets-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/chembl-mcp-server/build/index.js') ? {
          chembl: {
            command: 'node',
            args: ['/tmp/chembl-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/nlm-mcp-server/build/index.js') ? {
          nlm: {
            command: 'node',
            args: ['/tmp/nlm-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/cdc-mcp-server/build/index.js') ? {
          cdc: {
            command: 'node',
            args: ['/tmp/cdc-mcp-server/build/index.js'],
            env: {
              CDC_APP_TOKEN: process.env.CDC_APP_TOKEN || '',
            },
          },
        } : {}),
        ...(fs.existsSync('/tmp/pubchem-mcp-server/build/index.js') ? {
          pubchem: {
            command: 'node',
            args: ['/tmp/pubchem-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/biorxiv-mcp-server/build/index.js') ? {
          biorxiv: {
            command: 'node',
            args: ['/tmp/biorxiv-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/medicare-mcp-server/build/index.js') ? {
          medicare: {
            command: 'node',
            args: ['/tmp/medicare-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/medicaid-mcp-server/build/index.js') ? {
          medicaid: {
            command: 'node',
            args: ['/tmp/medicaid-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/eu-filings-mcp-server/build/index.js') ? {
          eu_filings: {
            command: 'node',
            args: ['/tmp/eu-filings-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/ensembl-mcp-server/build/index.js') ? {
          ensembl: {
            command: 'node',
            args: ['/tmp/ensembl-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/uniprot-mcp-server/build/index.js') ? {
          uniprot: {
            command: 'node',
            args: ['/tmp/uniprot-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/stringdb-mcp-server/build/index.js') ? {
          stringdb: {
            command: 'node',
            args: ['/tmp/stringdb-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/reactome-mcp-server/build/index.js') ? {
          reactome: {
            command: 'node',
            args: ['/tmp/reactome-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/kegg-mcp-server/build/index.js') ? {
          kegg: {
            command: 'node',
            args: ['/tmp/kegg-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/alphafold-mcp-server/build/index.js') ? {
          alphafold: {
            command: 'node',
            args: ['/tmp/alphafold-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/pdb-mcp-server/build/index.js') ? {
          pdb: {
            command: 'node',
            args: ['/tmp/pdb-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/hpo-mcp-server/build/index.js') ? {
          hpo: {
            command: 'node',
            args: ['/tmp/hpo-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/gtex-mcp-server/build/index.js') ? {
          gtex: {
            command: 'node',
            args: ['/tmp/gtex-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/geneontology-mcp-server/build/index.js') ? {
          geneontology: {
            command: 'node',
            args: ['/tmp/geneontology-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/depmap-mcp-server/build/index.js') ? {
          depmap: {
            command: 'node',
            args: ['/tmp/depmap-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/gnomad-mcp-server/build/index.js') ? {
          gnomad: {
            command: 'node',
            args: ['/tmp/gnomad-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/cbioportal-mcp-server/build/index.js') ? {
          cbioportal: {
            command: 'node',
            args: ['/tmp/cbioportal-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/bindingdb-mcp-server/build/index.js') ? {
          bindingdb: {
            command: 'node',
            args: ['/tmp/bindingdb-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/geo-mcp-server/build/index.js') ? {
          geo: {
            command: 'node',
            args: ['/tmp/geo-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/clinpgx-mcp-server/build/index.js') ? {
          clinpgx: {
            command: 'node',
            args: ['/tmp/clinpgx-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/monarch-mcp-server/build/index.js') ? {
          monarch: {
            command: 'node',
            args: ['/tmp/monarch-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/jaspar-mcp-server/build/index.js') ? {
          jaspar: {
            command: 'node',
            args: ['/tmp/jaspar-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/clinvar-mcp-server/build/index.js') ? {
          clinvar: {
            command: 'node',
            args: ['/tmp/clinvar-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/cosmic-mcp-server/build/index.js') ? {
          cosmic: {
            command: 'node',
            args: ['/tmp/cosmic-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/gwas-mcp-server/build/index.js') ? {
          gwas: {
            command: 'node',
            args: ['/tmp/gwas-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/hmdb-mcp-server/build/index.js') ? {
          hmdb: {
            command: 'node',
            args: ['/tmp/hmdb-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/openalex-mcp-server/build/index.js') ? {
          openalex: {
            command: 'node',
            args: ['/tmp/openalex-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/brenda-mcp-server/build/index.js') ? {
          brenda: {
            command: 'node',
            args: ['/tmp/brenda-mcp-server/build/index.js'],
            env: {
              BRENDA_EMAIL: process.env.BRENDA_EMAIL || '',
              BRENDA_PASSWORD: process.env.BRENDA_PASSWORD || '',
            },
          },
        } : {}),
        ...(fs.existsSync('/tmp/cellxgene-mcp-server/build/index.js') ? {
          cellxgene: {
            command: 'node',
            args: ['/tmp/cellxgene-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
        ...(fs.existsSync('/tmp/esm-mcp-server/build/index.js') ? {
          esm: {
            command: 'node',
            args: ['/tmp/esm-mcp-server/build/index.js'],
            env: {
              ESM_FORGE_TOKEN: process.env.ESM_FORGE_TOKEN || '',
            },
          },
        } : {}),
        ...(fs.existsSync('/tmp/metabolomics-mcp-server/build/index.js') ? {
          metabolomics: {
            command: 'node',
            args: ['/tmp/metabolomics-mcp-server/build/index.js'],
            env: {},
          },
        } : {}),
      },
      hooks: {
        PreCompact: [{ hooks: [createPreCompactHook(containerInput.assistantName)] }],
        PreToolUse: [{ matcher: 'Bash', hooks: [createSanitizeBashHook()] }],
      },
    }
  })) {
    messageCount++;
    const msgType = message.type === 'system' ? `system/${(message as { subtype?: string }).subtype}` : message.type;
    log(`[msg #${messageCount}] type=${msgType}`);

    if (message.type === 'assistant' && 'uuid' in message) {
      lastAssistantUuid = (message as { uuid: string }).uuid;
    }

    if (message.type === 'system' && message.subtype === 'init') {
      newSessionId = message.session_id;
      log(`Session initialized: ${newSessionId}`);
    }

    if (message.type === 'system' && (message as { subtype?: string }).subtype === 'task_started') {
      activeTasks++;
      log(`Task started (active: ${activeTasks})`);
    }

    if (message.type === 'system' && (message as { subtype?: string }).subtype === 'task_notification') {
      const tn = message as { task_id: string; status: string; summary: string };
      log(`Task notification: task=${tn.task_id} status=${tn.status} summary=${tn.summary}`);
      if (tn.status === 'completed' || tn.status === 'failed' || tn.status === 'cancelled') {
        activeTasks = Math.max(0, activeTasks - 1);
        log(`Task ended (active: ${activeTasks})`);
      }
    }

    if (message.type === 'result') {
      resultCount++;
      const textResult = 'result' in message ? (message as { result?: string }).result : null;
      log(`Result #${resultCount}: subtype=${message.subtype}${textResult ? ` text=${textResult.slice(0, 200)}` : ''} (activeTasks: ${activeTasks})`);

      // If subagent tasks were started and this is the first result, push back
      // once to give the agent a chance to wait for task completion.
      if (activeTasks > 0 && pushbackCount === 0) {
        pushbackCount++;
        log(`Pushing follow-up: ${activeTasks} tasks started, forcing agent to wait (pushback #${pushbackCount})`);
        stream.push(
          `[SYSTEM] You returned a result but you created ${activeTasks} subagent task(s). ` +
          `Use TaskOutput to wait for each task to complete, then synthesize and return the final answer. ` +
          `Do NOT return until all tasks are done.`
        );
        continue;
      }

      writeOutput({
        status: 'success',
        result: textResult || null,
        newSessionId
      });
    }
  }

  ipcPolling = false;
  log(`Query done. Messages: ${messageCount}, results: ${resultCount}, lastAssistantUuid: ${lastAssistantUuid || 'none'}, closedDuringQuery: ${closedDuringQuery}`);
  return { newSessionId, lastAssistantUuid, closedDuringQuery };
}

async function main(): Promise<void> {
  let containerInput: ContainerInput;

  try {
    const stdinData = await readStdin();
    containerInput = JSON.parse(stdinData);
    // Delete the temp file the entrypoint wrote — it contains secrets
    try { fs.unlinkSync('/tmp/input.json'); } catch { /* may not exist */ }
    log(`Received input for group: ${containerInput.groupFolder}`);
  } catch (err) {
    writeOutput({
      status: 'error',
      result: null,
      error: `Failed to parse input: ${err instanceof Error ? err.message : String(err)}`
    });
    process.exit(1);
  }

  // Build SDK env: merge secrets into process.env for the SDK only.
  // Secrets never touch process.env itself, so Bash subprocesses can't see them.
  const sdkEnv: Record<string, string | undefined> = { ...process.env };
  for (const [key, value] of Object.entries(containerInput.secrets || {})) {
    sdkEnv[key] = value;
  }

  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  const mcpServerPath = path.join(__dirname, 'ipc-mcp-stdio.js');

  let sessionId = containerInput.sessionId;
  fs.mkdirSync(IPC_INPUT_DIR, { recursive: true });

  // Clean up stale _close sentinel from previous container runs
  try { fs.unlinkSync(IPC_INPUT_CLOSE_SENTINEL); } catch { /* ignore */ }

  // Build initial prompt (drain any pending IPC messages too)
  let prompt = containerInput.prompt;
  if (containerInput.isScheduledTask) {
    prompt = `[SCHEDULED TASK - The following message was sent automatically and is not coming directly from the user or group.]\n\n${prompt}`;
  }
  const pending = drainIpcInput();
  if (pending.length > 0) {
    log(`Draining ${pending.length} pending IPC messages into initial prompt`);
    prompt += '\n' + pending.join('\n');
  }

  // Send immediate ack so the user isn't left in the dark while the agent works
  writeOutput({
    status: 'success',
    result: '_Working on it..._',
  });

  // Query loop: run query → wait for IPC message → run new query → repeat
  let resumeAt: string | undefined;
  try {
    while (true) {
      log(`Starting query (session: ${sessionId || 'new'}, resumeAt: ${resumeAt || 'latest'})...`);

      const queryResult = await runQuery(prompt, sessionId, mcpServerPath, containerInput, sdkEnv, resumeAt);
      if (queryResult.newSessionId) {
        sessionId = queryResult.newSessionId;
      }
      if (queryResult.lastAssistantUuid) {
        resumeAt = queryResult.lastAssistantUuid;
      }

      // If _close was consumed during the query, exit immediately.
      // Don't emit a session-update marker (it would reset the host's
      // idle timer and cause a 30-min delay before the next _close).
      if (queryResult.closedDuringQuery) {
        log('Close sentinel consumed during query, exiting');
        break;
      }

      // Emit session update so host can track it
      writeOutput({ status: 'success', result: null, newSessionId: sessionId });

      log('Query ended, waiting for next IPC message...');

      // Wait for the next message or _close sentinel
      const nextMessage = await waitForIpcMessage();
      if (nextMessage === null) {
        log('Close sentinel received, exiting');
        break;
      }

      log(`Got new message (${nextMessage.length} chars), starting new query`);
      prompt = nextMessage;
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    log(`Agent error: ${errorMessage}`);
    writeOutput({
      status: 'error',
      result: null,
      newSessionId: sessionId,
      error: errorMessage
    });
    process.exit(1);
  }
}

main();
