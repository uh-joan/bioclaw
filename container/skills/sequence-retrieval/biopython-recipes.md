# Biopython & gget Recipes

Executable code templates for sequence analysis using Biopython and gget.

---

## Recipe 1: Read FASTA File and Calculate Sequence Statistics

Parse a FASTA file and compute length, GC content, and base composition.

```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction

fasta_file = "sequences.fasta"
for record in SeqIO.parse(fasta_file, "fasta"):
    seq = record.seq
    gc = gc_fraction(seq) * 100  # returns float 0-1, convert to percent
    print(f"ID: {record.id}")
    print(f"  Length: {len(seq)} bp")
    print(f"  GC content: {gc:.1f}%")
    print(f"  A:{seq.count('A')} T:{seq.count('T')} G:{seq.count('G')} C:{seq.count('C')}")
    print(f"  Description: {record.description}")
```

---

## Recipe 2: Search NCBI Entrez with Rate Limiting

Query PubMed, GenBank, or Protein databases via Entrez with proper rate limiting.

```python
from Bio import Entrez
import time

Entrez.email = "your.email@example.com"  # required for NCBI compliance
# Entrez.api_key = "your_key"  # optional: 10 req/sec vs 3 req/sec

def search_ncbi(db, query, max_results=10):
    """Search an NCBI database and return record IDs."""
    handle = Entrez.esearch(db=db, term=query, retmax=max_results)
    results = Entrez.read(handle)
    handle.close()
    time.sleep(0.34)  # respect 3 req/sec rate limit
    return results["IdList"]

# Search PubMed, GenBank, and Protein databases
pmids = search_ncbi("pubmed", "BRCA1 breast cancer")
nucl_ids = search_ncbi("nucleotide", "TP53[Gene] AND Homo sapiens[Orgn]")
prot_ids = search_ncbi("protein", "EGFR[Gene] AND human[Orgn] AND refseq[filter]")
print(f"PubMed: {pmids}\nNucleotide: {nucl_ids}\nProtein: {prot_ids}")
```

---

## Recipe 3: Fetch GenBank Record by Accession and Extract Features

Download a GenBank record and iterate over its annotated features.

```python
from Bio import Entrez, SeqIO

Entrez.email = "your.email@example.com"

accession = "NM_007294"  # BRCA1 mRNA
handle = Entrez.efetch(db="nucleotide", id=accession, rettype="gb", retmode="text")
record = SeqIO.read(handle, "genbank")
handle.close()

print(f"ID: {record.id} | {record.description}")
print(f"Length: {len(record.seq)} bp | Organism: {record.annotations.get('organism')}")

# Extract gene, CDS, and exon features with their qualifiers
for feature in record.features:
    if feature.type in ("gene", "CDS", "exon"):
        gene = feature.qualifiers.get("gene", ["N/A"])[0]
        product = feature.qualifiers.get("product", ["N/A"])[0]
        print(f"  {feature.type}: {gene} | {product} | {feature.location}")
```

---

## Recipe 4: Run NCBI BLAST and Parse Top Hits

Submit a sequence to NCBI BLAST and parse alignment results.

```python
from Bio.Blast import NCBIWWW, NCBIXML

query_seq = "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGP"

# Submit BLAST (blocks until results ready, may take minutes)
result_handle = NCBIWWW.qblast(
    program="blastp",      # blastp for protein, blastn for DNA
    database="swissprot",
    sequence=query_seq,
    hitlist_size=10
)
blast_record = NCBIXML.read(result_handle)
result_handle.close()

for alignment in blast_record.alignments:
    hsp = alignment.hsps[0]  # best high-scoring pair
    identity_pct = (hsp.identities / hsp.align_length) * 100
    print(f"{alignment.title[:80]}")
    print(f"  Score: {hsp.score}  E-value: {hsp.expect:.2e}")
    print(f"  Identity: {hsp.identities}/{hsp.align_length} ({identity_pct:.1f}%)")
```

---

## Recipe 5: Parse PDB Structure File and Calculate Distances

Load a PDB structure, iterate chains/residues, and measure atomic distances.

