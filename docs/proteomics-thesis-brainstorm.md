# Proteomics + AI Thesis — What We Can Build

*Based on Antonio Linares' "Peptides are the tip of the iceberg" article (2026-03-20)*

## Core Thesis

The proteome is code. Amino acid sequences → peptides → proteins → proteoforms (via PTMs). AlphaFold predicts structure. AI + proteome digital twins will identify dysfunction. Personalized peptides fix it. Data flywheel: more patients → more data → better AI → better outcomes.

## Our Arsenal

| Asset | Relevance |
|---|---|
| **37 biomedical MCPs** | UniProt, AlphaFold, PDB, STRING-db, BindingDB = the proteomics stack |
| **ct-predict (0.926 AUC)** | Already proving "dump biomedical data into AI → predict outcomes" |
| **161 container skills** | protein-therapeutic-design, binder-discovery, proteomics-analysis, enzyme-engineering |
| **peptgothi-chat** | Peptide-focused assistant already exists |
| **autoresearch loop** | The autonomous improvement flywheel — already built |
| **kg-openpharma** | Knowledge graph backbone for connecting proteome data |

---

## Proposed Projects

### 1. Peptide Trial Predictor (immediate — extend ct-predict)

Add proteomics features to ct-predict from existing MCPs:

- **UniProt**: target protein length, subcellular localization, PTM count (phosphorylation sites, glycosylation sites), signal peptide presence, transmembrane domains
- **AlphaFold**: predicted structure confidence (pLDDT), disorder regions, binding site accessibility
- **PDB**: number of resolved structures, ligand co-crystals, resolution quality
- **STRING-db**: protein interaction partners count, clustering coefficient
- **BindingDB**: existing ligand diversity for target

**Hypothesis**: Trials targeting proteins with more PTM sites, higher disorder, or poor structural coverage fail more often.

**Effort**: ~1 day to write `backfill_proteomics.py`, let autoresearch run overnight.

### 2. Proteomic Dysfunction Scorer (new autoresearch project)

Predict **"is this protein target dysfunctional in this disease?"**

**Data sources (all available):**
- OpenTargets: genetic associations
- ClinVar: pathogenic variants
- GTEx: expression deviation from healthy tissue
- STRING-db: interaction network disruption
- Reactome/KEGG: pathway position
- GWAS: population-level associations
- DepMap: essentiality

**Label**: Known working targets (DrugBank approved) vs failed targets (ct-predict failures).

**Output**: protein + disease → likelihood of therapeutic success.

**Effort**: ~2-3 days to build dataset + train.py, then autoresearch takes over.

### 3. Peptide Design Agent (extend BioClaw skills)

Wire existing skills into a workflow:

1. User describes proteomic dysfunction
2. Agent pulls sequences from **UniProt**
3. Agent gets structures from **AlphaFold**
4. Agent maps interactions via **STRING-db**
5. Agent finds co-crystals from **PDB**
6. Agent finds known binders from **BindingDB**
7. Agent synthesizes candidate peptide targeting strategy

Not LigandForge, but the **research step before LigandForge**.

### 4. PTM State Mapper (new skill)

Takes a protein → outputs a proteoform state map:

1. Pull sequence from UniProt
2. Pull known PTM sites from UniProt annotations
3. Cross-reference with Reactome pathways (which PTMs activate/deactivate what)
4. Cross-reference with PubMed for disease associations
5. Output proteoform state map (like Linares' collagen phosphorylation diagram)

### 5. Disease → Proteome Disruption Pipeline (full Linares loop)

```
Input: "Parkinson's disease"
  ↓
Step 1: OpenTargets → top 20 associated protein targets
Step 2: For each → UniProt PTM map + AlphaFold structure
Step 3: ClinVar + GWAS → pathogenic variants
Step 4: STRING-db → interaction network clustering
Step 5: ct-predict → which targets tried in trials? What worked/failed?
Step 6: Proteomic Dysfunction Scorer → rank untried targets
Step 7: PDB + BindingDB → druggability assessment
  ↓
Output: Top 5 proteomic intervention points, ranked by predicted success
```

### 6. Proteomics-Only Autoresearch (thesis validation)

Train ct-predict using ONLY protein-level features. If proteomic features alone get >0.85 AUC, strong evidence for Linares' thesis.

## Priority Ranking

| # | Project | Effort | Signal Value | Builds Toward |
|---|---------|--------|-------------|---------------|
| 1 | Proteomics features for ct-predict | 1 day | High | Everything |
| 2 | Proteomic Dysfunction Scorer | 2-3 days | Very high | Peptide design, disease pipeline |
| 3 | PTM State Mapper skill | 1 day | Medium | Disease pipeline |
| 4 | Peptide Design Agent | 2 days | High | Full loop |
| 5 | Disease → Proteome Pipeline | 3 days | Very high | Investment thesis validation |
| 6 | Proteomics-only autoresearch | 1 day | High | Academic signal |

---

## Gaps — What We Don't Have But Need

### Data Layer Gaps

#### 1. Proteome Digital Twin Data
Linares' central promise. No MCP or public API gives us patient-level proteome snapshots.
- **What exists**: UK Biobank Pharma Proteomics Project (~3,000 proteins × 54,000 participants), but access requires application + institutional affiliation
- **What we'd need**: An MCP or data pipeline to query mass-spec proteomics datasets (ProteomeXchange, PRIDE Archive, MassIVE)
- **Gap severity**: Critical — this is the "key:value pair" in his thesis
- **Workaround**: Use tissue-level expression proxies from GTEx + Human Protein Atlas (no MCP for HPA yet)
- **Key development: Nautilus Biotechnology** — see dedicated section below. Iterative proteoform mapping may be the technology that actually produces this data at proteoform resolution.

#### 2. Post-Translational Modification Databases
We have UniProt PTM annotations, but they're incomplete. The deep PTM databases are missing:
- **PhosphoSitePlus** — gold standard for phosphorylation, ubiquitination, acetylation, methylation sites. No MCP exists.
- **PTMcode** — functional associations between PTM sites. No MCP.
- **dbPTM** — integrated PTM resource. No MCP.
- **iPTMnet** — PTM network analysis. No MCP.
- **Gap severity**: High — proteoforms are the core of the thesis and we can't systematically query PTM state

#### 3. Human Protein Atlas
Tissue/cell-type protein expression + subcellular localization + pathology data. Complements GTEx (RNA) with actual protein-level measurements.
- No MCP exists
- Has a public API (proteinatlas.org/api)
- **Gap severity**: High — protein expression ≠ RNA expression, and this distinction matters for druggability

#### 4. Protein Stability & Half-life Data
How quickly a protein is degraded/recycled in vivo. Critical for peptide therapeutic design (target a stable vs transient protein = very different strategy).
- **ProteomicsDB** has some turnover data
- No MCP exists
- **Gap severity**: Medium

#### 5. Protein-Protein Interaction Structural Data
STRING-db gives us interaction networks, but not the 3D binding interfaces.
- **PDBe** (Protein Data Bank Europe) has better interface annotations than our PDB MCP
- **RCSB PDB** has computed binding site data
- **InterPro/Pfam** — domain-level interactions. No MCP.
- **Gap severity**: Medium-high — peptide design requires knowing *where* proteins touch

### Compute & Tooling Gaps

#### 6. Structure Prediction (local AlphaFold / ESMFold)
We can query AlphaFold DB for known structures, but can't predict new ones. Linares' thesis requires predicting structures for novel peptide sequences.
- **AlphaFold3** or **ESMFold** running locally or via API
- **Chai-1** — newer, faster, handles protein-ligand complexes
- **Gap severity**: Critical for peptide design pipeline — without this we can describe targets but can't computationally validate peptide candidates

#### 7. Molecular Docking / Binding Affinity Prediction
Once you have a candidate peptide and a target structure, you need to predict if they actually bind.
- **AutoDock Vina**, **GNINA**, **DiffDock** — all open source, none integrated
- **Gap severity**: Critical for closing the peptide design loop

#### 8. Peptide Property Prediction
Given a candidate amino acid sequence, predict: stability, solubility, cell permeability, immunogenicity, half-life in vivo.
- Tools exist (PeptideRanker, ToxinPred, CellPPD) but none are integrated
- **Gap severity**: High — without this, peptide suggestions are purely theoretical

#### 9. Sequence-to-Function Models — PARTIALLY CLOSED by BioReason-Pro (2026-03-19)
Beyond AlphaFold (structure), we need models that predict what a protein *does*:
- **ESM-2** (Meta) — protein language model, embeddings encode function
- **ProtTrans** — protein transformers
- These could be run via Ollama-style local inference
- **Gap severity**: ~~Medium~~ **Closing** — BioReason-Pro is a dramatically better answer than raw embeddings

**BioReason-Pro** ([bioRxiv 2026-03-19](https://www.biorxiv.org/content/10.64898/2026.03.19.712954v1)) from Bo Wang's lab (UHN/UofT/Vector Institute) + Arc Institute (Hani Goodarzi) changes this gap substantially. See detailed section below.

##### What BioReason-Pro Is

A multimodal reasoning LLM that takes a protein sequence and produces *explanations*, not just labels:
- **Structured reasoning traces** — step-by-step chain of thought showing how it arrives at functional conclusions
- **Functional summaries** — literature-grounded overviews of function, localization, pathway involvement
- **GO term annotations** — molecular function, biological processes, cellular components
- **Proposed mechanisms and testable interaction partners**

Previous biology AI (AlphaFold, ESM, etc.) all produce answers, not explanations. BioReason-Pro generates hypotheses with supporting evidence.

##### Architecture

Three-component system:
1. **ESM3 protein embeddings** — sequence-level representations from EvolutionaryScale's protein foundation model
2. **GO-GPT** — novel autoregressive transformer treating Gene Ontology prediction as sequence generation, capturing hierarchical + cross-aspect dependencies. Surpasses top public CAFA5 models.
3. **Qwen3-4B backbone** — LLM that reasons over integrated biological inputs (InterPro domains, STRING protein-protein interactions, PDB structures, organism info)

Training: SFT on ~130K proteins with synthetic reasoning traces from GPT-5, then RL against real biological data. During RL, reasoning traces got shorter AND more accurate simultaneously.

##### Key Results

- **27 protein experts preferred its annotations over UniProt 79% of the time** (blinded evaluation, sequences >150aa). Not "79% correct" — 79% more *informative and complete* than existing curated entries.
- 73.6% weighted Fmax on GO terms (best public CAFA5 baseline)
- De novo predicted experimentally confirmed binding partners with per-residue attention localizing to exact contact residues in cryo-EM structures
- Generated coherent hypotheses for AI-designed anti-CRISPR proteins with zero sequence/structural similarity to known proteins

##### Limitations

- Struggles with irregular proteins lacking clear domain structure
- "Mixed results" on ~100aa sequences, poor on short peptides (<0.5% of training data)
- The 79% metric is specifically for >150aa — weaker on shorter sequences
- Training reasoning traces generated by GPT-5 (synthetic) — could propagate errors
- Expert evaluation was 27 "colleagues" — independent replication needed
- Preprint only (4 days old as of 2026-03-23), not peer-reviewed

##### How It Connects to Our Projects

| Our Project | BioReason-Pro Impact |
|---|---|
| **Proteomic Dysfunction Scorer (#2)** | Provides functional hypotheses for any protein — mechanism, binding partners, pathway context. Instead of assembling from 7 MCPs, query BioReason-Pro first as synthesis layer, validate against MCPs |
| **Peptide Design Agent (#3)** | Step 1 ("user describes dysfunction") gets grounded — BioReason-Pro explains what a target does, how it interacts, what mechanisms are involved |
| **Disease → Proteome Pipeline (#5)** | Step 2 ("understand what each target does") is exactly BioReason-Pro's job. For the ~99.9% without good UniProt annotations, this was previously a dead end |
| **ct-predict proteomics features (#1)** | BioReason-Pro functional annotations could be a feature source — predicted GO terms, pathway membership, interaction density |

##### Integration Path: BioReason-Pro MCP

**No public API exists.** The atlas (bioreason.net) is a curated demo, not a queryable database. The app (app.bioreason.net) is a Google-auth web UI with no documented endpoints.

**What exists:**
- Open weights: `wanglab/bioreason-pro-rl` (4B params, F32 safetensors) — Apache 2.0
- Full source: [github.com/bowang-lab/BioReason-Pro](https://github.com/bowang-lab/BioReason-Pro) with `gogpt_api.py`, `interpro_api.py`, inference pipeline
- GO-GPT model: `wanglab/gogpt` (separate checkpoint)
- Training data: `wanglab/bioreason-pro-rl-reasoning-data`

**MCP approach: run locally + wrap as MCP server.**

| Detail | Value |
|--------|-------|
| Base LLM | Qwen3-4B — ~16GB F32, ~3-4GB quantized Q4. Fits on Mac. |
| Additional models | ESM3 (embeddings) + GO-GPT (GO term generation) — sizes TBD |
| Input | Protein sequence (amino acid string) |
| Output | Reasoning trace + functional summary + GO annotations + interaction partners |
| Hardware question | Whether full pipeline (ESM3 + GO-GPT + Qwen3-4B) runs on Apple Silicon / MPS or needs CUDA |
| Effort estimate | 3-5 days (clone, test inference, wrap as MCP, integrate into container) |

**Next step:** Clone repo, run `eval.py` pipeline, check if ESM3 + GO-GPT + Qwen3-4B run on Apple Silicon. If yes, wrapping as MCP is straightforward.

##### Sources

- [BioReason-Pro bioRxiv preprint](https://www.biorxiv.org/content/10.64898/2026.03.19.712954v1)
- [Arc Institute blog post](https://arcinstitute.org/news/bioreason-pro)
- [GitHub repo](https://github.com/bowang-lab/BioReason-Pro)
- [HuggingFace — RL model](https://huggingface.co/wanglab/bioreason-pro-rl)
- [HuggingFace — SFT model](https://huggingface.co/wanglab/bioreason-pro-sft)
- [HuggingFace — GO-GPT](https://huggingface.co/wanglab/gogpt)
- [BioReason (predecessor) — NeurIPS 2025 / arXiv](https://arxiv.org/abs/2505.23579)
- [Bo Wang — Xaira Therapeutics](https://www.xaira.com/team/bo-wang)
- [Bo Wang X/Twitter announcement](https://x.com/BoWang87/status/1929334758896812465)

##### Who Built It

- **Bo Wang** — PhD Stanford CS (2017), SVP & Head of Biomedical AI at Xaira Therapeutics ($1B AI drug discovery startup), Assistant Professor UofT, Chief AI Scientist at UHN (Canada's largest research hospital), CIFAR AI Chair at Vector Institute. Created scGPT (Nature's "Seven Technologies to Watch in 2025").
- **Hani Goodarzi** — Arc Institute
- Collaborators across Stanford, UC Berkeley, UCSF, UPenn, EPFL, ETH Zurich, Cohere, Xaira Therapeutics
- Notable: Adib Fallahpour (20-year-old 3rd year CS/Neuro student at UofT, IBO Silver Medalist) among key contributors

---

### Related: Nautilus Biotechnology & Iterative Proteoform Mapping (2026-03-23)

*From Antonio Linares' "This company is Palantir for peptides" (2026-03-23). Same author as the "peptides are the tip of the iceberg" article that started this doc.*

#### The Core Technology

**Nautilus Biotechnology** ($NAUT, $380M market cap, pre-revenue) has built an **iterative proteoform mapping platform** that solves the fundamental limitation of mass spectrometry:

| Approach | How It Reads Proteins | Limitation |
|----------|----------------------|------------|
| **Mass spectrometry** | Fragments proteins to read them | Destroys PTM state in the process — cannot tell if you're looking at one protein with glycans at positions A and B, or two proteins each with one glycan |
| **Nautilus iterative mapping** | Cycles fluorescently tagged probes across intact, immobilized proteins; registers binding events via computer vision | Requires lab setting (for now); fluorescent tags alter binding kinetics |

Iterative mapping reads the protein **intact and in place**, cycling through probes repeatedly until a complete picture emerges. In principle, this gives **infinite resolution over proteoform state** — the exact modifications at exact positions on the intact protein.

**Dynamic range**: 3+ orders of magnitude vs. industry average of 1 order. This means Nautilus can detect low-abundance disease-relevant proteoforms alongside high-abundance ones in the same sample. Most disease-relevant proteoforms (truncations, modifications preceding clinical symptoms) exist at low abundance — a platform that can't see them can't find the bug before it crashes the system.

#### The Moat

Binding kinetics change when fluorescent tags enter the picture. Tags are bulky molecules that interfere with precision binding — attaching one to a probe risks altering the very interaction you're trying to measure. This introduces noise hardest to separate from genuine signal at exactly the low-abundance range where disease-relevant proteoforms live. Every new protein class magnifies this calibration challenge, making the platform increasingly hard to replicate as Nautilus scales verticals.

Linares' read: "This feels like one of those rare situations where there is simply no one else in the room."

#### Current Milestones

| Timeline | Milestone |
|----------|-----------|
| Q4 2024 | Announced platform reconfiguration (surface chemistry, assay configuration) — extended timeline but positioned for maximum impact |
| Q4 2025 | **Tau assay** (Alzheimer's) launched in early access — ahead of schedule. Collaborators submitting samples, receiving data. |
| 2025-2026 | **Alpha-synuclein assay** (Parkinson's) — 18-month collaboration funded by Michael J. Fox Foundation |
| H2 2026 | **Oncology-focused proteoform assay** entering early access |
| Long term | Expanding across oncology, immunology, cardiology |

#### Financials

| Metric | Value |
|--------|-------|
| Market cap | $380M |
| Revenue | Pre-revenue |
| Cash | $103.4M (down from $345.7M peak in 2021 — natural development drawdown) |
| Operating loss | $66.8M (2025), improved from $81.5M (2024) |
| Debt | $30M (flat for 3 consecutive years) |
| Runway | Not in a race against collapsing runway |

#### The Alzheimer's/Parkinson's Proteoform Thesis

Both diseases manifest as **proteoform misfolding diseases**:
- **Alzheimer's**: amyloid beta plaques + hyperphosphorylated tau tangles destroy synaptic architecture
- **Parkinson's**: alpha-synuclein misfolds into Lewy bodies, kills dopaminergic neurons

But the plaques and tangles are **not the disease** — they're the wreckage. Both share a common upstream failure: the **mitophagy axis**. PINK1 (kinase that flags damaged mitochondria) and OPTN (receptor that executes clearance) are themselves proteoform-dependent. When either arrives in a dysfunctional proteoform state → damaged mitochondria accumulate → oxidative stress → misfolding cascade begins.

This is exactly the kind of root-cause proteomic analysis that iterative mapping enables and mass spectrometry cannot.

#### How This Connects to Our Stack

**Gap #1 (Proteome Digital Twin Data) — this is the technology that fills it.**

Our gap matrix lists "Proteome digital twin data" as Critical severity with the workaround being GTEx + HPA proxies. The fundamental problem: no technology could produce patient-level proteome snapshots at proteoform resolution. Nautilus' iterative mapping is designed to do exactly that.

| Our Need | Nautilus Provides |
|----------|------------------|
| Patient-level proteome snapshots | Intact proteoform mapping (not fragmented mass-spec) |
| PTM state resolution | Exact modification positions on intact proteins |
| Low-abundance proteoform detection | 3+ orders of magnitude dynamic range |
| Disease-relevant proteoforms | Tau, alpha-synuclein assays already in early access |

**Linares' long-term vision**: monthly proteomic snapshot → processed by AI alongside longitudinal biomarkers → eventually real-time digital twin with AI running permanently in the background. This maps directly to our Level 3 architecture (continuous delivery) and the Personal Biomarker Dashboard agent — the difference being Nautilus provides the proteomic layer while Oura provides the physiological layer.

**For our Disease → Proteome Pipeline (Project #5)**: The pipeline currently relies on population-level databases (OpenTargets, ClinVar, GWAS). If Nautilus data becomes accessible, we could run the same pipeline on an individual's actual proteomic snapshot — not "what genes are associated with Parkinson's?" but "which of YOUR proteoforms are in a dysfunctional state?"

**What we can't do yet**: Nautilus has no public API or data access program for computational researchers. Their early access is for wet-lab collaborators submitting physical samples. We're watching for when proteoform data becomes programmatically queryable — that's the integration point.

#### Updated Gap #1 Assessment

| Aspect | Before | After Nautilus |
|--------|--------|----------------|
| Technology exists? | Mass-spec only (destroys PTM state) | Iterative mapping preserves intact proteoform state |
| Data accessible? | UK Biobank (mass-spec, institutional access only) | Early access program (wet-lab collaborators only) |
| Programmatic access? | ProteomeXchange/PRIDE (mass-spec data) | No API yet — watching for it |
| Timeline to our integration | Build PRIDE MCP as proxy | Medium-term: wait for Nautilus data API; near-term: PRIDE MCP remains the workaround |

---

### Pipeline & Integration Gaps

#### 10. LigandForge or Equivalent
Linares specifically names this as the tool for computing personalized peptides. We have nothing comparable.
- Open alternatives: **RFdiffusion** (protein design), **ProteinMPNN** (sequence design from structure)
- These require GPU compute
- **Gap severity**: Critical — this is the "compiler" in his code metaphor

#### 11. Proteome Comparison / Diff Tool
If you have two proteome snapshots (healthy vs diseased), you need to diff them.
- No tool exists that does this cleanly
- Would need to build: take two sets of protein abundances + PTM states, compute δ
- **Gap severity**: High — this is the "stimuli: δProteome" concept

#### 12. Wet Lab / Synthesis Bridge
Even with perfect computational peptide design, you need to actually make the peptide.
- Peptide synthesis services exist (GenScript, Bachem, custom peptide houses)
- No API integration to order peptides programmatically
- **Gap severity**: Low for now (research phase), critical for production

### Knowledge & Ontology Gaps

#### 13. Proteoform Ontology
No standardized way to represent "protein X with phosphorylation at position 45 and glycosylation at position 120."
- **ProForma notation** exists but isn't widely adopted in APIs
- Our knowledge graph (kg-openpharma) doesn't model proteoforms
- **Gap severity**: Medium — becomes critical when building the proteomic dysfunction scorer

#### 14. Disease-Proteoform Associations
"Which specific proteoforms are associated with which diseases?" — this mapping barely exists in structured databases.
- Scattered across literature (PubMed)
- Could be mined with deep-research skill + PubMed MCP
- **Gap severity**: High — this is the core training data for the dysfunction scorer

---

## Gap Priority Matrix

| Gap | Severity | Can We Build an MCP? | Workaround? |
|-----|----------|---------------------|-------------|
| Proteome digital twin data | Critical | Near-term: PRIDE MCP (mass-spec). Long-term: Nautilus API (proteoform-level, no API yet) | GTEx + HPA proxy |
| PTM databases (PhosphoSitePlus) | High | Yes (has API) | UniProt annotations (partial) |
| Human Protein Atlas | High | Yes (has REST API) | GTEx RNA as proxy |
| Local structure prediction | Critical | No (needs GPU compute) | Query AlphaFold DB only |
| Molecular docking | Critical | Possible (CLI wrapper) | Literature-based binding data |
| Peptide property prediction | High | Yes (wrap existing tools) | Manual literature lookup |
| LigandForge / RFdiffusion | Critical | No (needs GPU) | Manual design + literature |
| Proteoform ontology | Medium | Build into kg-openpharma | ProForma strings |
| Disease-proteoform mapping | High | Mine from PubMed | Manual curation |
| Protein stability data | Medium | Yes (ProteomicsDB API) | Predict from sequence |
| PPI structural interfaces | Medium-high | Yes (PDBe API) | PDB + literature |
| Sequence-to-function models | ~~Medium~~ **Closing** | **BioReason-Pro local MCP** (4B params, Apache 2.0) | AlphaFold confidence as proxy |

## Immediate Next Steps

1. **Test BioReason-Pro locally** — clone repo, run inference pipeline on Apple Silicon, check ESM3 + GO-GPT + Qwen3-4B feasibility
2. **Build BioReason-Pro MCP** — if local inference works, wrap as MCP server (protein sequence → reasoning trace + GO terms + functional summary)
3. **Build PhosphoSitePlus MCP** — has an API, fills the biggest proteoform gap
4. **Build Human Protein Atlas MCP** — has REST API, fills protein expression gap
5. **Backfill proteomics features into ct-predict** — uses existing MCPs, tests thesis immediately
6. **Add ProteomeXchange/PRIDE MCP** — starts accessing real proteomics datasets

## The Meta-Play

Linares' flywheel: more data → better AI → better outcomes → more users → more data.

We're already running this with autoresearch on clinical trials. The next step is predicting **which proteomic interventions will work** — same pattern, different target variable. Our infrastructure (autoresearch + MCPs + BioClaw) is built for exactly this.

The critical missing pieces are all on the **compute side** (structure prediction, docking, peptide design) rather than the data side. We can query and analyze proteomics data today. We can't yet *design* new proteins computationally. That's the gap between "research assistant" and "peptide compiler."

---

## Related: The Peptide Pharmacogenomics Cohort (2026-03-21)

*"20 people. 90 days. The first real data on whether your peptides actually work for you."*

### What It Is

A real-world cohort study (not a clinical trial) connecting **pharmacogenomics to peptide outcomes** — the first dataset of its kind. 20 participants, $1,000 each, 90 days.

### How It Works

1. **Genetic testing** — 116-marker panel built specifically for peptide metabolism (enzyme pathways, hormone receptors, recovery mechanisms)
2. **Biological age test** — baseline measurement via finger prick
3. **Personalized protocol** — which peptides match your genetics, which to drop, dosing adjustments based on metabolizer status
4. **90-day run** — participants source own peptides, follow personalized protocol
5. **Retest biological age** — same methodology, compare delta

### Key Peptides Mentioned

- **GLP-1 agonists** (semaglutide) — fastest-selling drug class in pharma history
- **BPC-157** — gastric peptide, injury recovery (tendon, meniscus)
- **CJC-1295 + Ipamorelin** — growth hormone secretagogue stack (sleep, recovery, body comp)
- **Selank / Semax** — nootropic/anxiolytic peptides (focus, anxiety, replacing SSRIs)

### Why This Matters for Us

This cohort is building **exactly the dataset that doesn't exist** — the link between genetics and peptide response. The core insight maps directly to Linares' thesis:

> "Two people can take the exact same peptide at the exact same dose and have completely different outcomes. Not because the peptide is bad, but because their genetics handle it differently."

This is pharmacogenomics applied to peptides: CYP enzyme variants, receptor polymorphisms, metabolizer phenotypes → differential peptide efficacy. It's the same "proteome as code" idea but from the **genetic input side** rather than the proteomic output side.

### How This Connects to Our Stack

| Their Component | Our Equivalent | Gap? |
|---|---|---|
| 116-marker genetic panel | ClinPGx MCP (pharmacogenomics guidelines) | Partial — ClinPGx covers drug metabolism genes but not peptide-specific markers |
| Biological age testing | No equivalent | Yes — need epigenetic clock / biological age MCP |
| Personalized protocol generation | BioClaw agent + pharmacogenomics skill | Partial — we can reason about PGx but lack peptide-specific decision rules |
| Outcome tracking (Δ biological age) | No equivalent | Yes — need longitudinal data collection |
| Peptide-genotype response dataset | Nothing exists anywhere | Yes — this is the novel dataset |

### New Gaps Identified

#### 15. Biological Age / Epigenetic Clock Data
The cohort uses biological age as the outcome measure. We have no way to interpret or work with epigenetic clock data.
- **DNA methylation clocks**: Horvath, GrimAge, PhenoAge, DunedinPACE
- **Providers**: TruDiagnostic, Elysium Index
- No MCP or data source integrated
- **Gap severity**: High — this is the measurable outcome in the "peptide works vs doesn't" question

#### 16. Peptide-Specific Pharmacogenomics Knowledge Base
ClinPGx covers traditional drugs (warfarin, clopidogrel, SSRIs) but NOT peptides. No structured database maps:
- Which CYP/enzyme variants affect BPC-157 metabolism?
- Which receptor polymorphisms modulate GLP-1 response?
- Which genetic variants predict growth hormone secretagogue sensitivity?
- **Gap severity**: Critical — this knowledge is scattered across papers, not structured. The cohort is literally building this from scratch.

#### 17. Metabolizer Phenotype → Peptide Dosing Rules
Even if we know someone is a CYP2D6 poor metabolizer, we don't have peptide-specific dosing adjustment rules (unlike for SSRIs/opioids where CPIC guidelines exist).
- **Gap severity**: High — the cohort will generate these rules empirically

#### 18. Longitudinal Self-Tracking Integration
The cohort tracks participants over 90 days. We have no infrastructure for:
- Ingesting wearable data (Oura, Whoop, Apple Health)
- Tracking subjective outcomes over time
- Correlating protocol changes with biomarker shifts
- **Gap severity**: Medium — becomes critical for any real-world validation

### Updated Gap Priority Matrix

| Gap | Severity | Can We Build? | Workaround? |
|-----|----------|--------------|-------------|
| Proteome digital twin data | Critical | Near-term: PRIDE MCP (mass-spec). Long-term: Nautilus API (proteoform-level, no API yet) | GTEx + HPA proxy |
| PTM databases (PhosphoSitePlus) | High | Yes (has API) | UniProt annotations (partial) |
| Human Protein Atlas | High | Yes (has REST API) | GTEx RNA as proxy |
| Local structure prediction | Critical | No (needs GPU) | Query AlphaFold DB only |
| Molecular docking | Critical | Possible (CLI wrapper) | Literature-based binding data |
| Peptide property prediction | High | Yes (wrap existing tools) | Manual literature lookup |
| LigandForge / RFdiffusion | Critical | No (needs GPU) | Manual design + literature |
| **Peptide-PGx knowledge base** | **Critical** | **Mine from PubMed** | **Manual curation** |
| **Biological age / epigenetic clocks** | **High** | **Possible (API wrappers)** | **None** |
| **Metabolizer → peptide dosing rules** | **High** | **Build from literature** | **None — doesn't exist yet** |
| Proteoform ontology | Medium | Build into kg-openpharma | ProForma strings |
| Disease-proteoform mapping | High | Mine from PubMed | Manual curation |
| Protein stability data | Medium | Yes (ProteomicsDB API) | Predict from sequence |
| PPI structural interfaces | Medium-high | Yes (PDBe API) | PDB + literature |
| Sequence-to-function models | ~~Medium~~ **Closing** | **BioReason-Pro local MCP** (4B params, Apache 2.0) | AlphaFold confidence as proxy |
| **Longitudinal tracking** | **Medium** | **Build custom** | **Spreadsheets** |

### New Project Ideas from This

#### 7. Peptide-PGx Literature Miner (autoresearch + PubMed MCP)

Use deep-research skill to systematically mine PubMed for every paper connecting a genetic variant to a peptide's metabolism or efficacy. Build the structured dataset that the cohort is generating empirically but from published literature.

**Input**: List of popular peptides (BPC-157, GLP-1 agonists, CJC-1295, Ipamorelin, Selank, Semax, TB-500, PT-141, etc.)
**Process**: For each peptide, search PubMed + OpenAlex for: metabolizing enzymes, receptor genes, transporter genes, known polymorphisms affecting response
**Output**: Structured CSV: peptide × gene × variant × effect (↑/↓ efficacy, ↑/↓ clearance, adverse reaction)

This would be the **first structured peptide pharmacogenomics database**. Even partial, it's valuable.

**Effort**: 2-3 days with BioClaw deep-research skill + PubMed MCP. Could run as a scheduled autoresearch task.

#### 8. Peptide Response Predictor (new autoresearch project)

Like ct-predict but for individual peptide response. Train on:
- Pharmacogenomics data (ClinPGx)
- Known drug-gene interactions (DrugBank)
- Peptide mechanism data (ChEMBL, PubChem)
- Published case reports (PubMed mining)

**Label**: Reported efficacy from literature, clinical reports, and eventually cohort data.

**Output**: Given a person's metabolizer profile + a peptide → predicted response score.

This is the "AI doctor" from Linares' thesis, but scoped to peptides.

#### 9. Biological Age Delta Predictor

If the cohort publishes results (even anonymized), train a model:
- Input: genetic panel results + peptide protocol + baseline biological age
- Output: predicted Δ biological age after 90 days

Even with n=20, this establishes a framework. As cohorts scale, the model improves — Linares' flywheel.

### The Convergence

Linares describes the vision top-down (proteome → AI → cure). This cohort is building it bottom-up (genetics → peptide matching → measure outcomes). They meet in the middle:

```
Linares (top-down):     Proteome snapshot → AI finds bugs → design peptide fix
Cohort (bottom-up):     Genetic profile → match peptides → measure if it works
                                    ↕
                         Both need the same thing:
                    genotype-to-peptide-response mapping
```

Our tools sit at the intersection. We have the MCPs to query both sides (genetics via ClinVar/GWAS/ClinPGx, peptides via ChEMBL/DrugBank/PubChem) and the autoresearch loop to find patterns.

### Updated Immediate Next Steps

1. **Build Peptide-PGx Literature Miner** — mine PubMed for peptide × gene × variant associations (new, high value)
2. **Build PhosphoSitePlus MCP** — fills proteoform gap
3. **Build Human Protein Atlas MCP** — fills protein expression gap
4. **Backfill proteomics features into ct-predict** — tests thesis with existing data
5. **Add ProteomeXchange/PRIDE MCP** — access real proteomics datasets
6. **Investigate local ESM-2 via Ollama** — protein language model
7. **Scope biological age data sources** — what APIs exist for epigenetic clock providers?

---

## Related: "The Pharmacy In Your Kitchen" (2026-03-21)

*The full-stack vision: continuous sensing → AI synthesis → adaptive therapeutic output, moved from hospital to home.*

### The Three-Layer Model

This article completes the picture. Linares described the proteomics layer (what to fix). The cohort described the pharmacogenomics layer (who responds to what). This article describes the **delivery architecture** — how it all reaches the individual.

The author frames three layers converging:

| Layer | What It Does | Current State | 2034 Vision |
|---|---|---|---|
| **1. Data / Sensing** | Continuous biological monitoring | Wearables (Oura, Whoop, CGMs), intermittent labs | Ambient sensor mesh: sleep architecture, autonomic recovery, glucose dynamics, inflammatory tone, respiratory variation, pathogen exposure — all passive, all continuous |
| **2. Intelligence / AI** | Synthesis of longitudinal biological data | Fragmented EHRs, protocol-following alerts | AI that models the individual over time — not retrieving guidelines but modeling the person. Connects signals to mechanisms, generates personalized actions |
| **3. Output / Therapeutics** | Adaptive drug formulation & delivery | Mass-produced fixed-dose tablets from centralized manufacturing | Compact home devices that formulate personalized therapeutic packets calibrated to your physiology *that morning* |

### The Core Argument

> "The average patient, clinically speaking, does not exist."

Medicine is built around statistical abstractions: standard doses, standard protocols, standard thresholds. This worked when we couldn't measure individuals continuously. Now we can (or will). The shift is:

- **Episodic → Continuous**: from "labs twice a year" to living biological map
- **Reactive → Preventive**: from "treat after threshold crossed" to "correct drift before it becomes disease"
- **Standardized → Personalized**: from "same pill for everyone" to "formulated for your biology today"
- **Centralized → Distributed**: from hospital/pharmacy to home/kitchen

### The Hypertension Example

Two patients with identical blood pressure diagnoses can have completely different underlying biology:
- Sympathetic overactivation + sleep disruption
- Visceral adiposity + insulin resistance
- Sleep apnea
- Alcohol + declining fitness + vascular stiffness
- Renal sodium handling

Yet they get the same diagnostic label and similar treatment. The article argues this "standard of care" is often just "the cleanest approximation the system can operationalize at scale."

### How This Connects to Our Stack

This article describes the **deployment layer** we haven't thought about. We've been focused on:
- Data querying (MCPs)
- Pattern finding (autoresearch/ct-predict)
- Knowledge synthesis (BioClaw agent)

But the full loop requires **continuous individual monitoring → AI interpretation → adaptive output**. Here's how our tools map:

| Their Vision | Our Current Capability | Gap |
|---|---|---|
| Continuous biological sensing | None — we work with population-level databases | Need wearable/CGM data integration |
| Longitudinal personal baseline | Per-group memory in BioClaw (behavioral, not biological) | Need biological time-series storage |
| AI that models the individual | BioClaw agent + autoresearch (models populations, not individuals) | Need individual-level modeling |
| Adaptive therapeutic formulation | 116-marker panel → peptide protocol (static, one-time) | Need dynamic protocol adjustment |
| Drift detection (deviation from personal baseline) | No equivalent | Need anomaly detection on personal time-series |

### New Gaps Identified

#### 19. Continuous Biomarker Data Integration
The article's "data layer" requires ingesting streams from:
- **CGMs** (continuous glucose monitors — Dexcom, Libre)
- **Wearables** (Oura, Whoop, Apple Watch — HRV, sleep stages, SpO2, skin temperature)
- **Smart scales** (body composition over time)
- **Blood pressure monitors** (home readings over time)
- Some have APIs (Oura, Whoop). Others require workarounds.
- **Gap severity**: High for the "pharmacy in your kitchen" vision. Not needed for current research projects.

#### 20. Personal Baseline Modeling
The article's key insight: what matters is **deviation from YOUR baseline**, not population thresholds. Requires:
- Time-series database for individual biomarkers
- Anomaly detection (is today's reading unusual *for this person*?)
- Trend analysis (is this metric drifting over weeks/months?)
- **Gap severity**: Medium — future layer, not needed for current peptide/proteomics work

#### 21. Dynamic Protocol Adjustment
The cohort gives you ONE protocol for 90 days. The kitchen pharmacy vision requires:
- Continuous re-evaluation: "your glucose variability worsened → adjust metabolic peptides"
- Feedback loop: biomarker response → protocol modification → new biomarker reading
- This is the autoresearch loop applied to a single person instead of a population model
- **Gap severity**: Medium-high — the differentiator between static PGx and living medicine

### The Three Articles as One System

These three articles describe **the same system at three different zoom levels**:

```
Article 1 — Linares (Molecular):
  DNA → amino acids → peptides → proteins → proteoforms
  "The proteome is code and we're learning to write it"
  LEVEL: What to fix (molecular targets)

Article 2 — Cohort (Individual):
  Genetic panel → metabolizer profile → personalized peptide protocol → measure Δ
  "Which peptides work for which people"
  LEVEL: Who responds to what (pharmacogenomics)

Article 3 — Kitchen Pharmacy (System):
  Continuous sensing → AI synthesis → adaptive formulation → home delivery
  "Medicine moves closer to the person"
  LEVEL: How to deliver it (architecture)
```

### What This Means for Us

We're building at Level 1 (molecular) and Level 2 (individual prediction). Level 3 (continuous delivery) is years away but informs architecture decisions now:

1. **BioClaw's agent architecture already supports the loop** — sense (MCPs query data) → synthesize (agent reasons) → act (protocol recommendation). The question is whether to start accepting individual biomarker streams alongside population databases.

2. **The autoresearch pattern scales from populations to individuals** — today it optimizes a model across 2,151 trials. Tomorrow it could optimize a protocol for one person across 90 days of CGM + HRV + sleep data.

3. **The "kitchen pharmacy" is really just a tighter feedback loop** — same architecture, faster cycle time, narrower scope (n=1 instead of n=2000).

### Updated Project Ideas

#### 10. Personal Biomarker Dashboard Agent

A BioClaw skill that:
1. Ingests Oura/Whoop API data (or CSV export)
2. Builds personal baseline over 30+ days
3. Detects drift and anomalies ("your HRV has dropped 15% over 2 weeks")
4. Cross-references with PubMed for mechanistic explanations
5. Suggests protocol adjustments based on peptide-PGx knowledge base

This bridges Level 2 (individual PGx) and Level 3 (continuous monitoring). Doesn't require hardware — just API integration with existing wearables.

#### 11. N-of-1 Protocol Optimizer

Apply the autoresearch pattern to a single person:
- Input: daily biomarker readings + current peptide protocol
- The agent proposes small protocol changes (timing, dosing, compound swaps)
- Tracks biomarker response over 1-2 week windows
- Keeps changes that improve metrics, reverts those that don't
- Over time, converges on an optimized personal protocol

This is literally the autoresearch loop applied to n=1. Same architecture, different data source.

### Updated Full Architecture Vision

```
LEVEL 1 — Molecular Intelligence (have)
  ├── 37 biomedical MCPs (UniProt, AlphaFold, STRING-db, etc.)
  ├── 161 domain skills (proteomics, drug discovery, etc.)
  ├── ct-predict (0.926 AUC trial outcome prediction)
  ├── BioReason-Pro MCP (planned — protein sequence → function reasoning)
  └── Autoresearch loop (autonomous model improvement)

LEVEL 2 — Individual Matching (building)
  ├── 116-marker panel reverse-engineering (documented)
  ├── Peptide-PGx Literature Miner (proposed)
  ├── Peptide Response Predictor (proposed)
  └── Biological Age Delta Predictor (proposed)

LEVEL 3 — Continuous Delivery (future)
  ├── Wearable data integration (Oura/Whoop APIs)
  ├── Personal baseline modeling (time-series + anomaly detection)
  ├── N-of-1 protocol optimizer (autoresearch for individuals)
  └── Dynamic protocol adjustment (feedback loop)
```

### Updated Immediate Next Steps

1. **Test BioReason-Pro locally** — clone repo, run inference on Apple Silicon, check ESM3 + GO-GPT + Qwen3-4B feasibility
2. **Build BioReason-Pro MCP** — if local inference works, wrap as MCP (protein sequence → reasoning + GO terms + functional summary). Closes Gap #9, accelerates Projects #2, #3, #5.
3. **Build Peptide-PGx Literature Miner** — mine PubMed for peptide × gene × variant associations
4. **Build PhosphoSitePlus MCP** — fills proteoform gap
5. **Build Human Protein Atlas MCP** — fills protein expression gap
6. **Backfill proteomics features into ct-predict** — tests thesis with existing data
7. **Add ProteomeXchange/PRIDE MCP** — access real proteomics datasets
8. **Scope biological age data sources** — APIs for epigenetic clock providers
9. **Prototype Oura/Whoop API integration** — first step toward continuous sensing layer
10. **Design n-of-1 protocol optimizer** — apply autoresearch pattern to individual biomarker streams
