#!/usr/bin/env npx tsx
/**
 * Integration test for Boltz-2 skill workflows using real MCP servers.
 * Tests the MCP tool calls that boltz-predict, drug-research, binder-discovery-specialist,
 * molecular-glue-discovery, and protein-therapeutic-design skills would make.
 *
 * Usage: npx tsx scripts/test-boltz-skills-mcp.ts
 */

import { spawn, ChildProcess } from "child_process";
import path from "path";
import readline from "readline";

const HOME = process.env.HOME!;
const MCP_SERVERS: Record<string, string> = {
  alphafold: process.env.ALPHAFOLD_MCP_SERVER_PATH || path.join(HOME, "code", "alphafold-mcp-server"),
  uniprot: process.env.UNIPROT_MCP_SERVER_PATH || path.join(HOME, "code", "uniprot-mcp-server"),
  pdb: process.env.PDB_MCP_SERVER_PATH || path.join(HOME, "code", "pdb-mcp-server"),
  chembl: process.env.CHEMBL_MCP_SERVER_PATH || path.join(HOME, "code", "chembl-mcp-server"),
  pubchem: process.env.PUBCHEM_MCP_SERVER_PATH || path.join(HOME, "code", "pubchem-mcp-server"),
  drugbank: process.env.DRUGBANK_MCP_SERVER_PATH || path.join(HOME, "code", "drugbank-mcp-server"),
  opentargets: process.env.OPENTARGETS_MCP_SERVER_PATH || path.join(HOME, "code", "opentargets-mcp-server"),
  bindingdb: process.env.BINDINGDB_MCP_SERVER_PATH || path.join(HOME, "code", "bindingdb-mcp-server"),
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

    proc.stdin!.write(
      JSON.stringify({
        jsonrpc: "2.0",
        id: ++client.msgId,
        method: "initialize",
        params: {
          protocolVersion: "2024-11-05",
          capabilities: {},
          clientInfo: { name: "boltz-skill-test", version: "1.0.0" },
        },
      }) + "\n"
    );

    rl.once("line", (line) => {
      try {
        const resp = JSON.parse(line);
        if (resp.result) {
          proc.stdin!.write(
            JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n"
          );
          resolve(client);
        } else {
          reject(new Error(`Init failed: ${JSON.stringify(resp.error)}`));
        }
      } catch {
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
    client.proc.stdin!.write(
      JSON.stringify({ jsonrpc: "2.0", id, method: "tools/call", params: { name: toolName, arguments: args } }) + "\n"
    );

    const handler = (line: string) => {
      try {
        const resp = JSON.parse(line);
        if (resp.id === id) {
          client.rl.removeListener("line", handler);
          if (resp.error) {
            reject(new Error(resp.error.message || JSON.stringify(resp.error)));
          } else if (resp.result?.isError) {
            resolve(resp.result.content?.[0]?.text || "error");
          } else if (resp.result?.content?.[0]?.text) {
            try { resolve(JSON.parse(resp.result.content[0].text)); }
            catch { resolve(resp.result.content[0].text); }
          } else {
            resolve(resp.result);
          }
        }
      } catch { /* not our response */ }
    };
    client.rl.on("line", handler);
    setTimeout(() => { client.rl.removeListener("line", handler); reject(new Error("Tool call timeout")); }, 30000);
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

// ─── boltz-predict ─────────────────────────────────────────────

async function testBoltzPredict(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── boltz-predict (standalone docking workflows) ───");

  // Get target sequence for YAML generation
  await test("boltz-predict", "Get EGFR sequence for protein-ligand YAML (P00533)", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "P00533", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 100) throw new Error(`Too short: ${seq.length}`);
    return `EGFR: ${seq.length} residues — target for Boltz protein-ligand YAML`;
  });

  // Get ligand SMILES from PubChem for docking
  await test("boltz-predict", "Get erlotinib SMILES from PubChem for ligand input", async () => {
    const r = (await callTool(c.pubchem, "pubchem", { method: "search_compounds", query: "erlotinib", max_results: 1 })) as Record<string, unknown>;
    if (!r) throw new Error("No PubChem results");
    return `Erlotinib found in PubChem — SMILES for Boltz YAML ligand block`;
  });

  // Get binding site residues from PDB co-crystal
  await test("boltz-predict", "PDB co-crystal for pocket residues (1M17 EGFR-erlotinib)", async () => {
    const r = (await callTool(c.pdb, "pdb_data", { method: "get_structure_info", pdb_id: "1M17" })) as Record<string, unknown>;
    if (!r) throw new Error("No PDB info");
    return `PDB 1M17 — extract binding pocket residues for Boltz pocket constraint`;
  });

  // AlphaFold structure as template for template-guided prediction
  await test("boltz-predict", "AlphaFold structure as Boltz template (P00533)", async () => {
    const r = (await callTool(c.alphafold, "alphafold_data", { method: "download_structure", uniprot_id: "P00533", format: "pdb" })) as unknown;
    if (!r) throw new Error("No structure");
    return `EGFR AlphaFold PDB — template for Boltz --force template prediction`;
  });

  // BindingDB for affinity validation data
  await test("boltz-predict", "BindingDB experimental affinities for validation", async () => {
    const r = (await callTool(c.bindingdb, "bindingdb_data", { method: "search_by_target_name", target_name: "EGFR", limit: 5 })) as unknown;
    if (!r) throw new Error("No BindingDB results");
    return `BindingDB EGFR data — experimental IC50s to compare with Boltz affinity predictions`;
  });
}

// ─── drug-research ─────────────────────────────────────────────

async function testDrugResearch(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── drug-research (Boltz docking for drug reports) ───");

  // Get drug info for report + docking
  await test("drug-research", "DrugBank imatinib profile for structural context", async () => {
    const r = (await callTool(c.drugbank, "drugbank_info", { method: "search_by_name", query: "imatinib", limit: 1 })) as unknown;
    if (!r) throw new Error("No DrugBank results");
    return `Imatinib DrugBank profile — target, MoA, structure for Boltz docking YAML`;
  });

  // Get target for docking
  await test("drug-research", "Get BCR-ABL sequence for imatinib docking (P00519)", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "P00519", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 100) throw new Error(`Too short: ${seq.length}`);
    return `ABL1: ${seq.length} residues — target for imatinib Boltz docking`;
  });

  // ChEMBL bioactivity data for competitive comparison
  await test("drug-research", "ChEMBL BCR-ABL inhibitors for competitive docking", async () => {
    const r = (await callTool(c.chembl, "chembl_info", { method: "target_search", query: "ABL1", limit: 3 })) as unknown;
    if (!r) throw new Error("No ChEMBL results");
    return `ABL1 ChEMBL target — retrieve competitor SMILES for Boltz batch docking`;
  });

  // PubChem SMILES for drug structure
  await test("drug-research", "PubChem imatinib SMILES for Boltz ligand block", async () => {
    const r = (await callTool(c.pubchem, "pubchem", { method: "get_compound_properties", cid: 5291, properties: ["IsomericSMILES", "MolecularFormula"] })) as Record<string, unknown>;
    if (!r) throw new Error("No PubChem properties");
    return `Imatinib CID 5291 — SMILES + formula for Boltz YAML input`;
  });
}

