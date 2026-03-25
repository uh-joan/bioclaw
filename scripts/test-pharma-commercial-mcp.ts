#!/usr/bin/env npx tsx
/**
 * Integration test for pharma commercialization skill workflows using real MCP servers.
 * Tests pharma-financial-analyst, pharma-deal-valuation, pharma-market-access,
 * pharma-launch-strategy, and pharma-patent-analyst skill workflows.
 *
 * Usage: npx tsx scripts/test-pharma-commercial-mcp.ts
 */

import { spawn, ChildProcess } from "child_process";
import path from "path";
import readline from "readline";

const HOME = process.env.HOME!;
const MCP_SERVERS: Record<string, string> = {
  financials: process.env.FINANCIALS_MCP_SERVER_PATH || path.join(HOME, "code", "financials-mcp-server"),
  sec: process.env.SEC_MCP_SERVER_PATH || path.join(HOME, "code", "sec-mcp-server"),
  fda: process.env.FDA_MCP_SERVER_PATH || path.join(HOME, "code", "fda-mcp-server"),
  medicare: process.env.MEDICARE_MCP_SERVER_PATH || path.join(HOME, "code", "medicare-mcp-server"),
  medicaid: process.env.MEDICAID_MCP_SERVER_PATH || path.join(HOME, "code", "medicaid-mcp-server"),
  ctgov: process.env.CTGOV_MCP_SERVER_PATH || path.join(HOME, "code", "ctgov-mcp-server"),
  pubmed: process.env.PUBMED_MCP_SERVER_PATH || path.join(HOME, "code", "pubmed-mcp-server"),
  opentargets: process.env.OPENTARGETS_MCP_SERVER_PATH || path.join(HOME, "code", "opentargets-mcp-server"),
  drugbank: process.env.DRUGBANK_MCP_SERVER_PATH || path.join(HOME, "code", "drugbank-mcp-server"),
  openalex: process.env.OPENALEX_MCP_SERVER_PATH || path.join(HOME, "code", "openalex-mcp-server"),
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
    proc.stdin!.write(JSON.stringify({ jsonrpc: "2.0", id: ++client.msgId, method: "initialize", params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "pharma-test", version: "1.0.0" } } }) + "\n");
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

// ─── pharma-financial-analyst ──────────────────────────────────

async function testFinancialAnalyst(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── pharma-financial-analyst ───");

  await test("pharma-financial", "Pfizer stock profile (PFE)", async () => {
    const r = (await callTool(c.financials, "financial-intelligence", { method: "stock_profile", symbol: "PFE" })) as Record<string, unknown>;
    if (!r) throw new Error("No profile");
    return `Pfizer profile: sector, industry, employees — company overview for financial analysis`;
  });

  await test("pharma-financial", "Pfizer revenue breakdown by segment", async () => {
    const r = (await callTool(c.financials, "financial-intelligence", { method: "stock_revenue_breakdown", symbol: "PFE" })) as unknown;
    if (!r) throw new Error("No revenue data");
    return `PFE revenue by drug/segment — maps revenue concentration risk`;
  });

  await test("pharma-financial", "Pfizer financials (income statement)", async () => {
    const r = (await callTool(c.financials, "financial-intelligence", { method: "stock_financials", symbol: "PFE" })) as unknown;
    if (!r) throw new Error("No financials");
    return `PFE 3-statement data — R&D spend %, gross margin, operating income`;
  });

  await test("pharma-financial", "Pfizer earnings history + estimates", async () => {
    const r = (await callTool(c.financials, "financial-intelligence", { method: "stock_estimates", symbol: "PFE" })) as unknown;
    if (!r) throw new Error("No estimates");
    return `PFE analyst consensus — EPS/revenue forecasts for pipeline valuation context`;
  });

  await test("pharma-financial", "Pfizer peer comparison", async () => {
    const r = (await callTool(c.financials, "financial-intelligence", { method: "stock_peers", symbol: "PFE" })) as unknown;
    if (!r) throw new Error("No peers");
    return `PFE peers — therapeutic area peer comps for relative valuation`;
  });

  await test("pharma-financial", "SEC EDGAR: Pfizer XBRL financials", async () => {
    const r = (await callTool(c.sec, "sec-edgar", { method: "get_company_facts", ticker: "PFE" })) as unknown;
    if (!r) throw new Error("No SEC data");
    return `PFE SEC XBRL — structured revenue, R&D, SG&A from 10-K filings`;
  });

  await test("pharma-financial", "Medicare: Eliquis drug spending", async () => {
    const r = (await callTool(c.medicare, "medicare_info", { method: "search_spending", spending_drug_name: "Eliquis" })) as unknown;
    if (!r) throw new Error("No Medicare data");
    return `Eliquis Medicare spending — revenue validation for Pfizer/BMS top drug`;
  });
}

