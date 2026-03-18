# Collect Clinical Trial Data

Write a Python script `collect_real.py` and run it. The script should:

1. Import MCP wrappers from `mcp/servers/`
2. Query ClinicalTrials.gov for completed/terminated Phase 2/3 trials
3. For each trial, query all other MCPs for features
4. Append each trial row to `data/trials_raw.csv` immediately after collecting its features
5. Print progress after each trial

## Setup (top of script)

```python
import sys, os
sys.path.insert(0, os.path.abspath('.'))
os.environ['MCP_CONFIG_FILE'] = os.path.abspath('mcp-config.json')
```

## Available wrappers

All in `mcp/servers/`. Key imports:

```python
from mcp.servers.ct_gov_mcp import search, get_study
from mcp.servers.fda_mcp import lookup_drug
from mcp.servers.opentargets_mcp import search_targets, get_target_disease_associations
from mcp.servers.chembl_mcp import compound_search, get_bioactivity, get_mechanism
from mcp.servers.drugbank_mcp import search_by_name as drugbank_search
from mcp.servers.bindingdb_mcp import search_by_name as bindingdb_search
from mcp.servers.clinpgx_mcp import get_clinical_annotations
from mcp.servers.pubmed_mcp import search_keywords as pubmed_search
from mcp.servers.openalex_mcp import search_works
from mcp.servers.biorxiv_mcp import search_preprints
from mcp.servers.reactome_mcp import find_pathways_by_gene
from mcp.servers.stringdb_mcp import get_protein_interactions
from mcp.servers.gtex_mcp import get_gene_expression
from mcp.servers.gnomad_mcp import get_gene_constraint
from mcp.servers.clinvar_mcp import get_gene_variants_summary
from mcp.servers.gwas_mcp import get_gene_associations
from mcp.servers.depmap_mcp import get_gene_dependency
from mcp.servers.cbioportal_mcp import get_gene as cbioportal_gene
from mcp.servers.hpo_mcp import search_terms as hpo_search
from mcp.servers.monarch_mcp import get_disease_genes
from mcp.servers.ema_mcp import search_medicines as ema_search
```

## CSV schema

Read `collect.py` — it has the full COLUMNS list. Use `csv.DictWriter` with those columns.

## Trials to collect

Hardcode a list of ~60 trials with known outcomes. Mix of successes and failures:

**Successes (FDA-approved drugs, label=1):**
- Pembrolizumab (PDCD1) — KEYNOTE trials in melanoma, NSCLC, etc.
- Nivolumab (PDCD1) — CheckMate trials
- Trastuzumab (ERBB2) — breast cancer
- Olaparib (PARP1) — ovarian, breast
- Osimertinib (EGFR) — NSCLC
- Palbociclib (CDK4/CDK6) — breast cancer
- Atezolizumab (CD274) — bladder, NSCLC
- Durvalumab (CD274) — NSCLC
- Alectinib (ALK) — NSCLC
- Dabrafenib+trametinib (BRAF/MAP2K1) — melanoma
- Ribociclib (CDK4/CDK6) — breast cancer
- Lorlatinib (ALK) — NSCLC
- Sotorasib (KRAS) — NSCLC
- Encorafenib (BRAF) — colorectal
- Tucatinib (ERBB2) — breast cancer
- Capmatinib (MET) — NSCLC
- Trastuzumab deruxtecan (ERBB2) — breast cancer, gastric
- Sacituzumab govitecan (TROP2) — breast cancer
- Avelumab (CD274) — Merkel cell, urothelial
- Cemiplimab (PDCD1) — CSCC, NSCLC
- Lenvatinib (VEGFR) — thyroid, HCC
- Cabozantinib (MET/VEGFR) — RCC, HCC
- Baricitinib (JAK1/JAK2) — RA (non-oncology)
- Upadacitinib (JAK1) — RA (non-oncology)

**Failures (terminated/failed Phase 2-3, label=0):**
- Epacadostat (IDO1) — ECHO-301 melanoma
- Rociletinib (EGFR) — TIGER trials NSCLC
- Onartuzumab (MET) — MetLung NSCLC
- Selumetinib (MAP2K1) — thyroid (some trials failed)
- Iniparib (PARP1) — breast cancer (turned out not PARP inhibitor)
- Bavituximab (PTDSS1) — NSCLC
- Ganitumab (IGF1R) — pancreatic
- Figitumumab (IGF1R) — NSCLC
- Dalotuzumab (IGF1R) — breast cancer
- Linsitinib (IGF1R) — adrenocortical
- Trebananib (ANGPT1/2) — ovarian
- Ramucirumab failures in certain indications
- Ipatasertib (AKT1) — breast cancer IPATential trial
- Buparlisib (PI3K) — breast (toxicity)
- Taselisib (PI3K) — SANDPIPER trial issues
- Sapanisertib (MTOR) — multiple failures
- Mocetinostat (HDAC) — multiple trials
- Entinostat (HDAC) — breast cancer Phase 3 failure
- Tivozanib (VEGFR) — initial NSCLC failure
- Custirsen (CLU) — prostate/NSCLC failures
- Perifosine (AKT) — colorectal
- Evacetrapib (CETP) — cardiovascular (non-oncology)
- Atabecestat (BACE1) — Alzheimer's (non-oncology, CNS)
- Verubecestat (BACE1) — Alzheimer's (non-oncology, CNS)
- Aducanumab concerns (APP) — controversial, could label either way
- Lanabecestat (BACE1) — Alzheimer's

## For each trial

1. Search ClinicalTrials.gov: `search(condition=..., intervention=..., phase="PHASE3", pageSize=5)`
2. Get NCT ID from results, then `get_study(nct_id)` for full details
3. Parse trial design features (phase, enrollment, masking, sponsor, endpoint, etc.)
4. Query each MCP wrapper for the drug/target/disease — wrap each in try/except, fill "" on error
5. Build row dict with all COLUMNS
6. `append_row(row)` — write to CSV immediately
7. Print: `f"[{i+1}/{total}] {nct_id} {drug_name} label={label}"`

## Critical rules

- Wrap EVERY MCP call in try/except — if one fails, fill "" and continue
- Append to CSV after EACH trial — do not batch
- Initialize CSV with headers FIRST before the loop
- Do NOT fabricate data
- The script must be runnable: `python collect_real.py`

Write the script, then run it with Bash.
