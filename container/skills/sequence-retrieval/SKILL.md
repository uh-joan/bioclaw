---
name: sequence-retrieval
description: Biological sequence retrieval and analysis. DNA sequence, RNA sequence, protein sequence, CDS, genomic sequence, transcript sequence, FASTA, sequence alignment, batch sequence retrieval, sequence comparison, gene to protein. Use when user mentions sequence retrieval, get sequence, DNA sequence, protein sequence, CDS, coding sequence, FASTA, transcript sequence, genomic sequence, batch sequences, sequence comparison, gene sequence, or amino acid sequence.
---

# Sequence Retrieval

> **Code recipes**: See [recipes.md](recipes.md) in this directory for copy-paste executable code templates.

Unified interface for retrieving biological sequences from Ensembl (DNA, RNA, CDS) and UniProt (protein). Handles single-gene lookups, batch retrieval across gene lists, format conversion between FASTA and raw sequence, cross-species ortholog collection, and sequence validation. Routes each request to the appropriate database based on molecule type and use case.

## Report-First Workflow

1. **Create report file immediately**: `[gene_or_panel]_sequence_retrieval_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Phylogenetic analysis of retrieved sequences → use `phylogenetics`
- 3D protein structure retrieval and visualization → use `protein-structure-retrieval`
- Variant effect interpretation on sequences → use `variant-interpretation`
- Antibody sequence engineering and humanization → use `antibody-engineering`
- Protein therapeutic design from sequences → use `protein-therapeutic-design`
- Protein-protein interaction network analysis → use `protein-interactions`

## Cross-Reference: Other Skills

- **Phylogenetic analysis of retrieved sequences** -> use phylogenetics skill
- **3D structure for retrieved protein sequences** -> use protein-structure-retrieval skill
- **Variant effects on retrieved sequences** -> use variant-interpretation skill
- **Antibody sequence engineering** -> use antibody-engineering skill
- **Protein therapeutic design from sequences** -> use protein-therapeutic-design skill

---

## Available MCP Tools

### `mcp__ensembl__ensembl_data` (DNA, RNA, and CDS Sequences)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by stable ID or symbol | `gene_id`, `species`, `expand` |
| `get_transcripts` | All transcripts for a gene with exon structure | `gene_id`, `canonical_only` |
| `search_genes` | Search genes by name, description, or identifier | `query`, `species`, `limit`, `biotype` |
| `get_sequence` | Fetch genomic DNA sequence by coordinates or feature ID | `region`, `species`, `format` |
| `get_cds_sequence` | Get coding sequence (CDS) for a transcript | `transcript_id` |
| `translate_sequence` | Convert DNA sequence to protein (local codon table) | `sequence` |
| `get_homologs` | Find orthologous genes across species | `gene_id`, `target_species` |
| `get_xrefs` | External database cross-references | `gene_id`, `external_db` |
| `batch_gene_lookup` | Look up multiple genes simultaneously (max 200) | `gene_ids` |
| `batch_sequence_fetch` | Fetch sequences for multiple regions (max 50) | `regions`, `format` |

### `mcp__uniprot__uniprot_data` (Protein Sequences and Annotations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_proteins` | Search UniProt by name, keyword, or organism | `query`, `organism`, `size` |
| `get_protein_info` | Full protein details by accession | `accession`, `format` |
| `search_by_gene` | Find proteins by gene name/symbol | `gene`, `organism`, `size` |
| `get_protein_sequence` | FASTA or JSON sequence retrieval | `accession`, `format` |
| `get_protein_features` | Domains, active sites, binding sites, PTMs | `accession` |
| `compare_proteins` | Side-by-side comparison of 2-10 proteins | `accessions` |
| `get_protein_homologs` | Find homologous proteins across species | `accession` |
| `get_protein_orthologs` | Identify orthologs by gene name | `gene`, `organism` |
| `batch_protein_lookup` | Process up to 100 accessions | `accessions` |
| `get_external_references` | Links to PDB, EMBL, RefSeq, Ensembl, GO | `accession` |
| `analyze_sequence_composition` | Amino acid composition, hydrophobicity | `accession` |