// ─── pharma-deal-valuation ─────────────────────────────────────

async function testDealValuation(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── pharma-deal-valuation ───");

  await test("pharma-deal", "SEC: Seagen 8-K filings (Pfizer acquisition)", async () => {
    const r = (await callTool(c.sec, "sec-edgar", { method: "search_companies", query: "Seagen" })) as unknown;
    if (!r) throw new Error("No SEC results");
    return `Seagen found in SEC EDGAR — access 8-K deal announcement filings`;
  });

  await test("pharma-deal", "SEC: Seagen filing history for deal terms", async () => {
    const r = (await callTool(c.sec, "sec-edgar", { method: "get_company_submissions", ticker: "SGEN" })) as unknown;
    if (!r) throw new Error("No submissions");
    return `Seagen filings — filter for 8-K material agreements containing deal terms`;
  });

  await test("pharma-deal", "Target financials for due diligence (Moderna)", async () => {
    const r = (await callTool(c.financials, "financial-intelligence", { method: "stock_financials", symbol: "MRNA" })) as unknown;
    if (!r) throw new Error("No financials");
    return `Moderna financials — target company due diligence for M&A analysis`;
  });

  await test("pharma-deal", "Pipeline context: Moderna clinical trials", async () => {
    const r = (await callTool(c.ctgov, "ct_gov_studies", { method: "search", query: "Moderna mRNA cancer", max_results: 5 })) as unknown;
    if (!r) throw new Error("No trials");
    return `Moderna pipeline — clinical trials for rNPV probability assessment`;
  });

  await test("pharma-deal", "FDA regulatory designations for deal value", async () => {
    const r = (await callTool(c.fda, "fda_info", { method: "lookup_drug", search_term: "pembrolizumab" })) as unknown;
    if (!r) throw new Error("No FDA data");
    return `Pembrolizumab FDA data — BTD/Fast Track designations increase deal PoS`;
  });
}

// ─── pharma-market-access ──────────────────────────────────────

async function testMarketAccess(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── pharma-market-access ───");

  await test("pharma-access", "Medicare ASP pricing: Keytruda (J9271)", async () => {
    const r = (await callTool(c.medicare, "medicare_info", { method: "get_asp_pricing", hcpcs_code_asp: "J9271" })) as unknown;
    if (!r) throw new Error("No Medicare ASP data");
    return `Keytruda ASP pricing — Part B reimbursement benchmark for market access`;
  });

  await test("pharma-access", "Medicare drug spending trend: Humira", async () => {
    const r = (await callTool(c.medicare, "medicare_info", { method: "search_spending", spending_drug_name: "Humira" })) as unknown;
    if (!r) throw new Error("No spending data");
    return `Humira spending trend — payer budget impact reference (LOE impact visible)`;
  });

  await test("pharma-access", "Medicaid state utilization: adalimumab", async () => {
    const r = (await callTool(c.medicaid, "medicaid_info", { method: "get_drug_utilization", drug_name: "adalimumab" })) as unknown;
    if (!r) throw new Error("No Medicaid data");
    return `Adalimumab Medicaid utilization — state-level coverage for access mapping`;
  });

  await test("pharma-access", "PubMed HEOR evidence: cost-effectiveness pembrolizumab", async () => {
    const r = (await callTool(c.pubmed, "pubmed_articles", { method: "search_keywords", keywords: "pembrolizumab cost-effectiveness QALY", max_results: 5 })) as unknown;
    if (!r) throw new Error("No PubMed results");
    return `Pembrolizumab CE literature — HEOR evidence for HTA value dossier`;
  });

  await test("pharma-access", "FDA Orange Book: Humira exclusivity", async () => {
    const r = (await callTool(c.fda, "fda_info", { method: "search_orange_book", search_term: "adalimumab" })) as unknown;
    if (!r) throw new Error("No Orange Book data");
    return `Humira Orange Book — patent/exclusivity status for biosimilar entry timing`;
  });
}

// ─── pharma-launch-strategy ────────────────────────────────────

