# Personal Biomarker Dashboard Agent

A BioClaw skill that turns Oura Ring data into a **living biological model of you** — not just showing numbers, but interpreting them through the lens of your peptide protocol and suggesting what to change.

## The Core Loop

```
Every morning (scheduled task):

  1. PULL — Query Oura MCP for last 24h + rolling 30-day window
     ├── Sleep: stages, duration, efficiency, latency
     ├── HRV: overnight average, trend
     ├── Resting HR: overnight nadir
     ├── Readiness: recovery index, temperature deviation
     ├── SpO2: overnight average + dips
     └── Activity: steps, calories, training load

  2. BASELINE — Compare today vs your personal norms
     ├── 30-day rolling averages per metric
     ├── Day-of-week patterns (your Tuesday is different from your Saturday)
     ├── Standard deviation bands (is today's reading 1σ or 3σ off?)
     └── Trend direction over 7/14/30 days (improving, stable, declining)

  3. DETECT — Flag what's unusual FOR YOU
     ├── Acute anomalies: "HRV dropped 22ms overnight — 2.4σ below your baseline"
     ├── Drift: "Resting HR has trended up 3bpm over 14 days"
     ├── Pattern breaks: "Deep sleep dropped below 60min for 4 consecutive nights"
     └── Correlations: "Your HRV drops correlate with nights you train after 7pm"

  4. INTERPRET — Connect signals to mechanisms
     ├── Query PubMed: "What causes acute HRV drops + elevated resting HR?"
     ├── Cross-reference with known peptide mechanisms:
     │   "BPC-157 modulates vagal tone → HRV. Your HRV decline may indicate
     │    reduced vagal output. Consider: timing, dose, or stacking with Selank
     │    (GABAergic → parasympathetic support)"
     └── Factor in context you've told it:
         "You mentioned travel this week — circadian disruption explains
          the temperature deviation + sleep efficiency drop"

  5. SUGGEST — Protocol adjustments
     ├── "Move ipamorelin dose to 30min pre-sleep (your GH pulse timing
     │    is misaligned with your current sleep onset pattern)"
     ├── "Your deep sleep has been declining for 2 weeks. Consider adding
     │    magnesium glycinate or adjusting CJC-1295 frequency"
     ├── "Recovery metrics are strong — current protocol is working.
     │    No changes recommended."
     └── Always with confidence level + reasoning

  6. LOG — Store everything
     ├── Daily snapshot → append to personal time-series
     ├── Anomalies → flag for weekly review
     ├── Suggestions made → track whether you followed them
     └── Outcomes → did the metric improve after the change?
```

## What It Looks Like Day-to-Day

You wake up. Your phone buzzes (WhatsApp via BioClaw):

```
📊 Morning Brief — March 22

Sleep: 7h12m (▼18min vs baseline) | Efficiency: 88% (normal)
Deep: 52min (▼ below your 65min avg — 4th consecutive night)
HRV: 38ms (▼ from 47ms 14-day avg — 1.8σ)
RHR: 54bpm (▲ 3bpm trend over 10 days)
Readiness: 71 (▼ from 82 avg)

⚠️ Pattern detected: Deep sleep + HRV declining together for 4 days.
Your resting HR is trending up. This pattern typically indicates
accumulated sympathetic stress or insufficient recovery.

Given your current stack (CJC-1295/Ipa 5x/week, BPC-157 daily):
→ Consider dropping training intensity for 2-3 days
→ Your GHSR receptor may be downregulating from daily GHS dosing —
  try 3-on/2-off protocol this week and watch HRV response
→ If HRV doesn't recover by day 7, flag for deeper review

Confidence: Medium (based on 34 days of your data + literature)
```

## Intelligence Layers

Three layers that get smarter over time:

### Layer 1: Statistical (works from day 1)

Basic anomaly detection. Rolling averages, standard deviations, trend lines. No biology needed — just math on your Oura data.

- "This number is unusual for you"
- "This metric is trending in X direction"

### Layer 2: Mechanistic (needs MCPs)

Cross-references your patterns with biological mechanisms via PubMed, DrugBank, etc.

- "HRV decline + RHR increase together suggests sympathetic dominance"
- "BPC-157 upregulates NO via eNOS → vasodilation → normally supports HRV. If HRV is dropping despite BPC-157, consider: dose timing, NOS3 polymorphism (if you have genetic data), or competing stressor"

### Layer 3: Personal Model (learns over time)

After 60-90 days, the agent has enough data to build YOUR model:

- "Last time your HRV dropped like this, it recovered after you took 2 rest days and moved ipamorelin to pre-sleep"
- "Your deep sleep responds to CJC-1295 with a 48h lag — you see the benefit two nights later, not the same night"
- "You consistently sleep worse on days with >8,000 steps + evening training. Morning training doesn't show this pattern"

This layer is stored in the BioClaw group's CLAUDE.md — persistent memory across conversations.

## Architecture in BioClaw

```
┌─────────────────────────────────────────────────┐
│  Scheduled Task (daily, 6:30am)                 │
│  "Run biomarker dashboard for today"            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Container Agent                                │
│  ├── Oura MCP → pull last 24h + 30-day window   │
│  ├── Read groups/{user}/biomarker-history.csv    │
│  ├── Compute baselines + detect anomalies       │
│  ├── If anomaly detected:                       │
│  │   ├── PubMed MCP → mechanistic lookup        │
│  │   ├── DrugBank MCP → peptide interactions    │
│  │   └── ClinPGx MCP → if genetic data exists   │
│  ├── Generate morning brief                     │
│  ├── Append today's data to history CSV         │
│  └── Update CLAUDE.md with learned patterns     │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Router → WhatsApp (morning message)            │
└─────────────────────────────────────────────────┘
```

## Data Source: Oura MCP