### `mcp__pubmed__pubmed_articles` (Supporting Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search with date/journal filters | `term`, `journal`, `start_date`, `end_date`, `num_results` |

### `mcp__opentargets__opentargets_info` (Target Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |

---

## Retrieval Decision Tree

Use this decision tree to determine which MCP server and method to call based on the user's request.

```
User request: "Get me the sequence for [GENE/PROTEIN]"
                          |
                   What type of sequence?
                   /        |          \            \
                  /         |           \            \
          Genomic DNA    mRNA/CDS     Protein    Multiple species
              |              |           |              |
              v              v           v              v
         Ensembl          Ensembl    UniProt         Ensembl
       get_sequence    get_cds_     get_protein_   get_homologs
       (with region    sequence     sequence       + batch_
        or gene ID)   (transcript   (preferred)    sequence_fetch
                        ID)            |
                                       |
                                 If no UniProt
                                 accession:
                                       |
                                       v
                                    Ensembl
                                 translate_
                                 sequence

Additional routing:
- "Protein with domain annotations" -> UniProt get_protein_features
- "Compare protein sequences"       -> UniProt compare_proteins
- "Batch of genes"                   -> Ensembl batch_gene_lookup + batch_sequence_fetch
- "Batch of proteins"                -> UniProt batch_protein_lookup
- "Map gene to protein ID"          -> Ensembl get_xrefs or UniProt get_external_references
```

---

## Retrieval Workflows

### Workflow 1: Single Gene -> All Sequences (DNA, CDS, Protein)

Starting from a gene symbol, retrieve the full set of sequences: genomic DNA, coding sequence, and protein.

```
Step 1: Resolve gene symbol to Ensembl ID
mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "TP53", expand: true)
-> Returns: ENSG00000141510, canonical transcript ENST00000269305, genomic coordinates

Step 2: Get genomic DNA sequence
mcp__ensembl__ensembl_data(method: "get_sequence", region: "ENSG00000141510", species: "homo_sapiens", format: "fasta")
-> Returns: Full genomic sequence including introns and UTRs

Step 3: Get coding sequence (CDS)
mcp__ensembl__ensembl_data(method: "get_cds_sequence", transcript_id: "ENST00000269305")
-> Returns: Spliced coding sequence (exons only, start to stop codon)

Step 4: Get protein sequence from UniProt (preferred source)
mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "TP53", organism: "homo_sapiens")
-> Returns: UniProt accession P04637

mcp__uniprot__uniprot_data(method: "get_protein_sequence", accession: "P04637", format: "fasta")
-> Returns: Canonical protein sequence in FASTA format

Step 5 (alternative): Translate CDS via Ensembl if no UniProt entry
mcp__ensembl__ensembl_data(method: "translate_sequence", sequence: "<CDS_FROM_STEP_3>")
-> Returns: Translated amino acid sequence
```

### Workflow 2: Protein Sequence with Annotations

Retrieve a protein sequence together with functional annotations, domains, and composition analysis.

```
Step 1: Find the protein
mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "EGFR", organism: "homo_sapiens")
-> Returns: P00533 (EGFR_HUMAN)

Step 2: Get the full sequence
mcp__uniprot__uniprot_data(method: "get_protein_sequence", accession: "P00533", format: "fasta")
-> Returns: 1210 amino acid sequence in FASTA format

Step 3: Get functional features overlaid on sequence
mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "P00533")
-> Returns: Signal peptide (1-24), Furin-like domain (165-480), Tyrosine kinase domain (712-979),
   active sites, binding sites, PTM sites, disulfide bonds

Step 4: Analyze sequence composition
mcp__uniprot__uniprot_data(method: "analyze_sequence_composition", accession: "P00533")
-> Returns: Amino acid frequencies, molecular weight, isoelectric point, hydrophobicity profile

Step 5: Get cross-references for structural context
mcp__uniprot__uniprot_data(method: "get_external_references", accession: "P00533")
-> Returns: PDB entries, Ensembl gene ID, RefSeq IDs, Pfam domains
```

