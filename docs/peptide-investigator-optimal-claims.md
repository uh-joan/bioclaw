# Peptide Investigator — Optimal Test Claims from Reddit

**Date:** 2026-03-11
**Pipeline:** Apify Reddit scraper → claim extraction → scoring → curation
**Funnel:** 240 scraped items → 66 filtered claims → 12 optimal inputs

---

## How Claims Were Selected

Each claim was scored on:
- **Specificity** — named peptide + named condition + dose/timeline (+30)
- **Claim language** — negative claims (+25), positive (+20), exploration (+15)
- **Engagement** — upvotes and comments as proxy for community demand
- **Subreddit relevance** — peptide-specific subs get a boost (+10)
- **Clarity** — single peptide + single condition = cleanest input (+10)

Excluded: sourcing questions, dosing/reconstitution, regulatory discussions, vendor reviews, generic lifestyle posts.

---

## The 12 Claims

### #1 | NEGATIVE | BPC-157 → Vision/Eye Side Effects
**Source:** r/bpc_157
**Skill input:** "investigate this: someone on r/bpc_157 says they got light sensitivity and eye irritation after only 1.5 weeks on BPC-157. They say it's rare but real."
**Why optimal:** Specific side effect claim with timeline. Testable against literature. High engagement. Negative claims are highest value.
**Expected verdict:** Risky — angiogenesis promotion in ocular tissue is a real mechanistic concern.

---

### #2 | POSITIVE | GHK-Cu → Knee Pain Resolution
**Source:** r/PeptideSelect
**Skill input:** "investigate this: someone on r/PeptideSelect says they added GHK-Cu to their BPC/TB-500 stack and their knee pain is 'actually gone, not just less bad' after one week at 1mg daily"
**Why optimal:** Specific dose, specific timeline, specific outcome. Stack context (BPC+TB-500+GHK-Cu). Tests whether GHK-Cu adds value to a common stack.
**Expected verdict:** Weak Evidence — mechanism plausible via copper-dependent tissue repair, but no human knee data exists.

---

### #3 | NEGATIVE | Retatrutide → Emotional Blunting / Mood Changes
**Source:** r/Retatrutide
**Skill input:** "investigate this: someone on r/Retatrutide says reta causes emotional blunting and makes them 'less sociable and less fun to be around' at 12mg dose alongside great weight loss"
**Why optimal:** Unreported psychiatric side effect at specific dose. Triple agonist mechanism could explain CNS effects. High investigation value.
**Expected verdict:** Risky — glucagon receptor agonism has CNS effects; emotional blunting not well-characterized in trials but reported in community.

---

### #4 | POSITIVE | CJC-1295 + Ipamorelin → Chronic Insomnia
**Source:** r/BodyHackGuide
**Skill input:** "investigate this: someone on r/BodyHackGuide says 3 months of CJC-1295 (no DAC) + Ipamorelin fixed their chronic insomnia and improved body composition with data"
**Why optimal:** Most common GH secretagogue stack. Insomnia is a major community pain point. User claims data backing the claim. Testable mechanism via GH/sleep architecture.
**Expected verdict:** Weak Evidence — GH pulses are tied to slow-wave sleep architecture, mechanism is real, but no RCTs on CJC/IPA for insomnia.

---

### #5 | EXPLORATION | Thymosin Alpha-1 → Hashimoto's Thyroiditis
**Source:** r/Hashimotos
**Skill input:** "investigate this: someone on r/Hashimotos is asking about Thymosin Alpha-1, BPC-157, and TB-500 for treating Hashimoto's thyroiditis symptoms"
**Why optimal:** Autoimmune condition + immune-modulating peptide. TA1 actually has clinical data for immune modulation. Tests whether the skill can find real evidence for a less common peptide.
**Expected verdict:** Plausible — Thymosin Alpha-1 is approved in several countries for immune modulation, with clinical data in hepatitis and as an immune adjuvant.

---

### #6 | POSITIVE | BPC-157 → Chronic Gastritis
**Source:** r/Gastritis
**Skill input:** "investigate this: someone on r/Gastritis says BPC-157 almost healed their chronic gastritis after years of weight loss, nausea, and vomiting"
**Why optimal:** BPC-157 is literally derived from gastric juice. This is the most mechanistically plausible claim possible. Tests whether the skill correctly assigns "Plausible" when the biology is direct.
**Expected verdict:** Plausible — BPC-157 is a gastric pentadecapeptide with extensive preclinical data on gastric protection and mucosal healing.

---

### #7 | NEGATIVE | CJC-1295 + Ipamorelin → Lower Back Pain
**Source:** r/Biohacking
**Skill input:** "investigate this: someone on r/Biohacking says CJC-1295/Ipamorelin is causing severe lower back pain at age 59, thinks his pituitary is pumping out too much HGH"
**Why optimal:** GH-mediated side effect with age context. Tests interaction analysis — at 59, IGF-1 baseline matters. Could be acromegaly-like symptoms from GH excess.
**Expected verdict:** Risky — GH elevation causes fluid retention and joint/bone pain; at 59, lower baseline GH means exogenous stimulation has outsized effects.

---

