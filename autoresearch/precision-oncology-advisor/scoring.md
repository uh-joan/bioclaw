# Scoring: precision-oncology-advisor
Target: 0.9

1. **Treatment Recommendation Accuracy (0.30)**: Matches expected tier-1 drug with correct evidence grade = 1.0
2. **Biomarker-Drug Matching (0.25)**: Correct biomarker-to-drug linkage = 1.0; wrong biomarker interpretation = 0
3. **Resistance/Co-mutation Awareness (0.20)**: Resistance planning or co-mutation impact addressed = 1.0
4. **Evidence Grading (0.15)**: Correct evidence level (1A/1B/2A etc.) = 1.0
5. **Completeness (0.10)**: Required sections present = 1.0

Override: If EGFR+ patient given ICI monotherapy over TKI, case score = 0. If MSI-H CRC given chemo over ICI first-line, case score = 0.
