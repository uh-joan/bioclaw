---
name: autoresearch
description: Use when optimizing an existing skill's accuracy by running it against test cases, scoring outputs, and iterating with one change per round until consistent quality. Triggers on skill optimization, prompt improvement, autoresearch loop, scoring checklist, skill accuracy, skill quality, iterative improvement.
---

# Autoresearch

Automated skill optimization loop. Run a skill against scored test cases, identify the weakest output, make one targeted change, re-score, keep or revert. Repeat until the skill hits target quality consistently.

**This is NOT for creating new skills** — use `writing-skills` for that. Autoresearch assumes a skill already exists and has measurable outputs you can score.

**REQUIRED BACKGROUND:** You MUST understand `writing-skills` (TDD cycle) and `dispatching-parallel-agents` (parallel subagent execution) before using this skill.

## When to Use

- Skill exists but produces inconsistent quality (some inputs great, others wrong)
- You have 5+ test cases with known-good expected outputs
- Quality is measurable (classification accuracy, checklist pass rate, structural completeness)
- You want systematic improvement, not guesswork

## When NOT to Use

- Skill doesn't exist yet — use `writing-skills` RED-GREEN-REFACTOR
- No measurable outputs (e.g., brainstorming skills — quality is subjective)
- Fewer than 5 test cases — too few to distinguish signal from noise
- Skill is a pure reference/API doc — nothing to optimize

## The Loop

```
┌─────────────────────────────────────────┐
│  1. BASELINE: Run skill on all cases    │
│     Score each output against checklist │
│                    ↓                    │
│  2. DIAGNOSE: Find lowest-scoring case  │
│     Identify the specific failure mode  │
│                    ↓                    │
│  3. CHANGE: Make ONE targeted edit to   │
│     the skill addressing that failure   │
│                    ↓                    │
│  4. RE-SCORE: Run ALL cases again       │
│     Compare to previous round           │
│                    ↓                    │
│  5. DECIDE: Score improved? → KEEP      │
│             Score same/worse? → REVERT  │
│                    ↓                    │
│  6. Target met 3x in a row? → DONE     │
│     Otherwise → back to step 2          │
└─────────────────────────────────────────┘
```

## Setup: Before Starting

### 1. Define Test Cases

Test cases are input-output pairs where you know the correct answer.

**File:** `autoresearch/eval-cases.json`

```json
[
  {
    "id": "descriptive-short-name",
    "input": "The prompt or task to give the agent",
    "expected": "The correct output or classification",
    "expected_details": { "key_criteria": ["list", "of", "required", "elements"] }
  }
]
```

**Requirements:**
- Minimum 5 cases, ideally 10+
- Cover the full output space (if skill classifies into 5 categories, include at least 1 per category)
- Include edge cases — the tricky inputs where the skill currently struggles
- Include easy cases — to catch regressions

### 2. Build Scoring Checklist

A scoring function that turns agent output into a number. Must be deterministic — same output always gets same score.

**File:** `autoresearch/scoring.md`

```markdown
## Scoring Checklist for [skill-name]

For each test case output, score these criteria (1 = yes, 0 = no):

1. **Correct primary output?** Does the main answer match expected?
   - Full match = 1.0, adjacent category = 0.5, wrong = 0
2. **Key criteria present?** Are all expected_details elements present?
   - Recall = (found / expected) — partial credit
3. **No hallucinated elements?** Nothing fabricated or unsupported?
   - Clean = 1.0, minor fabrication = 0.5, major = 0
4. **Follows skill workflow?** Report structure, section ordering correct?
   - Full compliance = 1.0, minor deviation = 0.5

Case score = average of criteria scores
Round score = average of all case scores
```

Adapt this template to your skill. 3-6 criteria is the sweet spot — fewer is too coarse, more creates noise.

### 3. Set Target

Pick a round score that means "good enough":
- **0.9** for most skills (allows 1 partial miss in 10 cases)
- **1.0** for safety-critical skills (variant classification, dosing)
- **0.8** if the skill is new and you're bootstrapping

Target must be hit **3 consecutive rounds** to declare victory — prevents lucky runs.

## Running the Loop

### Step 1: Baseline

Save the current skill as `autoresearch/logs/skill-round-0.md` (the original, untouched).

Run each test case through the skill. For each case:
1. Dispatch a subagent with the skill loaded and the test case input
2. Capture the full output
3. Score against checklist

Save results:

```json
// autoresearch/logs/round-0.json
{
  "round": 0,
  "score": 0.75,
  "results": [
    {
      "id": "case-name",
      "expected": "correct answer",
      "predicted": "agent's answer",
      "score": 0.5,
      "failure_mode": "over-classified: applied PM1 without hotspot evidence"
    }
  ],
  "timestamp": "ISO-8601"
}
```

### Step 2: Diagnose

Find the **lowest-scoring case**. Read the agent's full output for that case. Identify the **specific failure mode** — not "it was wrong" but *why* it was wrong.

Common failure modes:
- **Over-application**: Applied a criterion without sufficient evidence
- **Under-application**: Missed a criterion that had clear evidence
- **Wrong workflow**: Skipped a step, wrong order, incomplete report
- **Hallucination**: Fabricated evidence or citations
- **Misinterpretation**: Read the input correctly but drew wrong conclusion

