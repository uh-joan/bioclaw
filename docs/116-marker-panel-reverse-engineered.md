# Reverse-Engineered: 116-Marker Peptide Pharmacogenomics Panel

*Reconstructed from first principles based on the cohort description: "enzyme pathways, hormone receptors, and recovery mechanisms that actually govern how your body responds to specific peptide compounds."*

The article mentions three categories explicitly. Here's what a purpose-built 116-marker panel for peptide therapy would almost certainly include, mapped to the specific peptides people actually take.

---

## Category 1: Drug-Metabolizing Enzymes (~28 markers)

These determine how fast you clear compounds. "One person's liver clears the compound before it does anything useful. Another metabolizes it slowly and gets stronger effects than expected."

### CYP Enzymes (the core pharmacogenomics genes)

| # | Gene | Key Variants | Peptide Relevance |
|---|------|-------------|-------------------|
| 1-5 | **CYP2D6** | *4, *5 (del), *6, *10, *41, *1xN (dup) | Broadly affects drug metabolism; mentioned explicitly in article. Ultra-rapid vs poor metabolizer status changes effective dose of many compounds |
| 6-8 | **CYP3A4** | *1B, *22 | Major metabolizer — processes ~50% of all drugs. Affects semaglutide, many peptide-drug interactions |
| 9-10 | **CYP3A5** | *3, *6 | Works with CYP3A4. Non-expressors (*3/*3) are ~85% of Caucasians |
| 11-13 | **CYP2C9** | *2, *3, *8 | **Confirmed**: affects semaglutide pharmacokinetics. Poor metabolizers get higher drug levels |
| 14-16 | **CYP2C19** | *2, *3, *17 | Rapid vs poor metabolizer. Affects proton pump inhibitors (gut pH → peptide absorption) |
| 17-18 | **CYP1A2** | *1C, *1F | Caffeine metabolism, but also affects inflammatory pathways relevant to BPC-157 |
| 19-20 | **CYP2B6** | *6, *18 | Secondary metabolizer, relevant for some drug interactions |

### Phase II Enzymes (conjugation/clearance)

| # | Gene | Key Variants | Peptide Relevance |
|---|------|-------------|-------------------|
| 21-22 | **UGT1A1** | *28, *6 | Glucuronidation — how liver packages compounds for excretion |
| 23 | **NAT2** | slow/rapid acetylator | Acetylation speed affects many compound half-lives |
| 24 | **GSTP1** | Ile105Val | Glutathione conjugation — oxidative stress clearance, relevant to recovery peptides |
| 25 | **TPMT** | *2, *3A, *3C | Thiopurine methyltransferase — methylation capacity |
| 26 | **COMT** | Val158Met | Catechol-O-methyltransferase — dopamine/norepinephrine clearance. **Critical for Selank/Semax** (nootropic peptides that modulate catecholamine signaling) |
| 27-28 | **MTHFR** | C677T, A1298C | Methylation cycle — affects homocysteine, B-vitamin metabolism, and downstream methylation of many substrates including neurotransmitters |

---

## Category 2: Peptide-Degrading Enzymes (~12 markers)

These are *specific to peptides* — the enzymes that chop peptides apart before they can work. This is what makes this panel different from a standard PGx panel.

| # | Gene | Key Variants | Peptide Relevance |
|---|------|-------------|-------------------|
| 29-30 | **DPP4** | rs3788979, rs2268891 | **Dipeptidyl peptidase-4** — the primary enzyme that degrades GLP-1. Variants affect how fast you destroy semaglutide/liraglutide. Also cleaves GIP, PYY, NPY, substance P |
| 31-33 | **MME (Neprilysin)** | rs3736187, rs701109, rs9827586 | Degrades enkephalins, substance P, natriuretic peptides, bradykinin, oxytocin. Variants affect peptide half-life across many classes |
| 34-35 | **ACE** | I/D polymorphism, rs4343 | Angiotensin-converting enzyme — processes angiotensin peptides, bradykinin. The I/D polymorphism is one of the most studied in all of pharmacogenomics |
| 36 | **ACE2** | rs2285666 | Processes angiotensin II → Ang(1-7). Variants affect RAS balance |
| 37 | **PRCP** | rs6112983 | Prolylcarboxypeptidase — cleaves angiotensin, alpha-MSH (melanocortin pathway → PT-141) |
| 38 | **PCSK9** | loss-of-function variants | Proprotein convertase — affects protein/peptide processing and lipid metabolism |
| 39-40 | **ANPEP (CD13)** | coding variants | Aminopeptidase N — broad peptide degradation at cell surface, affects bioavailability of many peptides |

---

## Category 3: Peptide Target Receptors (~30 markers)

"A third has a variant in the receptor pathway that means the signal never arrives where it needs to go."

### GLP-1 / Incretin Pathway (semaglutide, tirzepatide, liraglutide)

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 41-42 | **GLP1R** | rs6923761 (Gly168Ser), rs3765467 | **Confirmed**: Ser/Ser homozygotes show dramatically reduced HbA1c response. The Gly168Ser variant reduces receptor binding affinity by ~30% and alters adipose tissue expression. Sex-specific effects on weight loss |
| 43 | **GIPR** | rs10423928 | GIP receptor — tirzepatide is a dual GLP-1/GIP agonist. Variant affects incretin response |
| 44 | **GCG** | rs4664447 | Glucagon/GLP-1 precursor gene — affects endogenous peptide levels |
| 45 | **ARRB1** | rs7940667 | Beta-arrestin — GLP-1R desensitization. Variants may predict who benefits from early GLP-1RA initiation |

### Growth Hormone Axis (CJC-1295, ipamorelin, MK-677, sermorelin, tesamorelin)

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 46-47 | **GHSR** | rs2948694, rs572169 | **Ghrelin receptor** — ipamorelin and MK-677 bind here. Variants associated with obesity, GH response, alcohol use |
| 48 | **GHRHR** | rs4988496 | GHRH receptor — CJC-1295 and sermorelin act here. Variants affect GH pulse amplitude |
| 49 | **GH1** | rs2665802 | Growth hormone gene itself — affects baseline GH production |
| 50 | **GHR** | d3-GHR (exon 3 deletion) | Growth hormone receptor — the d3 deletion creates a more sensitive receptor. Affects how much GH signal gets transduced |
| 51-52 | **IGF1** | rs35767, rs6214 | IGF-1 levels — the downstream effector of GH. Variants affect baseline IGF-1, which determines room for improvement |
| 53 | **IGF1R** | rs2229765 | IGF-1 receptor sensitivity |
| 54 | **IGFBP3** | rs2854744 | IGF binding protein — modulates free vs bound IGF-1 |

### Melanocortin / Sexual Function (PT-141/bremelanotide)

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 55-56 | **MC4R** | rs17782313, rs2229616 (V103I) | Melanocortin-4 receptor — PT-141 target. Also central to appetite/energy homeostasis |
| 57 | **MC1R** | common variants | Melanocortin-1 receptor — tanning peptides (melanotan), also inflammation modulation |
| 58 | **POMC** | rs1042571 | Pro-opiomelanocortin — precursor for MSH, ACTH, beta-endorphin. Upstream of melanocortin signaling |

### Neurotrophin / Nootropic Pathway (Selank, Semax, Dihexa)

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 59 | **BDNF** | Val66Met (rs6265) | Brain-derived neurotrophic factor — Semax upregulates BDNF. Met carriers have impaired BDNF secretion; may respond differently |
| 60 | **NTRK2** | rs1187272 | BDNF receptor (TrkB) — downstream of BDNF signaling |
| 61 | **HTR2A** | rs6311, rs7997012 | Serotonin 2A receptor — Selank modulates serotonin. Variants affect anxiety response |
| 62 | **SLC6A4** | 5-HTTLPR (S/L) | Serotonin transporter — short allele = reduced reuptake = different Selank response |
| 63 | **GAD1** | rs3749034 | Glutamate decarboxylase — GABA synthesis. Selank is anxiolytic partly through GABA modulation |

### Opioid / Pain (BPC-157 pain relief, enkephalin peptides)

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 64 | **OPRM1** | A118G (rs1799971) | Mu-opioid receptor — affects pain sensitivity, endorphin signaling. BPC-157 modulates opioid system |
| 65 | **OPRD1** | rs2234918 | Delta-opioid receptor — enkephalin target |

### Other Hormone Receptors

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 66 | **OXTR** | rs53576 | Oxytocin receptor — oxytocin peptide response, social bonding, stress |
| 67 | **LEPR** | rs1137101 (Q223R) | Leptin receptor — energy balance, interacts with GLP-1 pathway |
| 68 | **ADIPOQ** | rs1501299 | Adiponectin — insulin sensitivity, metabolic health marker |
| 69 | **INSR** | rs1799817 | Insulin receptor — affects insulin sensitivity, relevant to GLP-1/metabolic peptides |
| 70 | **VDR** | rs2228570 (FokI), rs1544410 (BsmI) | Vitamin D receptor — immune modulation, bone health, affects multiple peptide pathways |

---

## Category 4: Recovery & Tissue Repair Mechanisms (~22 markers)

BPC-157 and TB-500 target tissue repair. These genes determine baseline repair capacity.

### Collagen / Connective Tissue

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 71 | **COL1A1** | rs1800012 (Sp1) | Collagen type I — tendon/bone strength. BPC-157 is used for tendon repair; baseline collagen quality matters |
| 72 | **COL5A1** | rs12722 | Collagen type V — Achilles tendon injury risk, ligament laxity |
| 73 | **MMP1** | rs1799750 (1G/2G) | Matrix metalloproteinase 1 — collagen breakdown. 2G allele = more MMP1 = faster tissue turnover |
| 74 | **MMP3** | rs3025058 (5A/6A) | Stromelysin — ECM remodeling. Affects how quickly damaged tissue is cleared for repair |
| 75 | **MMP9** | rs3918242 | Gelatinase B — basement membrane breakdown. BPC-157 modulates MMP expression |

### Inflammatory / Immune Response

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 76 | **IL6** | rs1800795 (-174 G/C) | Interleukin-6 — central inflammatory cytokine. GG genotype = higher IL-6. BPC-157 and TB-500 modulate IL-6 |
| 77 | **TNF** | rs1800629 (-308 G/A) | TNF-alpha — pro-inflammatory. A allele = higher TNF production = different recovery profile |
| 78 | **IL1B** | rs16944 | IL-1 beta — inflammasome pathway. Affects baseline inflammation |
| 79 | **IL10** | rs1800896 | IL-10 — anti-inflammatory cytokine. High producers may need less intervention |
| 80 | **CRP** | rs1205 | C-reactive protein — baseline inflammation marker |
| 81-82 | **HLA** | selected alleles | Immune self/non-self — affects immunogenicity of exogenous peptides (will your immune system attack the peptide?) |

### Nitric Oxide / Vascular (BPC-157's primary mechanism)

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 83 | **NOS3 (eNOS)** | rs1799983 (Glu298Asp), rs2070744 | **Critical for BPC-157** — BPC-157 works primarily through the NO system. Variants affect NO production, vasodilation, angiogenesis |
| 84 | **VEGFA** | rs2010963 | Vascular endothelial growth factor — BPC-157 upregulates VEGF for angiogenesis. Variants affect baseline VEGF levels |

### Growth Factor Signaling

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 85 | **EGF** | rs4444903 | Epidermal growth factor — wound healing, tissue repair |
| 86 | **TGFB1** | rs1800469 | TGF-beta — fibrosis, tissue remodeling, immune regulation |
| 87 | **FGF2** | rs1048201 | Fibroblast growth factor — tissue repair, angiogenesis |

### Oxidative Stress / Detox

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 88 | **SOD2** | rs4880 (Ala16Val) | Superoxide dismutase — mitochondrial antioxidant. Val/Val = less efficient → more oxidative damage → more need for recovery peptides |
| 89 | **CAT** | rs1001179 | Catalase — hydrogen peroxide clearance |
| 90 | **GPX1** | rs1050450 | Glutathione peroxidase — selenium-dependent antioxidant |
| 91 | **NFE2L2 (NRF2)** | rs6721961 | Master antioxidant regulator — controls expression of hundreds of protective genes |

---

## Category 5: Transporters & Bioavailability (~10 markers)

How well peptides get where they need to go.

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 92-93 | **ABCB1 (MDR1/P-gp)** | C3435T (rs1045642), G2677T (rs2032582) | P-glycoprotein efflux pump — actively pumps compounds OUT of cells. TT genotype = reduced efflux = higher intracellular drug levels |
| 94 | **ABCG2** | rs2231142 (Q141K) | Breast cancer resistance protein — another efflux pump |
| 95 | **SLCO1B1** | *5 (rs4149056) | Organic anion transporter — liver uptake of many drugs |
| 96 | **SLC22A1 (OCT1)** | *2, *3, *4, *5 | Organic cation transporter — affects metformin and other charged molecules |
| 97 | **FUT2** | rs601338 (secretor status) | Fucosyltransferase — secretor/non-secretor affects gut microbiome composition → peptide absorption |

---

## Category 6: Metabolic / Endocrine Baseline (~12 markers)

Your hormonal starting point determines what peptides can do for you.

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 98 | **PPARG** | Pro12Ala (rs1801282) | Insulin sensitivity — Ala carriers are more insulin-sensitive, may respond differently to metabolic peptides |
| 99 | **TCF7L2** | rs7903146 | Strongest T2D risk variant — affects incretin (GLP-1) signaling |
| 100 | **FTO** | rs9939609 | Fat mass and obesity — interacts with GLP-1 pathway, affects hunger/satiety response |
| 101 | **ADRB2** | Arg16Gly (rs1042713) | Beta-2 adrenergic receptor — fat mobilization, bronchodilation |
| 102 | **ADRB3** | Trp64Arg (rs4994) | Beta-3 adrenergic receptor — brown fat thermogenesis |
| 103 | **APOE** | ε2/ε3/ε4 | Apolipoprotein E — lipid metabolism, neurodegeneration risk, affects response to neuroprotective peptides (Semax, Selank) |
| 104-105 | **AR** | CAG repeat length | Androgen receptor — longer repeats = lower sensitivity. Affects response to peptides that modulate testosterone/GH axis |
| 106 | **ESR1** | rs2234693 (PvuII) | Estrogen receptor alpha — sex-specific peptide responses |
| 107 | **CYP19A1** | rs4646 | Aromatase — testosterone → estrogen conversion rate |
| 108 | **SHBG** | rs6259 | Sex hormone binding globulin — free vs bound hormone ratio |
| 109 | **CLOCK** | rs1801260 | Circadian rhythm — GH is released during deep sleep; clock gene variants affect sleep architecture → CJC-1295/ipamorelin timing |

---

## Category 7: Aging / Longevity Markers (~7 markers)

The cohort measures biological age. These genes affect aging rate.

| # | Gene | Key Variants | Relevance |
|---|------|-------------|-----------|
| 110 | **TERT** | rs2736100 | Telomerase — telomere maintenance, cellular aging |
| 111 | **FOXO3** | rs2802292 | Forkhead box O3 — one of the most replicated longevity genes |
| 112 | **SIRT1** | rs7895833 | Sirtuin 1 — NAD+ dependent deacetylase, caloric restriction mimicry |
| 113 | **MTOR (FRAP1)** | rs1057079 | Mechanistic target of rapamycin — central growth/aging switch. Rapamycin + peptide stacks are emerging |
| 114 | **AMPK (PRKAA2)** | rs2796498 | AMP-activated protein kinase — energy sensor, metformin target, interacts with GLP-1 pathway |
| 115 | **CETP** | rs5882 | Cholesteryl ester transfer protein — lipid metabolism, longevity association |
| 116 | **KLOTHO** | rs9536314 (KL-VS) | Anti-aging hormone — affects phosphate metabolism, oxidative stress, cognitive aging |

---

## Summary by Peptide → Which Markers Matter

| Peptide | Primary Markers | Category |
|---------|----------------|----------|
| **Semaglutide / Liraglutide** | GLP1R (rs6923761), CYP2C9 (*2/*3), DPP4, TCF7L2, ARRB1, FTO, GIPR | Receptor + metabolism + metabolic |
| **Tirzepatide** | GLP1R, GIPR, CYP2C9, DPP4, TCF7L2, FTO | Dual receptor + metabolism |
| **BPC-157** | NOS3 (eNOS), VEGFA, COL1A1, COL5A1, MMP1/3/9, IL6, TNF, OPRM1 | NO system + repair + inflammation |
| **TB-500 (Thymosin Beta-4)** | IL6, IL10, TNF, MMP9, VEGFA, TGFB1, NOS3 | Inflammation + repair |
| **CJC-1295** | GHRHR, GH1, GHR (d3), IGF1, IGF1R, IGFBP3, CLOCK | GH axis + circadian |
| **Ipamorelin** | GHSR, GH1, GHR (d3), IGF1, IGF1R, IGFBP3, CLOCK | Ghrelin receptor + GH axis |
| **MK-677** | GHSR, same GH axis genes, plus metabolic (FTO, PPARG) | Ghrelin receptor + metabolic |
| **PT-141 (Bremelanotide)** | MC4R, MC1R, POMC, PRCP | Melanocortin pathway |
| **Selank** | HTR2A, SLC6A4, GAD1, COMT, OPRM1, BDNF | Serotonin + GABA + opioid |
| **Semax** | BDNF (Val66Met), NTRK2, COMT, APOE | Neurotrophin + catecholamine |
| **Melanotan II** | MC1R, MC4R, POMC | Melanocortin |
| **GHK-Cu** | COL1A1, MMP1/3, TGFB1, SOD2, NFE2L2 | Collagen + antioxidant |
| **Epithalon** | TERT, FOXO3, SIRT1 | Telomere + longevity |
| **SS-31 (Elamipretide)** | SOD2, CAT, GPX1, MTOR, AMPK | Mitochondrial + oxidative stress |

---

## What Makes This Panel Different from Standard PGx

Standard PGx panels (Quest, Invitae, GeneSight) cover ~30-40 genes focused on **drug metabolism** (CYPs, UGTs, transporters) for traditional pharmaceuticals.

This 116-marker panel adds three layers that standard panels don't cover:

1. **Peptide-degrading enzymes** (DPP4, NEP/MME, ACE, PRCP) — specific to peptide half-life
2. **Peptide target receptors** (GHSR, GLP1R, MC4R, OXTR) — specific to peptide mechanism
3. **Tissue repair / recovery genes** (NOS3, VEGFA, COL1A1, MMPs, cytokines) — specific to what recovery peptides act on

Standard panels answer: "How fast do you metabolize drugs?"
This panel answers: "How fast do you destroy peptides, how sensitive are your receptors to them, and how capable is your repair machinery?"

---

## Feasibility Assessment: Can We Replicate This?

### What we can query today (via existing MCPs):

| Source | What It Gives Us |
|--------|-----------------|
| **ClinPGx** | CPIC guidelines for CYP genes, established drug-gene pairs |
| **ClinVar** | Pathogenicity of specific variants |
| **gnomAD** | Population frequencies for all variants |
| **GWAS Catalog** | Phenotype associations for each SNP |
| **Ensembl** | Gene structure, transcript variants |
| **PharmGKB** (via PubMed) | Drug-gene-variant relationships |

### What we'd need to build:

1. **A mapping table**: peptide → target gene → actionable variants → predicted effect
2. **A scoring engine**: given a genotype profile, rank peptides by predicted response
3. **The panel design itself**: which 116 SNPs to genotype (this document is a first draft)

### Could BioClaw generate personalized peptide recommendations today?

**Partially yes.** If a user provided their raw genetic data (23andMe, AncestryDNA), BioClaw could:
1. Extract relevant SNPs from the raw file
2. Look up each variant via ClinVar + ClinPGx + GWAS
3. Cross-reference with peptide mechanisms via PubMed deep research
4. Generate a personalized report

**What's missing**: the peptide-specific interpretation layer. We know CYP2C9*3 slows semaglutide metabolism, but we don't have structured rules for most peptide-gene pairs. The cohort is building these rules empirically. We could build them from literature.

---

## Sources

- [Pharmacogenomics of GLP-1 receptor agonists (Lancet)](https://www.thelancet.com/journals/landia/article/PIIS2213-8587(22)00340-0/fulltext)
- [Pharmacogenomics of Tirzepatide (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12473131/)
- [GLP1R biased agonism and polymorphic variation](https://www.sciencedirect.com/science/article/pii/S1043661822003565)
- [GHSR genetic linkage and obesity (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2793077/)
- [NEP/MME genetic variation and function (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3316445/)
- [CYP450 population-scale sequencing (Nature)](https://www.nature.com/articles/s41397-022-00288-2)
- [DPP-4 peptide degradation](https://pubmed.ncbi.nlm.nih.gov/29412814/)
- [BPC-157 multifunctionality review (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11859134/)
- [CPIC Guidelines](https://cpicpgx.org/guidelines/)
- [DunedinPACE epigenetic clock (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8853656/)
- [Predicting GLP-1RA treatment response](https://www.tandfonline.com/doi/pdf/10.1080/14656566.2025.2517802)