### Workflow 3: Batch Retrieval

Retrieve sequences for a list of genes or proteins in a single operation.

**Batch gene lookup and DNA/CDS retrieval (Ensembl):**

```
Step 1: Look up multiple genes at once
mcp__ensembl__ensembl_data(method: "batch_gene_lookup", gene_ids: ["BRCA1", "BRCA2", "TP53", "EGFR", "KRAS"])
-> Returns: Ensembl IDs, coordinates, canonical transcripts for all 5 genes

Step 2: Batch fetch genomic sequences
mcp__ensembl__ensembl_data(method: "batch_sequence_fetch", regions: ["ENSG00000012048", "ENSG00000139618", "ENSG00000141510", "ENSG00000146648", "ENSG00000133703"], format: "fasta")
-> Returns: FASTA sequences for all 5 genes
```

**Batch protein retrieval (UniProt):**

```
Step 1: Look up multiple proteins
mcp__uniprot__uniprot_data(method: "batch_protein_lookup", accessions: ["P38398", "P51587", "P04637", "P00533", "P01116"])
-> Returns: Full protein info for BRCA1, BRCA2, TP53, EGFR, KRAS

Step 2: Compare subset of proteins
mcp__uniprot__uniprot_data(method: "compare_proteins", accessions: ["P38398", "P51587"])
-> Returns: Side-by-side comparison of BRCA1 and BRCA2 (length, domains, features)
```

### Workflow 4: Cross-Species Ortholog Sequences

Retrieve orthologous sequences across species for comparative analysis.

```
Step 1: Find orthologs via Ensembl
mcp__ensembl__ensembl_data(method: "get_homologs", gene_id: "ENSG00000141510", target_species: "mus_musculus")
-> Returns: Mouse ortholog ENSMUSG00000059552 (Trp53)

Step 2: Expand to multiple species
mcp__ensembl__ensembl_data(method: "get_homologs", gene_id: "ENSG00000141510")
-> Returns: All orthologs (mouse, rat, zebrafish, chicken, etc.)

Step 3: Batch fetch ortholog sequences
mcp__ensembl__ensembl_data(method: "batch_sequence_fetch", regions: ["ENSG00000141510", "ENSMUSG00000059552", "ENSRNOG00000010756", "ENSDARG00000035559"], format: "fasta")
-> Returns: FASTA sequences for TP53 orthologs across human, mouse, rat, zebrafish

Step 4: Get protein orthologs via UniProt
mcp__uniprot__uniprot_data(method: "get_protein_orthologs", gene: "TP53", organism: "homo_sapiens")
-> Returns: Orthologous protein accessions across species

Step 5: Compare ortholog protein sequences
mcp__uniprot__uniprot_data(method: "compare_proteins", accessions: ["P04637", "P02340", "P10361"])
-> Returns: Comparison of human, mouse, and chicken TP53 proteins
```

### Workflow 5: Region-Based Retrieval

Retrieve sequences for specific genomic regions by coordinates.

```
Step 1: Fetch sequence for a defined region
mcp__ensembl__ensembl_data(method: "get_sequence", region: "17:7661779-7687550", species: "homo_sapiens", format: "fasta")
-> Returns: Genomic DNA for the TP53 locus on chromosome 17

Step 2: Fetch a smaller region (e.g., single exon)
mcp__ensembl__ensembl_data(method: "get_sequence", region: "17:7676594-7676521", species: "homo_sapiens", format: "fasta")
-> Returns: Sequence of a single exon

Step 3: Fetch flanking regulatory region
mcp__ensembl__ensembl_data(method: "get_sequence", region: "17:7661000-7661779", species: "homo_sapiens", format: "fasta")
-> Returns: Upstream promoter/regulatory region

Step 4: Batch fetch multiple regions
mcp__ensembl__ensembl_data(method: "batch_sequence_fetch", regions: ["17:7661779-7687550", "13:32315086-32400266", "7:140424943-140624564"], format: "fasta")
-> Returns: Genomic sequences for TP53, BRCA2, and BRAF loci
```

