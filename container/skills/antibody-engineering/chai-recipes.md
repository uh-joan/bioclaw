# Chai-1 Antibody Engineering Recipes

Recipes for glycosylated antibody modeling and restraint-guided antibody complex prediction using Chai-1. Chai-1 is the only open-source tool with native glycan support — critical for Fc engineering and effector function analysis.

> **Parent skill**: [SKILL.md](SKILL.md) — full antibody engineering pipeline.
> **See also**: [chai-predict skill](../chai-predict/SKILL.md) — standalone Chai-1 prediction with full CLI reference.

---

## Recipe 1: Fc Glycosylation Impact on Effector Function

Model the N297 glycan on antibody Fc to assess its impact on FcγR binding geometry. Afucosylated glycans enhance ADCC — predict both fucosylated and afucosylated forms.

```bash
# Fucosylated (standard) — reduced ADCC
cat > fc_fucosylated.fasta << 'FASTA'
>protein|name=fc
CPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPG
>glycan|name=core-fucosylated
NAG(4-1 NAG(4-1 BMA(3-1 MAN(2-1 NAG(4-1 GAL)))(6-1 MAN(2-1 NAG(4-1 GAL)))))(6-1 FUC)
FASTA

# Afucosylated — enhanced ADCC
cat > fc_afucosylated.fasta << 'FASTA'
>protein|name=fc
CPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPG
>glycan|name=afucosylated
NAG(4-1 NAG(4-1 BMA(3-1 MAN(2-1 NAG(4-1 GAL)))(6-1 MAN(2-1 NAG(4-1 GAL)))))
FASTA

chai-lab fold --use-msa-server fc_fucosylated.fasta fc_fuc/
chai-lab fold --use-msa-server fc_afucosylated.fasta fc_afuc/

python3 << 'PYTHON'
import numpy as np

fuc = np.load("fc_fuc/scores.model_idx_0.npz", allow_pickle=True)
afuc = np.load("fc_afuc/scores.model_idx_0.npz", allow_pickle=True)

print("Fc Glycoform Comparison (ADCC impact)")
print("=" * 55)
print(f"{'Glycoform':<20} {'Score':>7} {'pTM':>6} {'ipTM':>6}")
print("-" * 55)
print(f"{'Fucosylated':<20} {fuc['aggregate_score'].item():>7.3f} {fuc['ptm'].item():>6.3f} {fuc['iptm'].item():>6.3f}")
print(f"{'Afucosylated':<20} {afuc['aggregate_score'].item():>7.3f} {afuc['ptm'].item():>6.3f} {afuc['iptm'].item():>6.3f}")
print()
print("Afucosylated Fc has more open CH2 domain → better FcγRIIIa engagement → enhanced ADCC")
PYTHON
```

---

## Recipe 2: ADC Glycosite Engineering

Model antibody-drug conjugate (ADC) with engineered glycosylation sites for site-specific drug attachment.

```bash
# Antibody with engineered glycosylation at non-native site
cat > adc_glyco.fasta << 'FASTA'
>protein|name=engineered-fc
CPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQY(SEP)STYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPG
>glycan|name=native-n297
NAG(4-1 NAG(4-1 BMA(3-1 MAN)(6-1 MAN)))
>glycan|name=engineered-site
NAG(4-1 NAG)
FASTA

chai-lab fold --use-msa-server adc_glyco.fasta adc_results/
```

---

## Recipe 3: Crosslink-Guided Antibody-Antigen Complex

Use XL-MS crosslink data from hydrogen-deuterium exchange or crosslinking experiments to guide antibody-antigen complex prediction.

```bash
cat > ab_ag.fasta << 'FASTA'
>protein|name=vh
EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS
>protein|name=vl
DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK
>protein|name=antigen
MANTIGENSEQUENCE
FASTA

# Known epitope contacts from HDX or crosslinking
cat > epitope_restraints.csv << 'CSV'
restraint_id,chainA,res_idxA,chainB,res_idxB,connection_type,confidence,min_distance,max_distance,comment
1,A,33,C,45,contact,0.9,0,12.0,CDR-H1 to epitope
2,A,52,C,78,contact,0.8,0,12.0,CDR-H2 to epitope
3,A,100,C,82,contact,0.9,0,12.0,CDR-H3 to epitope
4,B,30,C,90,contact,0.7,0,12.0,CDR-L1 to epitope
CSV

chai-lab fold --use-msa-server --constraint-path epitope_restraints.csv ab_ag.fasta ab_ag_results/
```

---

## Recipe 4: Bispecific with Glycan Analysis

Model a bispecific antibody format and assess glycan impact on stability.

```bash
cat > bispecific_glyco.fasta << 'FASTA'
>protein|name=vh1
VH1SEQUENCE
>protein|name=vl1
VL1SEQUENCE
>protein|name=vh2
VH2SEQUENCE
>protein|name=vl2
VL2SEQUENCE
>protein|name=fc
FCSEQUENCE
>glycan|name=fc-glycan
NAG(4-1 NAG(4-1 BMA(3-1 MAN)(6-1 MAN)))
FASTA

chai-lab fold --use-msa-server bispecific_glyco.fasta bispecific_results/

python3 << 'PYTHON'
import numpy as np

scores = np.load("bispecific_results/scores.model_idx_0.npz", allow_pickle=True)
print(f"Bispecific + glycan: score={scores['aggregate_score'].item():.3f} "
      f"pTM={scores['ptm'].item():.3f} ipTM={scores['iptm'].item():.3f}")

if "per_chain_pair_iptm" in scores:
    pair = scores["per_chain_pair_iptm"]
    print(f"\nChain pair interfaces:")
    for i in range(pair.shape[0]):
        for j in range(i+1, pair.shape[1]):
            if pair[i,j] > 0.1:
                print(f"  Chain {i}-{j}: {pair[i,j]:.3f}")
PYTHON
```
