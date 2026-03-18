# Peptigotchi — Product Proposal

## The Insight

Reddit scrape (58 posts, 11 subreddits, 240+ signals) reveals one unifying truth: **people are self-administering injectable compounds with zero institutional support.** The top pain points are:

| # | Pain Point | Intensity | Posts |
|---|-----------|-----------|-------|
| 1 | Side effects with no medical guidance | Extreme | 22 |
| 2 | Reconstitution/dosing is terrifying | High | 19 |
| 3 | Can't verify what's in the vial | Extreme | 18 |
| 4 | Regulatory confusion | High | 10 |
| 5 | Protocol complexity (stacking) | Medium-High | 8 |
| 6 | Newbie onramp is hostile | Medium-High | 6 |
| 7 | No trusted source post-shutdowns | Extreme | 5 |

## The Concept

A Tamagotchi-style companion that **gamifies responsible peptide use.** Your Peptigotchi is a little creature whose health mirrors how well you're managing your protocol. Skip a log? It gets sick. Stack 5 peptides with no interaction check? It panics. Nail your reconstitution math? It evolves.

**The trick:** it's not a game about peptides — it's a **habit tracker + safety net + education system** disguised as a pet.

## Core Mechanics

### 1. The Creature (Your Protocol Avatar)

Your Peptigotchi has 5 vital stats, each mapped to a real pain point:

| Stat | What It Tracks | Pain Point Addressed |
|------|---------------|---------------------|
| **Purity** | Whether you've verified your source/COA | Can't verify what's in the vial |
| **Precision** | Reconstitution/dosing accuracy | Dosing is terrifying |
| **Stability** | Side effect logging consistency | No medical guidance |
| **Harmony** | Stack interaction safety | Protocol complexity |
| **Knowledge** | Educational milestones completed | Hostile newbie onramp |

**Creature states:**
- **Thriving** (all stats green) — creature evolves, unlocks cosmetics
- **Stressed** (1-2 yellow) — creature shows warning animations
- **Sick** (any red) — creature visibly ill, sends nudges
- **Critical** (multiple red) — creature begs for help, surfaces safety info

### 2. Daily Loop (The Tamagotchi Clock)

Every day, the Peptigotchi expects you to:

| Action | Effort | Stat Fed |
|--------|--------|----------|
| **Log your dose** (what, how much, when, site) | 30 sec | Precision |
| **Check in** (how do you feel? any sides?) | 30 sec | Stability |
| **Verify source** (first use of new vial: COA, vendor, batch) | 2 min | Purity |

Miss a day? Stats decay. The creature gets sad. Three missed days? It goes to sleep (not dead — Tamagotchis die, Peptigotchis hibernate. You can always come back.)

### 3. Safety Systems (The Real Value)

**Reconstitution Calculator** — Pain point #3
- Input: peptide mg, BAC water ml, desired dose mcg
- Output: exact units to draw, with visual syringe diagram
- Peptigotchi celebrates when you complete it ("Precision +10!")
- Built from the real need — someone on Reddit literally built one themselves

**Side Effect Tracker** — Pain point #2
- Daily check-in logs symptoms against known profiles
- Pattern detection: "You've reported insomnia 4 of the last 7 days on BPC-157 — this matches reports from 23% of users"
- Escalation prompts: "This pattern suggests you should consult a healthcare provider" (never medical advice, always referral)
- Peptigotchi's Stability stat reflects consistency of logging

**Stack Conflict Checker** — Pain point #6
- When you add a peptide to your protocol, Peptigotchi checks interactions
- Uses the existing peptide-investigator pipeline (PubMed, DrugBank, ChEMBL)
- "Adding tesamorelin to your BPC-157 + TB-500 + retatrutide stack — checking... ⚠️ Zero interaction data for this 4-compound combination. Harmony stat at risk."
- Visual: creature looks nervous when stacks are unvalidated

**Regulatory Status Feed** — Pain point #5
- Each peptide in your protocol shows current FDA category
- Push notification when status changes (like the Feb 2026 RFK announcement about 14 peptides returning to Category 1)
- Peptigotchi's Knowledge stat increases when you read updates

### 4. Education System (The Onramp) — Pain point #7

**Peptigotchi Academy** — unlock-based learning:

| Level | Unlocks At | Teaches |
|-------|-----------|---------|
| **Egg** | Account creation | What are peptides? Amino acid chains, mechanisms |
| **Hatchling** | First peptide added | Reconstitution basics, sterile technique |
| **Juvenile** | 7-day streak | Reading COAs, understanding purity % |
| **Adult** | 30-day streak | Stack management, half-lives, timing |
| **Elder** | 90-day streak | Literature reading, evidence grading, spotting BS claims |

Each level unlocks creature evolutions + cosmetics (hats, backgrounds, colors). Vanity is the best motivator.

**Claim Investigator** (powered by existing peptide-investigator skill) — user pastes a Reddit claim → Peptigotchi runs the 7-step investigation pipeline → returns verdict (Plausible / Weak Evidence / Unsupported / Risky) with sources. Knowledge stat goes up.

### 5. Community (Solving the Trust Problem) — Pain point #4, #7

**Anonymous Protocol Sharing** — opt-in
- Share your protocol (peptides, doses, duration, reported effects) anonymously
- Aggregate data: "1,247 users running BPC-157 at 250mcg/day. 78% report positive tendon outcomes. 23% report sleep disruption."
- This is the verification infrastructure Reddit is missing — crowd-sourced outcomes data

**Vendor Reputation** (careful territory)
- Users rate vendors on: shipping speed, COA availability, batch consistency
- No direct vendor links (legal minefield) — just reputation scores
- Addresses the "Peptide Sciences shut down, now what?" panic

### 6. Progression & Retention

| Milestone | Reward |
|-----------|--------|
| 7-day logging streak | Creature evolution |
| First reconstitution calculated | "Precision Master" badge |
| First claim investigated | "Skeptic" badge |
| All 5 stats green for 7 days | Rare creature variant |
| Shared first anonymous protocol | "Contributor" badge |
| 90-day streak | Elder creature + mentor status |

## What It's NOT

- **Not medical advice.** Every screen has disclaimers. Side effect tracker suggests "consult a provider," never diagnoses.
- **Not a marketplace.** No selling, no vendor links, no affiliate revenue.
- **Not a social network.** Anonymous data sharing only. No profiles, no DMs, no influencers.

## Technical Architecture (NanoClaw Integration)

This fits naturally into the existing NanoClaw infrastructure:

```
User (mobile app / WhatsApp / Telegram)
  ↓
NanoClaw channel
  ↓
Peptigotchi container agent
  ├── peptide-investigator skill (claim checking)
  ├── MCP servers (PubMed, DrugBank, FDA, ChEMBL, ClinicalTrials.gov)
  ├── SQLite (protocol logs, side effects, streaks, creature state)
  └── groups/{user}/CLAUDE.md (persistent creature memory)
```

**MVP channel:** WhatsApp or Telegram (already built). The Peptigotchi lives in your chat. You talk to it. It talks back with creature status, reminders, and safety checks.

**Later:** Dedicated mobile app with actual creature animations.

## MVP Scope (What to Build First)

Phase 1 — the 3 things that address the most painful pain points:

1. **Reconstitution calculator** (pain #3, 19 posts) — highest effort-to-value ratio
2. **Daily dose + side effect logger with pattern detection** (pain #2, 22 posts) — the core loop
3. **Creature with 5 stats that reflect your behavior** — the hook

Everything else (claim investigator, stack checker, community, vendor reputation) layers on top.

---

## Peptigotchi Lite — Offline-Capable Version

### Why Lite?

The full Peptigotchi relies on MCP servers (PubMed, DrugBank, ChEMBL, FDA) for real-time claim investigation and interaction checking. Lite ships with a **pre-built peptide knowledge base** covering the most common compounds, so the core experience — dosing, tracking, side effect alerts, stack warnings — works without any network connection.

Online features (claim investigator, regulatory feed, community sharing) become available when connected but are not required.

### The Lite Peptide Set (12 Compounds)

Selected by Reddit mention frequency, diversity of use cases, and likelihood a user will encounter them in their first 6 months.

#### Tier 1: Core (the big 5 — covers ~80% of community activity)

| Peptide | Category | Common Uses | Key Side Effects | Typical Dose Range |
|---------|----------|-------------|-----------------|-------------------|
| **BPC-157** | Healing | Tendon/ligament repair, gut healing (IBD, GERD, gastritis) | Anxiety/panic, anhedonia, insomnia, light sensitivity, paradoxical joint pain | 250-500 mcg/day SubQ |
| **Semaglutide** | GLP-1 Agonist | Weight loss, appetite suppression, T2 diabetes | Hair loss (ROR 2.46 FAERS), gastroparesis, nausea, muscle loss (30% of weight lost), emotional blunting | 0.25-2.4 mg/week SubQ |
| **Tirzepatide** | GLP-1/GIP Dual | Weight loss, insulin sensitivity | GI distress, sulfur burps, nausea, injection site reactions | 2.5-15 mg/week SubQ |
| **Retatrutide** | Triple Agonist | Weight loss (28.7% in trials) | Sleep disruption (~8%), emotional blunting, joint pain, product authenticity issues | 1-12 mg/week SubQ |
| **TB-500** | Healing | Joint/tendon repair (usually stacked with BPC-157) | Tumor growth concern (animal data), paradoxical joint pain, angiogenesis risk | 2-5 mg 2x/week SubQ |

#### Tier 2: Common stacks (the next 5 — most frequent supporting compounds)

| Peptide | Category | Common Uses | Key Side Effects | Typical Dose Range |
|---------|----------|-------------|-----------------|-------------------|
| **CJC-1295** | GH Secretagogue | Body composition, sleep, recovery (stacked with Ipamorelin) | Water retention/edema, lower back pain, elevated GH effects in older users | 100-300 mcg/day SubQ |
| **Ipamorelin** | GH Secretagogue | Sleep quality, fat loss, recovery | Mild — headache, dizziness, flushing | 100-300 mcg/day SubQ |
| **GHK-Cu** | Copper Peptide | Skin/wound healing, collagen, knee pain | Skin irritation with retinol, hype exceeds evidence for systemic use | 1-2 mg/day SubQ or topical |
| **Tesamorelin** | GH Releasing | Fat loss, body composition (FDA-approved for HIV lipodystrophy) | Joint pain (1-10%, dose-dependent), carpal tunnel, fluid retention | 1-2 mg/day SubQ |
| **Thymosin Alpha-1** | Immune | Immune modulation, autoimmune conditions (Hashimoto's) | Generally well-tolerated; flu-like symptoms possible | 1.6 mg 2x/week SubQ |

#### Tier 3: Emerging (2 compounds gaining fast traction)

| Peptide | Category | Common Uses | Key Side Effects | Typical Dose Range |
|---------|----------|-------------|-----------------|-------------------|
| **Semax** | Neuropeptide | Cognitive enhancement, focus, anxiety | Tolerance development, limited Western evidence, nasal irritation | 200-600 mcg/day intranasal |
| **Selank** | Neuropeptide | Anxiety/GAD, addiction recovery support | Tolerance questions, sedation at higher doses | 250-500 mcg/day intranasal |

### Pre-Built Data Model Per Compound

Each of the 12 compounds ships with a static JSON knowledge card:

```json
{
  "compound": "BPC-157",
  "aliases": ["Body Protection Compound-157", "Bepecin"],
  "pubchem_cid": 9941957,
  "category": "healing",
  "administration": {
    "routes": ["subcutaneous", "intramuscular", "oral"],
    "typical_dose_mcg": { "min": 250, "max": 500 },
    "frequency": "1-2x daily",
    "common_vial_sizes_mg": [5, 10],
    "reconstitution": {
      "solvent": "bacteriostatic water",
      "typical_volume_ml": 2,
      "storage_days_refrigerated": 28
    }
  },
  "mechanism_summary": "Upregulates VEGFR2 (angiogenesis), modulates nitric oxide, interacts with dopamine system. Promotes tendon/ligament fibroblast migration and collagen synthesis.",
  "evidence_grade": "animal_strong_human_absent",
  "evidence_detail": "50+ rat/mouse studies showing tendon, ligament, muscle, and GI healing. Zero human RCTs. All human evidence is anecdotal/community-reported.",
  "known_side_effects": [
    {
      "effect": "anxiety_panic",
      "frequency": "common",
      "severity": "moderate_to_severe",
      "mechanism": "Suspected dopamine system modulation",
      "reddit_signal_strength": "high",
      "onset_typical_days": "3-14"
    },
    {
      "effect": "anhedonia",
      "frequency": "uncommon",
      "severity": "severe",
      "mechanism": "Dopamine downregulation hypothesis",
      "reddit_signal_strength": "medium",
      "onset_typical_days": "7-21",
      "persistence_note": "Reports of persistence 6+ weeks post-cessation"
    },
    {
      "effect": "insomnia",
      "frequency": "common",
      "severity": "moderate",
      "mechanism": "Unknown — possibly CNS stimulation",
      "reddit_signal_strength": "medium",
      "onset_typical_days": "3-10"
    },
    {
      "effect": "light_sensitivity",
      "frequency": "rare",
      "severity": "moderate",
      "mechanism": "Unknown — possible retinal VEGF effect",
      "reddit_signal_strength": "low",
      "onset_typical_days": "7-14"
    }
  ],
  "interactions": [
    {
      "with": "TB-500",
      "type": "common_stack",
      "concern": "Both promote angiogenesis — theoretical tumor risk amplification",
      "evidence": "no_human_data"
    },
    {
      "with": "anticoagulants",
      "type": "caution",
      "concern": "BPC-157 may affect platelet aggregation",
      "evidence": "animal_data_only"
    }
  ],
  "regulatory": {
    "fda_status": "not_approved",
    "fda_category": "category_2_as_of_2024",
    "note": "Included in 14 peptides expected to return to Category 1 per RFK Feb 2026 announcement — status pending",
    "last_updated": "2026-03"
  },
  "community_insights": {
    "top_positive_use": "Tendon/ligament healing — highest volume of positive reports",
    "top_negative_report": "Anxiety/mood disruption — frequently reported, often unexpected",
    "common_mistake": "Using for gut healing but not monitoring mood/sleep changes",
    "pro_tip": "Start low (150mcg), monitor mood daily for first 2 weeks before increasing"
  }
}
```

### What Works Offline vs. Online

| Feature | Offline | Online |
|---------|---------|--------|
| Reconstitution calculator | Yes — math is local | — |
| Dose logging & streak tracking | Yes — local SQLite | Syncs to cloud backup |
| Side effect check-in | Yes — logs locally | — |
| Side effect pattern detection | Yes — matches against pre-built profiles for 12 compounds | Enhanced with latest community data |
| Stack conflict warnings | Yes — pre-built interaction matrix (12x12 = 144 pairs) | Full DrugBank/ChEMBL lookup for any compound |
| Creature stats & evolution | Yes — all local | — |
| Education content (Academy) | Yes — shipped with app | Updated lessons over time |
| Claim investigator | No — requires MCP servers | Yes — full 7-step pipeline |
| Regulatory status feed | Cached — last-known status ships with app | Yes — push updates on changes |
| Community protocol sharing | No | Yes — anonymous aggregation |
| Vendor reputation | No | Yes |

### Pre-Built Interaction Model (3 Layers)

The original spec only had peptide×peptide (12×12). Real users stack peptides **on top of** medications, hormones, supplements, and lifestyle factors. The Reddit data confirms this — users running 7+ compounds with exercise, fasting, and hormones simultaneously.

The interaction model ships with 3 layers:

#### Layer 1: Peptide × Peptide (12×12 = 144 pairs)

```
interaction_data[compound_a][compound_b] = {
  commonly_stacked: true/false,
  known_conflicts: "description" | null,
  evidence_level: "human_data" | "animal_data" | "theoretical" | "no_data",
  community_reports: "summary of Reddit signals",
  recommendation: "safe_to_stack" | "monitor_closely" | "avoid" | "no_data_caution"
}
```

**Notable peptide×peptide interactions:**
- BPC-157 + TB-500: Most common stack. Theoretical angiogenesis amplification. "monitor_closely"
- CJC-1295 + Ipamorelin: Standard GH stack. Well-characterized. "safe_to_stack"
- BPC-157 + Retatrutide: No interaction data. "no_data_caution"
- Tesamorelin + Retatrutide: Stacking creates 4+ compound protocol with zero data. "avoid"
- Semaglutide + Tirzepatide: Same receptor class — redundant/dangerous. "avoid"
- GHK-Cu + Retinol (topical): Skin irritation reported. "monitor_closely"

#### Layer 2: Peptide × Common Medications/Hormones (~20 drug classes)

Users don't take peptides in isolation. The model ships with interaction data for the most common co-administered substances:

| Drug Class | Examples | Why It Matters |
|-----------|----------|---------------|
| **Testosterone / TRT** | Test E, Test C, HCG | Most common co-admin. Reta user on 400mg Test E found dose stopped working — testosterone increases appetite, counteracting GLP-1 suppression |
| **Anticoagulants** | Warfarin, aspirin, heparin | BPC-157 may affect platelet aggregation (animal data). Critical safety flag |
| **Retinoids** | Accutane (isotretinoin), tretinoin | User asked about Accutane + GHK-Cu — zero info exists. Retinol + GHK-Cu topical causes irritation |
| **SSRIs / SNRIs** | Sertraline, escitalopram, venlafaxine | BPC-157 modulates dopamine — theoretical interaction with serotonergic drugs. Anhedonia risk amplification |
| **Metformin** | Metformin | Common in GLP-1 users (T2 diabetes). Additive GI side effects with tirzepatide/semaglutide |
| **NSAIDs** | Ibuprofen, naproxen | BPC-157 used for inflammation — NSAIDs may counteract or compound. GI bleeding risk with GLP-1 gastroparesis |
| **Thyroid meds** | Levothyroxine | Thymosin Alpha-1 used for Hashimoto's — interaction with thyroid hormone replacement unknown |
| **Stimulants** | Adderall, modafinil, caffeine | Semax/Selank users often stacking for cognitive enhancement. Additive CNS stimulation |
| **Sleep aids** | Melatonin, trazodone, zolpidem | CJC-1295/Ipamorelin taken at bedtime for GH pulse. Drug interactions with sleep aids unknown |
| **PEDs / Anabolics** | Primo, tren, anavar, orals | Reddit shows heavy overlap between peptide and PED communities. Liver/cardiovascular load stacking |
| **Statins** | Atorvastatin, rosuvastatin | GH secretagogues (CJC/IPA/tesamorelin) can elevate IGF-1, which affects lipid metabolism |
| **Blood pressure meds** | ACE inhibitors, ARBs, beta-blockers | GLP-1 agonists can lower BP — additive hypotension risk |
| **Insulin** | Rapid, long-acting | GLP-1 agonists affect insulin secretion — hypoglycemia risk when combined |
| **Oral contraceptives** | Combined pill, progestin-only | GLP-1 gastroparesis can delay absorption of oral medications including birth control |
| **Antibiotics** | General | Reconstituted peptides + bacteriostatic water — contamination risk if immunocompromised |

```json
{
  "peptide": "BPC-157",
  "drug_interactions": [
    {
      "drug_class": "anticoagulants",
      "examples": ["warfarin", "aspirin", "heparin"],
      "concern": "BPC-157 may affect platelet aggregation and clotting cascade",
      "evidence": "animal_data_only",
      "mechanism": "Modulates NO system which influences platelet function",
      "recommendation": "avoid_or_consult_provider",
      "alert_level": "critical"
    },
    {
      "drug_class": "ssri_snri",
      "examples": ["sertraline", "escitalopram", "venlafaxine"],
      "concern": "BPC-157 modulates dopamine system — theoretical amplification of anhedonia/emotional blunting when combined with serotonergic drugs",
      "evidence": "theoretical",
      "mechanism": "Dopamine-serotonin crosstalk",
      "recommendation": "monitor_closely",
      "alert_level": "warning"
    },
    {
      "drug_class": "testosterone_trt",
      "examples": ["testosterone_enanthate", "testosterone_cypionate", "HCG"],
      "concern": "No known direct conflict. Common co-admin in biohacker community",
      "evidence": "community_data",
      "mechanism": "Independent pathways",
      "recommendation": "safe_to_stack",
      "alert_level": "info"
    }
  ]
}
```

#### Layer 3: Peptide × Lifestyle Factors (~10 factors)

Exercise, fasting, sleep, and other lifestyle choices directly affect peptide efficacy and side effects. This layer provides contextual alerts based on user-reported lifestyle data.

| Factor | Relevant Peptides | Interaction |
|--------|------------------|-------------|
| **Fasting / IF (16:8, OMAD)** | GLP-1 agonists, CJC-1295/Ipamorelin | GLP-1s suppress appetite — combining with aggressive fasting risks muscle loss, hypoglycemia, and malnutrition. CJC/IPA best taken fasted (GH release blunted by food) |
| **Resistance training** | BPC-157, TB-500, GH secretagogues | Timing matters — BPC-157 near injury site post-workout may enhance local healing. GH secretagogues before bed for recovery. Overtraining + peptides = false sense of recovery |
| **Cardio / endurance** | GLP-1 agonists, BPC-157 | GLP-1 muscle loss is worse without resistance training. Caloric deficit + cardio + GLP-1 = accelerated lean mass loss |
| **Sleep quality** | CJC-1295/Ipamorelin, Retatrutide | CJC/IPA taken at bedtime to amplify natural GH pulse. Retatrutide disrupts sleep in ~8% of users — poor sleep blunts GH release, creating a vicious cycle |
| **Alcohol** | All peptides, especially GLP-1s | GLP-1 gastroparesis + alcohol = dangerously rapid intoxication (delayed gastric emptying means alcohol hits harder when it finally absorbs). BPC-157 used for gut healing — alcohol directly counteracts |
| **Sun exposure** | Melanotan II, GHK-Cu | MT-II requires some UV to activate melanogenesis. GHK-Cu used for skin — UV damage counteracts repair |
| **Stress / cortisol** | BPC-157, Semax/Selank, GLP-1s | Chronic stress elevates cortisol → counteracts healing peptides. BPC-157 anxiety side effect worse under existing stress. Semax/Selank used for anxiety — stress context matters for dosing |
| **Temperature (sauna, cold plunge)** | GH secretagogues, all reconstituted peptides | Sauna increases endogenous GH — stacking with CJC/IPA may cause excess. Cold exposure affects injection site absorption. Vial temperature instability accelerates degradation |
| **Travel** | All injectable peptides | Cold chain maintenance, syringe transport, timezone shifts for dosing schedules. Reddit user running 5 peptides asked about travel storage |
| **Menstrual cycle** | GLP-1 agonists, Kisspeptin | GLP-1 efficacy varies with cycle phase. Kisspeptin directly interacts with reproductive axis. Oral contraceptive absorption delayed by gastroparesis |

```json
{
  "peptide": "semaglutide",
  "lifestyle_interactions": [
    {
      "factor": "fasting_intermittent",
      "concern": "GLP-1 already suppresses appetite aggressively — combining with 16:8 or OMAD increases risk of excessive caloric deficit and muscle loss",
      "recommendation": "If fasting, prioritize protein intake in eating window (1g/lb target). Track body composition, not just weight.",
      "alert_trigger": "user_reports_fasting_protocol",
      "creature_effect": "Stability -5 if fasting + no protein tracking"
    },
    {
      "factor": "resistance_training",
      "concern": "30% of GLP-1 weight loss is lean mass. Resistance training is the primary mitigation",
      "recommendation": "Minimum 3x/week resistance training strongly recommended while on GLP-1. Without it, muscle loss accelerates.",
      "alert_trigger": "user_reports_no_resistance_training",
      "creature_effect": "Harmony -10 if on GLP-1 with no resistance training logged"
    },
    {
      "factor": "alcohol",
      "concern": "GLP-1 gastroparesis delays gastric emptying — alcohol absorbs unpredictably, often hitting harder than expected",
      "recommendation": "Reduce alcohol consumption. If drinking, eat beforehand and halve your usual intake as a starting point.",
      "alert_trigger": "user_reports_alcohol",
      "creature_effect": "Stability -5, Knowledge +2 (educational moment)"
    }
  ]
}
```

#### Interaction Model Summary

| Layer | Scope | Pairs | Size | Offline? |
|-------|-------|-------|------|----------|
| Peptide × Peptide | 12 compounds | 144 | ~30 KB | Yes |
| Peptide × Drugs | 12 × ~20 drug classes | ~240 | ~60 KB | Yes |
| Peptide × Lifestyle | 12 × ~10 factors | ~120 | ~25 KB | Yes |
| **Total interaction data** | | **~504 pairs** | **~115 KB** | **Yes** |

When the user sets up their profile, they optionally declare:
1. **Current medications** (matched against Layer 2 drug classes)
2. **Lifestyle factors** (exercise type, fasting protocol, sleep habits, alcohol use)
3. **Peptide protocol** (which of the 12 they're running)

The creature's **Harmony stat** reflects the aggregate safety of their full stack — peptides + drugs + lifestyle. Adding a medication the app knows interacts with their peptide drops Harmony. Logging resistance training while on GLP-1 boosts it.

#### How Interactions Surface In-App

```
Scenario: User is on semaglutide + BPC-157, reports intermittent fasting 16:8, no gym

Creature Harmony: 35% (RED)

Alerts:
⚠️ "You're fasting 16:8 while on semaglutide — high risk of muscle loss
    without resistance training. Harmony stat critical."
    [Learn more] → Academy: "GLP-1 + Exercise" lesson

ℹ️ "BPC-157 + semaglutide: No known direct conflict. Independent pathways."
    → Harmony neutral for this pair

📋 "Your full stack check: 2 peptides, 0 medications declared,
    2 lifestyle factors. Declare any medications for a complete picture."
    [Add medications]
```

```
Scenario: User adds "sertraline" to their medications while running BPC-157

Creature Harmony: drops from 70% → 50% (YELLOW)

Alert:
⚠️ "BPC-157 modulates dopamine. Sertraline affects serotonin. Theoretical
    risk of amplified anhedonia/emotional blunting. Monitor mood closely."
    [Learn more] → Academy: "Peptide-Drug Interactions" lesson

Side effect detector now adds to BPC-157 fingerprint:
  → ENHANCED watch for: anhedonia, emotional_blunting (elevated priority)
```

### Side Effect Fingerprints

Each compound ships with a "fingerprint" — the pattern of side effects the app watches for during daily check-ins:

```
BPC-157 fingerprint:
  watch_for: [anxiety, panic, anhedonia, insomnia, light_sensitivity, joint_pain_paradoxical]
  critical_alert: anxiety + anhedonia co-occurring → "Stop and consult provider"
  expected_onset_window: days 3-14
  persistence_risk: anhedonia may persist weeks after cessation

Retatrutide fingerprint:
  watch_for: [sleep_disruption, emotional_blunting, joint_pain, nausea, fatigue]
  critical_alert: sleep_disruption > 5 days consecutive → "Dose reduction recommended"
  expected_onset_window: weeks 2-8
  dose_dependent: true — stronger at >4mg/week

Semaglutide fingerprint:
  watch_for: [nausea, hair_loss, gastroparesis, muscle_loss, mood_changes]
  critical_alert: persistent_vomiting OR inability_to_eat → "Seek medical attention"
  expected_onset_window: weeks 1-4 (GI), months 2-6 (hair)
  dose_dependent: true — titrate slowly
```

### Lite Architecture

```
┌──────────────────────────────────────┐
│         Peptigotchi Lite App         │
│                                      │
│  ┌────────────┐  ┌────────────────┐  │
│  │ Creature   │  │ Reconstitution │  │
│  │ Engine     │  │ Calculator     │  │
│  │ (stats,    │  │ (pure math,    │  │
│  │  decay,    │  │  syringe viz)  │  │
│  │  evolution)│  │                │  │
│  └────────────┘  └────────────────┘  │
│                                      │
│  ┌────────────┐  ┌────────────────┐  │
│  │ Dose       │  │ Side Effect    │  │
│  │ Logger     │  │ Detector       │  │
│  │ (SQLite)   │  │ (fingerprint   │  │
│  │            │  │  matching)     │  │
│  └────────────┘  └────────────────┘  │
│                                      │
│  ┌────────────┐  ┌────────────────┐  │
│  │ Stack      │  │ Academy        │  │
│  │ Checker    │  │ (education     │  │
│  │ (12x12     │  │  content,      │  │
│  │  matrix)   │  │  unlocks)      │  │
│  └────────────┘  └────────────────┘  │
│                                      │
│  ┌──────────────────────────────────┐│
│  │  Static Knowledge Base (JSON)    ││
│  │  12 compounds × knowledge cards  ││
│  │  144-pair interaction matrix     ││
│  │  Side effect fingerprints        ││
│  │  Reconstitution defaults         ││
│  │  Regulatory status (cached)      ││
│  └──────────────────────────────────┘│
│                                      │
│  ┌──────────────────────────────────┐│
│  │  Online Extensions (when avail)  ││
│  │  • Claim investigator (MCP)      ││
│  │  • Regulatory push updates       ││
│  │  • Community protocol sharing    ││
│  │  • Knowledge base updates        ││
│  └──────────────────────────────────┘│
└──────────────────────────────────────┘
```

### Data Size Estimate

| Component | Size |
|-----------|------|
| 12 knowledge cards (JSON) | ~50 KB |
| Layer 1: Peptide × Peptide (144 pairs) | ~30 KB |
| Layer 2: Peptide × Drugs (~240 pairs) | ~60 KB |
| Layer 3: Peptide × Lifestyle (~120 pairs) | ~25 KB |
| 12 side effect fingerprints | ~15 KB |
| Education content (5 levels) | ~200 KB |
| Reconstitution reference data | ~5 KB |
| Regulatory status cache | ~3 KB |
| **Total static knowledge base** | **~388 KB** |

Still under 400KB — ships in any app bundle, updates via a single JSON download, caches indefinitely.