```python
from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)  # QUIET suppresses warnings
structure = parser.get_structure("protein", "structure.pdb")
model = structure[0]  # first model (NMR may have multiple)

# Hierarchy: Structure -> Model -> Chain -> Residue -> Atom
for chain in model:
    print(f"Chain {chain.id}: {len(list(chain.get_residues()))} residues")
    for residue in chain:
        if residue.id[0] != " ":  # skip water/heteroatoms
            continue
        if "CA" in residue:
            ca = residue["CA"].get_vector()
            print(f"  {residue.get_resname()} {residue.id[1]}: CA at ({ca[0]:.2f}, {ca[1]:.2f}, {ca[2]:.2f})")

# Measure CA-CA distance between two residues
chain_a = model["A"]
res1_ca = chain_a[50]["CA"].get_vector()
res2_ca = chain_a[100]["CA"].get_vector()
distance = (res1_ca - res2_ca).norm()
print(f"\nCA-CA distance (res 50-100): {distance:.2f} Angstroms")
```

---

## Recipe 6: Multiple Sequence Alignment Parsing and Statistics

Read an MSA file and compute conservation and gap statistics.

```python
from Bio import AlignIO
from collections import Counter

alignment = AlignIO.read("alignment.fasta", "fasta")  # also: clustal, phylip, stockholm
num_seqs = len(alignment)
aln_length = alignment.get_alignment_length()
print(f"Sequences: {num_seqs} | Alignment length: {aln_length} columns")

# Count conserved columns (>90% identity, excluding gaps)
conserved = 0
for col_idx in range(aln_length):
    column = alignment[:, col_idx]
    most_common, freq = Counter(column).most_common(1)[0]
    if freq / num_seqs > 0.9 and most_common != "-":
        conserved += 1
print(f"Conserved columns (>90%): {conserved}/{aln_length} ({conserved/aln_length*100:.1f}%)")

# Per-sequence gap statistics
for record in alignment:
    gaps = record.seq.count("-")
    print(f"  {record.id}: {gaps} gaps ({gaps/aln_length*100:.1f}%)")
```

---

## Recipe 7: Build Phylogenetic Tree from Distance Matrix

Construct a neighbor-joining tree from a distance matrix.

```python
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from Bio import Phylo
import io

names = ["Human", "Chimp", "Gorilla", "Orangutan", "Mouse"]
# Lower-triangular distance matrix (row i has i elements)
matrix = [
    [],
    [0.03],
    [0.05, 0.04],
    [0.10, 0.09, 0.08],
    [0.30, 0.30, 0.30, 0.31],
]

dm = DistanceMatrix(names, matrix)
constructor = DistanceTreeConstructor()
nj_tree = constructor.nj(dm)      # neighbor-joining
upgma_tree = constructor.upgma(dm) # UPGMA for comparison

Phylo.draw_ascii(nj_tree)

# Export to Newick format
output = io.StringIO()
Phylo.write(nj_tree, output, "newick")
print(f"Newick: {output.getvalue()}")
```

---

## Recipe 8: Translate DNA to Protein with Correct Genetic Code Table

Translate DNA using standard or alternative genetic codes.

```python
from Bio.Seq import Seq
from Bio.Data import CodonTable

dna_seq = Seq("ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG")

# Standard translation (NCBI table 1)
print(f"Standard:  {dna_seq.translate()}")
print(f"To stop:   {dna_seq.translate(to_stop=True)}")
# Vertebrate mitochondrial code (table 2)
print(f"Mito code: {dna_seq.translate(table=2)}")

# List available genetic code tables
for tid in sorted(CodonTable.generic_by_id.keys()):
    print(f"  Table {tid}: {CodonTable.generic_by_id[tid].names[0]}")

# Validate CDS: checks start codon, stop codon, and length multiple of 3
cds_seq = Seq("ATGGCCATTGTAATGGGCCGCTGA")
print(f"Validated CDS: {cds_seq.translate(cds=True)}")
```

---

## Recipe 9: Restriction Enzyme Site Analysis

Find restriction enzyme cut sites in a DNA sequence.

```python
from Bio.Seq import Seq
from Bio.Restriction import EcoRI, BamHI, HindIII, RestrictionBatch, Analysis

dna_seq = Seq(
    "ATGCGAATTCATGCGGATCCATGCAAGCTTATGCGAATTCATGC"
    "GGATCCATGCAAGCTTATGCGAATTCATGCGGATCCATGCAAGCTT"
)

# Individual enzyme searches
print(f"EcoRI:   {EcoRI.search(dna_seq)}")
print(f"BamHI:   {BamHI.search(dna_seq)}")
print(f"HindIII: {HindIII.search(dna_seq)}")

# Batch analysis with multiple enzymes
batch = RestrictionBatch([EcoRI, BamHI, HindIII])
analysis = Analysis(batch, dna_seq)
for enzyme, positions in analysis.full().items():
    status = f"cuts at {positions} ({len(positions)} sites)" if positions else "no sites"
    print(f"  {enzyme}: {status}")

# Find enzymes that cut exactly once (useful for cloning)
print(f"Single-cutters: {analysis.with_N_sites(1)}")
```

