---
name: protein-therapeutic-design
description: De novo protein therapeutic design and engineering. Protein binder design, enzyme engineering, scaffold optimization, RFdiffusion concepts, ProteinMPNN sequence design, structure prediction, binding interface analysis, developability assessment. Use when user mentions protein design, de novo protein, protein binder, protein engineering, RFdiffusion, ProteinMPNN, protein scaffold, binding interface design, antibody alternative, miniprotein, enzyme design, or therapeutic protein design.
---

# Protein Therapeutic Design

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste executable code templates.
> **ESM recipes**: See [esm-recipes.md](esm-recipes.md) for advanced ESM3 multimodal generation, ESMFold, ESM-IF1 inverse folding, ESM C embeddings, variant scoring, and Forge API batch processing.
> **ColabFold recipes**: See [colabfold-recipes.md](colabfold-recipes.md) for design validation via ColabFold structure prediction (self-consistency checks, mutant screening, complex prediction).
> **Boltz-2 recipes**: See [boltz-recipes.md](boltz-recipes.md) for designed protein-ligand complex prediction, template-forced validation, and binding affinity estimation via Boltz-2.
> **Chai-1 recipes**: See [chai-recipes.md](chai-recipes.md) for glycoprotein design validation, restraint-guided complex prediction, and modified residue modeling via Chai-1.
> **ProteinMPNN recipes**: See [proteinmpnn-recipes.md](proteinmpnn-recipes.md) for inverse folding sequence design from scaffold structures, interface design, and the full design-predict-validate loop.
> **Protenix recipes**: See [protenix-recipes.md](protenix-recipes.md) for highest-accuracy design validation with inference-time scaling, mini model screening, and multi-tool validation cascade.

De novo protein therapeutic design specialist covering the full computational pipeline from target characterization through binder design, sequence optimization, and developability assessment. Uses UniProt for protein data and domain architecture, STRING for interaction networks and functional context, DrugBank for competitive landscape, PubMed for literature evidence, and ChEMBL for existing bioactivity data. Guides design of miniproteins, repeat proteins, de novo enzymes, constrained peptides, and nanobody-like scaffolds using computational methodology concepts from RFdiffusion, ProteinMPNN, ESMFold, and AlphaFold2.

## Report-First Workflow

1. **Create report file immediately**: `[target]_therapeutic_design_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Antibody humanization, CDR engineering, and biologics CMC** -> use antibody-engineering skill
- **Small molecule binder discovery and ADMET filtering** -> use binder-discovery-specialist skill
- **Protein structure retrieval and AlphaFold models** -> use protein-structure-retrieval skill
- **Structure prediction for novel sequences (design validation)** -> use colabfold-predict skill
- **Protein-protein interaction networks and pathway context** -> use protein-interactions skill
- **Multi-dimensional target validation scoring** -> use drug-target-validator skill

## When NOT to Use This Skill

- Antibody humanization or CDR grafting → use `antibody-engineering`
- Small molecule hit-to-lead or ADMET optimization → use `binder-discovery-specialist`
- Protein structure retrieval or quality assessment → use `protein-structure-retrieval`
- PPI network analysis or hub protein identification → use `protein-interactions`
- Target validation scoring with genetic and clinical evidence → use `drug-target-validator`
- Medicinal chemistry or SAR-driven compound optimization → use `medicinal-chemistry`

## Available MCP Tools

### `mcp__uniprot__uniprot_data` (Target Protein Data & Sequence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_proteins` | Search proteins by keyword or name | `query`, `organism`, `size` |
| `get_protein_info` | Full protein profile (function, localization, disease) | `accession`, `format` |
| `search_by_gene` | Find proteins by gene name | `gene`, `organism`, `size` |
| `get_protein_sequence` | Get protein sequence (FASTA/JSON) | `accession`, `format` |
| `get_protein_features` | Protein features (domains, sites, PTMs, disulfides) | `accession` |
| `get_protein_structure` | Structural data (PDB IDs, AlphaFold) | `accession` |
| `get_protein_domains_detailed` | Detailed domain architecture and boundaries | `accession` |
| `get_protein_variants` | Known protein variants and mutations | `accession` |
| `get_protein_interactions` | Protein-protein interactions from UniProt | `accession` |
| `search_by_function` | Search proteins by molecular function | `function`, `organism`, `size` |
| `search_by_localization` | Search proteins by subcellular location | `location`, `organism`, `size` |
| `get_external_references` | Cross-database references (PDB, Pfam, InterPro) | `accession` |
| `compare_proteins` | Compare two protein sequences | `accession1`, `accession2` |
| `get_protein_homologs` | Find homologous proteins | `accession`, `organism`, `size` |
| `analyze_sequence_composition` | Amino acid composition and properties | `accession` |

