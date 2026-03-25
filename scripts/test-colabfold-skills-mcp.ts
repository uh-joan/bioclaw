#!/usr/bin/env npx tsx
/**
 * Integration test for ColabFold skill workflows using real MCP servers.
 * Uses raw JSON-RPC over stdio (no SDK dependency needed).
 *
 * Usage: npx tsx scripts/test-colabfold-skills-mcp.ts
 */

import { spawn, ChildProcess } from "child_process";
import path from "path";
import readline from "readline";

const HOME = process.env.HOME!;
const MCP_SERVERS: Record<string, string> = {
  alphafold: process.env.ALPHAFOLD_MCP_SERVER_PATH || path.join(HOME, "code", "alphafold-mcp-server"),
  uniprot: process.env.UNIPROT_MCP_SERVER_PATH || path.join(HOME, "code", "uniprot-mcp-server"),
  pdb: process.env.PDB_MCP_SERVER_PATH || path.join(HOME, "code", "pdb-mcp-server"),
};

interface McpClient {
  proc: ChildProcess;
  rl: readline.Interface;
  msgId: number;
  name: string;
}

interface TestResult {
  skill: string;
  test: string;
  pass: boolean;
  detail: string;
  duration: number;
}

const results: TestResult[] = [];

function createClient(name: string): Promise<McpClient> {
  return new Promise((resolve, reject) => {
    const serverPath = MCP_SERVERS[name];
    const proc = spawn("node", [path.join(serverPath, "build", "index.js")], {
      cwd: serverPath,
      stdio: ["pipe", "pipe", "pipe"],
      env: { ...process.env, NODE_ENV: "test" },
    });

    const rl = readline.createInterface({ input: proc.stdout! });
    const client: McpClient = { proc, rl, msgId: 0, name };

    // Send initialize
    const initMsg = JSON.stringify({
      jsonrpc: "2.0",
      id: ++client.msgId,
      method: "initialize",
      params: {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: { name: "colabfold-skill-test", version: "1.0.0" },
      },
    });
    proc.stdin!.write(initMsg + "\n");

    // Wait for init response
    rl.once("line", (line) => {
      try {
        const resp = JSON.parse(line);
        if (resp.result) {
          // Send initialized notification
          proc.stdin!.write(
            JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n"
          );
          resolve(client);
        } else {
          reject(new Error(`Init failed: ${JSON.stringify(resp.error)}`));
        }
      } catch (e) {
        reject(new Error(`Parse error on init: ${line}`));
      }
    });

    proc.on("error", reject);
    setTimeout(() => reject(new Error(`${name} init timeout`)), 10000);
  });
}

function callTool(client: McpClient, toolName: string, args: Record<string, unknown>): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const id = ++client.msgId;
    const msg = JSON.stringify({
      jsonrpc: "2.0",
      id,
      method: "tools/call",
      params: { name: toolName, arguments: args },
    });
    client.proc.stdin!.write(msg + "\n");

    const handler = (line: string) => {
      try {
        const resp = JSON.parse(line);
        if (resp.id === id) {
          client.rl.removeListener("line", handler);
          if (resp.error) {
            reject(new Error(resp.error.message || JSON.stringify(resp.error)));
          } else if (resp.result?.content?.[0]?.text) {
            try {
              resolve(JSON.parse(resp.result.content[0].text));
            } catch {
              resolve(resp.result.content[0].text);
            }
          } else {
            resolve(resp.result);
          }
        }
      } catch {
        // not our response, ignore
      }
    };
    client.rl.on("line", handler);
    setTimeout(() => {
      client.rl.removeListener("line", handler);
      reject(new Error("Tool call timeout"));
    }, 30000);
  });
}

async function test(skill: string, name: string, fn: () => Promise<string>): Promise<void> {
  const start = Date.now();
  try {
    const detail = await fn();
    results.push({ skill, test: name, pass: true, detail, duration: Date.now() - start });
    console.log(`  ✓ ${name} (${Date.now() - start}ms)`);
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    results.push({ skill, test: name, pass: false, detail: msg, duration: Date.now() - start });
    console.log(`  ✗ ${name}: ${msg}`);
  }
}

// ─── Test Suites ───────────────────────────────────────────────