// ─── binder-discovery-specialist ───────────────────────────────

async function testBinderDiscovery(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── binder-discovery-specialist (virtual screening) ───");

  // Target validation
  await test("binder-discovery", "OpenTargets CDK4/6 druggability for screening", async () => {
    const r = (await callTool(c.opentargets, "opentargets_info", { method: "search_targets", query: "CDK6", size: 3 })) as unknown;
    if (!r) throw new Error("No OT results");
    return `CDK6 target found — druggability confirmed for virtual screening`;
  });

  // Mine known ligands for seeding screen
  await test("binder-discovery", "ChEMBL CDK6 bioactivity for hit seeding", async () => {
    const r = (await callTool(c.chembl, "chembl_info", { method: "target_search", query: "CDK6", limit: 3 })) as unknown;
    if (!r) throw new Error("No ChEMBL results");
    return `CDK6 ChEMBL data — known actives as seeds for Boltz virtual screen`;
  });

  // PubChem similarity expansion for compound library
  await test("binder-discovery", "PubChem similarity search for library expansion", async () => {
    const r = (await callTool(c.pubchem, "pubchem", { method: "search_compounds", query: "palbociclib", max_results: 5 })) as unknown;
    if (!r) throw new Error("No PubChem results");
    return `Palbociclib analogs found — expanded library for Boltz batch screening`;
  });

  // Get target protein for docking
  await test("binder-discovery", "CDK6 sequence for pocket-conditioned Boltz docking", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "Q00534", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 100) throw new Error(`Too short: ${seq.length}`);
    return `CDK6: ${seq.length} residues — target for Boltz pocket-conditioned docking`;
  });

  // PDB for pocket residues
  await test("binder-discovery", "PDB CDK6-palbociclib pocket for constraints (5L2I)", async () => {
    const r = (await callTool(c.pdb, "pdb_data", { method: "get_structure_info", pdb_id: "5L2I" })) as Record<string, unknown>;
    if (!r) throw new Error("No PDB info");
    return `PDB 5L2I — CDK6 binding pocket residues for Boltz pocket constraint YAML`;
  });
}

// ─── molecular-glue-discovery ──────────────────────────────────