### Workflow 6: Sequence Comparison

Compare sequences at the protein level using UniProt, or perform pairwise alignment with Python.

```
Step 1: UniProt side-by-side comparison
mcp__uniprot__uniprot_data(method: "compare_proteins", accessions: ["P04637", "Q00987"])
-> Returns: Comparison of TP53 and MDM2 — length, domains, features, organism

Step 2: Composition comparison
mcp__uniprot__uniprot_data(method: "analyze_sequence_composition", accession: "P04637")
mcp__uniprot__uniprot_data(method: "analyze_sequence_composition", accession: "Q00987")
-> Compare amino acid frequencies, hydrophobicity, molecular weight

Step 3: Retrieve sequences for local alignment
mcp__uniprot__uniprot_data(method: "get_protein_sequence", accession: "P04637", format: "fasta")
mcp__uniprot__uniprot_data(method: "get_protein_sequence", accession: "Q00987", format: "fasta")
-> Use Python pairwise alignment (see code template below)
```

**Python pairwise alignment template:**

```python
from Bio import SeqIO, pairwise2
from Bio.pairwise2 import format_alignment
from io import StringIO

# Parse FASTA sequences (retrieved from MCP calls above)
seq1_fasta = """>sp|P04637|P53_HUMAN Cellular tumor antigen p53
MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPS..."""
seq2_fasta = """>sp|Q00987|MDM2_HUMAN E3 ubiquitin-protein ligase Mdm2
MCNTNMSVPTDGAVTTSQIPASEQETLVRPKPLLLKL..."""

seq1 = str(list(SeqIO.parse(StringIO(seq1_fasta), "fasta"))[0].seq)
seq2 = str(list(SeqIO.parse(StringIO(seq2_fasta), "fasta"))[0].seq)

# Global alignment with BLOSUM62
alignments = pairwise2.align.globalxx(seq1, seq2, one_alignment_only=True)
print(format_alignment(*alignments[0]))

# Calculate identity
aligned_1, aligned_2 = alignments[0].seqA, alignments[0].seqB
matches = sum(a == b for a, b in zip(aligned_1, aligned_2) if a != "-")
identity = matches / max(len(seq1), len(seq2)) * 100
print(f"Sequence identity: {identity:.1f}%")
```

---

## Sequence Validation

Python code template for validating retrieved sequences and computing basic statistics.