### `mcp__stringdb__stringdb_data` (Interaction Networks & Functional Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_protein_interactions` | Direct interaction partners with scores | `identifiers`, `species`, `required_score` |
| `get_interaction_network` | Full interaction network graph | `identifiers`, `species`, `required_score` |
| `get_functional_enrichment` | GO terms, KEGG pathways, domain enrichment | `identifiers`, `species` |
| `get_protein_annotations` | Functional annotations from STRING | `identifiers`, `species` |
| `search_proteins` | Search STRING database for proteins | `identifier`, `species` |

### `mcp__drugbank__drugbank_info` (Existing Therapeutics & Competitive Landscape)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile (mechanism, targets, pharmacodynamics) | `drugbank_id` |
| `search_by_target` | All drugs acting on a target | `target`, `limit` |

### `mcp__pubmed__pubmed_articles` (Literature Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search with date range | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details by PMID | `pmid` |

### `mcp__chembl__chembl_info` (Bioactivity & Small Molecule Benchmarks)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50, Kd) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |

### `mcp__alphafold__alphafold_data` (AlphaFold Predicted Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_structure` | Get AlphaFold predicted structure for design input | `uniprotId`, `format` (json/pdb/cif) |
| `download_structure` | Download structure file for computational design | `uniprotId`, `format` |
| `check_availability` | Check if prediction exists | `uniprotId` |
| `get_confidence_scores` | Get pLDDT scores for binding site selection | `uniprotId` |
| `analyze_confidence_regions` | Identify high/low confidence regions | `uniprotId` |
| `compare_structures` | Compare two predicted structures | `uniprotId1`, `uniprotId2` |
| `find_similar_structures` | Find structurally similar proteins for scaffold inspiration | `uniprotId` |

### `mcp__pdb__pdb_data` (Experimental Structures from PDB)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_structures` | Search experimental structures for design templates | `query`, `limit`, `experimental_method`, `resolution_range`, `sort_by` |
| `get_structure_info` | Get structure details (resolution, chains, ligands) | `pdb_id`, `format` |
| `download_structure` | Download structure file for design input | `pdb_id`, `format` |
| `search_by_uniprot` | Find PDB structures for target protein | `uniprot_id`, `limit` |
| `get_structure_quality` | Resolution, R-factor, validation | `pdb_id` |

### `mcp__bindingdb__bindingdb_data` (BindingDB — Small Molecule Competitive Landscape)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_ligands_by_target` | Known small molecule binders — assess competition from small molecules | `uniprot_id`, `affinity_type`, `affinity_cutoff` |
| `get_target_info` | Target protein characterization from BindingDB | `uniprot_id` |

### BindingDB Competitive Landscape Assessment

Check BindingDB for existing small molecule binders to assess the competitive landscape for biologic vs small molecule approach. If potent small molecule binders already exist, the protein therapeutic must offer clear differentiation (novel epitope, undruggable pocket, PPI disruption).

```
1. mcp__bindingdb__bindingdb_data(method="get_ligands_by_target", uniprot_id="TARGET_UNIPROT_ID", affinity_type="IC50", affinity_cutoff=1000)
   -> Retrieve all small molecules with IC50 < 1000 nM for the target

2. mcp__bindingdb__bindingdb_data(method="get_target_info", uniprot_id="TARGET_UNIPROT_ID")
   -> Get BindingDB target characterization — number of known ligands, assay coverage

Use this data to:
- Assess whether small molecules already cover the target well (favors biologic only if novel mechanism)
- Identify binding sites occupied by small molecules — design protein binder for different epitope
- Determine if target is "undruggable" by small molecules (supports protein therapeutic approach)
- Benchmark protein binder affinity targets against best small molecule Kd/IC50 values
```

---

## Python Environment

The container has Python 3.11+ with standard scientific libraries. Use Python for sequence analysis, property calculations, and scoring. All code blocks are executable via Bash.

---

## Design Pipeline

### Phase 1: Target Characterization

Comprehensive characterization of the target protein — structure, domains, binding interfaces, interaction partners, and biological context.

