#!/usr/bin/env npx tsx
/**
 * Autoresearch: Clinical Trial Outcome Predictor
 *
 * Autonomous ML research loop. Agent modifies features.py and train.py,
 * evaluates on held-out set, keeps improvements, discards regressions.
 *
 * Usage: npx tsx autoresearch/run-ct.ts [--rounds N]
 */

import { execFile } from "child_process";
import {
  readFileSync,
  writeFileSync,
  mkdirSync,
  existsSync,
  appendFileSync,
} from "fs";
import { join, dirname } from "path";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const ROOT = join(dirname(new URL(import.meta.url).pathname), "projects", "ct-predictor");
const PROGRAM_PATH = join(ROOT, "program.md");
const FEATURES_PATH = join(ROOT, "features.py");
const TRAIN_PATH = join(ROOT, "train.py");
const EVALUATE_PATH = join(ROOT, "evaluate.py");
const RESULTS_TSV = join(ROOT, "results.tsv");
const LAST_EVAL_PATH = join(ROOT, "last_eval.json");
const LOG_DIR = join(ROOT, "logs");

const MODEL = "sonnet";
const MAX_ROUNDS = parseInt(
  process.argv.find((_, i, a) => a[i - 1] === "--rounds") ?? "20"
);
const TRAIN_TIMEOUT = 120_000; // 2 minutes max for train + evaluate

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function run(cmd: string, args: string[], timeout = TRAIN_TIMEOUT): Promise<string> {
  return new Promise((resolve, reject) => {
    execFile(
      cmd,
      args,
      {
        maxBuffer: 10 * 1024 * 1024,
        timeout,
        cwd: ROOT,
        encoding: "utf-8",
      },
      (err, stdout, stderr) => {
        if (err) reject(new Error(`${err.message}\nstderr: ${stderr}`));
        else resolve(stdout);
      }
    );
  });
}

function claudeQuery(
  prompt: string,
  opts?: { model?: string; timeout?: number; allowWrite?: boolean }
): Promise<string> {
  return new Promise((resolve, reject) => {
    const model = opts?.model ?? MODEL;
    const timeout = opts?.timeout ?? 300_000;
    const args = ["-p", "--model", model, "--max-turns", "5"];
    if (opts?.allowWrite) {
      args.push("--allowedTools", "Read,Write,Edit,Bash");
    } else {
      args.push("--allowedTools", "Read");
    }

    const child = execFile(
      "claude",
      args,
      {
        maxBuffer: 10 * 1024 * 1024,
        timeout,
        env: {
          ...process.env,
          CLAUDE_CODE_DISABLE_NONESSENTIAL: "1",
          CLAUDECODE: "",
        },
        encoding: "utf-8",
        cwd: ROOT,
      },
      (err, stdout) => {
        if (err) reject(err);
        else resolve(stdout);
      }
    );

    child.stdin?.write(prompt);
    child.stdin?.end();
  });
}

function parseEvalResults(): {
  auc_roc: number;
  precision_at_80_recall: number;
  n_features: number;
  model_type: string;
} | null {
  try {
    const data = JSON.parse(readFileSync(LAST_EVAL_PATH, "utf-8"));
    return data;
  } catch {
    return null;
  }
}

function initResultsTsv() {
  if (!existsSync(RESULTS_TSV)) {
    writeFileSync(
      RESULTS_TSV,
      "experiment_id\ttimestamp\tchanges\tauc_roc\tprecision_at_80recall\tn_features\tmodel_type\tdecision\n"
    );
  }
}

function logResult(
  round: number,
  changes: string,
  auc: number,
  p80r: number,
  nFeatures: number,
  modelType: string,
  decision: string
) {
  const row = [
    `exp-${String(round).padStart(3, "0")}`,
    new Date().toISOString(),
    changes.replace(/\t/g, " ").replace(/\n/g, " "),
    auc.toFixed(6),
    p80r.toFixed(6),
    nFeatures,
    modelType,
    decision,
  ].join("\t");
  appendFileSync(RESULTS_TSV, row + "\n");
}

// ---------------------------------------------------------------------------
// Main Loop
// ---------------------------------------------------------------------------