```python
import re
from collections import Counter

def validate_fasta(fasta_text: str) -> dict:
    """Parse and validate a FASTA string. Returns sequence records with stats."""
    records = []
    current_header = None
    current_seq = []

    for line in fasta_text.strip().split("\n"):
        line = line.strip()
        if line.startswith(">"):
            if current_header is not None:
                seq = "".join(current_seq)
                records.append({"header": current_header, "sequence": seq})
            current_header = line[1:]
            current_seq = []
        elif line:
            current_seq.append(line.upper())

    if current_header is not None:
        seq = "".join(current_seq)
        records.append({"header": current_header, "sequence": seq})

    validated = []
    for rec in records:
        seq = rec["sequence"]
        is_protein = bool(re.search(r"[EFILPQZ]", seq)) and not re.search(r"[BJOUXZ]", seq)
        is_dna = bool(re.fullmatch(r"[ACGTNRYSWKMBDHV]+", seq))
        is_rna = bool(re.fullmatch(r"[ACGUNRYSWKMBDHV]+", seq)) and "U" in seq

        if is_rna:
            mol_type = "RNA"
            valid_chars = set("ACGUNRYSWKMBDHV")
        elif is_dna:
            mol_type = "DNA"
            valid_chars = set("ACGTNRYSWKMBDHV")
        else:
            mol_type = "protein"
            valid_chars = set("ACDEFGHIKLMNPQRSTVWY*X")

        invalid = set(seq) - valid_chars
        composition = dict(Counter(seq))

        validated.append({
            "header": rec["header"],
            "length": len(seq),
            "molecule_type": mol_type,
            "valid": len(invalid) == 0,
            "invalid_characters": sorted(invalid) if invalid else [],
            "composition": composition,
            "gc_content": (seq.count("G") + seq.count("C")) / len(seq) * 100 if mol_type in ("DNA", "RNA") and len(seq) > 0 else None,
            "has_stop_codon": seq.endswith("*") if mol_type == "protein" else None,
            "starts_with_met": seq.startswith("M") if mol_type == "protein" else None,
            "starts_with_atg": seq.startswith("ATG") if mol_type == "DNA" else None,
        })

    return validated


def sequence_stats(seq: str) -> dict:
    """Compute summary statistics for a raw sequence string."""
    seq = seq.upper().replace(" ", "").replace("\n", "")
    comp = Counter(seq)
    if re.fullmatch(r"[ACGT]+", seq):
        mol_type = "DNA"
    elif re.fullmatch(r"[ACGU]+", seq):
        mol_type = "RNA"
    else:
        mol_type = "protein"

    stats = {"length": len(seq), "molecule_type": mol_type, "composition": dict(comp)}
    if mol_type in ("DNA", "RNA"):
        stats["gc_content"] = (comp.get("G", 0) + comp.get("C", 0)) / len(seq) * 100
    else:
        stats["hydrophobic_fraction"] = sum(comp.get(aa, 0) for aa in "AILMFWVP") / len(seq) * 100
    return stats
```

---

## Format Conversion

### FASTA to Raw Sequence

```python
def fasta_to_raw(fasta_text: str) -> str:
    """Extract raw sequence from FASTA, stripping headers and whitespace."""
    lines = fasta_text.strip().split("\n")
    seq_lines = [line.strip() for line in lines if not line.startswith(">")]
    return "".join(seq_lines)


def raw_to_fasta(sequence: str, header: str = "sequence", line_width: int = 80) -> str:
    """Wrap a raw sequence string into FASTA format."""
    wrapped = "\n".join(sequence[i:i+line_width] for i in range(0, len(sequence), line_width))
    return f">{header}\n{wrapped}"
```

### DNA to Protein Translation

```python
# Standard genetic code (NCBI translation table 1)
CODON_TABLE = {
    "TTT":"F","TTC":"F","TTA":"L","TTG":"L","CTT":"L","CTC":"L","CTA":"L","CTG":"L",
    "ATT":"I","ATC":"I","ATA":"I","ATG":"M","GTT":"V","GTC":"V","GTA":"V","GTG":"V",
    "TCT":"S","TCC":"S","TCA":"S","TCG":"S","CCT":"P","CCC":"P","CCA":"P","CCG":"P",
    "ACT":"T","ACC":"T","ACA":"T","ACG":"T","GCT":"A","GCC":"A","GCA":"A","GCG":"A",
    "TAT":"Y","TAC":"Y","TAA":"*","TAG":"*","CAT":"H","CAC":"H","CAA":"Q","CAG":"Q",
    "AAT":"N","AAC":"N","AAA":"K","AAG":"K","GAT":"D","GAC":"D","GAA":"E","GAG":"E",
    "TGT":"C","TGC":"C","TGA":"*","TGG":"W","CGT":"R","CGC":"R","CGA":"R","CGG":"R",
    "AGT":"S","AGC":"S","AGA":"R","AGG":"R","GGT":"G","GGC":"G","GGA":"G","GGG":"G",
}


def translate_dna(dna_seq: str, frame: int = 0) -> str:
    """Translate a DNA sequence to protein in the given reading frame (0, 1, or 2)."""
    dna_seq = dna_seq.upper().replace(" ", "").replace("\n", "")
    protein = []
    for i in range(frame, len(dna_seq) - 2, 3):
        codon = dna_seq[i:i+3]
        aa = CODON_TABLE.get(codon, "X")
        protein.append(aa)
    return "".join(protein)


def three_frame_translation(dna_seq: str) -> dict:
    """Translate in all three forward reading frames."""
    return {
        f"frame_{f}": translate_dna(dna_seq, frame=f)
        for f in range(3)
    }
```

