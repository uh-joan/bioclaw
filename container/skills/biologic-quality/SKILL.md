---
name: biologic-quality
description: "Glycosylation analysis, CQA assessment for biologics, biosimilarity evaluation, charge variant analysis, aggregation profiling, biologic developability"
---

# Biologic Quality & Glycoengineering

Specialist for biologic quality attribute assessment and glycoengineering analysis. Covers critical quality attribute (CQA) identification and ranking per ICH Q8/Q9/Q11 frameworks, glycosylation profiling (N-linked/O-linked), charge variant characterization, aggregation propensity evaluation, biosimilarity assessment, and developability screening for monoclonal antibodies, fusion proteins, bispecifics, and antibody-drug conjugates. Uses UniProt for protein sequence and post-translational modification data, PDB and AlphaFold for Fc and glycan structural context, DrugBank and FDA databases for approved biologic references and BLA information, PubMed for quality-related literature, EMA for EU biosimilar guidance, ClinicalTrials for biosimilar study data, and KEGG for glycan biosynthesis pathway mapping.

## Report-First Workflow

1. **Create report file immediately**: `[product]_biologic_quality_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Antibody humanization, affinity maturation, or format selection -> use `antibody-engineering`
- De novo protein therapeutic design and scaffold engineering -> use `protein-therapeutic-design`
- Mass spectrometry-based proteomics characterization -> use `proteomics-analysis`
- FDA regulatory strategy for BLA or biosimilar submissions -> use `fda-consultant`
- Quality management system audits and CAPA -> use `qms-audit-expert` or `capa-officer`
- Formulation science and excipient optimization -> use `formulation-science`

## Cross-Reference: Other Skills

- **De novo protein therapeutic design and scaffold engineering** -> use protein-therapeutic-design skill
- **Drug target validation and competitive landscape** -> use drug-research skill
- **Proteomic characterization and mass spectrometry analysis** -> use proteomics-analysis skill
- **PK/PD modeling and clinical pharmacology** -> use clinical-pharmacology skill

## Available MCP Tools

### `mcp__uniprot__uniprot_data` (Protein Sequence, PTMs, Glycosylation Sites)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_proteins` | Search proteins by keyword, organism, or name | `query`, `organism`, `size` |
| `get_protein` | Full protein profile including function, localization, PTMs | `accession`, `format` |
| `get_protein_features` | Protein features: glycosylation sites, disulfides, signal peptides, domains | `accession` |
| `get_protein_isoforms` | Retrieve protein isoforms and splice variants | `accession` |

### `mcp__pdb__pdb_data` (Fc Structure, Glycan Conformations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_structures` | Search PDB for Fc structures, glycosylated antibodies | `query`, `rows` |
| `get_structure` | Get structure details including bound glycans and resolution | `pdb_id` |

### `mcp__alphafold__alphafold_data` (Structural Context for CQAs)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_prediction` | Retrieve AlphaFold predicted structure for CQA mapping | `uniprotId`, `format` |
| `search_structures` | Search AlphaFold database for structural models | `query`, `organism` |

### `mcp__drugbank__drugbank_data` (Approved Biologics Reference)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search approved biologics by name or target | `query`, `limit` |
| `get_drug` | Full drug profile: mechanism, formulation, pharmacology | `drugbank_id` |

### `mcp__fda__fda_data` (Biologic BLAs, Biosimilar Approvals)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug/biologic approvals database | `query`, `limit` |
| `get_drug_label` | Retrieve prescribing information and BLA details | `application_number` |

### `mcp__pubmed__pubmed_data` (Biologic Quality Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search biologic quality, glycosylation, biosimilarity literature | `keywords`, `num_results` |
| `fetch_details` | Get full article details by PMID | `pmid` |

### `mcp__ema__ema_data` (EU Biosimilar Guidelines)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_medicines` | Search EMA-approved biologics and biosimilars | `query`, `limit` |
| `get_medicine` | Get medicine details including EPAR and assessment report references | `product_number` |

### `mcp__clinicaltrials__ct_data` (Biosimilar Clinical Trials)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search biosimilar PK and clinical equivalence studies | `query`, `limit` |

### `mcp__kegg__kegg_data` (Glycan Biosynthesis Pathways)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `find_pathway` | Find glycan biosynthesis pathways (N-glycan, O-glycan) | `query` |
| `get_pathway` | Get pathway details: enzymes, intermediates, regulation | `pathway_id` |

---

## Core Workflows

### 1. CQA Identification & Ranking (ICH Q8/Q9/Q11 Framework)

Systematic identification and risk-based ranking of critical quality attributes for biologics according to ICH guidelines. Uses prior knowledge, platform experience, and product-specific data to distinguish CQAs from non-critical attributes.