---

## Recipe 10: Sequence Format Conversion

Convert between GenBank, FASTA, and FASTQ formats.

```python
from Bio import SeqIO
from io import StringIO

# GenBank to FASTA (file-based)
count = SeqIO.write(SeqIO.parse("input.gb", "genbank"), "output.fasta", "fasta")
print(f"GenBank -> FASTA: {count} records")

# FASTQ to FASTA (strips quality scores)
count = SeqIO.write(SeqIO.parse("reads.fastq", "fastq"), "reads.fasta", "fasta")
print(f"FASTQ -> FASTA: {count} records")

# In-memory conversion: GenBank record to FASTA string
record = SeqIO.read("single_record.gb", "genbank")
buf = StringIO()
SeqIO.write(record, buf, "fasta")
print(buf.getvalue()[:200])

# Filtered conversion: only sequences longer than 500 bp
def long_seqs(infile, fmt, min_len=500):
    for rec in SeqIO.parse(infile, fmt):
        if len(rec.seq) >= min_len:
            yield rec

count = SeqIO.write(long_seqs("input.gb", "genbank"), "long_seqs.fasta", "fasta")
print(f"Long sequences (>500 bp): {count} records")
```

---

## Recipe 11: Extract Coding Sequences (CDS) from GenBank Records

Parse GenBank files and extract all CDS features with translations.

```python
from Bio import SeqIO

cds_records = []
for record in SeqIO.parse("genome.gb", "genbank"):
    print(f"Processing: {record.id} ({len(record.seq)} bp)")
    for feature in record.features:
        if feature.type != "CDS":
            continue
        gene = feature.qualifiers.get("gene", ["unknown"])[0]
        product = feature.qualifiers.get("product", ["unknown"])[0]
        protein_id = feature.qualifiers.get("protein_id", ["N/A"])[0]
        # Extract nucleotide sequence spanning this CDS
        cds_seq = feature.location.extract(record.seq)
        translation = feature.qualifiers.get("translation", [None])[0]
        print(f"  {gene} | {product} | {protein_id} | {len(cds_seq)} bp")
        cds_records.append({
            "gene": gene, "product": product,
            "nucleotide_seq": str(cds_seq), "protein_seq": translation,
        })

print(f"\nTotal CDS extracted: {len(cds_records)}")
```

---

## Recipe 12: Pairwise Sequence Alignment (Global and Local)

Perform pairwise alignments with configurable scoring.

```python
from Bio import Align
from Bio.Seq import Seq

seq1 = Seq("MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPS")
seq2 = Seq("MEEPQSDLSVEPPLSQETFADLWKLLPENNVLSPLQS")

aligner = Align.PairwiseAligner()
aligner.match_score = 2.0
aligner.mismatch_score = -1.0
aligner.open_gap_score = -5.0
aligner.extend_gap_score = -0.5

# Global alignment (Needleman-Wunsch)
aligner.mode = "global"
best_global = aligner.align(seq1, seq2)[0]
print("Global alignment:")
print(best_global)
print(f"Score: {best_global.score}")

# Local alignment (Smith-Waterman)
aligner.mode = "local"
best_local = aligner.align(seq1, seq2)[0]
print("Local alignment:")
print(best_local)

# Percent identity
matches = sum(1 for a, b in zip(str(seq1), str(seq2)) if a == b)
print(f"Identity: {matches/max(len(seq1), len(seq2))*100:.1f}%")
```

---

## Recipe 13: Gene Info Lookup by Symbol (gget)

Retrieve Ensembl gene information using gget.

```python
import gget

# Returns DataFrame with Ensembl ID, description, biotype, coordinates
result = gget.info(["TP53", "BRCA1", "EGFR"], species="human")

for idx, row in result.iterrows():
    print(f"Gene: {idx}")
    print(f"  Description: {row.get('description', 'N/A')}")
    print(f"  Biotype: {row.get('biotype', 'N/A')}")
    print(f"  Chr{row.get('chromosome', '?')}:{row.get('start', '?')}-{row.get('end', '?')}")
    print(f"  Strand: {row.get('strand', 'N/A')}")

# Single gene detailed lookup
tp53 = gget.info("TP53", species="human")
print(tp53.to_string())
```

---

## Recipe 14: Sequence Retrieval by Ensembl ID (gget)

Fetch nucleotide or protein sequences from Ensembl.