```
1. mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "TARGET_GENE", organism: "human", size: 5)
   -> Get UniProt accession, confirm target identity, note isoforms

2. mcp__uniprot__uniprot_data(method: "get_protein_info", accession: "UNIPROT_ACC", format: "json")
   -> Full target profile: function, subcellular location, tissue expression, disease associations

3. mcp__uniprot__uniprot_data(method: "get_protein_domains_detailed", accession: "UNIPROT_ACC")
   -> Domain architecture: extracellular domains, binding domains, catalytic sites, disordered regions

4. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
   -> Feature annotations: disulfide bonds, glycosylation sites, active sites, metal binding

5. mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "UNIPROT_ACC", limit: 10)
   -> Find all experimental structures — note resolution and coverage

6. mcp__pdb__pdb_data(method: "get_structure_quality", pdb_id: "XXXX")
   -> Assess quality of best experimental structure for design input

7. mcp__alphafold__alphafold_data(method: "get_structure", uniprotId: "UNIPROT_ACC", format: "pdb")
   -> AlphaFold predicted structure for regions without experimental data

8. mcp__alphafold__alphafold_data(method: "analyze_confidence_regions", uniprotId: "UNIPROT_ACC")
   -> Identify high-confidence regions suitable for binding site selection

9. mcp__uniprot__uniprot_data(method: "get_protein_sequence", accession: "UNIPROT_ACC", format: "fasta")
   -> Canonical sequence for design input

7. mcp__uniprot__uniprot_data(method: "get_protein_variants", accession: "UNIPROT_ACC")
   -> Known variants at binding interface — design must tolerate common polymorphisms

8. mcp__stringdb__stringdb_data(method: "get_protein_interactions", identifiers: "TARGET_GENE", species: 9606, required_score: 700)
   -> Natural binding partners — reveals which interfaces are already engaged

9. mcp__stringdb__stringdb_data(method: "get_functional_enrichment", identifiers: "TARGET_GENE", species: 9606)
   -> Pathway context: what biological processes the target participates in

10. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "TARGET_NAME protein structure binding interface epitope", num_results: 15)
    -> Published structural and binding data for the target

DECISION GATE: Proceed only if target has structural data (PDB or AlphaFold) AND identifiable surface regions.
Report: target type (soluble/membrane/secreted), available structures, known binding interfaces.
```

**Target Characterization Checklist:**

| Parameter | Required Information |
|-----------|---------------------|
| **Protein type** | Soluble, membrane-bound, secreted, intracellular |
| **Structural coverage** | PDB structures via `mcp__pdb__pdb_data`, AlphaFold pLDDT via `mcp__alphafold__alphafold_data` |
| **Domain architecture** | Binding domains, catalytic domains, disordered regions |
| **Known interfaces** | Natural protein-protein interaction surfaces |
| **PTMs at surface** | Glycosylation, phosphorylation that affect accessibility |
| **Polymorphisms** | Common variants at candidate binding sites |

### Phase 2: Binding Site Selection

Identify and rank candidate binding sites on the target surface.

```
1. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
   -> Map all annotated sites: active site, binding site, disulfide bonds, modified residues

2. mcp__uniprot__uniprot_data(method: "get_protein_interactions", accession: "UNIPROT_ACC")
   -> Identify known PPI interfaces — design can target, mimic, or avoid these

3. mcp__stringdb__stringdb_data(method: "get_interaction_network", identifiers: "TARGET_GENE,PARTNER1,PARTNER2", species: 9606, required_score: 700)
   -> Map the full interaction neighborhood to understand interface competition

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "TARGET_NAME binding site epitope mapping surface hot spot", num_results: 10)
   -> Published binding site characterization data
```

**Python code template — Interface residue analysis:**

```bash
python3 << 'PYEOF'
def analyze_binding_site(sequence, site_residues):
    """Analyze candidate binding site properties from sequence and residue indices."""
    surface_propensity = {
        'A':0.49,'R':0.95,'N':0.81,'D':0.81,'C':0.32,'E':0.93,'Q':0.81,
        'G':0.48,'H':0.66,'I':0.29,'L':0.41,'K':0.93,'M':0.44,'F':0.42,
        'P':0.75,'S':0.70,'T':0.71,'W':0.49,'Y':0.67,'V':0.36
    }
    hydrophobicity = {
        'A':1.8,'R':-4.5,'N':-3.5,'D':-3.5,'C':2.5,'E':-3.5,'Q':-3.5,
        'G':-0.4,'H':-3.2,'I':4.5,'L':3.8,'K':-3.9,'M':1.9,'F':2.8,
        'P':-1.6,'S':-0.8,'T':-0.7,'W':-0.9,'Y':-1.3,'V':4.2
    }
    site_seq = ''.join(sequence[i-1] for i in site_residues if i <= len(sequence))
    avg_surface = sum(surface_propensity.get(aa, 0.5) for aa in site_seq) / max(len(site_seq), 1)
    avg_hydro = sum(hydrophobicity.get(aa, 0) for aa in site_seq) / max(len(site_seq), 1)
    pos_charged = sum(1 for aa in site_seq if aa in 'RK')
    neg_charged = sum(1 for aa in site_seq if aa in 'DE')
    aromatic = sum(1 for aa in site_seq if aa in 'FWY')

    score = 0
    if avg_surface > 0.6: score += 25
    if -2.0 < avg_hydro < 1.0: score += 25
    if aromatic >= 2: score += 25
    if 15 <= len(site_seq) <= 40: score += 25

    print(f"Site: {len(site_seq)} residues | Surface: {avg_surface:.2f} | Hydro: {avg_hydro:.2f}")
    print(f"Charge: +{pos_charged}/-{neg_charged} | Aromatic: {aromatic} | Score: {score}/100")
    return score

# Usage: analyze_binding_site("MKTL...", [45, 47, 49, 72, 74, 76, 78, 95, 97, 99])
print("Template loaded. Replace with actual target data.")
PYEOF
```

