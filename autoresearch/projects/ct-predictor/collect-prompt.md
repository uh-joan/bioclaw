# Clinical Trial Data Collection (Incremental)

You are a data collection agent. Build a dataset of completed Phase 2/3 clinical trials with features from MCP biomedical databases.

## Architecture

You have Python MCP wrapper functions available. Instead of calling MCP tools directly (which burns context tokens), **write and execute Python code** that imports from the wrapper modules and processes data locally.

The wrappers are in `mcp/servers/`. The MCP config is in `mcp-config.json`.

Set up the environment first:
```python
import sys, os
sys.path.insert(0, os.path.abspath('.'))
os.environ['MCP_CONFIG_FILE'] = os.path.abspath('mcp-config.json')
```

## Process

### Step 0: Initialize CSV

```python
import csv
from collect import COLUMNS

with open('data/trials_raw.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
print("Initialized CSV with headers")
```

### Step 1: Find trials

Write a Python script that searches for trials and collects features incrementally.

```python
import sys, os, csv, json, traceback
sys.path.insert(0, os.path.abspath('.'))
os.environ['MCP_CONFIG_FILE'] = os.path.abspath('mcp-config.json')

from collect import COLUMNS
from mcp.servers.ct_gov_mcp import search, get_study
from mcp.servers.fda_mcp import lookup_drug
from mcp.servers.opentargets_mcp import search_targets, search_diseases, get_target_disease_associations
from mcp.servers.chembl_mcp import compound_search, get_bioactivity, get_mechanism
from mcp.servers.drugbank_mcp import search_by_name as drugbank_search
from mcp.servers.bindingdb_mcp import search_by_name as bindingdb_search
from mcp.servers.clinpgx_mcp import get_clinical_annotations
from mcp.servers.pubmed_mcp import search_keywords as pubmed_search
from mcp.servers.openalex_mcp import search_works as openalex_search
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

OUTPUT = 'data/trials_raw.csv'

def safe_call(func, *args, **kwargs):
    """Call MCP wrapper, return None on any error."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"  [skip] {func.__name__}: {e}")
        return None

def extract_trial_features(nct_id, drug_name, target_gene, condition, indication_area):
    """Extract all features for one trial from MCP servers."""
    row = {"nct_id": nct_id, "intervention_name": drug_name, "condition": condition, "indication_area": indication_area}

    # 1. CT.gov full details
    details = safe_call(get_study, nct_id)
    if details:
        proto = details.get('data', {}).get('protocolSection', {}) if isinstance(details, dict) else {}
        # Extract trial design features from proto...
        # (parse enrollment, phase, sponsor, masking, etc.)

    # 2. FDA approval check
    fda = safe_call(lookup_drug, search_term=drug_name, limit=5)
    # Parse approval status → label

    # 3. OpenTargets
    if target_gene:
        ot_targets = safe_call(search_targets, query=target_gene, size=1)
        # Get ensembl ID, then associations...

    # 4. ChEMBL
    chembl = safe_call(compound_search, query=drug_name, limit=5)
    # Extract selectivity, IC50...

    # 5. DrugBank
    db = safe_call(drugbank_search, query=drug_name)
    # Extract interactions, targets, enzymes, half-life...

    # 6. BindingDB
    binding = safe_call(bindingdb_search, name=drug_name)
    # Extract Ki, Kd...

    # 7. ClinPGx
    pgx = safe_call(get_clinical_annotations, drug=drug_name)
    # Extract guideline count, actionable...

    # 8. PubMed
    pubs = safe_call(pubmed_search, keywords=f"{target_gene} {condition}", num_results=5)
    # Count publications...

    # 9. OpenAlex
    works = safe_call(openalex_search, query=f"{target_gene} {condition}")
    # Citation velocity...

    # 10. bioRxiv
    preprints = safe_call(search_preprints, query=f"{target_gene} {condition}", limit=10)
    # Count preprints...

    # 11. Reactome
    pathways = safe_call(find_pathways_by_gene, gene=target_gene)
    # Count pathways...

    # 12. STRING-db
    ppi = safe_call(get_protein_interactions, protein=target_gene)
    # Interaction degree...

    # 13. GTEx
    expr = safe_call(get_gene_expression, gene=target_gene)
    # Tissue specificity...

    # 14. gnomAD
    constraint = safe_call(get_gene_constraint, gene=target_gene)
    # pLI, LOEUF...

    # 15. ClinVar
    variants = safe_call(get_gene_variants_summary, gene=target_gene)
    # Pathogenic count...

    # 16. GWAS
    gwas = safe_call(get_gene_associations, gene=target_gene)
    # Hit count, best p-value...

    # 17. DepMap
    dep = safe_call(get_gene_dependency, gene=target_gene)
    # Essentiality score...

    # 18. cBioPortal
    cbio = safe_call(cbioportal_gene, gene=target_gene)
    # Mutation frequency...

    # 19. HPO
    pheno = safe_call(hpo_search, query=condition)
    # Phenotype count...

    # 20. Monarch
    genes = safe_call(get_disease_genes, disease=condition)
    # Gene count...

    # 21. EMA
    ema = safe_call(ema_search, query=drug_name)
    # Approval status...

    return row

def append_row(row):
    """Append one trial row to CSV."""
    with open(OUTPUT, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        clean = {col: row.get(col, "") for col in COLUMNS}
        writer.writerow(clean)

# === MAIN COLLECTION LOOP ===
# Search for trials, then process each one
```

### Step 2: Collect trials

The above is a TEMPLATE. You should write the actual working code, filling in the parsing logic for each MCP response. The key principles:

1. **Search ClinicalTrials.gov** for completed Phase 3 trials with known drugs (pembrolizumab, nivolumab, trastuzumab, olaparib, osimertinib, etc.) AND terminated Phase 2/3 trials
2. **For each trial**, call `extract_trial_features()` with the drug name, target gene, and condition
3. **Append immediately** to CSV after each trial — `append_row(row)`
4. **Print progress** after each trial: `print(f"Trial {i+1}/{total}: {nct_id} ({drug_name}) → label={label}")`
5. **Continue on errors** — if one MCP fails, fill that field with "" and move on

### Important details

- Label determination: If FDA `lookup_drug` returns an approved NDA/BLA for the studied indication → label=1. If trial terminated/withdrawn → label=0. If completed but no approval → label=0.
- Target gene mapping: pembrolizumab→PDCD1, nivolumab→PDCD1, trastuzumab→ERBB2, olaparib→PARP1, osimertinib→EGFR, etc. You know these — map them correctly.
- Indication areas: oncology, cns, cardiovascular, metabolic, immunology, infectious, respiratory, rare, other
- Use `safe_call()` wrapper for ALL MCP calls to handle errors gracefully
- Process data LOCALLY in Python — don't return raw MCP responses to context
- **Target: 50+ trials** (25+ success, 25+ failure). Include diverse drugs and indication areas.

### Step 3: Verify

After collection, run:
```python
import pandas as pd
df = pd.read_csv('data/trials_raw.csv')
print(f"Trials: {len(df)}")
print(f"Success: {df['label'].sum()}")
print(f"Failure: {(1-df['label']).sum()}")
filled = (df.notna() & (df != '')).mean()
print(f"Feature completeness:\n{filled[filled > 0].sort_values(ascending=False)}")
```

## Do NOT

- Do NOT fabricate data — use real MCP query results only
- Do NOT pause to ask the user — keep collecting
- Do NOT return raw MCP responses to context — process in Python
- Do NOT wait until the end to write — append each row immediately