Write one sentence: "The skill fails on [case] because [specific reason]."

### Step 3: One Change

Make **exactly one** edit to the skill that addresses the diagnosed failure mode.

**Good changes** (targeted, specific):
- Add a guardrail table with apply/don't-apply thresholds for a criterion
- Add a worked example showing the correct handling of the failure case type
- Tighten a vague instruction ("check population data" → "confirm AF < 0.0001 across ALL major gnomAD populations: NFE, AFR, EAS, SAS, AMR, ASJ")
- Add a pre-output verification checklist

**Bad changes** (broad, multiple):
- Rewrite the entire workflow section
- Add guardrails for 5 different criteria at once
- Change the skill's scope or description
- "General improvements"

Save the modified skill as `autoresearch/logs/skill-round-N.md`.

### Step 4: Re-Score

Run ALL test cases again with the modified skill. Score every case — not just the one you targeted.

**Critical:** Run all cases to catch regressions. A change that fixes case A but breaks case B is a net negative.

### Step 5: Keep or Revert

Compare round N score to round N-1:

| Outcome | Action |
|---------|--------|
| Round score improved | **KEEP** the change |
| Round score unchanged, target case improved, no regressions | **KEEP** — targeted improvement without cost |
| Round score unchanged, no improvement | **REVERT** — change didn't help |
| Round score decreased | **REVERT** — change caused regressions |
| Target case improved but other case regressed | **REVERT** — net negative |

Log the decision:

```json
// Append to round-N.json
{
  "change_description": "Added PM1 conservative threshold table",
  "change_target": "scn5a-vus case over-classification",
  "decision": "KEEP",
  "reason": "Target case improved 0.5 → 1.0, no regressions, round score 0.9 → 1.0"
}
```

**Reverted changes are valuable.** They tell you what doesn't work. Log them.

### Step 6: Check Termination

If round score >= target for 3 consecutive rounds: **DONE**.

Otherwise: go to Step 2 with the current best skill version.

**Hard stop at 10 rounds.** If you haven't hit the target in 10 rounds, the problem isn't the skill — it might be the test cases, the scoring, or the skill's scope.

## Output Artifacts

When the loop completes, you should have:

```
autoresearch/
  eval-cases.json           # Test cases (input)
  scoring.md                # Scoring checklist (input)
  logs/
    skill-round-0.md        # Original skill (baseline)
    round-0.json            # Baseline scores
    skill-round-1.md        # After change 1
    round-1.json            # Scores + change log
    ...
    skill-round-N.md        # Final version
    round-N.json            # Final scores
    _improved_skill.md      # Copy of best version (deploy this)
    changelog.md            # Summary of all changes
```

### Changelog Format

```markdown
# Autoresearch Changelog: [skill-name]

Baseline: 0.75 → Final: 1.0 (N rounds)

| Round | Score | Change | Target Case | Decision |
|-------|-------|--------|-------------|----------|
| 0 | 0.75 | — (baseline) | — | — |
| 1 | 0.90 | Added classification guardrails table | scn5a-vus | KEEP |
| 2 | 1.00 | Added compound het conservatism section | ryr1-compound-het | KEEP |

## Reverted Changes
| Round | Change | Why Reverted |
|-------|--------|--------------|
| (none in this run) | | |

## Patterns Observed
- [What types of changes consistently improved scores]
- [What types of changes consistently hurt or had no effect]
```

## Parallelizing Test Runs

For skills with 10+ test cases, dispatch subagents in parallel using `dispatching-parallel-agents`:

- Each subagent gets: the skill + one test case input
- Each subagent returns: the agent's output
- You score all outputs after collection

This cuts wall-clock time from O(N) to O(1) per round.

## Connecting to writing-skills TDD

Autoresearch and TDD are complementary:

| Concern | TDD (writing-skills) | Autoresearch |
|---------|---------------------|--------------|
| **When** | Creating new skill | Improving existing skill |
| **Tests** | Pressure scenarios (qualitative) | Scored test cases (quantitative) |
| **Failure signal** | Agent rationalizes/violates | Agent produces wrong output |
| **Fix** | Close rationalization loopholes | Tighten instructions for accuracy |
| **Termination** | Bulletproof under max pressure | Target score 3x in a row |

**Use both:** TDD to create the skill, autoresearch to optimize its accuracy once deployed.

## Common Mistakes

**Running only the target case after a change**
You must re-run ALL cases. Regressions are invisible otherwise.

**Making multiple changes per round**
If the score improves, you don't know which change helped. If it drops, you don't know which hurt. One change, one measurement.

**Scoring inconsistently between rounds**
The same output must always get the same score. If your scoring requires judgment, tighten the checklist criteria until it's mechanical.

**Optimizing past 10 rounds**
Diminishing returns. If 10 rounds can't reach the target, the bottleneck is elsewhere — revisit test cases, scoring criteria, or skill scope.

**Not logging reverted changes**
Reverted changes are data. They narrow the search space for future rounds. Always log what you tried and why it failed.