```python
import gget

# Nucleotide sequence by transcript ID
nt_seq = gget.seq("ENST00000269305", translate=False)  # TP53 canonical
print("Nucleotide (first 200 chars):")
print(nt_seq[:200])

# Protein sequence (translated)
protein_seq = gget.seq("ENST00000269305", translate=True)
print("\nProtein (first 200 chars):")
print(protein_seq[:200])

# By gene ID (returns all transcripts)
gene_seqs = gget.seq("ENSG00000141510", translate=False)
print("\nAll transcripts (first 300 chars):")
print(gene_seqs[:300])
```

---

## Recipe 15: Quick BLAST Search via gget

Run a BLAST search through gget's simplified interface.

```python
import gget

query = "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGP"

# Auto-detects nucleotide vs protein; returns DataFrame
results = gget.blast(
    query,
    program="blastp",       # blastp for protein, blastn for nucleotide
    database="swissprot",   # nr, swissprot, refseq_protein, etc.
    limit=10
)

if results is not None and not results.empty:
    for idx, row in results.iterrows():
        print(f"Hit: {row.get('description', 'N/A')[:70]}")
        print(f"  E-value: {row.get('e_value', 'N/A')}  Identity: {row.get('percent_identity', 'N/A')}%")
        print(f"  Accession: {row.get('accession', 'N/A')}")
else:
    print("No BLAST hits found.")
```

---

## Recipe 16: Gene Enrichment Analysis via Enrichr (gget)

Perform gene set enrichment analysis using Enrichr.

```python
import gget

gene_list = ["TP53", "BRCA1", "BRCA2", "ATM", "CHEK2",
             "RAD51", "PALB2", "CDK2", "CCND1", "RB1"]

# Databases: GO_Biological_Process_2023, KEGG_2021_Human,
# Reactome_2022, MSigDB_Hallmark_2020, WikiPathways_2023_Human
results = gget.enrichr(gene_list, database="GO_Biological_Process_2023")

if results is not None and not results.empty:
    results_sorted = results.sort_values("adjusted_p_value")
    for idx, row in results_sorted.head(10).iterrows():
        genes = row.get("overlapping_genes", [])
        gene_str = ", ".join(genes) if isinstance(genes, list) else genes
        print(f"{row.get('term', 'N/A')}")
        print(f"  p-adj: {row.get('adjusted_p_value', 0):.2e} | Genes: {gene_str}")
```

---

## Recipe 17: AlphaFold Structure Prediction Lookup (gget)

Retrieve AlphaFold-predicted protein structures.

```python
import gget
from Bio.PDB import PDBParser

# Fetch AlphaFold prediction by UniProt accession (or Ensembl ID)
pdb_path = gget.alphafold("P04637")  # TP53 / p53
print(f"Structure downloaded: {pdb_path}")

# Parse the predicted structure to extract confidence scores
parser = PDBParser(QUIET=True)
structure = parser.get_structure("af_pred", pdb_path)
model = structure[0]
# B-factor field stores pLDDT confidence (0-100)
for chain in model:
    for residue in chain:
        if "CA" in residue:
            plddt = residue["CA"].get_bfactor()
            # >90: high confidence, 70-90: good, <50: low
            conf = "high" if plddt > 90 else "good" if plddt > 70 else "low"
            if residue.id[1] <= 5:  # print first 5 only
                print(f"  {residue.get_resname()} {residue.id[1]}: pLDDT={plddt:.1f} ({conf})")
```

---

## Recipe 18: Gene Expression Data from ARCHS4 (gget)

Query gene expression across tissues and cell types from ARCHS4.

```python
import gget

# Retrieve median expression across human tissues
result = gget.archs4("TP53", which="tissue", species="human")  # or "cell_line"

if result is not None and not result.empty:
    result_sorted = result.sort_values("median_expression", ascending=False)
    print("TP53 expression (top 10 tissues):")
    for idx, row in result_sorted.head(10).iterrows():
        tissue = row.get("tissue", idx)
        expr = row.get("median_expression", 0)
        print(f"  {tissue}: {expr:.2f}")  # values in log2(TPM+1) scale

# Compare multiple genes: find highest-expressing tissue for each
for gene in ["TP53", "MDM2", "CDKN1A"]:
    expr = gget.archs4(gene, which="tissue", species="human")
    if expr is not None and not expr.empty:
        top = expr.sort_values("median_expression", ascending=False).iloc[0]
        print(f"{gene}: highest in {top.get('tissue', 'N/A')} ({top.get('median_expression', 0):.2f})")
```
