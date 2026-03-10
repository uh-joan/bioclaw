<p align="center">
  <img src="assets/nanoclaw-logo.png" alt="BioClaw" width="400">
</p>

<p align="center">
  A biomedical AI assistant with 37 MCP-powered research tools running securely in containers. Built on <a href="https://github.com/qwibitai/nanoclaw">NanoClaw</a>.
</p>

BioClaw bundles 37 pharma and bioinformatics MCP servers directly into the container image — no cloning repos, no configuring paths. One image, zero setup.

## What's Included

**37 MCP servers** covering:

| Category | Servers |
|----------|---------|
| **Drug & Regulatory** | FDA, EMA, DrugBank, ChEMBL, PubChem, OpenTargets, ClinicalTrials.gov |
| **Literature** | PubMed, bioRxiv, OpenAlex, NLM |
| **Genomics & Variants** | ClinVar, COSMIC, GWAS Catalog, gnomAD, Ensembl, GTEx, GEO, JASPAR |
| **Proteomics & Structure** | UniProt, AlphaFold, PDB, STRING-db, BindingDB |
| **Pathways & Ontology** | Reactome, KEGG, Gene Ontology, HPO, Monarch |
| **Cancer & Dependencies** | DepMap, cBioPortal |
| **Metabolomics** | HMDB |
| **Pharmacogenomics** | ClinPGx |
| **Healthcare** | Medicare, Medicaid, CDC, EU Filings |

## Quick Start

```bash
git clone https://github.com/uh-joan/bioclaw.git
cd bioclaw
claude
```

Then run `/setup`. Claude Code handles dependencies, authentication, container setup and service configuration.

## Building the Container

```bash
# Build the MCP-bundled image (stages all 37 servers, then builds)
./container/build-mcp-bundled.sh
```

Set in `.env`:
```bash
CONTAINER_IMAGE=nanoclaw-agent-mcp:latest
```

All MCP servers are pre-built inside the image. No `*_MCP_SERVER_PATH` env vars needed.

### Dev Override

To iterate on a specific MCP server locally, set its path in `.env`:

```bash
# This overrides the bundled version (host mount takes priority)
FDA_MCP_SERVER_PATH=/path/to/my/fda-mcp-server
```

## Architecture

Built on [NanoClaw](https://github.com/qwibitai/nanoclaw) — a lightweight personal Claude assistant.

```
Channels --> SQLite --> Polling loop --> Container (Claude Agent SDK + 37 MCP servers) --> Response
```

Single Node.js process. Agents run in isolated Linux containers with all MCP servers available. The container entrypoint wires up bundled servers via symlinks, with host mounts taking priority for dev overrides.

Key additions over NanoClaw:
- `container/Dockerfile.mcp-bundled` — Dockerfile with all MCP servers baked in
- `container/build-mcp-bundled.sh` — Build script that stages and bundles MCP artifacts
- `container/skills/` — 17 bioinformatics skill sets (immunoinformatics, pharmacogenomics, etc.)

For the full NanoClaw architecture, see [docs/SPEC.md](docs/SPEC.md).

## Channels

Talk to your assistant from WhatsApp, Telegram, Discord, Slack, or Gmail. Add channels with skills:

```
/add-whatsapp
/add-telegram
/add-slack
/add-discord
/add-gmail
```

## Usage

```
@Nano search PubMed for recent CRISPR delivery papers and summarize the top 5
@Nano look up the drug interactions for pembrolizumab using DrugBank and ChEMBL
@Nano find ClinVar variants for BRCA1 classified as pathogenic
@Nano check FDA adverse events for ozempic in the last 6 months
@Nano get the protein structure for P53 from AlphaFold and describe the binding domains
@Nano every Monday at 8am, compile new bioRxiv preprints on single-cell RNA-seq
```

## Customizing

NanoClaw doesn't use configuration files. Tell Claude Code what you want:

- "Add a new MCP server for my internal API"
- "Change the trigger word to @Bio"
- "Store weekly literature summaries in the group folder"

Or run `/customize` for guided changes.

## Requirements

- macOS or Linux
- Node.js 20+
- [Claude Code](https://claude.ai/download)
- [Docker](https://docker.com/products/docker-desktop) (or [Apple Container](https://github.com/apple/container) on macOS)

## Upstream

BioClaw is a fork of [NanoClaw](https://github.com/qwibitai/nanoclaw). To pull upstream updates:

```
/update-nanoclaw
```

## License

MIT