### Reverse Complement, RNA/DNA Conversion

```python
COMPLEMENT = {"A":"T","T":"A","G":"C","C":"G","R":"Y","Y":"R","S":"S","W":"W",
              "K":"M","M":"K","B":"V","V":"B","D":"H","H":"D","N":"N"}

def reverse_complement(dna_seq: str) -> str:
    """Return the reverse complement of a DNA sequence."""
    seq = dna_seq.upper().replace(" ", "").replace("\n", "")
    return "".join(COMPLEMENT.get(b, "N") for b in reversed(seq))

def dna_to_rna(dna_seq: str) -> str:
    return dna_seq.upper().replace("T", "U")

def rna_to_dna(rna_seq: str) -> str:
    return rna_seq.upper().replace("U", "T")
```

---

## Cross-Database ID Resolution

Mapping between gene symbols, Ensembl IDs, and UniProt accessions is critical for sequence retrieval across databases.

### Gene Symbol -> Ensembl ID -> UniProt Accession

```
Step 1: Resolve gene symbol to Ensembl ID
mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "BRCA1")
-> Returns: ENSG00000012048

Step 2: Get UniProt cross-reference from Ensembl
mcp__ensembl__ensembl_data(method: "get_xrefs", gene_id: "ENSG00000012048", external_db: "Uniprot/SWISSPROT")
-> Returns: P38398 (BRCA1_HUMAN)

Step 3: Verify via UniProt
mcp__uniprot__uniprot_data(method: "get_protein_info", accession: "P38398")
-> Returns: Full protein record confirming gene name BRCA1
```

### UniProt Accession -> Ensembl ID

```
Step 1: Get external references from UniProt
mcp__uniprot__uniprot_data(method: "get_external_references", accession: "P04637")
-> Returns: Ensembl gene ENSG00000141510, Ensembl transcript ENST00000269305, RefSeq NM_000546

Step 2: Confirm in Ensembl
mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "ENSG00000141510", expand: true)
-> Returns: TP53 gene details with transcripts
```

### Ensembl ID -> UniProt Accession (Batch)

```
Step 1: Batch lookup Ensembl genes
mcp__ensembl__ensembl_data(method: "batch_gene_lookup", gene_ids: ["ENSG00000012048", "ENSG00000139618", "ENSG00000141510"])
-> Returns: BRCA1, BRCA2, TP53 gene info

Step 2: Get cross-references for each
mcp__ensembl__ensembl_data(method: "get_xrefs", gene_id: "ENSG00000012048", external_db: "Uniprot/SWISSPROT")
mcp__ensembl__ensembl_data(method: "get_xrefs", gene_id: "ENSG00000139618", external_db: "Uniprot/SWISSPROT")
mcp__ensembl__ensembl_data(method: "get_xrefs", gene_id: "ENSG00000141510", external_db: "Uniprot/SWISSPROT")
-> Returns: P38398, P51587, P04637
```

### Gene Name -> All Database IDs (Complete Resolution)