### #8 | EXPLORATION | Kisspeptin → Lean PCOS / Anovulation
**Source:** r/PCOS
**Skill input:** "investigate this: someone on r/PCOS says they have lean PCOS with anovulatory cycles and high testosterone, and is asking about kisspeptin-10 since insulin is normal so GLP-1s won't help"
**Why optimal:** Kisspeptin actually has human RCT data for reproductive endocrinology. Tests whether the skill can find strong evidence and assign "Plausible" for a lesser-known peptide. Also tests the nuance of why GLP-1 wouldn't help here.
**Expected verdict:** Plausible — kisspeptin-10 has human RCT data showing restoration of LH pulsatility in hypothalamic amenorrhea and PCOS.

---

### #9 | EXPLORATION | Semax + Selank → Stimulant-Induced Cognitive Damage
**Source:** r/Nootropics
**Skill input:** "investigate this: someone on r/Nootropics abused ADHD stimulants for 3 years and wants to restore brain with semax, selank, cerebrolysin and dihexa"
**Why optimal:** Neuropeptide stack for neurological recovery. Semax/Selank have Russian clinical data. Tests whether the skill can evaluate non-Western evidence sources.
**Expected verdict:** Weak Evidence — Russian clinical trials exist for Semax (ACTH fragment) and Selank (tuftsin analogue) but limited Western validation.

---

### #10 | EXPLORATION | MOTS-C → Mitochondrial Function / Post-Weight-Loss Recovery
**Source:** r/ResearchCompounds
**Skill input:** "investigate this: someone on r/ResearchCompounds lost 90lbs on tirzepatide and wants to add MOTS-C for mitochondrial function plus KLOW (BPC-157+TB-500) for recovery while on that dose"
**Why optimal:** MOTS-C is a mitochondrial-derived peptide with real metabolic data. Tests complex stack interaction analysis. User already on tirzepatide — interaction check is critical.
**Expected verdict:** Weak Evidence — MOTS-C has preclinical data for AMPK activation and metabolic regulation, but human evidence is early-stage.

---

### #11 | NEGATIVE | GHK-Cu → Skin Irritation with Retinol
**Source:** r/PurePeptides
**Skill input:** "investigate this: someone on r/PurePeptides is stacking GHK-Cu with retinol for skin and asking if it causes irritation"
**Why optimal:** Copper peptide + retinoid interaction is a real dermatological question. Tests whether the skill can evaluate topical peptide safety, not just injectable.
**Expected verdict:** Weak Evidence — GHK-Cu has wound healing data; retinol interaction is pH/formulation dependent, not well-studied.

---

### #12 | EXPLORATION | Selank → Anxiety / GAD in Addiction Recovery
**Source:** r/NooTopics
**Skill input:** "investigate this: someone on r/NooTopics has been sober 5 years from alcohol and has GAD + panic disorder, asking about selank for anxiety while on other medications"
**Why optimal:** Selank has anxiolytic data from Russian clinical trials. Tests interaction check with psychiatric medications. Tests whether the skill handles the addiction recovery context safely.
**Expected verdict:** Weak Evidence — Selank (tuftsin analogue) has Russian clinical data showing anxiolytic effects comparable to benzodiazepines without dependence, but limited Western trials.

---

## Coverage Analysis

### Peptides Covered (11)
BPC-157, GHK-Cu, Retatrutide, CJC-1295, Ipamorelin, Thymosin Alpha-1, Kisspeptin, Semax, Selank, MOTS-C, Melanotan II

### Conditions Covered (12)
Eye effects, knee pain, emotional blunting, insomnia, autoimmune (Hashimoto's), gastritis, back pain, PCOS/anovulation, cognitive damage, mitochondrial function, skin/topical, anxiety

### Claim Type Distribution
| Type | Count | Purpose |
|------|-------|---------|
| Positive | 4 | Tests "Plausible" and "Weak Evidence" verdicts |
| Negative | 4 | Tests "Risky" verdicts and side effect analysis |
| Exploration | 4 | Tests whether skill handles "should I try this?" questions |

### Expected Verdict Distribution
| Verdict | Count | Claims |
|---------|-------|--------|
| Plausible | 3 | BPC-157→gastritis, Kisspeptin→PCOS, TA1→Hashimoto's |
| Weak Evidence | 5 | GHK-Cu→knee, CJC/IPA→insomnia, Semax/Selank→cognition, MOTS-C→mito, GHK-Cu→skin, Selank→anxiety |
| Risky | 3 | BPC-157→eyes, Retatrutide→mood, CJC/IPA→back pain |
| Unsupported | 0 | (intentionally excluded — no value in testing obvious failures) |

---

## Apify Scrape Configuration

5 parallel runs using `comchat~reddit-api-scraper`:

| Run | Query Strategy | Items |
|-----|---------------|-------|
| 1 | Positive claims: "[peptide] helped/healed/fixed my" | 45 |
| 2 | Negative claims: "[peptide] caused/made worse/side effect" | 50 |
| 3 | Exploration: "has anyone tried [peptide] for" | 45 |
| 4 | Compound+condition combos from pain data | 50 |
| 5 | Comments: "[peptide] completely/transformed/changed" | 50 |
| **Total** | | **240** |

Filtering removed sourcing, dosing, regulatory, and vendor posts. Scoring prioritized specificity (compound + condition), claim language strength, engagement metrics, and subreddit relevance.