**Step 1 — Retrieve reference biologic information**

```
mcp__drugbank__drugbank_data.search_drugs({ query: "trastuzumab", limit: 5 })
mcp__fda__fda_data.search_drugs({ query: "Herceptin", limit: 5 })
```

**Step 2 — Get protein sequence and known glycosylation sites**

```
mcp__uniprot__uniprot_data.search_proteins({ query: "trastuzumab heavy chain", organism: "Homo sapiens", size: 5 })
mcp__uniprot__uniprot_data.get_protein_features({ accession: "P04626" })
```

**Step 3 — Review Fc structure for glycan-dependent function**

```
mcp__pdb__pdb_data.search_structures({ query: "IgG1 Fc glycosylated", rows: 5 })
mcp__pdb__pdb_data.get_structure({ pdb_id: "1HZH" })
```

**Step 4 — Literature on CQA impact for this modality**

```
mcp__pubmed__pubmed_data.search({ keywords: "critical quality attributes monoclonal antibody risk assessment", num_results: 15 })
```

**CQA Risk Assessment Matrix (ICH Q9)**

For each potential CQA, assess:

| Quality Attribute | Severity | Probability | Detectability | RPN | CQA? |
|-------------------|----------|-------------|---------------|-----|------|
| Glycosylation (afucosylation) | High | Medium | High | ... | Yes |
| Aggregation (HMWS) | High | Medium | High | ... | Yes |
| Charge variants (acidic) | Medium | Medium | High | ... | Yes |
| Deamidation (Asn) | Medium | High | High | ... | Yes |
| Oxidation (Met) | Medium | Medium | High | ... | Yes |
| Host cell proteins (HCP) | High | Low | Medium | ... | Yes |
| Subvisible particles | High | Low | Medium | ... | Yes |
| Glycation | Low | Low | High | ... | No |

**Modality-specific CQAs:** mAbs (glycosylation, charge variants, aggregation, Fc effector function); fusion proteins (linker integrity, non-Fc glycosylation, proteolytic clipping); ADCs (DAR, drug distribution, unconjugated drug, linker stability); bispecifics (chain pairing, assembly, per-arm stability).

### 2. Glycosylation Analysis

Comprehensive N-linked and O-linked glycan profiling with functional impact assessment.

**Step 1 — Identify glycosylation sites on the biologic**

```
mcp__uniprot__uniprot_data.get_protein_features({ accession: "<target_accession>" })
```

Look for feature type "Glycosylation" — N-linked sites at Asn-X-Ser/Thr sequons (X != Pro).

**Step 2 — Retrieve Fc glycan structural context**

```
mcp__pdb__pdb_data.search_structures({ query: "IgG1 Fc N297 glycan", rows: 10 })
mcp__alphafold__alphafold_data.get_prediction({ uniprotId: "<accession>", format: "pdb" })
```

**Step 3 — Map glycan biosynthesis pathway**

```
mcp__kegg__kegg_data.find_pathway({ query: "N-glycan biosynthesis" })
mcp__kegg__kegg_data.get_pathway({ pathway_id: "hsa00510" })
```

**Step 4 — Literature on glycan-function relationships**

```
mcp__pubmed__pubmed_data.search({ keywords: "IgG glycosylation ADCC fucosylation FcgammaRIIIa", num_results: 15 })
```

**Key Glycan Species and Their Functional Impact:**

| Glycan Species | Structure | Impact on Function |
|---------------|-----------|-------------------|
| G0F | GlcNAc2Man3GlcNAc2Fuc | Baseline; most common in CHO-produced mAbs |
| G1F | GlcNAc2Man3GlcNAc2Fuc + 1 Gal | Slightly enhanced CDC via C1q binding |
| G2F | GlcNAc2Man3GlcNAc2Fuc + 2 Gal | Enhanced CDC; common in serum IgG |
| G0 (afucosylated) | GlcNAc2Man3GlcNAc2 | 5-50x enhanced ADCC via FcgammaRIIIa binding |
| Man5 | GlcNAc2Man5 | Rapid clearance via mannose receptor; reduced half-life |
| Man6-Man9 | High mannose species | Cleared by mannose receptor on macrophages/dendritic cells |
| G2F+SA | G2F + 1-2 sialic acid (Neu5Ac) | Anti-inflammatory properties; extended half-life; reduced ADCC |
| G0F+bisecting GlcNAc | G0F + bisecting GlcNAc on beta-Man | Enhanced ADCC (prevents core fucosylation) |

**Glycosylation critical thresholds for mAbs:**