```
Step 1: Search by gene name in both databases
mcp__ensembl__ensembl_data(method: "search_genes", query: "KRAS", species: "homo_sapiens", limit: 5)
mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "KRAS", organism: "homo_sapiens")

Step 2: Cross-validate IDs
mcp__ensembl__ensembl_data(method: "get_xrefs", gene_id: "ENSG00000133703")
-> Ensembl ID: ENSG00000133703
-> UniProt:    P01116
-> RefSeq:     NM_004985
-> HGNC:       6407

Step 3: Confirm protein identity
mcp__uniprot__uniprot_data(method: "get_protein_info", accession: "P01116")
-> GTPase KRas, 189 amino acids, reviewed (Swiss-Prot)
```

## Evidence Grading

| Grade | Source | Confidence |
|-------|--------|-----------|
| **E1** | UniProt reviewed (Swiss-Prot) protein sequence | Highest -- manually curated, experimentally validated |
| **E2** | Ensembl canonical transcript CDS / UniProt unreviewed (TrEMBL) | High -- computationally derived from reference genome |
| **E3** | Ensembl non-canonical transcript or alternative assembly | Moderate -- valid but may represent minor isoforms |
| **E4** | Ensembl translate_sequence (local translation) | Caution -- no database validation, verify reading frame |
| **E5** | Cross-species ortholog (inferred from homology) | Context-dependent -- suitable for comparative analysis only |

Always prefer E1 (UniProt reviewed) for protein sequences and E2 (Ensembl canonical) for DNA/CDS. Flag evidence grade when presenting results.

## Multi-Agent Workflow Examples

**"Get the DNA and protein sequence for BRCA2"**
1. Sequence Retrieval -> Ensembl lookup for genomic DNA and CDS, UniProt for protein sequence with annotations
2. Variant Interpretation -> Map known pathogenic variants onto the retrieved sequences
3. Protein Structure Retrieval -> Find 3D structures corresponding to the protein sequence

**"Retrieve TP53 orthologs across mammals for phylogenetic analysis"**
1. Sequence Retrieval -> Ensembl get_homologs for all mammalian orthologs, batch_sequence_fetch for sequences
2. Phylogenetics -> Build phylogenetic tree from the retrieved ortholog sequences
3. Protein Structure Retrieval -> Compare structural conservation across species

**"Get protein sequences for a panel of 50 cancer genes"**
1. Sequence Retrieval -> Ensembl batch_gene_lookup to resolve all gene symbols, UniProt batch_protein_lookup for protein sequences
2. Protein Interactions -> Network analysis of the retrieved gene panel
3. Gene Enrichment -> Pathway and ontology enrichment of the panel

**"Compare the coding sequences of human and mouse EGFR"**
1. Sequence Retrieval -> Ensembl get_homologs to find mouse ortholog, get_cds_sequence for both species, UniProt compare_proteins for protein-level comparison
2. Phylogenetics -> Estimate divergence and selection pressure (dN/dS) on the coding sequences
3. Variant Interpretation -> Identify functionally constrained regions from cross-species alignment

**"Extract the kinase domain sequence from ABL1 for structural modeling"**
1. Sequence Retrieval -> UniProt get_protein_features to locate the kinase domain boundaries, get_protein_sequence for the full sequence, extract domain subsequence
2. Protein Structure Retrieval -> Find experimental structures covering the kinase domain
3. Antibody Engineering -> If designing binders against the kinase domain, use domain boundaries for epitope selection

## Completeness Checklist

- [ ] Gene symbol or identifier resolved to Ensembl stable ID
- [ ] Correct sequence type retrieved (genomic DNA, CDS, mRNA, or protein) per request
- [ ] UniProt reviewed (Swiss-Prot) protein sequence used when available (E1 evidence)
- [ ] Cross-database ID mapping validated (Ensembl <-> UniProt <-> RefSeq)
- [ ] Sequence validated (correct molecule type, no invalid characters, expected length)
- [ ] FASTA format provided with informative headers
- [ ] Batch retrieval used for multi-gene panels (max 200 genes or 100 proteins)
- [ ] Evidence grade noted for each retrieved sequence (E1-E5)
- [ ] Ortholog sequences collected if cross-species comparison requested
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