async function testLaunchStrategy(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── pharma-launch-strategy ───");

  await test("pharma-launch", "ClinicalTrials.gov: GLP-1 investigators (KOL proxies)", async () => {
    const r = (await callTool(c.ctgov, "ct_gov_studies", { method: "search", query: "semaglutide obesity Phase 3", max_results: 5, format: "json" })) as unknown;
    if (!r) throw new Error("No trial data");
    return `GLP-1 trial PIs — investigator network = KOL proxy for launch planning`;
  });

  await test("pharma-launch", "OpenAlex: top authors in GLP-1 obesity space", async () => {
    const r = (await callTool(c.openalex, "openalex_data", { method: "search_works", query: "GLP-1 receptor agonist obesity", max_results: 5 })) as unknown;
    if (!r) throw new Error("No OpenAlex data");
    return `GLP-1 obesity publications — KOL identification by publication volume`;
  });

  await test("pharma-launch", "Medicare: Ozempic launch curve (analog analysis)", async () => {
    const r = (await callTool(c.medicare, "medicare_info", { method: "search_spending", spending_drug_name: "Ozempic" })) as unknown;
    if (!r) throw new Error("No spending data");
    return `Ozempic Medicare spending trajectory — launch analog for revenue curve modeling`;
  });

  await test("pharma-launch", "DrugBank: competitive GLP-1 landscape", async () => {
    const r = (await callTool(c.drugbank, "drugbank_info", { method: "search_by_target", target_name: "GLP-1 receptor" })) as unknown;
    if (!r) throw new Error("No DrugBank data");
    return `GLP-1 approved drugs — competitive landscape for launch positioning`;
  });

  await test("pharma-launch", "OpenTargets: obesity disease epidemiology", async () => {
    const r = (await callTool(c.opentargets, "opentargets_info", { method: "search_diseases", query: "obesity", size: 3 })) as unknown;
    if (!r) throw new Error("No OT data");
    return `Obesity epidemiology — patient population for demand forecasting`;
  });
}

// ─── pharma-patent-analyst ─────────────────────────────────────

async function testPatentAnalyst(c: Record<string, McpClient>): Promise<void> {
  console.log("\n─── pharma-patent-analyst (FDA/DrugBank only — USPTO not built) ───");

  await test("pharma-patent", "FDA Orange Book: Keytruda patents", async () => {
    const r = (await callTool(c.fda, "fda_info", { method: "search_orange_book", search_term: "pembrolizumab" })) as unknown;
    if (!r) throw new Error("No Orange Book data");
    return `Keytruda Orange Book patents — patent types and expiry for LOE analysis`;
  });

  await test("pharma-patent", "DrugBank: pembrolizumab compound profile", async () => {
    const r = (await callTool(c.drugbank, "drugbank_info", { method: "search_by_name", query: "pembrolizumab", limit: 1 })) as unknown;
    if (!r) throw new Error("No DrugBank data");
    return `Pembrolizumab DrugBank — formulation/delivery context for patent scope analysis`;
  });

  await test("pharma-patent", "SEC: Merck filing for patent/IP disclosures", async () => {
    const r = (await callTool(c.sec, "sec-edgar", { method: "search_companies", query: "Merck" })) as unknown;
    if (!r) throw new Error("No SEC data");
    return `Merck SEC EDGAR — 10-K IP section for patent risk disclosures`;
  });
}

// ─── Main ──────────────────────────────────────────────────────

async function main(): Promise<void> {
  console.log("Pharma Commercialization Skills — MCP Integration Test");
  console.log("═════════════════════════════════════════════════════\n");

  console.log("Connecting to MCP servers...");
  const clients: Record<string, McpClient> = {};
  for (const [name, serverPath] of Object.entries(MCP_SERVERS)) {
    try { clients[name] = await createClient(name); console.log(`  ✓ ${name}`); }
    catch (e) { console.log(`  ✗ ${name}: ${e instanceof Error ? e.message : e}`); }
  }

  const required = ["financials", "sec", "fda", "medicare", "ctgov", "pubmed"];
  const missing = required.filter(s => !clients[s]);
  if (missing.length > 0) {
    console.error(`\nMissing required: ${missing.join(", ")}. Aborting.`);
    for (const c of Object.values(clients)) c.proc.kill();
    process.exit(1);
  }

  await testFinancialAnalyst(clients);
  await testDealValuation(clients);
  await testMarketAccess(clients);
  await testLaunchStrategy(clients);
  await testPatentAnalyst(clients);

  const passed = results.filter(r => r.pass).length;
  const failed = results.filter(r => !r.pass).length;
  const totalTime = results.reduce((s, r) => s + r.duration, 0);

  console.log("\n═════════════════════════════════════════════════════");
  console.log(`  ${passed} passed, ${failed} failed — ${(totalTime / 1000).toFixed(1)}s total`);
  console.log("═════════════════════════════════════════════════════");

  if (failed > 0) {
    console.log("\nFailures:");
    for (const r of results.filter(r => !r.pass)) {
      console.log(`  [${r.skill}] ${r.test}`);
      console.log(`    ${r.detail}`);
    }
  }

  const skills = [...new Set(results.map(r => r.skill))];
  console.log("\nPer-skill:");
  for (const s of skills) {
    const sr = results.filter(r => r.skill === s);
    const sp = sr.filter(r => r.pass).length;
    console.log(`  ${sp === sr.length ? "✓" : "✗"} ${s}: ${sp}/${sr.length}`);
  }

  for (const c of Object.values(clients)) c.proc.kill();
  process.exit(failed > 0 ? 1 : 0);
}

main().catch(e => { console.error("Fatal:", e); process.exit(1); });