- **Afucosylation**: >5% afucosylated species significantly enhances ADCC; critical for oncology mAbs
- **High mannose (Man5+)**: >10% may affect PK through mannose receptor-mediated clearance
- **Galactosylation**: G0F/G1F/G2F ratio affects CDC; G2F enhances C1q binding
- **Sialylation**: Neu5Gc (non-human sialic acid) is immunogenic; monitor in CHO-derived products
- **Alpha-1,3-galactose**: Immunogenic epitope (anti-Gal antibodies); must be absent

**CHO cell culture parameters affecting glycosylation:** Low DO increases high mannose; lower temp (30-33C) increases galactosylation; Mn2+ enhances galactosylation; uridine/galactose feed increases galactosylation; ammonia reduces galactosylation/sialylation; kifunensine produces Man9 (afucosylated); 2-fluorofucose reduces core fucosylation; extended culture increases high mannose.

### 3. Charge Variant Analysis

Cation exchange (CEX) chromatography and capillary isoelectric focusing (cIEF) profiling of acidic, main, and basic charge variants.

**Step 1 — Identify sequence-based charge liabilities**

```
mcp__uniprot__uniprot_data.get_protein({ accession: "<target_accession>", format: "fasta" })
```

Scan sequence for: Asn-Gly (highest deamidation risk), Asn-Ser, Asn-His, Asn-Ala deamidation motifs; C-terminal Lys; N-terminal pyroglutamate (Gln->pyroGlu).

**Step 2 — Literature on charge variant impact**

```
mcp__pubmed__pubmed_data.search({ keywords: "monoclonal antibody charge variants deamidation potency stability", num_results: 15 })
```

**Charge Variant Sources and Classification:**

| Modification | Variant Type | Impact |
|-------------|-------------|--------|
| Deamidation (Asn->Asp/isoAsp) | Acidic | May reduce binding if in CDR |
| Sialylation | Acidic | Typically minor on mAbs |
| Glycation (Lys) | Acidic | Can affect binding at high levels |
| C-terminal Lys clipping | Basic -> Main | No functional impact |
| N-terminal pyroGlu | Acidic -> Main | Expected; no impact |
| Succinimide intermediate | Basic | Transient deamidation intermediate |
| Oxidation (Met252/Met428) | Acidic | Reduces FcRn binding -> shorter half-life |
| Fragmentation (hinge) | Acidic/Basic | Loss of bivalent binding |
| Disulfide scrambling | Basic | May affect structure/function |

**Typical charge variant specifications for mAbs:**

- Acidic variants: typically NMT 25-35% (product-specific)
- Main peak: typically NLT 50-65%
- Basic variants: typically NMT 20-30%
- Deamidation at Asn in CDR: requires functional impact assessment

**Forced degradation conditions:** Thermal (40C, 1-4 weeks), pH stress (low pH 3.5, high pH 8.5-9.0), oxidative (0.1-1% H2O2, 24h), light (ICH Q1B: 1.2M lux-hours), freeze-thaw (5 cycles), agitation (300 rpm, 48-72h).

### 4. Aggregation Assessment

Size-based characterization of monomer purity, high molecular weight species (HMWS), and subvisible/visible particles.

**Step 1 — Assess structural aggregation propensity**

```
mcp__alphafold__alphafold_data.get_prediction({ uniprotId: "<accession>", format: "pdb" })
mcp__uniprot__uniprot_data.get_protein_features({ accession: "<target_accession>" })
```

Evaluate surface hydrophobic patches, unpaired cysteines, and flexible loops.

**Step 2 — Literature on aggregation mechanisms for the modality**

```
mcp__pubmed__pubmed_data.search({ keywords: "monoclonal antibody aggregation mechanism subvisible particles immunogenicity", num_results: 15 })
```

**Aggregation Assessment Methods:**

| Method | Size Range | Measures |
|--------|-----------|----------|
| SEC-HPLC | >10 nm | %HMWS, %monomer, %LMWS (spec: monomer >= 95-98%) |
| SEC-MALS | >10 nm | Absolute MW of aggregates |
| DLS | 1-1000 nm | Hydrodynamic radius, polydispersity |
| AUC-SV | 1-100 nm | Sedimentation coefficient (orthogonal to SEC) |
| MFI / HIAC | 2-100 um | Subvisible particles (USP <787>/<788>) |
| Visual inspection | >100 um | Essentially free of visible particles |

**Aggregation propensity factors:** Hydrophobic CDR patches (APRs via TANGO/Zyggregator), formulation (pH, surfactant PS80/PS20, stabilizer), process stress (freeze-thaw, shear, light), concentration (self-association above 50-100 mg/mL), and thermal stability (Tonset > 55C preferred).