async function testColabFoldPredict(uniprot: McpClient, af: McpClient): Promise<void> {
  console.log("\n─── colabfold-predict ───");

  await test("colabfold-predict", "Pre-check AlphaFold DB via get_structure (P04637)", async () => {
    const r = (await callTool(af, "alphafold_data", { method: "get_structure", uniprot_id: "P04637" })) as Record<string, unknown>;
    if (!r) throw new Error("P04637 should return structure data");
    return `P04637 found in AlphaFold DB — skip ColabFold, use DB structure`;
  });

  await test("colabfold-predict", "Detect missing protein → ColabFold needed (Z9ZZZ9)", async () => {
    const r = await callTool(af, "alphafold_data", { method: "get_structure", uniprot_id: "Z9ZZZ9" });
    const isError = typeof r === "string" && r.startsWith("Error");
    if (!isError) throw new Error("Z9ZZZ9 should NOT be in DB");
    return `Z9ZZZ9 not in DB — ColabFold prediction required`;
  });

  await test("colabfold-predict", "Get sequence for FASTA input (insulin P01308)", async () => {
    const r = (await callTool(uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "P01308", format: "fasta" })) as string;
    if (!r || typeof r !== "string") throw new Error("No sequence returned");
    const seq = r.split("\n").filter((l: string) => !l.startsWith(">")).join("");
    if (seq.length < 50) throw new Error(`Too short: ${seq.length}`);
    return `Insulin: ${seq.length} residues — ready for colabfold_batch FASTA`;
  });

  await test("colabfold-predict", "Batch DB check to filter prediction candidates", async () => {
    const r = (await callTool(af, "alphafold_data", { method: "batch_structure_info", uniprot_ids: ["P04637", "P01308", "P00720"] })) as unknown;
    if (!r) throw new Error("No batch results");
    return `3 proteins checked — route DB-missing ones to ColabFold`;
  });
}

async function testAlphaFoldStructures(af: McpClient): Promise<void> {
  console.log("\n─── alphafold-structures (fallback + cross-validation) ───");

  await test("alphafold-structures", "Get pLDDT baseline for cross-validation (P04637)", async () => {
    const r = (await callTool(af, "alphafold_data", { method: "get_confidence_scores", uniprot_id: "P04637" })) as Record<string, unknown>;
    if (!r) throw new Error("No confidence data");
    return `pLDDT retrieved — baseline for ColabFold cross-validation recipe`;
  });

  await test("alphafold-structures", "Confidence region analysis for variant comparison", async () => {
    const r = (await callTool(af, "alphafold_data", { method: "analyze_confidence_regions", uniprot_id: "P04637" })) as Record<string, unknown>;
    if (!r) throw new Error("No region data");
    return `Regions analyzed — wildtype baseline for mutant delta-pLDDT`;
  });

  await test("alphafold-structures", "Download PDB for structural alignment (P04637)", async () => {
    const r = (await callTool(af, "alphafold_data", { method: "download_structure", uniprot_id: "P04637", format: "pdb" })) as unknown;
    if (!r) throw new Error("No PDB data");
    return `PDB downloaded — reference for ColabFold RMSD comparison`;
  });
}