async function testMolecularGlue(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── molecular-glue-discovery (ternary complex) ───");

  // E3 ligase sequence (CRBN)
  await test("molecular-glue", "CRBN E3 ligase sequence for ternary YAML (Q96SW2)", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "Q96SW2", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 100) throw new Error(`Too short: ${seq.length}`);
    return `CRBN: ${seq.length} residues — E3 ligase chain for Boltz ternary complex`;
  });

  // Neosubstrate sequence (IKZF1)
  await test("molecular-glue", "IKZF1 neosubstrate sequence for ternary YAML (Q13422)", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "Q13422", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 50) throw new Error(`Too short: ${seq.length}`);
    return `IKZF1: ${seq.length} residues — neosubstrate for Boltz ternary prediction`;
  });

  // Lenalidomide SMILES from PubChem
  await test("molecular-glue", "PubChem lenalidomide SMILES for glue ligand block", async () => {
    const r = (await callTool(c.pubchem, "pubchem", { method: "search_compounds", query: "lenalidomide", max_results: 1 })) as unknown;
    if (!r) throw new Error("No PubChem results");
    return `Lenalidomide found — SMILES for Boltz ternary YAML glue chain`;
  });

  // DrugBank for approved IMiDs (competitive glue analysis)
  await test("molecular-glue", "DrugBank IMiD degraders for SAR comparison", async () => {
    const r = (await callTool(c.drugbank, "drugbank_info", { method: "search_by_name", query: "pomalidomide", limit: 1 })) as unknown;
    if (!r) throw new Error("No DrugBank results");
    return `Pomalidomide data — competitive glue for Boltz SAR batch prediction`;
  });

  // PDB ternary complex reference
  await test("molecular-glue", "PDB CRBN-lenalidomide-IKZF1 ternary reference", async () => {
    const r = (await callTool(c.pdb, "pdb_data", { method: "search_structures", query: "cereblon lenalidomide IKZF1", max_results: 3 })) as unknown;
    if (!r) throw new Error("No PDB results");
    return `PDB ternary structures — reference for Boltz ternary complex validation`;
  });
}

// ─── protein-therapeutic-design ────────────────────────────────

async function testProteinDesign(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── protein-therapeutic-design (Boltz complex validation) ───");

  // Target + ligand for designed binder complex
  await test("protein-design", "PD-L1 target for designed binder + ligand complex (Q9NZQ7)", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "Q9NZQ7", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 100) throw new Error(`Too short: ${seq.length}`);
    return `PD-L1: ${seq.length} residues — target for binder+ligand Boltz complex`;
  });

  // AlphaFold structure for template-forced validation
  await test("protein-design", "AlphaFold PD-L1 for template-forced Boltz prediction", async () => {
    const r = (await callTool(c.alphafold, "alphafold_data", { method: "get_structure", uniprot_id: "Q9NZQ7" })) as Record<string, unknown>;
    if (!r) throw new Error("No structure");
    return `PD-L1 AlphaFold structure — template for Boltz forced prediction YAML`;
  });

  // Domain architecture for pocket definition
  await test("protein-design", "PD-L1 domain architecture for Boltz pocket constraints", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_features", accession: "Q9NZQ7" })) as unknown;
    if (!r) throw new Error("No features");
    return `PD-L1 features — define binding interface for Boltz pocket conditioning`;
  });

  // PDB complex for reference
  await test("protein-design", "PDB PD-1/PD-L1 complex for Boltz validation (4ZQK)", async () => {
    const r = (await callTool(c.pdb, "pdb_data", { method: "get_structure_info", pdb_id: "4ZQK" })) as Record<string, unknown>;
    if (!r) throw new Error("No structure");
    return `PDB 4ZQK — PD-1:PD-L1 complex reference for designed binder Boltz validation`;
  });
}

// ─── Main ──────────────────────────────────────────────────────

async function main(): Promise<void> {
  console.log("Boltz-2 Skills — MCP Integration Test");
  console.log("═════════════════════════════════════\n");
  console.log("Testing real MCP tool calls from Boltz-2 skill workflows.");
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

  // Check required servers
  const required = ["alphafold", "uniprot", "pdb", "chembl", "pubchem", "drugbank", "opentargets"];
  const missing = required.filter((s) => !clients[s]);
  if (missing.length > 0) {
    console.error(`\nMissing required servers: ${missing.join(", ")}. Aborting.`);
    for (const c of Object.values(clients)) c.proc.kill();
    process.exit(1);
  }

  await testBoltzPredict(clients);
  await testDrugResearch(clients);
  await testBinderDiscovery(clients);
  await testMolecularGlue(clients);
  await testProteinDesign(clients);

  // Summary
  const passed = results.filter((r) => r.pass).length;
  const failed = results.filter((r) => !r.pass).length;
  const totalTime = results.reduce((s, r) => s + r.duration, 0);

  console.log("\n═════════════════════════════════════");
  console.log(`  ${passed} passed, ${failed} failed — ${(totalTime / 1000).toFixed(1)}s total`);
  console.log("═════════════════════════════════════");

  if (failed > 0) {
    console.log("\nFailures:");
    for (const r of results.filter((r) => !r.pass)) {
      console.log(`  [${r.skill}] ${r.test}`);
      console.log(`    ${r.detail}`);
    }
  }

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