**Aggregation scoring rubric:**

| Parameter | Low Risk (0-2) | Medium Risk (3-5) | High Risk (6-10) |
|-----------|---------------|-------------------|------------------|
| SEC HMWS (initial) | <0.5% | 0.5-2.0% | >2.0% |
| SEC HMWS growth (25C, 6mo) | <0.5% increase | 0.5-2.0% increase | >2.0% increase |
| DLS polydispersity | <15% | 15-25% | >25% |
| Tm1 (onset) | >65C | 55-65C | <55C |
| kD (interaction parameter) | >0 (repulsive) | -5 to 0 | <-5 (attractive) |
| AC-SINS (self-interaction) | Low shift | Medium shift | High shift |

### 5. Biosimilarity Evaluation

Comprehensive analytical, functional, PK, and clinical biosimilarity assessment following FDA and EMA guidance.

**Step 1 — Retrieve reference product information**

```
mcp__fda__fda_data.search_drugs({ query: "adalimumab BLA", limit: 5 })
mcp__ema__ema_data.search_medicines({ query: "Humira", limit: 5 })
mcp__drugbank__drugbank_data.search_drugs({ query: "adalimumab", limit: 5 })
```

**Step 2 — Review approved biosimilars and their analytical packages**

```
mcp__fda__fda_data.search_drugs({ query: "adalimumab biosimilar", limit: 10 })
mcp__ema__ema_data.search_medicines({ query: "adalimumab biosimilar", limit: 10 })
```

**Step 3 — Find biosimilar clinical study designs**

```
mcp__clinicaltrials__ct_data.search_studies({ query: "adalimumab biosimilar pharmacokinetic equivalence", limit: 10 })
```

**Step 4 — Literature on analytical similarity approaches**

```
mcp__pubmed__pubmed_data.search({ keywords: "biosimilar analytical similarity totality of evidence FDA guidance", num_results: 15 })
```

**Biosimilarity Assessment Tiers (FDA Stepwise Approach):**

| Tier | Assessment | Acceptance Criteria |
|------|-----------|-------------------|
| Structural | Primary/higher order structure (LC-MS, CD, DSC, HDX-MS) | Highly similar fingerprint |
| Functional | Target binding (SPR), Fc effector (ADCC, CDC, FcRn) | Within quality range of reference |
| Clinical PK | Single-dose PK equivalence (parallel/crossover) | 80-125% CI for AUC and Cmax |
| Clinical efficacy | Comparative efficacy in sensitive population | Margin: 80-125% for risk ratio |
| Immunogenicity | Comparative ADA incidence/titer | No clinically meaningful difference |

**ICH Q5E Comparability:** Pre-defined analytical methods covering all CQAs, statistical equivalence testing against reference product quality range (>=10 lots preferred), risk-based approach where CQAs with known clinical impact require tighter similarity ranges. Totality of evidence across all tiers determines the similarity conclusion.

### 6. Developability Assessment

Early-stage screening of biologic candidates for manufacturability and clinical viability.

**Step 1 — Sequence liability scanning**

```
mcp__uniprot__uniprot_data.get_protein({ accession: "<candidate_accession>", format: "fasta" })
```

Scan for known degradation hotspots in the sequence.

**Step 2 — Structural assessment of liability exposure**

```
mcp__alphafold__alphafold_data.get_prediction({ uniprotId: "<accession>", format: "pdb" })
mcp__pdb__pdb_data.search_structures({ query: "<antibody name> Fab", rows: 5 })
```

**Step 3 — Literature on developability screening**

```
mcp__pubmed__pubmed_data.search({ keywords: "antibody developability assessment sequence liabilities high concentration formulation", num_results: 15 })
```

**Sequence Liability Motifs:**

| Motif | Type | Risk Level | Notes |
|-------|------|-----------|-------|
| Asn-Gly (NG) | Deamidation | High | Fastest deamidation rate; half-life ~1 day at pH 7.4, 37C |
| Asn-Ser (NS) | Deamidation | Medium-High | Common hotspot; ~10x slower than NG |
| Asn-His (NH) | Deamidation | Medium | Moderate rate |
| Asn-Ala (NA) | Deamidation | Medium | Moderate rate |
| Asn-Thr (NT) | Deamidation | Low-Medium | Slower due to Thr branching |
| Asp-Gly (DG) | Isomerization | High | Asp -> isoAsp; succinimide intermediate |
| Asp-Ser (DS) | Isomerization | Medium | Moderate isomerization risk |
| Met (surface exposed) | Oxidation | High | Met252, Met428 in Fc critical for FcRn |
| Trp (surface exposed) | Oxidation/photodeg | Medium-High | Trp susceptible to photo-oxidation |
| Asn-X-Ser/Thr (X!=Pro) | N-glycosylation | Context-dep | Non-consensus glycosylation in CDR is a liability |
| Free Cys (unpaired) | Cysteinylation | Medium | Unpaired Cys can form adducts |
| Lys-rich patches | Glycation | Low-Medium | Non-enzymatic glucose attachment |
| Hydrophobic CDR patches | Self-association | High | Leads to viscosity and aggregation issues |

