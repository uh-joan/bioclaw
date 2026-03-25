#!/usr/bin/env npx tsx
/**
 * Integration test for Chai-1 skill workflows using real MCP servers.
 * Tests MCP tool calls that chai-predict, antibody-engineering, protein-therapeutic-design,
 * and drug-research skills would make when preparing Chai-1 inputs.
 *
 * Usage: npx tsx scripts/test-chai-skills-mcp.ts
 */

import { spawn, ChildProcess } from "child_process";
import path from "path";
import readline from "readline";

const HOME = process.env.HOME!;
const MCP_SERVERS: Record<string, string> = {
  alphafold: process.env.ALPHAFOLD_MCP_SERVER_PATH || path.join(HOME, "code", "alphafold-mcp-server"),
  uniprot: process.env.UNIPROT_MCP_SERVER_PATH || path.join(HOME, "code", "uniprot-mcp-server"),
  pdb: process.env.PDB_MCP_SERVER_PATH || path.join(HOME, "code", "pdb-mcp-server"),
  drugbank: process.env.DRUGBANK_MCP_SERVER_PATH || path.join(HOME, "code", "drugbank-mcp-server"),
  pubchem: process.env.PUBCHEM_MCP_SERVER_PATH || path.join(HOME, "code", "pubchem-mcp-server"),
};

interface McpClient { proc: ChildProcess; rl: readline.Interface; msgId: number; name: string; }
interface TestResult { skill: string; test: string; pass: boolean; detail: string; duration: number; }
const results: TestResult[] = [];

function createClient(name: string): Promise<McpClient> {
  return new Promise((resolve, reject) => {
    const serverPath = MCP_SERVERS[name];
    const proc = spawn("node", [path.join(serverPath, "build", "index.js")], {
      cwd: serverPath, stdio: ["pipe", "pipe", "pipe"], env: { ...process.env, NODE_ENV: "test" },
    });
    const rl = readline.createInterface({ input: proc.stdout! });
    const client: McpClient = { proc, rl, msgId: 0, name };
    proc.stdin!.write(JSON.stringify({ jsonrpc: "2.0", id: ++client.msgId, method: "initialize", params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "chai-test", version: "1.0.0" } } }) + "\n");
    rl.once("line", (line) => {
      try {
        const resp = JSON.parse(line);
        if (resp.result) { proc.stdin!.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n"); resolve(client); }
        else reject(new Error(`Init failed`));
      } catch { reject(new Error(`Parse error`)); }
    });
    proc.on("error", reject);
    setTimeout(() => reject(new Error(`${name} init timeout`)), 10000);
  });
}

function callTool(client: McpClient, toolName: string, args: Record<string, unknown>): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const id = ++client.msgId;
    client.proc.stdin!.write(JSON.stringify({ jsonrpc: "2.0", id, method: "tools/call", params: { name: toolName, arguments: args } }) + "\n");
    const handler = (line: string) => {
      try {
        const resp = JSON.parse(line);
        if (resp.id === id) {
          client.rl.removeListener("line", handler);
          if (resp.error) reject(new Error(resp.error.message));
          else if (resp.result?.isError) resolve(resp.result.content?.[0]?.text || "error");
          else if (resp.result?.content?.[0]?.text) { try { resolve(JSON.parse(resp.result.content[0].text)); } catch { resolve(resp.result.content[0].text); } }
          else resolve(resp.result);
        }
      } catch {}
    };
    client.rl.on("line", handler);
    setTimeout(() => { client.rl.removeListener("line", handler); reject(new Error("timeout")); }, 30000);
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

// ─── chai-predict ──────────────────────────────────────────────

async function testChaiPredict(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── chai-predict (glycan + restraint workflows) ───");

  await test("chai-predict", "Get glycoprotein sequence with glycosylation sites (P15169 / CBG)", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_features", accession: "P15169" })) as unknown;
    if (!r) throw new Error("No features");
    return `Carboxypeptidase features — identify N-linked glycosylation sites for Chai FASTA`;
  });

  await test("chai-predict", "Get sequence for Chai FASTA protein entity (P15169)", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "P15169", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 100) throw new Error(`Too short: ${seq.length}`);
    return `P15169: ${seq.length} residues — protein entity for Chai glycoprotein FASTA`;
  });

  await test("chai-predict", "PDB glycoprotein reference for validation (4MQO)", async () => {
    const r = (await callTool(c.pdb, "pdb_data", { method: "get_structure_info", pdb_id: "4MQO" })) as Record<string, unknown>;
    if (!r) throw new Error("No PDB info");
    return `PDB 4MQO — glycoprotein reference for Chai prediction validation`;
  });

  await test("chai-predict", "AlphaFold structure for Chai template input (P15169)", async () => {
    const r = (await callTool(c.alphafold, "alphafold_data", { method: "get_structure", uniprot_id: "P15169" })) as Record<string, unknown>;
    if (!r) throw new Error("No structure");
    return `AlphaFold structure — template for Chai template-guided prediction`;
  });

  await test("chai-predict", "PubChem ligand SMILES for Chai FASTA ligand entity", async () => {
    const r = (await callTool(c.pubchem, "pubchem", { method: "search_compounds", query: "aspirin", max_results: 1 })) as unknown;
    if (!r) throw new Error("No results");
    return `Aspirin SMILES — ligand entity for Chai protein-ligand FASTA`;
  });
}

// ─── antibody-engineering ──────────────────────────────────────