Using [daveremy/oura-mcp](https://github.com/daveremy/oura-mcp) — CLI + MCP server for Oura API v2, designed for Claude Code.

### Available Oura Endpoints (30 sensors)

| Category | Metrics |
|----------|---------|
| **Sleep** | Total duration, REM/deep/light/awake minutes, efficiency %, latency, 5-min phase classification, bedtime window |
| **HRV** | Overnight HRV average, HRV balance contribution (1-100) |
| **Heart Rate** | Resting HR, daytime HR, overnight nadir |
| **Readiness** | Composite score, recovery index, temperature deviation, activity balance, sleep balance, sleep regularity |
| **Activity** | Steps, calories, training load, movement |
| **SpO2** | Overnight average, dip events |
| **Stress** | Stress score |
| **Workouts** | Duration, type, HR zones |

### Auth

OAuth2 (personal access tokens deprecated). Register app at Oura developer portal. Requires active Oura membership for Gen3/Ring 4.

## Biomarker History Storage

Simple append-only CSV in the group folder:

```csv
date,sleep_total_min,sleep_deep_min,sleep_rem_min,sleep_efficiency,hrv_avg,rhr,readiness,spo2,temp_deviation,steps,training_load
2026-03-20,432,65,89,0.91,47,51,82,97.2,0.1,7842,312
2026-03-21,420,58,84,0.89,43,52,78,97.0,0.3,9231,445
2026-03-22,414,52,81,0.88,38,54,71,96.8,0.5,8104,380
```

No database needed. CSV is readable by the agent, appendable via Bash, and version-controlled in git. At ~365 rows/year it never gets large.

## Anomaly Detection Logic

### Acute Anomalies (single-day)

```
For each metric:
  z_score = (today - rolling_30d_mean) / rolling_30d_std

  if |z_score| > 2.0: flag as anomaly
  if |z_score| > 3.0: flag as significant anomaly
```

### Drift Detection (multi-day trend)

```
For each metric:
  7d_avg vs 30d_avg

  if 7d_avg deviates >10% from 30d_avg in consistent direction:
    flag as drift

  Also: linear regression slope over 14 days
  if slope is statistically significant (p < 0.05):
    flag as trend
```

### Pattern Detection (correlations)

```
After 30+ days of data:
  Compute pairwise correlations between metrics
  Flag strong correlations (|r| > 0.6) that are actionable:
    - HRV × deep sleep
    - RHR × training load (lagged 1-2 days)
    - Sleep efficiency × step count
    - Temperature deviation × readiness (next day)
```

### Consecutive Pattern Breaks

```
For each metric:
  if metric < (mean - 1σ) for N consecutive days:
    flag as sustained deviation

  N thresholds:
    3 days: "worth watching"
    5 days: "pattern break — investigate"
    7 days: "sustained change — protocol review recommended"
```

## Mechanistic Interpretation Rules

When anomalies are detected, the agent cross-references with peptide mechanisms:

### HRV Decline

| Possible Cause | Peptide Connection | Suggested Action |
|---|---|---|
| Sympathetic overdrive | Selank (GABAergic → parasympathetic) | Add or increase Selank dose |
| Overtraining | CJC-1295/Ipa (recovery via GH) | Reduce training, maintain GH stack |
| Poor sleep quality | Ipamorelin timing | Move dose to 30min pre-sleep |
| Inflammation | BPC-157 (anti-inflammatory via NO) | Check if BPC-157 dose is adequate |
| Circadian disruption | Melatonin / light exposure | Non-peptide intervention first |

### Deep Sleep Decline

| Possible Cause | Peptide Connection | Suggested Action |
|---|---|---|
| GH axis downregulation | Daily GHSR stimulation | Switch to 5-on/2-off or 3-on/2-off |
| Cortisol dysregulation | Selank (anxiolytic) | Evening Selank dose |
| Late training | Catecholamine clearance (COMT) | Train before 5pm |
| Alcohol | Impairs GH pulse | Non-peptide intervention |

### Elevated Resting HR (trending)

| Possible Cause | Peptide Connection | Suggested Action |
|---|---|---|
| Accumulated fatigue | Recovery peptides (BPC-157, TB-500) | Deload week + maintain recovery stack |
| Dehydration | GLP-1 agonists reduce appetite → less fluid intake | Increase water, check electrolytes |
| Subclinical infection | Thymosin Alpha-1 (immune) | Monitor, consider TA1 if persists |

## Progressive Enhancement Path

### Month 1: Statistical Dashboard (MVP)

- Install Oura MCP
- Daily pull + CSV append
- Rolling stats + anomaly flags
- Plain-language morning brief via WhatsApp
- **No peptide interpretation yet** — just "your numbers are off"

### Month 2-3: Add Mechanistic Layer

- Connect anomalies to PubMed MCP lookups
- Add peptide mechanism cross-referencing
- User tells agent their current stack → agent stores in CLAUDE.md
- Suggestions become peptide-aware

### Month 4-6: Personal Model

- 90+ days of data → real personal baselines
- Agent identifies YOUR specific patterns:
  - "Your HRV recovers faster after rest days than after light training days"
  - "Your deep sleep peaks when you take ipamorelin before 9pm"
- Correlation analysis between protocol changes and metric shifts
- Weekly summary with trend analysis

### Month 6+: Add Genetic Layer (optional)

- User uploads 23andMe/AncestryDNA raw file
- Agent extracts relevant SNPs (from 116-marker panel)
- Interpretations become genotype-aware:
  - "Your CYP2C9*3 status means you metabolize semaglutide slowly — lower dose may be optimal"
  - "Your GHSR rs2948694 variant is associated with reduced GH response — higher ipamorelin dose may be needed"
  - "Your NOS3 Glu298Asp variant suggests reduced NO production — BPC-157 may be less effective for you via this pathway"

## Implementation Checklist

| Step | Task | Effort |
|------|------|--------|
| 1 | Install daveremy/oura-mcp into BioClaw container image | 1 hour |
| 2 | Set up Oura OAuth2 app + get credentials | 30 min |
| 3 | Write `biomarker-dashboard` container skill (baseline + anomaly detection) | 1 day |
| 4 | Create scheduled task: daily 6:30am, target main group | 30 min |
| 5 | Test with 7 days of data (manual baseline seeding) | 1 week |
| 6 | Add mechanistic interpretation layer (PubMed + DrugBank cross-ref) | 1 day |
| 7 | Add peptide protocol tracking (user declares stack in CLAUDE.md) | 2 hours |
| 8 | Add weekly summary + trend report | 4 hours |
| 9 | Add genetic data interpretation (optional, 23andMe raw file) | 2 days |
| 10 | Build toward n-of-1 protocol optimizer | Ongoing |

## What It Becomes

**Month 1**: Statistical dashboard. "Your numbers are off today."

**Month 3**: Mechanistic advisor. "Your numbers are off and here's why, based on your stack and the literature."

**Month 6**: Personal optimizer. "Based on 180 days of your data, here's exactly what works for your body and what doesn't. Your optimal protocol is X, and I have the data to prove it."

**Month 12+**: With genetic data, it's not guessing — it knows your CYP2C9 status, your GHSR variants, your NOS3 genotype, and can explain WHY you respond the way you do.

## Future: N-of-1 Protocol Optimizer

The natural evolution. Same autoresearch loop used on ct-predict (population-level trial prediction), applied to one person:

1. Agent proposes small protocol change (timing, dose, compound)
2. Tracks biomarker response over 1-2 week window
3. Keeps changes that improve target metrics
4. Reverts changes that don't
5. Over months, converges on YOUR optimal protocol

Same architecture. Different data source. N=1 instead of N=2,151.