**Developability scoring parameters:**

| Parameter | Pass | Flag | Fail |
|-----------|------|------|------|
| CDR deamidation motifs (NG, NS) | 0 | 1 | >=2 |
| CDR isomerization motifs (DG, DS) | 0 | 1 | >=2 |
| Surface hydrophobicity (HIC retention) | <reference | Similar | >reference |
| Self-interaction (AC-SINS/CIC) | Low | Moderate | High |
| Viscosity at 150 mg/mL | <15 cP | 15-30 cP | >30 cP |
| Polyspecificity (BVP/PSR) | Low | Medium | High |
| Thermal stability (Tm1) | >65C | 55-65C | <55C |
| Expression titer (CHO transient) | >50 mg/L | 20-50 mg/L | <20 mg/L |
| Isoelectric point (pI) | 7.5-9.0 | 6.5-7.5 or >9.0 | <6.5 |

---

## Biologic Quality Scoring

Composite quality score (0-100) based on weighted assessment of six domains. Each domain scored 0-100, then weighted according to criticality.

| Domain | Weight | Score Range | Key Metrics |
|--------|--------|-------------|-------------|
| Glycosylation profile consistency | 20% | 0-100 | G0F/G1F/G2F ratio reproducibility; afucosylation level; high mannose %; sialylation consistency |
| Charge variant profile | 15% | 0-100 | %acidic/%main/%basic within specification; deamidation rate; stability on storage |
| Aggregation propensity | 20% | 0-100 | %HMWS initial and on stability; Tm; kD; subvisible particle count |
| Sequence liability risk | 15% | 0-100 | Number/location of deamidation/isomerization/oxidation motifs; CDR vs framework |
| Process robustness | 15% | 0-100 | CQA variability across batches; process parameter sensitivity; design space adequacy |
| Analytical comparability | 15% | 0-100 | Lot-to-lot consistency; method precision/accuracy; specification compliance |

**Scoring interpretation:**

| Score | Rating | Interpretation |
|-------|--------|---------------|
| 85-100 | Excellent | Product meets all specifications with wide margin; robust process control |
| 70-84 | Good | Minor variability in some attributes; acceptable for development progression |
| 55-69 | Acceptable | Some CQAs near specification limits; process optimization recommended |
| 40-54 | Marginal | Multiple CQAs at risk; significant process/formulation changes needed |
| 0-39 | Poor | Fundamental quality concerns; candidate redesign or process overhaul required |

**Glycosylation sub-score calculation:**

```
glycan_score = 100
if afucosylation_cv > 30%: glycan_score -= 20
if high_mannose > 10%: glycan_score -= 15
if high_mannose > 20%: glycan_score -= 30
if neu5gc_detected: glycan_score -= 10
if alpha_gal_detected: glycan_score -= 25
if g0f_g1f_g2f_ratio_drift > 15%: glycan_score -= 15
if sialylation_cv > 40%: glycan_score -= 10
```

---

## Python Code Templates

### Glycan Species Distribution Visualization

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_glycan_distribution(sample_name, glycan_data, reference_ranges=None):
    """
    Plot glycan species distribution with optional specification overlay.
    glycan_data: {"G0F": 45.2, "G1F": 28.1, "G2F": 8.3, "G0": 5.1, "Man5": 3.8, ...}
    reference_ranges: {"G0F": (35, 55), "Man5": (0, 10), ...}
    """
    species, values = list(glycan_data.keys()), list(glycan_data.values())
    color_map = {"Man": "#e74c3c", "SA": "#9b59b6", "G0F": "#3498db",
                 "G1F": "#1abc9c", "G2F": "#f39c12"}
    colors = [next((c for k, c in color_map.items() if k in sp), "#95a5a6") for sp in species]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(species, values, color=colors, edgecolor="black", linewidth=0.5)
    if reference_ranges:
        for i, sp in enumerate(species):
            if sp in reference_ranges:
                low, high = reference_ranges[sp]
                ax.hlines(y=[low, high], xmin=i-0.4, xmax=i+0.4,
                         colors="red", linestyles="dashed", linewidth=1.5)
    ax.set_ylabel("Relative Abundance (%)")
    ax.set_title(f"N-Glycan Profile: {sample_name}")
    plt.xticks(rotation=45, ha="right")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.5,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(f"glycan_profile_{sample_name}.png", dpi=150)
    return fig