**Binding Site Selection Criteria:**

| Criterion | Preferred | Acceptable | Avoid |
|-----------|----------|------------|-------|
| **Surface accessibility** | Fully exposed loop/helix | Partially accessible cleft | Buried interior |
| **Structural order** | Well-resolved (B-factor < 40) | AlphaFold pLDDT > 70 | Disordered (pLDDT < 50) |
| **Glycosylation** | No glycans within 10 A | Single glycan, manageable | Dense glycosylation shield |
| **Interface size** | 800-1500 A^2 | 600-2000 A^2 | < 500 A^2 (too small) |
| **Hot spot residues** | Trp, Tyr, Arg at interface | Mixed composition | Mostly Ala, Gly (featureless) |

### Phase 3: Computational Design Concepts

Guide the de novo design approach using RFdiffusion backbone generation, ProteinMPNN sequence design, and structure prediction validation.

**RFdiffusion Backbone Generation:**

```
Design parameters to specify:

1. Scaffold type:
   - Unconditional: generate novel fold from scratch
   - Binder design: condition on target structure, specify binding hotspot residues
   - Symmetric: generate symmetric oligomers (homo-dimers, trimers)
   - Motif scaffolding: incorporate a functional motif into a new scaffold

2. Key RFdiffusion parameters (for user's computational setup):
   - contigs: define chain lengths and target residue ranges
     Example: "A1-100/0 50-80" = target residues 1-100 fixed, design 50-80 residue binder
   - hotspot_residues: target residues the binder should contact
     Example: "A45,A47,A72,A74,A95" = five residues on chain A
   - num_designs: number of backbones to generate (typically 100-1000)

3. Recommended settings by modality:
   - Miniprotein binder (40-80 aa): contigs="A1-N/0 40-80", 500 designs
   - Repeat protein binder (100-200 aa): contigs="A1-N/0 100-200", 200 designs
   - Enzyme scaffold: motif scaffolding mode with catalytic residues fixed
```

**ProteinMPNN Sequence Design:**

```
1. Input: backbone coordinates from RFdiffusion (.pdb file)

2. Key parameters:
   - sampling_temp: 0.1 (conservative) to 0.3 (diverse)
   - num_seq_per_target: typically 8-32 sequences per backbone
   - fixed_positions: interface residues to preserve
   - tied_positions: for symmetric designs

3. Protocol:
   - Generate 16 sequences per backbone at temp=0.1 (high confidence)
   - Generate 16 sequences per backbone at temp=0.3 (explore diversity)
   - Filter by ProteinMPNN score (lower = better, typically < 1.5)
```

**Structure Prediction Validation:**

```
1. ESMFold (fast screening):
   - Filter: pLDDT > 80, pTM > 0.8, RMSD < 2 A from design model

2. AlphaFold2-multimer (gold standard for complexes):
   - Interface pLDDT > 70, PAE < 10 A across interface
   - Verify designed contacts are maintained

3. Success criteria:
   - Self-consistent: ESMFold matches ProteinMPNN design backbone
   - Complex validated: AF2-multimer predicts correct binding mode
```

### Phase 4: Sequence Optimization

Optimize designed sequences for expression, stability, and binding properties.

```
1. mcp__uniprot__uniprot_data(method: "analyze_sequence_composition", accession: "UNIPROT_ACC")
   -> Reference composition from natural proteins in the same fold class

2. mcp__uniprot__uniprot_data(method: "get_protein_homologs", accession: "CLOSEST_HOMOLOG", organism: "all", size: 20)
   -> Homolog sequences for evolutionary conservation analysis

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "de novo protein design sequence optimization expression solubility", num_results: 10)
   -> Published optimization strategies
```

**Python code template — Sequence property analysis:**