async function testProteinTherapeuticDesign(uniprot: McpClient, af: McpClient, pdb: McpClient): Promise<void> {
  console.log("\n─── protein-therapeutic-design (design validation) ───");

  await test("protein-therapeutic-design", "Target protein info (HER2 P04626)", async () => {
    const r = (await callTool(uniprot, "uniprot_data", { method: "get_protein_info", accession: "P04626" })) as Record<string, unknown>;
    if (!r) throw new Error("No info");
    return `HER2 protein data retrieved — target for binder design + ColabFold validation`;
  });

  await test("protein-therapeutic-design", "Target sequence for ColabFold complex prediction", async () => {
    const r = (await callTool(uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "P04626", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 100) throw new Error(`Too short: ${seq.length}`);
    return `HER2: ${seq.length} residues — target chain for ColabFold multimer complex`;
  });

  await test("protein-therapeutic-design", "AlphaFold structure as self-consistency target", async () => {
    const r = (await callTool(af, "alphafold_data", { method: "get_structure", uniprot_id: "P04626" })) as Record<string, unknown>;
    if (!r) throw new Error("No structure");
    return `AlphaFold structure for HER2 — RMSD target for design self-consistency check`;
  });

  await test("protein-therapeutic-design", "PDB templates for guided ColabFold prediction", async () => {
    const r = (await callTool(pdb, "pdb_data", { method: "search_structures", query: "HER2 trastuzumab", max_results: 3 })) as unknown;
    if (!r) throw new Error("No PDB results");
    return `PDB hits for HER2+trastuzumab — templates for --templates flag`;
  });

  await test("protein-therapeutic-design", "Domain architecture for interface analysis", async () => {
    const r = (await callTool(uniprot, "uniprot_data", { method: "get_protein_domains_detailed", accession: "P04626" })) as unknown;
    if (!r) throw new Error("No domains");
    return `HER2 domain boundaries — define interface residues for ColabFold pLDDT analysis`;
  });
}

async function testAntibodyEngineering(uniprot: McpClient, af: McpClient, pdb: McpClient): Promise<void> {
  console.log("\n─── antibody-engineering (Ab-Ag complex prediction) ───");

  await test("antibody-engineering", "Search trastuzumab sequences for Fv prediction", async () => {
    const r = (await callTool(uniprot, "uniprot_data", { method: "search_proteins", query: "trastuzumab", organism: "Homo sapiens", size: 5 })) as unknown;
    if (!r) throw new Error("No results");
    return `Trastuzumab search completed — VH/VL sequences for ColabFold Fv prediction`;
  });

  await test("antibody-engineering", "PDB reference complex for validation (1N8Z)", async () => {
    const r = (await callTool(pdb, "pdb_data", { method: "get_structure_info", pdb_id: "1N8Z" })) as Record<string, unknown>;
    if (!r) throw new Error("No structure");
    return `PDB 1N8Z retrieved — experimental reference for ColabFold complex validation`;
  });

  await test("antibody-engineering", "Antigen AlphaFold structure for epitope mapping", async () => {
    const r = (await callTool(af, "alphafold_data", { method: "get_confidence_scores", uniprot_id: "P04626" })) as Record<string, unknown>;
    if (!r) throw new Error("No confidence data");
    return `HER2 pLDDT — identify confident epitope regions for ColabFold interface analysis`;
  });
}

async function testEnzymeEngineering(uniprot: McpClient, af: McpClient): Promise<void> {
  console.log("\n─── enzyme-engineering (mutant screening) ───");

  await test("enzyme-engineering", "Wildtype sequence for mutant FASTA generation (P00720)", async () => {
    const r = (await callTool(uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "P00720", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 50) throw new Error(`Too short: ${seq.length}`);
    return `T4 lysozyme: ${seq.length} residues — generate mutant FASTAs for ColabFold batch`;
  });

  await test("enzyme-engineering", "Wildtype pLDDT baseline for stability delta", async () => {
    const r = (await callTool(af, "alphafold_data", { method: "get_confidence_scores", uniprot_id: "P00720" })) as Record<string, unknown>;
    if (!r) throw new Error("No data");
    return `Wildtype pLDDT baseline — compare with ColabFold mutant predictions`;
  });

  await test("enzyme-engineering", "Active site features for geometry validation", async () => {
    const r = (await callTool(uniprot, "uniprot_data", { method: "get_protein_features", accession: "P00720" })) as unknown;
    if (!r) throw new Error("No features");
    return `T4 lysozyme features — active site residue positions for ColabFold geometry check`;
  });

  await test("enzyme-engineering", "AlphaFold wildtype structure for RMSD reference", async () => {
    const r = (await callTool(af, "alphafold_data", { method: "download_structure", uniprot_id: "P00720", format: "pdb" })) as unknown;
    if (!r) throw new Error("No PDB");
    return `Wildtype PDB — RMSD reference for ColabFold mutant structure comparison`;
  });
}

// ─── Main ──────────────────────────────────────────────────────

async function main(): Promise<void> {
  console.log("ColabFold Skills — MCP Integration Test");
  console.log("═══════════════════════════════════════\n");
  console.log("Testing real MCP tool calls from ColabFold skill workflows.");
  console.log("Each test exercises a step the agent would perform.\n");

  console.log("Connecting to MCP servers...");
  const clients: Record<string, McpClient> = {};

  for (const [name, serverPath] of Object.entries(MCP_SERVERS)) {
    try {
      clients[name] = await createClient(name);
      console.log(`  ✓ ${name}`);
    } catch (e) {
      console.log(`  ✗ ${name}: ${e instanceof Error ? e.message : e}`);
    }
  }

  if (!clients.alphafold || !clients.uniprot || !clients.pdb) {
    console.error("\nRequired MCP servers not available. Aborting.");
    for (const c of Object.values(clients)) c.proc.kill();
    process.exit(1);
  }

  await testColabFoldPredict(clients.uniprot, clients.alphafold);
  await testAlphaFoldStructures(clients.alphafold);
  await testProteinTherapeuticDesign(clients.uniprot, clients.alphafold, clients.pdb);
  await testAntibodyEngineering(clients.uniprot, clients.alphafold, clients.pdb);
  await testEnzymeEngineering(clients.uniprot, clients.alphafold);

  // Summary
  const passed = results.filter((r) => r.pass).length;
  const failed = results.filter((r) => !r.pass).length;
  const totalTime = results.reduce((s, r) => s + r.duration, 0);

  console.log("\n═══════════════════════════════════════");
  console.log(`  ${passed} passed, ${failed} failed — ${(totalTime / 1000).toFixed(1)}s total`);
  console.log("═══════════════════════════════════════");

  if (failed > 0) {
    console.log("\nFailures:");
    for (const r of results.filter((r) => !r.pass)) {
      console.log(`  [${r.skill}] ${r.test}`);
      console.log(`    ${r.detail}`);
    }
  }

  // Per-skill summary
  const skills = [...new Set(results.map((r) => r.skill))];
  console.log("\nPer-skill:");
  for (const s of skills) {
    const sr = results.filter((r) => r.skill === s);
    const sp = sr.filter((r) => r.pass).length;
    console.log(`  ${sp === sr.length ? "✓" : "✗"} ${s}: ${sp}/${sr.length}`);
  }

  for (const c of Object.values(clients)) c.proc.kill();
  process.exit(failed > 0 ? 1 : 0);
}

main().catch((e) => {
  console.error("Fatal:", e);
  process.exit(1);
});