```

### Charge Variant Deconvolution

```python
import matplotlib.pyplot as plt

def plot_charge_variants(sample_name, acidic_pct, main_pct, basic_pct,
                         specs=None, stability_data=None):
    """
    Plot charge variant distribution with optional spec limits and stability trend.
    specs: {"acidic_max": 30, "main_min": 55, "basic_max": 25}
    stability_data: [{"timepoint": "T0", "acidic": 18, "main": 62, "basic": 20}, ...]
    """
    fig, axes = plt.subplots(1, 2 if stability_data else 1,
                              figsize=(14 if stability_data else 7, 6))
    if not stability_data:
        axes = [axes]

    categories, values = ["Acidic", "Main", "Basic"], [acidic_pct, main_pct, basic_pct]
    colors = ["#e74c3c", "#2ecc71", "#3498db"]
    bars = axes[0].bar(categories, values, color=colors, edgecolor="black", width=0.6)
    if specs:
        for key, color in [("acidic_max","#e74c3c"),("main_min","#2ecc71"),("basic_max","#3498db")]:
            if key in specs:
                axes[0].axhline(y=specs[key], color=color, linestyle="--", alpha=0.7, label=f"{key} ({specs[key]}%)")
        axes[0].legend(fontsize=9)
    axes[0].set_ylabel("Percentage (%)")
    axes[0].set_title(f"Charge Variant Profile: {sample_name}")
    axes[0].set_ylim(0, 100)

    if stability_data:
        for key, marker, color in [("acidic","o","#e74c3c"),("main","s","#2ecc71"),("basic","^","#3498db")]:
            axes[1].plot([d["timepoint"] for d in stability_data],
                        [d[key] for d in stability_data], f"{marker}-", color=color, label=key.title(), linewidth=2)
        axes[1].set_ylabel("Percentage (%)")
        axes[1].set_xlabel("Timepoint")
        axes[1].set_title("Charge Variant Stability Trend")
        axes[1].legend()
    plt.tight_layout()
    plt.savefig(f"charge_variants_{sample_name}.png", dpi=150)
    return fig
```

### SEC Aggregation Trend Analysis

```python
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def plot_sec_aggregation_trend(sample_name, stability_data, spec_hmws=2.0, spec_monomer=95.0):
    """
    Plot SEC monomer/HMWS trend with linear regression and spec limits.
    stability_data: [{"month": 0, "hmws": 0.3, "monomer": 99.1, "condition": "5C"}, ...]
    """
    cond_colors = {"5C": "#3498db", "25C": "#f39c12", "40C": "#e74c3c"}
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

    for cond in sorted(set(d["condition"] for d in stability_data)):
        cd = sorted([d for d in stability_data if d["condition"] == cond], key=lambda x: x["month"])
        months, hmws, monomer = [d["month"] for d in cd], [d["hmws"] for d in cd], [d["monomer"] for d in cd]
        color = cond_colors.get(cond, "#95a5a6")
        ax1.plot(months, hmws, "o-", color=color, label=cond, linewidth=2)
        ax2.plot(months, monomer, "s-", color=color, label=cond, linewidth=2)
        if len(months) >= 3:  # linear regression for shelf-life projection
            slope, intercept, *_ = stats.linregress(months, hmws)
            ext = np.linspace(0, max(months)*1.5, 50)
            ax1.plot(ext, slope*ext + intercept, "--", color=color, alpha=0.4)

    ax1.axhline(y=spec_hmws, color="red", linestyle=":", linewidth=2, label=f"Spec ({spec_hmws}%)")
    ax1.set_ylabel("HMWS (%)")
    ax1.set_title(f"SEC Stability Trend: {sample_name}")
    ax1.legend()
    ax2.axhline(y=spec_monomer, color="red", linestyle=":", linewidth=2, label=f"Spec ({spec_monomer}%)")
    ax2.set_ylabel("Monomer (%)")
    ax2.set_xlabel("Month")
    ax2.legend()
    plt.tight_layout()
    plt.savefig(f"sec_trend_{sample_name}.png", dpi=150)
    return fig