```bash
python3 << 'PYEOF'
def analyze_designed_sequence(sequence, name="designed_protein"):
    """Sequence analysis for designed proteins: MW, charge, hydrophobicity, flags."""
    aa_mw = {'A':89.09,'R':174.20,'N':132.12,'D':133.10,'C':121.16,'E':147.13,
             'Q':146.15,'G':75.03,'H':155.16,'I':131.17,'L':131.17,'K':146.19,
             'M':149.21,'F':165.19,'P':115.13,'S':105.09,'T':119.12,'W':204.23,
             'Y':181.19,'V':117.15}
    kd = {'A':1.8,'R':-4.5,'N':-3.5,'D':-3.5,'C':2.5,'E':-3.5,'Q':-3.5,
          'G':-0.4,'H':-3.2,'I':4.5,'L':3.8,'K':-3.9,'M':1.9,'F':2.8,
          'P':-1.6,'S':-0.8,'T':-0.7,'W':-0.9,'Y':-1.3,'V':4.2}
    seq = sequence.upper().replace(' ','').replace('\n','')
    length = len(seq)
    mw = sum(aa_mw.get(aa, 0) for aa in seq) - (length - 1) * 18.02
    avg_hydro = sum(kd.get(aa, 0) for aa in seq) / length
    net_charge = seq.count('R') + seq.count('K') + seq.count('H') * 0.1 - seq.count('D') - seq.count('E')
    cys = seq.count('C')

    # Hydrophobic stretch detection
    max_stretch, stretch = 0, 0
    for aa in seq:
        if kd.get(aa, 0) > 1.5: stretch += 1; max_stretch = max(max_stretch, stretch)
        else: stretch = 0

    flags = []
    if seq[0] != 'M': flags.append("No N-terminal Met")
    if cys % 2 != 0: flags.append(f"Odd Cys count ({cys})")
    if max_stretch > 7: flags.append(f"Hydrophobic stretch ({max_stretch} aa)")
    deamid = sum(1 for i in range(len(seq)-1) if seq[i]=='N' and seq[i+1] in 'GST')
    if deamid > 3: flags.append(f"Deamidation motifs ({deamid})")

    print(f"=== {name} ===")
    print(f"Length: {length} aa | MW: {mw/1000:.1f} kDa | Hydro: {avg_hydro:.2f}")
    print(f"Net charge (pH 7.4): {net_charge:+.1f} | Cys: {cys} | Max hydro stretch: {max_stretch}")
    if flags: [print(f"  FLAG: {f}") for f in flags]
    else: print("  No flags raised.")
    return {'length': length, 'mw_kda': mw/1000, 'avg_hydro': avg_hydro, 'net_charge': net_charge}

# Usage: analyze_designed_sequence("MEKLLKAYIDFLKENGKPVT...", "anti-IL6R_v1")
print("Template loaded. Replace with designed sequence.")
PYEOF
```

**Sequence Optimization Targets:**

| Property | Optimal Range | Rationale |
|----------|-------------|-----------|
| **Length** | 40-80 aa (miniprotein), 100-200 aa (scaffold) | Smaller = cheaper, faster folding |
| **Net charge** | -5 to +5 at pH 7.4 | Avoid extreme charge (aggregation) |
| **Avg hydrophobicity** | -1.0 to 0.5 (KD scale) | Balanced for solubility and core packing |
| **Cysteine count** | 0 or even number | Avoid unpaired Cys crosslinks |
| **Max hydrophobic stretch** | < 7 residues | Longer stretches seed aggregation |

### Phase 5: Developability Assessment

Evaluate designed protein therapeutics for manufacturing, stability, and clinical viability.

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "protein therapeutic developability aggregation immunogenicity stability", num_results: 15)
   -> Published developability frameworks for non-antibody biologics

2. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "CLOSEST_NATURAL_HOMOLOG")
   -> PTM patterns and stability features from natural relatives

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "TARGET_NAME", limit: 20)
   -> Approved therapeutics against same target — formulation benchmarks