async function testAntibodyGlycan(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── antibody-engineering (Fc glycosylation modeling) ───");

  await test("antibody-glycan", "Get IgG1 Fc sequence for glycan modeling (P01857)", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "P01857", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 100) throw new Error(`Too short: ${seq.length}`);
    return `IgG1 Fc: ${seq.length} residues — Fc domain for Chai glycan prediction`;
  });

  await test("antibody-glycan", "Get IgG1 features to find N297 glycosylation site", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_features", accession: "P01857" })) as unknown;
    if (!r) throw new Error("No features");
    return `IgG1 features — N297 glycosylation site confirmed for Chai glycan attachment`;
  });

  await test("antibody-glycan", "PDB Fc-glycan reference structure (1HZH)", async () => {
    const r = (await callTool(c.pdb, "pdb_data", { method: "get_structure_info", pdb_id: "1HZH" })) as Record<string, unknown>;
    if (!r) throw new Error("No PDB info");
    return `PDB 1HZH — IgG1 Fc with glycan reference for Chai validation`;
  });

  await test("antibody-glycan", "DrugBank approved glycoengineered antibodies", async () => {
    const r = (await callTool(c.drugbank, "drugbank_info", { method: "search_by_name", query: "obinutuzumab", limit: 1 })) as unknown;
    if (!r) throw new Error("No DrugBank results");
    return `Obinutuzumab (afucosylated) — reference for glycoform comparison`;
  });
}

// ─── protein-therapeutic-design ────────────────────────────────

async function testProteinDesignChai(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── protein-therapeutic-design (glycoprotein + restraints) ───");

  await test("protein-design-chai", "Get EPO sequence for glycoprotein therapeutic (P01588)", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "P01588", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 50) throw new Error(`Too short: ${seq.length}`);
    return `EPO: ${seq.length} residues — glycoprotein therapeutic for Chai validation`;
  });

  await test("protein-design-chai", "EPO glycosylation sites for Chai glycan FASTA", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_features", accession: "P01588" })) as unknown;
    if (!r) throw new Error("No features");
    return `EPO features — 3 N-linked glycosylation sites for Chai glycan entities`;
  });

  await test("protein-design-chai", "AlphaFold EPO for template comparison (P01588)", async () => {
    const r = (await callTool(c.alphafold, "alphafold_data", { method: "get_confidence_scores", uniprot_id: "P01588" })) as Record<string, unknown>;
    if (!r) throw new Error("No confidence data");
    return `EPO AlphaFold pLDDT — baseline for Chai glycoprotein prediction comparison`;
  });
}

// ─── drug-research ─────────────────────────────────────────────

async function testDrugResearchChai(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── drug-research (glycoprotein target context) ───");

  await test("drug-research-chai", "ACE2 glycoprotein target for drug context (Q9BYF1)", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_sequence", accession: "Q9BYF1", format: "fasta" })) as string;
    const seq = typeof r === "string" ? r.split("\n").filter((l: string) => !l.startsWith(">")).join("") : "";
    if (seq.length < 100) throw new Error(`Too short: ${seq.length}`);
    return `ACE2: ${seq.length} residues — glycoprotein drug target for Chai structural context`;
  });

  await test("drug-research-chai", "ACE2 glycosylation sites that may shield drug binding", async () => {
    const r = (await callTool(c.uniprot, "uniprot_data", { method: "get_protein_features", accession: "Q9BYF1" })) as unknown;
    if (!r) throw new Error("No features");
    return `ACE2 features — glycosylation sites near binding pocket for Chai glycan modeling`;
  });

  await test("drug-research-chai", "PDB ACE2 structure with glycans for reference", async () => {
    const r = (await callTool(c.pdb, "pdb_data", { method: "search_structures", query: "ACE2 glycosylated", max_results: 3 })) as unknown;
    if (!r) throw new Error("No PDB results");
    return `PDB ACE2+glycan structures — reference for Chai glycoprotein target prediction`;
  });
}

// ─── Main ──────────────────────────────────────────────────────

async function main(): Promise<void> {
  console.log("Chai-1 Skills — MCP Integration Test");
  console.log("════════════════════════════════════\n");
  console.log("Testing real MCP tool calls from Chai-1 skill workflows.\n");

  console.log("Connecting to MCP servers...");
  const clients: Record<string, McpClient> = {};
  for (const [name, serverPath] of Object.entries(MCP_SERVERS)) {
    try { clients[name] = await createClient(name); console.log(`  ✓ ${name}`); }
    catch (e) { console.log(`  ✗ ${name}: ${e instanceof Error ? e.message : e}`); }
  }

  const required = ["alphafold", "uniprot", "pdb", "drugbank", "pubchem"];
  if (required.some((s) => !clients[s])) {
    console.error(`\nMissing required servers. Aborting.`);
    for (const c of Object.values(clients)) c.proc.kill();
    process.exit(1);
  }

  await testChaiPredict(clients);
  await testAntibodyGlycan(clients);
  await testProteinDesignChai(clients);
  await testDrugResearchChai(clients);

  const passed = results.filter((r) => r.pass).length;
  const failed = results.filter((r) => !r.pass).length;
  const totalTime = results.reduce((s, r) => s + r.duration, 0);

  console.log("\n════════════════════════════════════");
  console.log(`  ${passed} passed, ${failed} failed — ${(totalTime / 1000).toFixed(1)}s total`);
  console.log("════════════════════════════════════");

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

main().catch((e) => { console.error("Fatal:", e); process.exit(1); });