```

### Thermal Stability (Tm) Comparison

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_tm_comparison(candidates, reference_tm=None):
    """
    Compare DSC Tm values across biologic candidates.
    candidates: [{"name": "mAb-A", "Tonset": 58, "Tm1": 68, "Tm2": 82}, ...]
    reference_tm: optional dict for reference product (plotted first)
    """
    if reference_tm:
        candidates = [reference_tm] + candidates
    names = [c["name"] for c in candidates]
    x, width = np.arange(len(names)), 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    for offset, key, label, color in [(-width,"Tonset","Tonset","#e74c3c"),
                                       (0,"Tm1","Tm1 (CH2)","#3498db"),
                                       (width,"Tm2","Tm2 (Fab/CH3)","#2ecc71")]:
        vals = [c.get(key, 0) for c in candidates]
        bars = ax.bar(x + offset, vals, width, label=label, color=color, alpha=0.8)
        for bar in bars:
            if bar.get_height() > 0:
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                       f"{bar.get_height():.0f}", ha="center", fontsize=8)

    ax.axhline(y=55, color="red", linestyle="--", alpha=0.5, label="Tm1 minimum (55C)")
    ax.set_ylabel("Temperature (C)")
    ax.set_title("Thermal Stability Comparison (DSC)")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.legend()
    plt.tight_layout()
    plt.savefig("tm_comparison.png", dpi=150)
    return fig
```

### Sequence Liability Scanning (Regex-Based Motif Detection)

```python
import re
from collections import defaultdict

def scan_sequence_liabilities(sequence, name="query"):
    """
    Scan a protein sequence for known degradation and modification hotspots.

    Args:
        sequence: amino acid sequence string (one-letter code)
        name: identifier for the sequence

    Returns:
        dict with liability counts and positions
    """
    liabilities = defaultdict(list)

    # Deamidation motifs (Asn-X where X promotes deamidation)
    deamidation_patterns = {
        "NG (high risk)": r"N(?=G)",
        "NS (medium-high risk)": r"N(?=S)",
        "NH (medium risk)": r"N(?=H)",
        "NA (medium risk)": r"N(?=A)",
        "NT (low-medium risk)": r"N(?=T)",
    }
    for label, pattern in deamidation_patterns.items():
        for match in re.finditer(pattern, sequence):
            liabilities["deamidation"].append({
                "motif": label,
                "position": match.start() + 1,
                "context": sequence[max(0, match.start()-3):match.start()+5]
            })

    # Isomerization motifs (Asp-X)
    isomerization_patterns = {
        "DG (high risk)": r"D(?=G)",
        "DS (medium risk)": r"D(?=S)",
        "DT (low-medium risk)": r"D(?=T)",
        "DD (medium risk)": r"D(?=D)",
    }
    for label, pattern in isomerization_patterns.items():
        for match in re.finditer(pattern, sequence):
            liabilities["isomerization"].append({
                "motif": label,
                "position": match.start() + 1,
                "context": sequence[max(0, match.start()-3):match.start()+5]
            })

    # Oxidation-susceptible residues
    for match in re.finditer(r"M", sequence):
        liabilities["oxidation_met"].append({
            "motif": "Met",
            "position": match.start() + 1,
            "context": sequence[max(0, match.start()-3):match.start()+5]
        })
    for match in re.finditer(r"W", sequence):
        liabilities["oxidation_trp"].append({
            "motif": "Trp",
            "position": match.start() + 1,
            "context": sequence[max(0, match.start()-3):match.start()+5]
        })

    # N-glycosylation sequons (N-X-S/T where X != P)
    for match in re.finditer(r"N(?=[^P][ST])", sequence):
        liabilities["n_glycosylation_sequon"].append({
            "motif": "N-X-S/T",
            "position": match.start() + 1,
            "context": sequence[max(0, match.start()-2):match.start()+6]
        })

    # Unpaired Cys detection (heuristic: odd total Cys count suggests unpaired)
    cys_positions = [m.start() + 1 for m in re.finditer(r"C", sequence)]
    if len(cys_positions) % 2 != 0:
        liabilities["unpaired_cys"].append({"motif": "Odd Cys count", "positions": cys_positions})

    # Clipping motifs (hinge-like sequences)
    for match in re.finditer(r"[DK]P", sequence):
        liabilities["clip_susceptible"].append({
            "motif": "DP/KP", "position": match.start() + 1,
            "context": sequence[max(0, match.start()-3):match.start()+5]
        })

    # Risk scoring
    severity = {"deamidation": 3, "isomerization": 2, "oxidation_met": 2,
                "oxidation_trp": 1, "n_glycosylation_sequon": 2, "unpaired_cys": 3, "clip_susceptible": 1}
    risk_score = sum(len(v) * severity.get(k, 1) for k, v in liabilities.items())
    risk_label = "LOW" if risk_score < 15 else "MEDIUM" if risk_score < 30 else "HIGH"

    print(f"\nSEQUENCE LIABILITY REPORT: {name}")
    print(f"Length: {len(sequence)} | Cys: {len(cys_positions)} | Risk: {risk_score} ({risk_label})")
    for cat, findings in liabilities.items():
        print(f"  {cat}: {len(findings)} sites")
        for f in findings[:3]:
            print(f"    - {f['motif']} at pos {f.get('position','N/A')} | {f.get('context','')}")

    return {"name": name, "length": len(sequence), "liabilities": dict(liabilities),
            "risk_score": risk_score, "risk_label": risk_label}
```

