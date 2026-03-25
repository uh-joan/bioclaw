# Scoring: gwas-snp-interpretation
Target: 0.9

1. **Gene/Locus Accuracy (0.25)**: Correct gene, variant, and genomic context = 1.0
2. **Effect Size and Direction (0.25)**: Correct OR/beta, risk vs protective allele = 1.0; wrong direction = 0
3. **Mechanism (0.20)**: Plausible biological mechanism explained = 1.0; "unknown" when mechanism is known = 0
4. **Clinical/Translational Relevance (0.20)**: Drug relevance, PRS inclusion, clinical action noted = 1.0
5. **Completeness (0.10)**: Key interpretive elements present = 1.0

Override: FTO mechanism attributed to FTO gene only (not IRX3/IRX5) = -0.3 (outdated interpretation). APOE dosage effect missing = -0.2.
