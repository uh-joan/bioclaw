# Wearable Integrations for Biomarker Dashboard Agent

**Chosen stack: Ultrahuman Ring Air + Dexcom G7 CGM**

- Ring = HRV, sleep stages, recovery, autonomic state (tracks GH-axis peptides, recovery peptides like BPC-157, ipamorelin, CJC-1295, Selank)
- CGM = real-time glucose dynamics (tracks GLP-1 agonists like semaglutide, tirzepatide, metabolic peptides)

---

## Smart Rings

| Device | API Access | MCP Exists? | Data | Notes |
|--------|-----------|-------------|------|-------|
| **Oura Ring** | OAuth2 REST API, 30 endpoints | Yes — [daveremy/oura-mcp](https://github.com/daveremy/oura-mcp) | Sleep stages, HRV, RHR, readiness, SpO2, temp, stress | Requires membership. Best documented API. |
| **Ultrahuman Ring Air** | Partner API + **UltraSignal** (raw PPG, accelerometer, temperature streams) | Yes — [Monasterolo21/Ultrahuman-MCP](https://github.com/Monasterolo21/Ultrahuman-MCP) | HR, HRV, sleep, steps, temp, SpO2 | UltraSignal gives raw sensor data — more powerful than Oura for custom analysis. US import issues due to Oura patent dispute. |

## Wrist Wearables

| Device | API Access | MCP Exists? | Data | Notes |
|--------|-----------|-------------|------|-------|
| **Whoop** | OAuth2 REST API, free with membership | Not yet (Python SDK `whoopy` exists) | Recovery, strain, HRV, sleep, HR zones | Strength: strain/recovery modeling. No screen. |
| **Garmin** | Official Health API + community Python wrapper [`garminconnect`](https://pypi.org/project/garminconnect/) | Not yet | HRV, sleep, stress, Body Battery, VO2max, SpO2, steps, HR | Richest data set. Body Battery is unique. Formal approval process for official API. |
| **Apple Watch** | No cloud API — data lives on-device only | Via [Open Wearables MCP](https://www.openwearables.io/) | HR, HRV, sleep, SpO2, ECG, blood oxygen, respiratory rate, wrist temp | Most sensors. No direct server-side access — needs mobile bridge. |
| **Fitbit** | OAuth2 Web API | Not yet | HR, HRV, sleep stages, SpO2, stress, activity | Google-owned. API mature but future uncertain. |
| **Samsung Galaxy Watch** | Samsung Health API | Not yet | HR, HRV, body composition (BIA), sleep, SpO2, blood pressure (some markets) | BIA body composition is unique. |
| **Polar** | Polar AccessLink API | Not yet | HR, HRV, sleep, training load, orthostatic test | Best HRV analysis. Used in sports science research. |

## Sleep-Specific

| Device | API Access | MCP Exists? | Data | Notes |
|--------|-----------|-------------|------|-------|
| **Eight Sleep Pod** | OAuth2 API | Yes — [8sleep-mcp](https://github.com/elizabethtrykin/8sleep-mcp) | HR, HRV, sleep stages, respiratory rate, bed temp, room temp | Actively controls sleep environment (temperature). Adjusts 3,200x/night. |

## CGMs (Continuous Glucose Monitors)

| Device | API Access | MCP Exists? | Data | Notes |
|--------|-----------|-------------|------|-------|
| **Dexcom G7** | FDA-cleared REST API, OAuth2 | Not yet ([Nightscout](https://github.com/nightscout/cgm-remote-monitor) is open-source) | Real-time glucose, glucose trend, events | Gold standard CGM. Limited Access = 5 users free. Full Access requires commercial review. |
| **Freestyle Libre** | No official API | Via Nightscout + LibreLinkUp hacks | Glucose readings every 15 min | Cheaper than Dexcom. Community workarounds. |
| **Ultrahuman M1 (CGM)** | Via Ultrahuman API | Via Ultrahuman MCP | Glucose + metabolic score | Bundled with Ring Air ecosystem. |

## Unified Aggregators

| Platform | What It Does | MCP? |
|----------|-------------|------|
| **[Open Wearables](https://www.openwearables.io/)** | Open-source, unifies Apple Health, Garmin, Polar, Suunto, Whoop. Has MCP server built in. | **Yes** |
| **[Terra API](https://tryterra.co/)** | Commercial, 99% device coverage. Unified JSON. HIPAA compliant. | Not yet |

---

## Chosen Stack: Ultrahuman Ring Air + Dexcom G7

### Why This Combo

| Signal | Device | Peptide Relevance |
|--------|--------|-------------------|
| HRV (overnight) | Ultrahuman | Recovery peptides (BPC-157, TB-500), GH secretagogues (CJC-1295/Ipa), anxiolytics (Selank) |
| Sleep stages (deep/REM) | Ultrahuman | GH-axis peptides (deep sleep = GH pulse), Selank/Semax (sleep quality) |
| Resting heart rate | Ultrahuman | Overall recovery, sympathetic/parasympathetic balance |
| SpO2 | Ultrahuman | Respiratory, mitochondrial function |
| Skin temperature | Ultrahuman | Inflammation, circadian rhythm, immune response |
| **Real-time glucose** | **Dexcom G7** | **GLP-1 agonists (semaglutide, tirzepatide), metabolic health, insulin sensitivity** |
| **Glucose variability** | **Dexcom G7** | **Glycemic response to meals, fasting, exercise — directly measures GLP-1 effect** |
| **Post-meal spikes** | **Dexcom G7** | **Tracks incretin pathway function in real-time** |

### Ultrahuman Advantage Over Oura

- **UltraSignal**: raw PPG, accelerometer, temperature streams — not just processed scores. Allows custom algorithm development.
- **No membership paywall** for API access (Oura requires active membership for Gen3/Ring 4 API access)
- **Integrated CGM ecosystem**: Ultrahuman also makes the M1 CGM, so their platform already thinks in ring + glucose terms

### Dexcom G7 Advantage

- FDA-cleared API — only CGM with official developer REST endpoints
- Real-time glucose readings (every 5 minutes)
- Glucose trend arrows (rising, falling, stable)
- Events (meals, exercise, insulin)
- 5 users free under Limited Access — perfect for personal use
- Nightscout open-source ecosystem as fallback

### What This Combo Uniquely Enables

The ring tracks **recovery and autonomic state**. The CGM tracks **metabolic state**. Together they create a much richer picture than either alone:

```
Morning Brief with Ring + CGM:

📊 Morning Brief — March 22

RECOVERY (Ultrahuman Ring):
  Sleep: 7h12m | Deep: 52min (▼ 4th night declining)
  HRV: 38ms (▼ from 47ms baseline — 1.8σ)
  RHR: 54bpm (▲ trending up 10 days)
  Readiness: Low

METABOLIC (Dexcom G7):
  Overnight glucose: 82 mg/dL avg (stable, normal)
  Glucose variability: 14% CV (▼ improved from 22% baseline)
  Time in range (70-140): 94% (▲ from 86% at protocol start)
  Post-dinner spike: 156 mg/dL → back to baseline in 48min
    (▼ faster than 72min avg — semaglutide is working)

⚠️ Recovery declining BUT metabolic improving.
  Your GLP-1 protocol is working (glucose metrics all improving).
  Recovery decline is likely training load, not metabolic.
  → Reduce training intensity, maintain semaglutide dose.
  → Consider 3-on/2-off for CJC-1295/Ipa to let GHSR recover.
```

### Implementation Plan

| Step | Task | Effort |
|------|------|--------|
| 1 | Install [Ultrahuman MCP](https://github.com/Monasterolo21/Ultrahuman-MCP) into container | 1 hour |
| 2 | Get Ultrahuman API credentials (Partner API key + user email) | 30 min |
| 3 | Build Dexcom MCP server (wrap their REST API — OAuth2, glucose endpoint, events endpoint) | 1 day |
| 4 | Register Dexcom developer app (Limited Access, 5 users free) | 30 min |
| 5 | Write `biomarker-dashboard` skill combining both data sources | 1-2 days |
| 6 | Create scheduled daily task (6:30am) | 30 min |
| 7 | Seed 7 days of data for initial baselines | 1 week |
| 8 | Add mechanistic interpretation layer | 1 day |
| 9 | Add peptide protocol tracking | 2 hours |

### Dexcom MCP Server (needs to be built)

The Dexcom API is straightforward REST:

```
Base URL: https://api.dexcom.com/v3

Endpoints:
  GET /users/self/egvs          → estimated glucose values
  GET /users/self/events        → user events (meals, exercise, insulin)
  GET /users/self/dataRange     → available data range
  GET /users/self/devices       → device info
  GET /users/self/alerts        → alert settings

Auth: OAuth2 (authorization code flow)
Rate limit: Generous for personal use
Data resolution: Every 5 minutes
```

An MCP server wrapping this would expose:
- `get_glucose_readings(start_date, end_date)` → array of {timestamp, value, trend}
- `get_glucose_stats(date)` → {avg, min, max, std, time_in_range, coefficient_of_variation}
- `get_events(start_date, end_date)` → meals, exercise, insulin events
- `get_overnight_glucose(date)` → overnight average, dawn effect detection

---

## The Other 20%: What Ring + CGM Can't See

Ring + CGM cover ~80% of the biomarker dashboard's needs (continuous autonomic + metabolic state). The remaining 20% falls into three buckets.

### 1. Blood Biomarkers — Periodic Deep Snapshots (10%)

Ring and CGM measure continuously but superficially — heart rhythm, glucose, skin temp. They can't see molecular-level changes:

| Biomarker | Why It Matters for Peptides | Frequency |
|-----------|---------------------------|-----------|
| **IGF-1** | Direct measure of whether CJC-1295/Ipamorelin is actually raising GH output | Every 4-8 weeks |
| **Testosterone / free T** | GH secretagogues affect the whole hormonal axis | Every 4-8 weeks |
| **Estradiol** | Aromatization — converting too much T→E2? | Every 4-8 weeks |
| **hsCRP** | Systemic inflammation — is BPC-157 actually reducing it? | Every 4-8 weeks |
| **Fasting insulin + HOMA-IR** | CGM shows glucose, but insulin resistance hides behind normal glucose for years. Semaglutide's real job is here. | Every 4-8 weeks |
| **Liver enzymes (ALT/AST)** | Peptide metabolism safety — stressing the liver? | Every 4-8 weeks |
| **Kidney (creatinine, BUN)** | Peptide clearance safety | Every 4-8 weeks |
| **Thyroid (TSH, fT3, fT4)** | GH axis interacts with thyroid. Some people crash T3 on GH secretagogues | Every 4-8 weeks |
| **Cortisol (AM)** | Stress axis — Selank/Semax modulate this. HRV is a proxy but cortisol is the direct measurement | Every 4-8 weeks |
| **Homocysteine** | Methylation status (MTHFR pathway) | Every 3-6 months |
| **Vitamin D (25-OH)** | Immune modulation, affects VDR pathway, interacts with BPC-157 response | Every 3-6 months |
| **Ferritin** | Iron status — affects mitochondrial function (the "power plant" from Linares' article) | Every 3-6 months |

**How to fill**: Services like InsideTracker, Marek Health, or direct lab orders (Quest/Labcorp). Build a `blood-panel` BioClaw skill that:
1. Reads lab PDF via existing PDF reader skill
2. Extracts values + reference ranges
3. Appends to `biomarker-history.csv` alongside ring/CGM data
4. Compares to YOUR previous results, not just population reference ranges

### 2. Subjective / Behavioral Data — The Human Layer (5%)

Wearables measure your body. They don't measure your mind or behavior:

| Data Point | Why It Matters | How to Capture |
|-----------|---------------|----------------|
| **Mood / energy** (1-10) | Selank, Semax, BPC-157 all have subjective effects | Daily WhatsApp check-in |
| **Libido** | PT-141, testosterone-modulating peptides | Weekly self-report |
| **Pain level** | BPC-157, TB-500 for injury recovery | Daily if relevant |
| **Brain fog / focus** | Semax, Selank — nootropic effects | Daily rating |
| **Training performance** | Lift more? Run faster? Recover quicker? | Manual or Strava integration |
| **Protocol adherence** | Did you take the peptide? What time? What dose? | Daily WhatsApp log |
| **Confounders** | Diet, alcohol, travel, stress, illness | Quick daily note |

**How to fill**: Daily evening WhatsApp check-in via scheduled task:

```
Agent (8pm): Quick check-in:
  Energy today (1-10)?
  Did you take all peptides as scheduled?
  Anything unusual? (travel, alcohol, stress, illness)

You: 7, yes, had 2 glasses of wine with dinner

Agent: Logged. Will factor wine into tomorrow's HRV interpretation.
```

Trivially implementable — scheduled task + CSV append. Low-frequency self-reported data that provides the context needed to interpret objective data correctly.

### 3. Body Composition / Physical Measurements (5%)

Neither ring nor CGM measures the physical changes peptides produce:

| Measurement | Why It Matters | Device | API? |
|------------|---------------|--------|------|
| **Body weight** | GLP-1 → weight loss. GH peptides → lean mass. | **Withings Body+** smart scale | Yes — Withings Health API (OAuth2) |
| **Body fat %** | More important than weight. Losing fat or muscle? | **Withings Body+** (BIA) or DEXA every 3-6mo | Yes |
| **Muscle mass** | CJC-1295/Ipa → muscle protein synthesis | **Withings Body+** (BIA) | Yes |
| **BMI** | Trending metric | **Withings Body+** | Yes |
| **Blood pressure** | Cardiovascular health | **Withings BPM Connect** | Yes — same Withings API |
| **Waist circumference** | Visceral fat proxy — semaglutide's biggest win | Manual, weekly | Self-report |
| **Photos** | Visual tracking (body comp, skin quality from GHK-Cu) | Monthly, stored in group folder | Manual |

#### Withings as the Third Device

Withings covers the body composition gap with one ecosystem:

- **Body+ scale**: weight, body fat %, muscle mass, water %, BMI — auto-syncs via WiFi
- **BPM Connect**: blood pressure + heart rate — auto-syncs
- **API**: OAuth2 REST API, well-documented, supports webhooks (push on new measurement)
- **MCP**: Community implementations exist for Home Assistant; straightforward to build a BioClaw MCP
- **No subscription required** for API access

A daily weigh-in + weekly BP reading fills most of the body comp gap automatically.

---

## Beyond the 80%: Full Data Audit

Ring + CGM covers continuous autonomic + metabolic state. Here's everything else that would meaningfully improve protocol decisions, vs noise we can skip.

### Actually Useful — Would Change Protocol Decisions

#### Nutrition / Meal Logging

The biggest blind spot. CGM shows glucose *response*, but without knowing input, the agent can't distinguish:
- "Glucose spiked because you ate pizza" vs "glucose spiked on the same meal as last week — semaglutide losing efficacy"
- Protein intake directly affects GH secretagogue response (amino acid availability)
- Caloric deficit/surplus changes how recovery peptides perform

**How**: Meal photos via WhatsApp → agent uses image vision skill (already have it) for estimation. Or integrate MyFitnessPal/Cronometer (both have APIs). Photo-based is lower friction.

#### Hydration

Dehydration confounds almost everything — HRV drops, glucose variability increases, recovery tanks. GLP-1 agonists suppress appetite → less fluid intake. Silent confounder.

**How**: **HidrateSpark smart water bottle** — Bluetooth, tracks intake automatically, syncs to app. Has a basic API via Apple Health/Google Fit bridge. Or self-report in evening check-in ("glasses of water today?"). Smart bottle is better because it's passive — no remembering to log.

#### Menstrual Cycle (if applicable)

Hormonal cycling massively affects HRV, sleep, glucose, body temperature, and peptide response. Without tracking cycle phase, the agent flags "anomalies" that are just luteal phase. Makes the entire dashboard useless for half the population without it.

**How**: Ultrahuman already estimates cycle phase from temperature shifts. Or manual tracking. Or Natural Cycles app (has API).

#### Training Load (quantified)

Ring captures general activity but not structured training. "Heavy squats yesterday" vs "8,000 steps" matters enormously for interpreting next-day HRV.

**How**: Strava or TrainingPeaks API. Both OAuth2. Adds: exercise type, duration, intensity, HR zones, perceived effort.

#### Cortisol (continuous)

HRV is a *proxy* for stress. Cortisol is the actual signal. AM blood cortisol in the blood panel catches it periodically, but misses daily rhythm:
- Morning spike (cortisol awakening response) — should be high
- Evening — should be low
- Flat curve = burnout, peptides won't fix it

**How**: Not practical for continuous measurement yet. Cortisol wearables are coming (Epicore Biosystems, future Apple Watch rumors) but nothing shippable today. Best proxy: ring stress score + subjective check-in.

### Nice-to-Have — Adds Context, Rarely Changes Decisions

| Data Source | What It Adds | How | Worth It? |
|------------|-------------|-----|-----------|
| **Air quality** (PM2.5, CO2) | Affects sleep, inflammation | Awair, PurpleAir smart monitors | Only if chronic exposure |
| **Light exposure** | Circadian rhythm → melatonin → sleep → GH pulse timing | Ultrahuman has some ambient sensing | Hard to measure well |
| **Ambient temp / humidity** | Sleep quality | Eight Sleep covers this | Only with Eight Sleep |
| **Microbiome** | Gut composition affects peptide absorption, GLP-1 sensitivity, inflammation | Viome, Ombre stool tests every 3-6mo | Slow-moving, no API |

### Not Worth Adding

| Data Source | Why Skip |
|------------|----------|
| **Continuous EEG** (Muse headband) | Too noisy, too much friction, marginal signal for peptide decisions |
| **Continuous blood pressure** | Doesn't exist reliably. Withings spot-checks are enough. |
| **Sweat composition** (Gatorade Gx) | Gimmick. Not actionable. |
| **Posture / movement quality** | Interesting, won't change peptide protocols |
| **Extra pulse ox** | Ring already does this overnight |
| **Genetic methylation panels** (beyond PGx) | Too slow-moving to affect protocol decisions |

---

## Complete Data Architecture

```
CONTINUOUS — automatic, every day (80%)
├── Ultrahuman Ring: HRV, sleep stages, RHR, SpO2, temp, recovery
└── Dexcom G7: glucose (5-min), variability, meal response, trends

DAILY AUTO — on measurement (7%)
├── Withings Body+: weight, body fat %, muscle mass, water %
├── Withings BPM Connect: blood pressure, resting HR
└── HidrateSpark: water intake (oz/mL per day)

DAILY SUBJECTIVE — evening WhatsApp check-in (5%)
├── Energy / mood / focus / pain (1-10 scales)
├── Protocol adherence (took peptides? timing? dose?)
├── Confounders (alcohol, travel, stress, illness)
├── Meal photos (agent estimates macros via image vision)
└── Cycle phase (if applicable)

PERIODIC — every 4-8 weeks (8%)
├── Blood panel PDF → agent reads + extracts values
├── IGF-1, testosterone, hsCRP, fasting insulin, liver/kidney, thyroid, cortisol
└── Compare to YOUR previous results, not population ranges

RARE — every 3-6 months
├── DEXA scan (gold standard body comp)
├── Homocysteine, vitamin D, ferritin, full metabolic panel
├── Microbiome test (Viome/Ombre)
└── Biological age test (epigenetic clock)

ONE-TIME
└── Genetic data (23andMe raw file → 116 PGx markers)
```

### Morning Brief with Full Stack

```
📊 Morning Brief — March 23

RECOVERY (Ultrahuman Ring):
  Sleep: 7h12m | Deep: 52min (▼ 4th night declining)
  HRV: 38ms (▼ from 47ms baseline — 1.8σ)
  RHR: 54bpm (▲ trending up 10 days)

METABOLIC (Dexcom G7):
  Overnight glucose: 82 mg/dL avg (stable)
  Time in range: 94% (▲ from 86% at protocol start)
  Post-dinner spike: 156→baseline in 48min (▼ improving)

BODY COMP (Withings):
  Weight: 81.2kg (▼ 0.4kg this week)
  Body fat: 18.1% (▼ from 19.3% at protocol start)
  BP: 118/74 (normal, stable)

HYDRATION (HidrateSpark):
  Yesterday: 2.1L (▼ below 2.8L target — 3rd day under target)

SUBJECTIVE (last night's check-in):
  Energy: 7/10 | Focus: 6/10
  Protocol: all taken on schedule
  Meals: [photo] → ~2,400 kcal, 140g protein, moderate carb
  Note: 2 glasses of wine with dinner

BLOOD PANEL (last draw: March 8):
  IGF-1: 287 ng/mL (▲ from 203 baseline — CJC/Ipa working)
  hsCRP: 0.4 mg/L (▼ from 1.8 — BPC-157 reducing inflammation)
  Fasting insulin: 4.2 μIU/mL (▼ from 8.1 — semaglutide working)

⚠️ Recovery declining despite metabolic + body comp improving.
  Wine + 3 days of low hydration likely contributing to HRV drop.
  Deep sleep trend is the real concern — 4th consecutive night below avg.
  → Increase water intake to 3L+ today (semaglutide suppresses thirst)
  → Try moving ipamorelin to 30min pre-sleep this week
  → Monitor deep sleep response over next 3 nights
```

---

## Implementation Priority

| Phase | Devices / Sources | Effort | Coverage |
|-------|-------------------|--------|----------|
| **Phase 1** | Ultrahuman Ring + Dexcom G7 | 2-3 days | 80% (continuous autonomic + metabolic) |
| **Phase 2** | Withings scale + BP cuff | 1 day | 87% (add body composition) |
| **Phase 3** | Evening WhatsApp check-in + meal photos | 2 hours | 92% (add subjective + nutrition) |
| **Phase 4** | HidrateSpark smart water bottle | 2 hours | 94% (add hydration tracking) |
| **Phase 5** | Blood panel PDF reader | 1 day | 100% (add molecular-level snapshots) |

### Future Additions

Once the core stack is solid:

| Addition | What It Adds | Effort |
|----------|-------------|--------|
| Eight Sleep MCP | Active sleep environment control + independent HR/HRV source | 1 hour (MCP exists) |
| Open Wearables MCP | Apple Watch, Garmin, Polar as additional signal sources | 1 hour (MCP exists) |
| Genetic data (23andMe) | Pharmacogenomics overlay — explain WHY you respond the way you do | 2 days |
| Strava / TrainingPeaks | Training load quantification — remove exercise as a confounder | 1 day |
| Continuous cortisol | Direct stress measurement (when wearable cortisol sensors ship) | TBD |