---

## Evidence Grading

All biologic quality assessments use a tiered evidence framework to weight data according to clinical relevance.

| Tier | Category | Description | Weight | Examples |
|------|----------|-------------|--------|----------|
| T1 | Clinical immunogenicity/efficacy data | Direct clinical evidence of CQA impact on safety or efficacy | Highest | Anti-drug antibody incidence correlated with glycan changes; PK differences linked to high mannose levels; efficacy differences in biosimilar trials |
| T2 | In vitro functional assays | Cell-based or binding assays demonstrating CQA-function relationship | High | ADCC reporter assay showing afucosylation-dependent killing; FcRn binding showing Met oxidation impact on recycling; target binding SPR with deamidated variants |
| T3 | Analytical characterization | Physicochemical and structural data characterizing quality attributes | Moderate | SEC purity profiles; glycan maps by HILIC-FLD; charge variant profiles by CEX; peptide mapping by LC-MS/MS; HDX-MS higher order structure |
| T4 | Computational prediction | In silico assessment of quality attribute risk | Supporting | Sequence liability scanning; aggregation propensity prediction (TANGO/CamSol); immunogenicity prediction (NetMHCII); viscosity prediction from surface charge |

**Evidence integration rules:**

- T1 evidence overrides all lower tiers (clinical outcome is definitive)
- T2 evidence establishes functional relevance when T1 data is absent
- T3 evidence characterizes the attribute but does not alone establish clinical impact
- T4 evidence is hypothesis-generating and must be confirmed by T2/T3 data
- For biosimilarity: totality of evidence across all tiers determines similarity conclusion
- For CQA designation: T1 or T2 evidence of functional impact required for "critical" classification
- Risk-based approach: higher-tier evidence permits reduced testing at lower tiers

**Key regulatory references:** ICH Q5E (comparability), Q6B (specifications), Q8(R2) (QbD/design space), Q9 (risk management/FMEA), Q11 (process-CQA linkage); FDA Biosimilar Guidance 2015 (stepwise approach), FDA Statistical Approaches 2017 (equivalence testing); EMA Biosimilar Guideline 2014; WHO Guidelines on Biosimilars 2009; USP <787>/<788>/<789> (subvisible particles), USP <1032> (biologic assay design).

---

## Reference: Common Biologic CQAs by Modality

**mAbs (IgG1/IgG2/IgG4):** Primary structure (peptide map, intact mass), glycosylation (G0F/G1F/G2F, afucosylation, high mannose — HILIC-FLD, LC-MS glycopeptide), charge variants (CEX-HPLC, icIEF), size variants (%monomer, %HMWS — SEC-HPLC, CE-SDS), potency (target binding SPR, ADCC/CDC reporter assays), process-related impurities (HCP, DNA, Protein A).

**Fc-Fusion Proteins:** Additional CQAs include linker integrity (clipping), non-Fc glycosylation (O-linked at receptor domain), receptor binding activity, and typically higher aggregation propensity than mAbs.

**ADCs:** Drug-antibody ratio (DAR average and distribution, target 2-4 for Cys-conjugated), unconjugated antibody (%DAR=0), free drug levels, conjugation site heterogeneity (site-specific preferred), and linker stability (cleavable vs non-cleavable).

## Completeness Checklist

- [ ] Report file created with all section headers and placeholders populated
- [ ] CQAs identified and ranked using ICH Q9 risk assessment matrix (severity, probability, detectability)
- [ ] Glycosylation profile characterized (G0F/G1F/G2F, afucosylation, high mannose, sialylation)
- [ ] Charge variant profile assessed (acidic/main/basic percentages with specification compliance)
- [ ] Aggregation propensity evaluated (SEC HMWS, DLS, Tm, kD)
- [ ] Sequence liability scan performed (deamidation, isomerization, oxidation motifs)
- [ ] Composite biologic quality score calculated with domain breakdown
- [ ] Biosimilarity assessment completed (if applicable) across all FDA stepwise tiers
- [ ] Evidence grading applied (T1-T4) to all quality attribute assessments
- [ ] Modality-specific CQAs addressed (mAb, fusion protein, ADC, or bispecific)