```

**Python code template — Developability scoring:**

```bash
python3 << 'PYEOF'
def score_developability(sequence, predicted_tm=None, predicted_plddt=None,
                         binding_kd_nm=None, expression_mg_per_l=None):
    """Developability score (0-100). Weights: seq (25%), structure (25%), binding (25%), mfg (25%)."""
    seq = sequence.upper().replace(' ','').replace('\n','')
    length = len(seq)
    kd = {'A':1.8,'R':-4.5,'N':-3.5,'D':-3.5,'C':2.5,'E':-3.5,'Q':-3.5,
          'G':-0.4,'H':-3.2,'I':4.5,'L':3.8,'K':-3.9,'M':1.9,'F':2.8,
          'P':-1.6,'S':-0.8,'T':-0.7,'W':-0.9,'Y':-1.3,'V':4.2}
    cys = seq.count('C')
    scores = {}

    # Sequence properties (25%)
    s = 100
    if length < 30 or length > 250: s -= 30
    elif length < 40 or length > 200: s -= 15
    if cys % 2 != 0: s -= 25
    max_stretch, stretch = 0, 0
    for aa in seq:
        if kd.get(aa, 0) > 1.5: stretch += 1; max_stretch = max(max_stretch, stretch)
        else: stretch = 0
    if max_stretch > 9: s -= 30
    elif max_stretch > 7: s -= 15
    deamid = sum(1 for i in range(len(seq)-1) if seq[i]=='N' and seq[i+1] in 'GST')
    if deamid > 3: s -= 10 * min(deamid - 3, 3)
    scores['sequence'] = max(0, s)

    # Predicted structure (25%)
    s = 50
    if predicted_plddt is not None:
        s = {90: 100, 80: 80, 70: 60, 60: 40}.get(
            max(k for k in [90,80,70,60,0] if predicted_plddt >= k), 20)
    if predicted_tm is not None:
        if predicted_tm > 75: s = min(s + 20, 100)
        elif predicted_tm > 65: s = min(s + 10, 100)
        elif predicted_tm < 50: s = max(s - 30, 0)
    scores['structure'] = s

    # Target binding (25%)
    s = 50
    if binding_kd_nm is not None:
        if binding_kd_nm < 1: s = 100
        elif binding_kd_nm < 10: s = 85
        elif binding_kd_nm < 50: s = 70
        elif binding_kd_nm < 200: s = 55
        elif binding_kd_nm < 1000: s = 35
        else: s = 15
    scores['binding'] = s

    # Manufacturability (25%)
    s = 80 if length <= 80 else 70 if length <= 150 else 55 if length <= 250 else 35
    if cys >= 4: s -= 15
    if expression_mg_per_l is not None:
        if expression_mg_per_l > 100: s = 100
        elif expression_mg_per_l > 50: s = 85
        elif expression_mg_per_l > 10: s = 70
        elif expression_mg_per_l > 1: s = 50
        else: s = 25
    scores['manufacturing'] = max(0, s)

    total = sum(v * 0.25 for v in scores.values())
    print(f"Sequence: {scores['sequence']}/100 | Structure: {scores['structure']}/100")
    print(f"Binding: {scores['binding']}/100 | Manufacturing: {scores['manufacturing']}/100")
    print(f"TOTAL: {total:.0f}/100", end=" — ")
    if total >= 80: print("EXCELLENT: proceed to validation")
    elif total >= 60: print("GOOD: optimize flagged components")
    elif total >= 40: print("MODERATE: significant redesign needed")
    else: print("POOR: consider alternative approach")
    return total, scores

# Usage: score_developability("MEKLL...", predicted_tm=72, predicted_plddt=88, binding_kd_nm=15)
print("Template loaded. Replace with designed sequence and prediction data.")
PYEOF
```

### Phase 6: Competitive Landscape

Assess existing therapeutics and binders targeting the same protein.

```
1. mcp__drugbank__drugbank_info(method: "search_by_target", target: "TARGET_NAME", limit: 20)
   -> All approved and investigational drugs for this target

2. mcp__drugbank__drugbank_info(method: "search_by_name", query: "KNOWN_DRUG_NAME")
   -> Get DrugBank ID for approved competitor

3. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Full drug profile: modality, mechanism, dosing, formulation

4. mcp__chembl__chembl_info(method: "target_search", query: "TARGET_NAME", limit: 10)
   -> ChEMBL target ID for bioactivity mining

5. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBLxxxxx", limit: 50)
   -> All reported binding data — small molecules, peptides, biologics

6. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   -> Mechanism of action for existing drugs

7. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "TARGET_NAME therapeutic protein binder design clinical", start_date: "2022-01-01", num_results: 15)
   -> Recent de novo protein design publications targeting the same protein

OUTPUT: Competitive landscape table with modality, affinity, clinical stage, differentiation opportunities.
```

**Competitive Landscape Template:**

| Competitor | Modality | Kd / IC50 | Stage | Differentiation Opportunity |
|-----------|----------|-----------|-------|---------------------------|
| Drug A | mAb (IgG1) | 0.5 nM | Approved | Novel epitope, smaller size |
| Drug B | Small molecule | 50 nM | Phase 2 | Allosteric PPI interface |
| **De novo design** | Miniprotein | Target < 10 nM | Preclinical | Size, cost, low immunogenicity |

### Phase 7: Validation Strategy

Recommend experimental assays, expression systems, and binding validation.

**Expression System Selection:**

| System | Best For | Yield | Timeline |
|--------|---------|-------|----------|
| **E. coli (cytoplasm)** | Disulfide-free miniproteins < 100 aa | 10-100 mg/L | 1-2 weeks |
| **E. coli (SHuffle)** | Disulfide-containing miniproteins | 5-50 mg/L | 2-3 weeks |
| **Pichia pastoris** | Larger proteins, glycoproteins | 10-500 mg/L | 4-6 weeks |
| **CHO cells** | Complex proteins requiring mammalian PTMs | 0.5-5 g/L (stable) | 3-6 months |
| **Cell-free (PURE)** | Rapid screening of many variants | 0.01-0.1 mg/mL | 1-2 days |

**Binding Assay Recommendations:**

| Assay | Measures | Throughput | Stage |
|-------|---------|-----------|-------|
| **Yeast surface display** | Kd, sorting | High (10^7 variants) | Initial screening |
| **Bio-layer interferometry** | kon, koff, Kd | Medium (96-well) | Hit validation |
| **Surface plasmon resonance** | kon, koff, Kd | Low-Medium | Lead characterization |
| **ITC** | Kd, DH, DS, stoichiometry | Low | Mechanistic understanding |

**Recommended Validation Cascade:**

```
Stage 1 — Computational (1-2 weeks):
  ESMFold for all sequences, AF2-multimer for top 50
  Filter: pLDDT > 80, interface PAE < 10, RMSD < 2 A