async function main() {
  console.log("=== Autoresearch: Clinical Trial Outcome Predictor ===");
  console.log(`Max rounds: ${MAX_ROUNDS}`);
  console.log(`Model: ${MODEL}`);
  console.log(`Project dir: ${ROOT}`);
  console.log("");

  mkdirSync(LOG_DIR, { recursive: true });
  initResultsTsv();

  // Load research program
  const program = readFileSync(PROGRAM_PATH, "utf-8");

  // Track best AUC
  let bestAuc = 0;

  for (let round = 1; round <= MAX_ROUNDS; round++) {
    console.log(`\n--- Round ${round}/${MAX_ROUNDS} ---`);

    // Read current state
    const currentFeatures = readFileSync(FEATURES_PATH, "utf-8");
    const currentTrain = readFileSync(TRAIN_PATH, "utf-8");
    const resultsLog = existsSync(RESULTS_TSV)
      ? readFileSync(RESULTS_TSV, "utf-8")
      : "(no results yet)";

    // Ask agent to modify features.py and/or train.py
    const modifyPrompt = `
You are an autonomous ML research agent. Your task is to improve a Clinical Trial Outcome Predictor.

## Research Program
${program}

## Current features.py
\`\`\`python
${currentFeatures}
\`\`\`

## Current train.py
\`\`\`python
${currentTrain}
\`\`\`

## Experiment History
\`\`\`
${resultsLog}
\`\`\`

## Current best AUC-ROC: ${bestAuc.toFixed(6)}

## Instructions

1. Review the experiment history and current code
2. Formulate a hypothesis about what change will improve AUC-ROC
3. Modify features.py and/or train.py by writing the updated files
4. Write the files to: ${FEATURES_PATH} and/or ${TRAIN_PATH}
5. Explain your hypothesis in 1-2 sentences

IMPORTANT: Write the complete file contents. Do not skip sections with "...".
Focus on ONE change at a time to isolate what works.
`;

    try {
      console.log("  Asking agent for modifications...");
      const response = await claudeQuery(modifyPrompt, {
        allowWrite: true,
        timeout: 300_000,
      });

      // Extract what changed from the agent's response
      const changesSummary = response.slice(0, 200).replace(/\n/g, " ");
      console.log(`  Changes: ${changesSummary}`);

      // Save agent response to logs
      writeFileSync(
        join(LOG_DIR, `round-${round}-agent.txt`),
        response
      );

      // Run training
      console.log("  Training...");
      const trainOutput = await run("python3", ["train.py"]);
      console.log(`  ${trainOutput.split("\n").slice(0, 3).join(" | ")}`);

      // Run evaluation
      console.log("  Evaluating...");
      const evalOutput = await run("python3", ["evaluate.py"]);
      console.log(`  ${evalOutput}`);

      // Parse results
      const results = parseEvalResults();
      if (!results) {
        console.log("  ERROR: Could not parse evaluation results");
        logResult(round, changesSummary, 0, 0, 0, "error", "error");
        continue;
      }

      const { auc_roc, precision_at_80_recall, n_features, model_type } = results;

      // Decision: keep or discard
      const improvement = auc_roc - bestAuc;
      let decision: string;

      if (auc_roc > bestAuc + 0.001) {
        decision = "KEEP";
        bestAuc = auc_roc;
        console.log(
          `  ✓ KEEP: AUC ${auc_roc.toFixed(4)} (+${improvement.toFixed(4)})`
        );

        // Git commit the improvement
        try {
          await run("git", ["add", "features.py", "train.py"]);
          await run("git", [
            "commit",
            "-m",
            `autoresearch: AUC ${auc_roc.toFixed(4)} (+${improvement.toFixed(4)}) — ${changesSummary.slice(0, 72)}`,
          ]);
        } catch {
          console.log("  (git commit skipped)");
        }
      } else if (
        Math.abs(auc_roc - bestAuc) <= 0.001 &&
        n_features <
          (parseEvalResults()?.n_features ?? Infinity)
      ) {
        decision = "KEEP (simpler)";
        bestAuc = auc_roc;
        console.log(
          `  ✓ KEEP (simpler): AUC ${auc_roc.toFixed(4)}, fewer features`
        );
      } else {
        decision = "DISCARD";
        console.log(
          `  ✗ DISCARD: AUC ${auc_roc.toFixed(4)} (best: ${bestAuc.toFixed(4)})`
        );

        // Revert changes
        try {
          await run("git", ["checkout", "--", "features.py", "train.py"]);
        } catch {
          console.log("  (git revert skipped)");
        }
      }

      logResult(
        round,
        changesSummary,
        auc_roc,
        precision_at_80_recall,
        n_features,
        model_type,
        decision
      );

      // Save round results
      writeFileSync(
        join(LOG_DIR, `round-${round}-results.json`),
        JSON.stringify({ round, ...results, decision, changes: changesSummary }, null, 2)
      );
    } catch (err: any) {
      console.log(`  ERROR: ${err.message?.slice(0, 200)}`);
      logResult(round, "error", 0, 0, 0, "error", "error");

      // Revert on error
      try {
        await run("git", ["checkout", "--", "features.py", "train.py"]);
      } catch {}
    }
  }

  console.log("\n=== Autoresearch Complete ===");
  console.log(`Best AUC-ROC: ${bestAuc.toFixed(6)}`);
  console.log(`Results: ${RESULTS_TSV}`);
  console.log(`Logs: ${LOG_DIR}`);
}

main().catch(console.error);