Stage 2 — Expression screen (2-3 weeks):
  Gene synthesis for top 20-50, E. coli 96-well expression
  Filter: soluble expression > 1 mg/L, monomer by SEC

Stage 3 — Binding validation (2-4 weeks):
  BLI or SPR for top 10-20 expressible designs
  Filter: Kd < 500 nM, on-rate > 10^4 M-1s-1

Stage 4 — Biophysical characterization (2-4 weeks):
  CD (secondary structure, Tm), DLS, SEC-MALS
  Filter: Tm > 60 C, monodisperse, correct MW

Stage 5 — Lead optimization (4-8 weeks):
  Affinity maturation by yeast display + FACS
  Epitope mapping via HDX-MS
  Target: Kd < 10 nM, Tm > 70 C
```

---

## Design Modalities

### Miniproteins (De Novo Binders)

| Property | Typical Range | Advantages |
|----------|-------------|-----------|
| **Size** | 35-80 aa, 4-9 kDa | Deep tissue penetration, fast clearance, low immunogenicity |
| **Topology** | 3-helix bundle, cystine knot | Highly stable, tunable binding surfaces |
| **Affinity** | 0.1-100 nM (optimized) | Comparable to antibodies |
| **Stability** | Tm 60-95 C | Thermostable, protease resistant |
| **Expression** | E. coli, 10-100 mg/L | Cheap, scalable |
| **Half-life** | Minutes (renal clearance) | Extend with PEG, Fc fusion, albumin binding |

### Designed Repeat Proteins

| Property | Typical Range | Advantages |
|----------|-------------|-----------|
| **Size** | 100-250 aa, 10-30 kDa | Tunable size by adding/removing repeats |
| **Topology** | Stacked helical or beta repeats | Large flat binding surface |
| **Affinity** | 0.01-10 nM | Very high from large interface |
| **Expression** | E. coli, 50-200 mg/L | Outstanding yields |

### De Novo Enzymes

| Property | Typical Range | Considerations |
|----------|-------------|---------------|
| **Size** | 150-400 aa | Must accommodate active site geometry |
| **Efficiency** | kcat/Km: 10^2-10^5 M-1s-1 | 10^3-10^6x below natural enzymes initially |
| **Design approach** | Theozyme-based | Define transition state, place catalytic residues, scaffold |
| **Optimization** | Directed evolution required | 10-100x improvement per round |

### Constrained Peptides

| Property | Typical Range | Advantages |
|----------|-------------|-----------|
| **Size** | 10-40 aa, 1-5 kDa | Smallest modality, oral delivery potential |
| **Cyclization** | Disulfide, head-to-tail, staple | Rigidity improves affinity and protease resistance |
| **Stability** | Improve with D-amino acids, N-methylation | Protease-resistant variants possible |

### Nanobody-Like Scaffolds

| Property | Typical Range | Advantages |
|----------|-------------|-----------|
| **Size** | 80-130 aa, 12-15 kDa | Smaller than Fab, access clefts/cavities |
| **Affinity** | 0.1-100 nM | Comparable to antibody Fv |
| **Expression** | E. coli, 10-100 mg/L | No light chain pairing needed |
| **Multimerization** | Easy genetic fusion | Avidity, bispecific capability |

---

## Developability Score (0-100)

| Component | Weight | Scoring Criteria |
|-----------|--------|-----------------|
| **Sequence properties** | 25% | Length, charge, hydrophobicity, aggregation motifs, PTM liabilities, Cys count |
| **Predicted structure** | 25% | ESMFold/AF2 pLDDT, pTM, RMSD to design model, interface confidence |
| **Target binding** | 25% | Predicted or measured Kd, interface area, hot spot contacts |
| **Manufacturability** | 25% | Expression yield, solubility, thermal stability, protease resistance |

| Total Score | Rating | Recommendation |
|-------------|--------|---------------|
| **80-100** | Excellent | Proceed to experimental validation |
| **60-79** | Good | Optimize flagged components, then validate |
| **40-59** | Moderate | Significant redesign needed |
| **< 40** | Poor | Restart with different approach or target site |

**Common Failure Modes:**

| Failure | Score Impact | Remediation |
|---------|-------------|-------------|
| Low pLDDT (< 70) | Structure -40 | Redesign backbone, increase core packing |
| Aggregation motifs | Sequence -30 | Replace hydrophobic patches with polar residues |
| Poor expression | Mfg -50 | Codon optimization, tag screening, different host |
| Weak binding (> 1 uM) | Binding -65 | Affinity maturation, different hotspot residues |
| Unpaired Cys | Sequence -25 | Remove or add partner Cys for disulfide |

---

## Evidence Grading System

| Tier | Evidence Type | Confidence | Action |
|------|-------------|------------|--------|
| **T1** | Experimental — crystal structure of complex, measured Kd < 100 nM, validated in vivo | Highest | Validated design, proceed to optimization |
| **T2** | Partial experimental — expressed, binding confirmed by BLI/SPR, or high-confidence AF2-multimer | High | Strong candidate, prioritize for characterization |
| **T3** | Computational — ESMFold/AF2 passes filters, good ProteinMPNN score, no experimental data | Moderate | Promising, requires experimental validation |
| **T4** | Conceptual — RFdiffusion backbone generated, sequence designed, not yet structure-validated | Low | Early stage, needs computational and experimental validation |

Always report evidence tier alongside developability score. A T2 design scoring 65 is more credible than a T3 design scoring 85.

---

## Multi-Agent Workflow Examples

**"Design a miniprotein binder against IL-17A for psoriasis"**
1. Protein Therapeutic Design -> Full pipeline: characterize IL-17A (homodimer interface, known epitopes), select binding site, RFdiffusion 50-70 aa binder, ProteinMPNN optimization, developability scoring
2. Antibody Engineering -> Benchmark against secukinumab/ixekizumab: affinity, epitope, clinical efficacy
3. Drug Target Validator -> IL-17A target validation for psoriasis, genetic evidence
4. Protein Interactions -> IL-17A/IL-17RA interaction network, competitive binding analysis

**"Engineer a thermostable enzyme for prodrug activation in tumors"**
1. Protein Therapeutic Design -> De novo enzyme: catalytic requirements (theozyme), scaffold selection, active site design, stability optimization for tumor pH (6.5-6.8)
2. Binder Discovery Specialist -> Identify existing prodrug substrates and pharmacophore requirements
3. Protein Structure Retrieval -> Template structures for catalytic triad/dyad placement

**"Create a bispecific miniprotein targeting PD-L1 and VEGF"**
1. Protein Therapeutic Design -> Design two independent binders, optimize each, design fusion linker, assess bispecific developability
2. Antibody Engineering -> Benchmark against atezolizumab (PD-L1) and bevacizumab (VEGF)
3. Drug Target Validator -> PD-L1 and VEGF co-expression analysis, dual targeting rationale

**"Design a repeat protein to neutralize a bacterial toxin"**
1. Protein Therapeutic Design -> Toxin receptor-binding domain characterization, DARPin-like design, large flat interface, rapid E. coli expression
2. Protein Structure Retrieval -> Toxin crystal structures, receptor-binding boundaries
3. Protein Interactions -> Toxin-receptor interaction residues for competitive design

**"Optimize a designed binder that expresses poorly"**
1. Protein Therapeutic Design -> Sequence analysis (aggregation, charge, hydrophobic patches), surface redesign, codon optimization, expression tag screening (MBP, SUMO, thioredoxin), stability engineering
2. Protein Structure Retrieval -> Compare design model vs ESMFold prediction, identify destabilizing features
3. Antibody Engineering -> Apply developability principles (PTM liabilities, deamidation) to designed protein

## Completeness Checklist

- [ ] Target protein fully characterized (structure, domains, known interfaces, PTMs)
- [ ] Binding site selected and scored with accessibility, order, and hot spot criteria
- [ ] Design modality chosen with rationale (miniprotein, repeat protein, enzyme, peptide, nanobody-like)
- [ ] RFdiffusion parameters specified (contigs, hotspot residues, number of designs)
- [ ] ProteinMPNN sequence design parameters defined (temperature, fixed positions)
- [ ] Sequence properties analyzed (length, charge, hydrophobicity, Cys count, aggregation motifs)
- [ ] Developability score computed (sequence, structure, binding, manufacturing components)
- [ ] Competitive landscape assessed (existing drugs, modalities, differentiation opportunity)
- [ ] Validation strategy recommended (expression system, binding assays, biophysical characterization)
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
