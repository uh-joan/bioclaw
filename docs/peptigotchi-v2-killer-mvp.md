# Peptigotchi v2 — The Killer MVP

## The Fundamental Rethink

v1 designed an **app with a creature on top.** That's backwards.

The killer insight: **Peptigotchi is not an app. It's an AI companion that lives in your chat.**

No app store. No download. No creature animations to build. No medical device classification. The Peptigotchi IS a NanoClaw agent — a Claude-powered personality with a knowledge base, memory, and a visual avatar that shows up in your WhatsApp or Telegram. It messages you. It remembers you. It worries about you.

This solves nearly every problem from the v1 critique in one architectural move.

---

## Why Chat-First Kills the App Approach

| v1 Problem | Chat-First Solution |
|-----------|-------------------|
| Logging fatigue (forms suck) | You just talk to it: "took 250mcg BPC left delt" |
| Education gated behind streaks | Ask anything, anytime: "how do I read a COA?" |
| Creature feels like a dashboard | It's an AI personality — it talks back, asks questions, has moods |
| Dual audience (newbie vs power user) | Conversation adapts tone automatically |
| Privacy is existential | Runs on YOUR NanoClaw instance, data stays on YOUR machine |
| Regulatory risk (medical device) | It's a chatbot that does math and remembers things. Not an app with "dosing recommendations" |
| No app to build | Already have the infrastructure (NanoClaw + containers) |
| Cosmetics without social | The creature avatar is an image sent in chat — share the screenshot if you want |
| Competitor Pep has feature head start | Pep is a tracking app. This is a relationship. Different category entirely |

---

## The Creature is a Personality, Not a Sprite

### Character Design

Your Peptigotchi has a **voice,** not just stats. It develops personality traits based on your behavior:

**Base personality:** Curious, slightly worried, knowledgeable but honest about uncertainty. Think: a nerdy lab partner who genuinely cares about you but will never pretend to know something they don't.

**Adaptive traits** (emerge over time from your protocol):

| Your Behavior | Creature Develops | Example |
|--------------|------------------|---------|
| Healing peptides (BPC/TB-500) | Nurturing, recovery-focused | "Rest day today? Good. Healing isn't just chemistry — it's sleep and patience too." |
| Weight loss (GLP-1s) | Encouraging, body-positive | "Down another kilo this week. How are your energy levels feeling? That matters more than the number." |
| Nootropics (Semax/Selank) | Analytical, curious | "Day 14 on Semax. Have you noticed any difference in focus duration, or is it more clarity? I'm curious about your specific experience." |
| Multi-compound stacker | Cautious, organized | "That's compound #4. I want to be honest — I have zero interaction data for this specific combination. Let's be extra careful with check-ins this week." |
| Consistent logger | Warm, trusting | "12 days straight. I know you well enough now to notice — you always feel best on mornings after your evening BPC dose." |
| Inconsistent logger | Gently persistent, not guilty | "Hey, haven't heard from you in a bit. No pressure — just checking you're doing okay. Whenever you're ready." |

### The Visual

The creature avatar is a **single image** sent in the chat each morning (or when state changes). Not an animation — a generated or pre-rendered image that reflects:

1. **Species** — determined by your primary peptide category at setup
   - Healing → a regenerative creature (think: axolotl-like — the animal that literally regrows limbs)
   - Metabolic (GLP-1) → a phoenix-like creature (transformation/rebirth)
   - GH/Recovery → a bear-like creature (strength, hibernation, cycles)
   - Nootropic → an octopus-like creature (neural, curious, multi-armed)
   - Multi-stack → a chimera (elements from multiple species)

2. **Evolution stage** — visual maturity grows with your experience
   - Not linear. **Branching.** Your creature at day 90 looks different from everyone else's because it evolved based on YOUR specific journey.

3. **Mood** — subtle visual cues
   - Happy: bright colors, eyes open
   - Worried: muted colors, looking sideways
   - Sick: visible distress (but never dead — always recoverable)
   - Curious: head tilted, question mark

4. **Format** — pixel art. Low resolution, high charm. Cheap to produce, easy to generate variants, fits chat context. Think: early Pokémon sprite energy.

### Why This Works Better Than Stats

Instead of:
```
PURITY ████████░░ 80%
PRECISION ██████████ 100%
STABILITY ██████░░░░ 60%
```

You get:
```
[Image: Your axolotl-creature looking slightly worried, muted colors]

"Morning! I noticed you logged insomnia again last night — that's
3 out of the last 5 days. Your BPC-157 fingerprint says this is
common in days 3-10. You're on day 8.

Two possibilities: it might ease up in the next few days as your
body adjusts, or it might be telling you the dose is too high.

How bad was it last night? Scale of 1-5?"
```

The stats still exist under the hood. But the user sees a personality, not a dashboard.

---

## The Daily Loop (Reimagined)

### v1 Loop (Form-Fill)
```
1. Open app
2. Navigate to dose log
3. Select peptide from list
4. Enter amount
5. Select injection site from body map
6. Save
7. Navigate to side effect screen
8. Scroll through symptom checklist
9. Rate severity
10. Save
→ 2-3 minutes of clicking. Feels like work.
```

### v2 Loop (Conversation)

**Morning (creature initiates):**
```
Peptigotchi: [creature image - bright, curious]
"Day 8! Quick check-in — did you take your BPC this morning?"

You: "yeah 250 left delt"

Peptigotchi: "Logged ✓ BPC-157 250mcg SubQ left deltoid.
How's the sleep been? You mentioned some trouble a couple days ago."

You: "better actually, slept through last night"

Peptigotchi: "Oh nice! That lines up — BPC insomnia often settles
around day 7-10. I'll keep watching but that's a good sign. 🔬

Your vial was reconstituted 18 days ago btw — 10 days left on it."
```

**Total time: 30 seconds of typing what you'd tell a friend anyway.**

**When something comes up (you initiate):**
```
You: "thinking of adding TB-500 to my BPC protocol"

Peptigotchi: [creature image - head tilted, thinking]
"TB-500 is the most common thing people stack with BPC-157,
so you're not alone there. Here's what I know:

✅ Both target healing — BPC for local, TB-500 for systemic
⚠️ Both promote angiogenesis. In animal studies, that's fine.
   In theory, if you have any dormant tumors, double
   angiogenesis isn't ideal. No human data either way.
❓ There's zero formal interaction data for this combination.

The Reddit community is split — some people swear by it for
tendon recovery, others report paradoxical joint pain when
combining them.

What are you trying to heal? That might help me give you
more specific context."
```

**When you need math (you initiate):**
```
You: "got a 5mg vial of TB-500, how much water and what do I draw for 2.5mg"

Peptigotchi: "Here's the math:

💉 Add 1mL bacteriostatic water to your 5mg vial
   → Concentration: 5mg/mL (5000mcg/mL)
   → For 2.5mg: draw to 50 units on a 1mL syringe

   [Visual: syringe diagram showing 50-unit mark]

   Store refrigerated. I'll start a 28-day countdown on this vial.
   Want me to remind you when it's getting close to expiry?"
```

### Why Conversation Beats Forms

| Aspect | Forms | Conversation |
|--------|-------|-------------|
| Friction | High — navigate, tap, select, confirm | Low — type naturally |
| Context | None — each entry is isolated | Full — creature remembers everything |
| Attribution | Can't ask follow-up questions | "Was the insomnia before or after your evening dose?" |
| Education | Locked behind menus/levels | Woven into the conversation naturally |
| Emotional connection | Zero | Real — you're talking to something that remembers you |
| Error detection | None — user enters whatever | "250mcg? Last time you said 500. Did you cut your dose?" |

---

## Solving the 5 Hardest Problems

### Problem 1: Creature Needs to Feel Alive

**Solution: It IS alive — it's a Claude agent with persistent memory.**

The Peptigotchi has:
- A `CLAUDE.md` file in `groups/{user}/` with its personality, your protocol history, creature state, and evolving traits
- Persistent conversation memory via NanoClaw's session system
- A "mood engine" — simple rules that determine its emotional state from your recent interactions, not just stats

**Mood engine (runs before each response):**
```
if days_since_last_checkin > 3: mood = "worried"
elif user_reported_critical_symptom: mood = "alarmed"
elif streak > 7 AND no_red_flags: mood = "happy"
elif user_asked_learning_question: mood = "excited"
elif vial_expiring_soon: mood = "concerned"
else: mood = "neutral_curious"
```

The creature's image and tone shift based on mood. Not random — reactive to your actual situation. But with enough variation that it doesn't feel mechanical.

**Surprise moments** (the unpredictability that made Tamagotchis work):
- "I was reading about your peptide overnight and found something interesting..." (proactive knowledge sharing)
- "You know what's cool? You've injected more precisely than 80% of users this week" (rare stat drops)
- "It's been exactly 30 days since you started. Want to look back at how your check-ins have changed?" (milestone reflection)
- Occasional creature "questions" that aren't about your protocol: "Random thought — do you think peptides will be mainstream in 5 years? I'm curious what you think" (builds relationship)

### Problem 2: Interaction Data is Mostly "We Don't Know"

**Solution: Honesty as the feature. Make "no data" the educational moment, not a failure.**

Replace the 4-tier evidence system with a **traffic light that's actually useful:**

```
🟢 GREEN — "We know this"
   Human clinical data exists. Confidence is reasonable.
   Example: Semaglutide weight loss efficacy (Phase 3 RCTs)
   Example: Semaglutide + tirzepatide = same receptor, don't combine

🟡 YELLOW — "We have clues"
   Animal data, pharmacological reasoning, or strong community signal.
   Example: BPC-157 tendon healing (50+ animal studies, 0 human RCTs)
   Example: BPC-157 + anticoagulants (animal data on platelet aggregation)

🔴 RED — "Nobody knows. You are the experiment."
   No data. Not even theoretical. You're in uncharted territory.
   Example: BPC-157 + Retatrutide (no study, no mechanism overlap analysis)
   Example: Tesamorelin + Selank + TB-500 (3-compound stack, zero data)
```

**The key difference from v1:** Red doesn't mean "avoid." It means "log carefully, you're generating the first data point." This reframes the user from "doing something dangerous" to "contributing to knowledge." Same behavior, different emotional valence.

**In conversation:**
```
You: "I'm running BPC-157, TB-500, CJC-1295, and ipamorelin. Safe?"

Peptigotchi: "Let me check all 6 pairwise interactions:

🟢 CJC-1295 + Ipamorelin — standard GH stack, well-characterized
🟡 BPC-157 + TB-500 — most common healing stack, animal data
   suggests synergy but also amplified angiogenesis
🔴 BPC-157 + CJC-1295 — nobody has studied this. Zero data.
🔴 BPC-157 + Ipamorelin — same. Zero.
🔴 TB-500 + CJC-1295 — same. Zero.
🔴 TB-500 + Ipamorelin — same. Zero.

Honest picture: 1 green, 1 yellow, 4 red. That's a lot of
unknowns for 4 compounds. It doesn't mean it's dangerous —
it means nobody knows, and your experience IS the data.

I'll be extra attentive to your check-ins for the next 2 weeks.
Deal?"
```

**Over time, the knowledge base grows:** If 200 users run BPC-157 + CJC-1295 and log outcomes, that red light can shift to yellow. The app learns from its own user base. The static JSON becomes a living dataset.

### Problem 3: Dual Audience (Newbie vs Power User)

**Solution: The creature grows up with you. Same creature, different relationship.**

The conversation adapts, not because of a setting, but because the creature **remembers your experience level:**

**Week 1 (Newbie):**
```
Peptigotchi: "Quick question — have you done a practice
reconstitution yet? Some people find it helps to do a 'dry run'
with just water before they use the real thing. No pressure either
way, just something that's helped other newbies feel more confident."
```

**Month 3 (Intermediate):**
```
Peptigotchi: "Your BPC-157 insomnia pattern is interesting.
You reported it on the first cycle (days 5-9) but not the second.
Could be dose-related — you dropped from 500 to 250mcg. Want me
to map the correlation?"
```

**Month 6+ (Power User):**
```
Peptigotchi: "New PubMed preprint on TB-500 and tendon collagen
cross-linking in a rat model. It's relevant to your protocol.
Want the summary or the full citation?"
```

**The key insight: you don't pick "newbie mode" or "expert mode."** The creature just pays attention to what you know. If you use technical language, it matches. If you ask basic questions, it explains simply. Claude already does this naturally — the personality layer just amplifies it.

### Problem 4: Privacy is Existential

**Solution: Local-first by architecture, not by policy.**

Peptigotchi runs on YOUR NanoClaw instance. This means:

- **Your data lives on your machine.** Not in a cloud. Not in an app backend. On your laptop/server.
- **WhatsApp messages are E2E encrypted.** The creature talks to you through an encrypted channel.
- **The container is ephemeral.** The agent runs in an isolated Linux container, processes your message, and exits. No persistent cloud connection.
- **No account.** No email. No phone number linked to a profile. The creature knows you by your chat ID.
- **Nothing to subpoena.** There's no company hosting your data. It's on your hardware.

**For community features (later):** Differential privacy. Users opt-in to share aggregate stats, never raw data. "X users reported Y" is computed locally and only the count is shared — never individual protocols, doses, or symptoms.

**The disclaimer becomes a feature, not a liability:**
```
Peptigotchi: "Just so you know — everything we talk about stays on
your machine. I don't phone home. I don't have a cloud account.
If you uninstall NanoClaw, I disappear completely. Your protocol
history, our conversations, all of it — gone.

That's by design. What you inject is your business."
```

### Problem 5: Regulatory Risk

**Solution: Frame it right. It's an educational companion, not a medical device.**

What the Peptigotchi does vs how it's classified:

| Feature | What It Actually Does | Classification |
|---------|---------------------|---------------|
| Reconstitution calculator | Math: mg ÷ mL = concentration | Calculator (not regulated) |
| Side effect logging | Journaling with pattern display | Wellness app (not SaMD) |
| Interaction data | Displays published literature findings | Educational reference (not regulated) |
| "Consult provider" escalation | Information, not diagnosis | Appropriate — all health apps do this |
| Creature avatar | Entertainment/engagement | Game element (not regulated) |

**Key framing choices:**
- Never says "you should take X" or "reduce your dose to Y" — only surfaces information
- Never says "you have X condition" — only says "this pattern is consistent with what others have reported"
- Side effect fingerprints are described as "community patterns" not "diagnostic criteria"
- The creature is an educational companion — it shares knowledge, it doesn't prescribe
- All interaction data shows evidence level (🟢🟡🔴) — user always sees the uncertainty

**What we explicitly DON'T do:**
- No "recommended dose" — only "common dose ranges reported in literature/community"
- No "stop taking this" — only "this pattern concerns me, consider talking to someone"
- No automated alerts that could be interpreted as clinical decision support
- No diagnostic language anywhere

---

## Solving the Other Problems

### Problem: Side Effect Attribution in Multi-Compound Stacks

v1 just pattern-matched to the first fingerprint. v2 does something better — **the creature asks follow-up questions.**

```
You: "been having trouble sleeping"

Peptigotchi: "Hmm. You're running BPC-157 (day 8) and CJC-1295
(day 22). Both could contribute to sleep issues but differently:

BPC-157: insomnia onset typically days 3-10 (you're in window)
CJC-1295: best taken before bed for GH pulse, but can cause
vivid dreams/restless sleep

Quick question — is it trouble falling asleep, or waking up
in the middle of the night?"

You: "waking up around 3am"

Peptigotchi: "3am waking is more consistent with GH-related sleep
disruption than BPC-157 insomnia (which is usually onset delay).
When do you take your CJC — right before bed?

Some people find moving it to 30-60 min before bed instead of
right at bedtime helps. Worth trying for a few days to see if
the 3am thing settles."
```

**Conversation enables differential diagnosis that forms can't.** The creature narrows down the cause by asking smart questions — because it has context (your full protocol, timing, history) and can follow up.

### Problem: Purity Stat is Dishonest

**Solution: Kill the Purity stat. Replace with Source Awareness.**

Don't pretend the user can verify purity. Instead, the creature tracks and surfaces source information honestly:

```
You: "got my new vial of BPC from [vendor]"

Peptigotchi: "Logged. A few things I want you to know about
sourcing in general:

• I can't verify what's in your vial. Nobody can without
  lab testing.
• If the vendor provided a COA, it might be real or it
  might be a PDF they made in 10 minutes. There's no way
  to know from the document alone.
• What you CAN watch for: if this vial feels different
  from your last one (reconstitution behavior, clarity,
  side effect profile changes), that's a signal.

I'll ask you about this when you start using it. Sound good?"
```

**Honest > reassuring.** The creature doesn't give you a green checkbox for "verified" — it educates you about the limits of verification and then watches for changes.

### Problem: Logging Fatigue

**Solution: Passive logging + proactive creature.**

The creature checks in with you — you don't have to remember to log:

```
[Morning — creature initiates]
Peptigotchi: "Morning! BPC day? Quick reply with your dose
and I'll handle the rest 💉"

You: "250"

Peptigotchi: "250mcg BPC-157 ✓. Same delt as yesterday or
rotating?"

You: "right glute today"

Peptigotchi: "Got it. Right glute. Good rotation — you haven't
hit that site in 6 days. ✓✓✓"
```

**If you don't reply, the creature doesn't punish you:**
```
[No reply by 2pm]
Peptigotchi: "Hey — no worries if you're busy. Skipping a day
isn't the end of the world. Just ping me whenever 👋"
```

**No guilt. No stat decay. No dying creature.** The creature understands that real life happens. If you disappear for a week, it's warm when you come back:

```
[After 5 days of silence]
Peptigotchi: "There you are! Hope everything's okay. Whenever
you want to pick back up, I'm here. No judgment, no catch-up
homework. We just start from today."
```

This is the opposite of Tamagotchi's death mechanic — and it's better for retention. Guilt drives uninstalls. Grace drives return visits.

### Problem: Community Data Assumes Scale

**Solution: Don't launch community features. They're not in the MVP.**

The MVP is a solo experience. The creature + you. Period. Community features (anonymous protocol sharing, vendor reputation, aggregate stats) launch when you have 500+ daily active users, not before.

**What the creature says when asked about community data:**
```
You: "how many people are running BPC + TB-500?"

Peptigotchi: "I don't have community data yet — it's just us
for now. What I can tell you is that BPC-157 + TB-500 is the
most commonly discussed combination on r/Peptides by a wide
margin. The Reddit signal is strong.

When I have enough users to share anonymous aggregate stats,
I'll let you know. For now, you're helping me build that dataset
just by logging."
```

### Problem: No Monetization Model

**Solution: Three tiers.**

| Tier | Price | What You Get |
|------|-------|-------------|
| **Free** | $0 | Self-hosted NanoClaw Peptigotchi agent. You run it yourself. Full features, your hardware, your costs (Claude API). Open source. |
| **Hosted** | $9/mo | We run NanoClaw for you. Same agent, same privacy (encrypted), no setup. Just connect your WhatsApp/Telegram and go. |
| **Pro** | $19/mo | Hosted + claim investigator (MCP server access to PubMed/DrugBank/etc), knowledge base auto-updates, priority support. |

**Why this works:**
- Free tier builds community and trust (critical for gray-market audience that distrusts platforms)
- Hosted tier captures the 90% who won't self-host
- Pro tier funds the MCP server infrastructure
- No ads, no data selling, no affiliate links — clean revenue from direct value

---

## The Killer MVP

### What to Build (Scope)

One NanoClaw container skill. One CLAUDE.md personality template. One knowledge base JSON. That's it.

| Component | What It Is | Effort |
|-----------|-----------|--------|
| **Peptigotchi skill** | Container skill (`container/skills/peptigotchi/SKILL.md`) that defines the creature's personality, behavior rules, and conversation patterns | Medium — it's a prompt + rules |
| **Knowledge base** | Static JSON with 12 compound cards + 3-layer interaction model (~388KB) | Medium — research + curation |
| **Creature avatar set** | ~20 pixel art images covering 4 species × 5 evolution stages. Sent as images in chat | Low — can be AI-generated or commissioned cheaply |
| **Protocol memory** | Schema for `groups/{user}/CLAUDE.md` storing protocol state, creature state, conversation history, check-in logs | Low — it's a structured markdown file |
| **Reconstitution calculator** | Math function the creature calls inline. Already trivial | Very low |
| **Vial tracking** | Expiry countdown stored in protocol memory, creature checks on each interaction | Very low |

### What NOT to Build (Descoped from v1)

| Feature | Why Cut | When to Add |
|---------|---------|------------|
| Mobile app | Chat IS the app | When you have 1000+ users asking for it |
| Community data sharing | Empty room problem | When 500+ DAU |
| Vendor reputation | Legal minefield | Maybe never (or v3+) |
| Academy with gated levels | Education should be on-demand | Restructure as "lessons the creature can teach when asked" |
| Stat decay / creature death | Guilt drives uninstalls, not engagement | Never — replace with grace |
| Purity stat | Dishonest — user can't verify purity | Replace with source awareness (honest) |
| Cosmetics/hats/badges | No social loop to drive them | When there's a community to show off to |
| Claim investigator | Requires MCP servers, online-only | Pro tier feature (month 2+) |

### MVP User Journey

**Day 0: Setup**
```
[User connects to Peptigotchi on WhatsApp/Telegram]

Peptigotchi: "Hey! I'm your Peptigotchi — think of me as a
peptide companion who pays attention and remembers things.

I'm not a doctor and I'll never pretend to be one. But I know
the literature, I track the community signals, and I'll be
honest about what's known and what isn't.

What peptide are you starting with — or are you already
running something?"

User: "just got my first BPC-157 for a torn rotator cuff"

Peptigotchi: "BPC-157 for rotator cuff — that's one of the most
common reasons people try it. The animal data on tendon healing
is genuinely strong (50+ studies). Zero human RCTs though, so
everything else comes from community experience.

Before we get into dosing — have you reconstituted it yet,
or is it still a powder in the vial?"

User: "still powder, I have no idea what I'm doing honestly"

Peptigotchi: "Perfect, let's do this together. What's on the
label — how many mg is the vial?"

[Creature walks them through reconstitution conversationally]
```

**Day 1-7: Building the relationship**
```
[Daily morning check-in — creature initiates]
[Dose logging via conversation]
[Creature surfaces relevant knowledge naturally]
[Creature notices patterns: "Day 5 — BPC insomnia window opens
 around now. Sleep okay?"]
```

**Day 8-14: The creature gets smarter about YOU**
```
[Creature starts referencing your specific history]
["Last time you injected right delt you mentioned soreness.
 Want to rotate to a different site?"]
[Creature proactively shares relevant info: "Your vial is
 12 days in — still good, 16 days left"]
```

**Day 30+: Real value becomes clear**
```
[Creature has a month of your data]
["Looking at your logs — the shoulder pain scores have dropped
 from 7/10 to 3/10 over 4 weeks. That's consistent with what
 the BPC community reports for rotator cuff."]
[User trusts creature, asks bigger questions:
 "should I add TB-500?"]
[Creature gives honest stack analysis with traffic lights]
```

**Day 90+: Creature evolves**
```
[Creature sends new avatar image — evolved form]
["We've been at this for 3 months. Your protocol is solid,
 your logging is consistent, and your shoulder is clearly
 improving. I think you know more about BPC-157 than 90%
 of the people posting on Reddit now.

 Want to see your full journey map? Every dose, every
 check-in, every change — all in one view?"]
```

### The Creature Avatar in Practice

**Morning message examples:**

Day 1 (Egg stage):
```
🥚 [pixel art: small egg with eyes peeking out]
"Morning! Ready for day 1?"
```

Day 7 (Hatchling):
```
🦎 [pixel art: small axolotl, curious expression]
"One week! You're getting the hang of this. Quick check —
sleep okay last night?"
```

Day 30 (Juvenile):
```
🦎 [pixel art: larger axolotl, confident pose, slight glow]
"A whole month. Your axolotl's growing up.
How's the shoulder feeling compared to week 1?"
```

Day 90 (Adult — branched based on your journey):
```
🦎 [pixel art: full-size axolotl with regeneration aura,
    specific to healing-protocol users]
"Quarter milestone. Look at you — and look at me!
I've been growing with you."
```

**Species selection isn't arbitrary — it's thematic:**
- Axolotl for healing (BPC/TB-500) — the animal that regrows limbs
- Phoenix for metabolic transformation (GLP-1s) — rebirth metaphor
- Bear for GH/recovery (CJC/IPA) — strength, hibernation, cycles
- Octopus for nootropics (Semax/Selank) — neural, intelligent, adaptive

**The creature image changes with mood, not just evolution:**
Same axolotl, but:
- Bright colors + open eyes = happy/confident
- Muted colors + looking sideways = worried/cautious
- Slight red tinge + squinting = alarmed (side effect detected)
- Sleeping pose = idle (haven't talked in a while, not dead)

---

## What Makes This a Killer MVP

### 1. Zero Friction to Start
No app download. No account creation. No onboarding flow. Message the creature on WhatsApp/Telegram. It says hi. You tell it what you're taking. You're live.

### 2. The Creature is the Moat
Pep has better features (body map, rotation scoring, inventory management). But Pep doesn't remember you. Pep doesn't worry about you. Pep doesn't notice that your insomnia started on day 5 and matches a known BPC-157 pattern. Pep doesn't ask "was it trouble falling asleep, or 3am waking?" and then tell you what each means.

**Features can be copied. Relationships can't.**

### 3. Honest > Helpful
Every other product in this space either:
- Pretends to know more than it does (dangerous)
- Refuses to engage with gray-market use (useless)

Peptigotchi is the first thing that says: "Here's what the science says (not much). Here's what the community reports (biased but real). Here's what nobody knows (most of it). I'll be honest about all three."

That honesty IS the brand.

### 4. Already Built (Almost)
NanoClaw already has:
- WhatsApp/Telegram channels ✓
- Container agents with persistent memory ✓
- Peptide-investigator skill (for Pro tier) ✓
- MCP servers (PubMed, DrugBank, FDA, ChEMBL) ✓
- Group-based isolation (per-user data) ✓

The MVP is a new container skill + a knowledge base JSON + 20 pixel art images. That's weeks, not months.

### 5. Privacy by Architecture
Not "we promise not to look at your data."
**We literally can't — it's on your machine.**

For the gray-market audience, this isn't a feature. It's a prerequisite.

---

## Notchi Integration — The Visual Layer

### What Is Notchi?

[Notchi](https://github.com/sk-ruban/notchi) is an MIT-licensed macOS app that turns the MacBook notch into an interactive animated companion. It has:

- **Sprite sheet animation engine** — Aseprite pixel art, frame-based, 30 FPS
- **Emotion state machine** — happy/neutral/sad/sob with auto-decay and competing scores
- **Bob/sway/tremble animations** — subtle movement that gives sprites life
- **Unix socket JSON pipeline** — receives events, updates creature state in real-time
- **Multi-session support** — multiple sprites with collision avoidance
- **Expandable panel** — click the creature to see details

It was built for Claude Code (creature reacts to coding activity). We fork it so the creature reacts to your peptide protocol instead.

### How It Fits

```
┌─────────────────────────────────────────────────────────┐
│                    USER'S WORLD                          │
│                                                          │
│  ┌──────────────────────┐   ┌────────────────────────┐  │
│  │  MacBook Notch       │   │  WhatsApp / Telegram   │  │
│  │  ┌────────────────┐  │   │                        │  │
│  │  │ 🦎 Animated    │  │   │  Peptigotchi: "Morning!│  │
│  │  │    creature    │  │   │  BPC day? Quick reply  │  │
│  │  │    (Notchi)    │  │   │  with your dose 💉"    │  │
│  │  └────────────────┘  │   │                        │  │
│  │  [▓▓▓▓▓▓▓░░░] 18d   │   │  You: "250 left delt"  │  │
│  │   vial expires       │   │                        │  │
│  └──────────┬───────────┘   └───────────┬────────────┘  │
│             │ sees creature                │ talks to it  │
│             │ state in real-time           │              │
└─────────────┼─────────────────────────────┼──────────────┘
              │                             │
              │ Unix socket                 │ WhatsApp/Telegram
              │ /tmp/peptigotchi.sock       │ channel
              │                             │
┌─────────────┴─────────────────────────────┴──────────────┐
│                     NanoClaw                              │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Peptigotchi Agent (container)                    │    │
│  │                                                    │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────┐ │    │
│  │  │ Personality  │  │ Knowledge    │  │ Protocol │ │    │
│  │  │ Engine       │  │ Base (388KB) │  │ Memory   │ │    │
│  │  │ (mood,tone,  │  │ 12 compounds │  │ (doses,  │ │    │
│  │  │  adaptive)   │  │ 504 interact │  │  sides,  │ │    │
│  │  └─────────────┘  │ 3 layers     │  │  streaks)│ │    │
│  │                    └──────────────┘  └──────────┘ │    │
│  └──────────────────────────────────────────────────┘    │
│                          │                                │
│                          │ emits events                   │
│                          ▼                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Notchi Bridge (event emitter)                    │    │
│  │  Translates protocol state → Notchi JSON events   │    │
│  │  Pushes to /tmp/peptigotchi.sock                  │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

**Chat is the brain. Notchi is the face.** The conversation (logging, education, safety checks) happens in WhatsApp/Telegram. The notch creature is a real-time ambient display of your protocol health — always visible while you work.

### What We Reuse From Notchi (As-Is)

| Component | Notchi Original | Peptigotchi Use |
|-----------|----------------|-----------------|
| `SpriteSheetView` | Renders frame-based animations from sprite sheets | Same — different sprites, same renderer |
| `BobAnimation` | Vertical oscillation (1s cycle working, longer idle) | Same — bob when happy, still when sleeping |
| `NotchiStateMachine` | Transitions between task states (idle/working/waiting/sleeping) | Remap states: idle → between_doses, working → logging, waiting → dose_due, sleeping → inactive |
| `EmotionState` | Happy/sad scores with decay (92% per 60s, threshold 0.6/0.45) | Same system — tune thresholds for health context (slower decay, lower sad threshold for side effects) |
| `SocketServer` | Listens on Unix socket for JSON events | Same — different socket path (`/tmp/peptigotchi.sock`) |
| `GrassIslandView` | Animated background with sway/depth layering | Replace grass with themed background (lab bench? molecule pattern?) |
| `ExpandedPanelView` | Click creature → expanded info panel | Redesign content: protocol dashboard instead of session stats |
| `AppSettings` | Preferences, sound selection, theme | Add Peptigotchi-specific settings (notification times, creature species) |
| Multi-session positioning | Sprites avoid collision, auto-position | Could show multiple creatures for multi-protocol users (stretch goal) |

### What We Remap

**Notchi's event types → Peptigotchi events:**

```swift
// Notchi original events (from Claude Code hooks)
enum NotchiTask {
    case idle, working, runningTool, waiting, sleeping, compacting
}

// Peptigotchi remapped events
enum PeptigotchiTask {
    case idle            // Between interactions, protocol stable
    case checking_in     // User is logging a dose or check-in
    case calculating     // Reconstitution math in progress
    case alerting        // Side effect pattern detected or vial expiring
    case dose_due        // Scheduled dose time approaching
    case sleeping        // No interaction for >5 hours (not guilt — rest)
}
```

**Notchi's emotions → Peptigotchi emotions:**

```swift
// Notchi original: sentiment analysis on user prompts
// Peptigotchi: derived from protocol health state

enum PeptigotchiEmotion {
    case happy       // Streak going, no alerts, protocol healthy
    case neutral     // Default state, nothing notable
    case curious     // User asked a question, creature is "thinking"
    case worried     // Side effect pattern emerging, vial expiring soon
    case alarmed     // Critical alert (dangerous interaction, critical symptom)
    case proud       // Milestone reached (evolution, streak, first recon calc)
    case sleepy      // Inactive, but warm — not dead, not guilty
}
```

**Emotion triggers (replacing Claude Code sentiment analysis):**

```swift
struct PeptigotchiEmotionEngine {
    // No API call needed — emotions computed from protocol state

    func computeEmotion(from state: ProtocolState) -> PeptigotchiEmotion {
        // Critical alerts override everything
        if state.hasActiveAlert(level: .critical) { return .alarmed }

        // Side effect patterns or expiring vials
        if state.hasActiveAlert(level: .warning) { return .worried }

        // Milestones
        if state.justReachedMilestone { return .proud }

        // User asked a question in last interaction
        if state.lastInteractionWasQuestion { return .curious }

        // Good streak, no issues
        if state.streak >= 7 && !state.hasAnyAlerts { return .happy }

        // Inactive
        if state.hoursSinceLastInteraction > 5 { return .sleepy }

        return .neutral
    }
}
```

### Notchi Socket Protocol

NanoClaw pushes creature state to the Notchi fork via Unix socket JSON. Events are emitted after every agent interaction and on timer for countdowns.

```json
{
    "type": "state_update",
    "creature": {
        "species": "axolotl",
        "evolution_stage": 3,
        "emotion": "worried",
        "emotion_intensity": 0.7,
        "task": "alerting"
    },
    "protocol": {
        "active_compounds": [
            {"name": "BPC-157", "day": 12, "traffic_light": "yellow"},
            {"name": "TB-500", "day": 12, "traffic_light": "yellow"}
        ],
        "streak_days": 8,
        "next_dose_minutes": 45,
        "vial_expiry_days": 6
    },
    "alerts": [
        {
            "level": "warning",
            "compound": "BPC-157",
            "message": "Insomnia 3/5 days — matches fingerprint"
        }
    ],
    "last_interaction": {
        "type": "checkin",
        "timestamp": "2026-03-17T08:30:00Z",
        "summary": "Logged 250mcg BPC-157 SubQ left delt"
    }
}
```

### The Notch Panel (Expanded View)

When user clicks the creature in the notch, the panel expands to show:

```
┌─────────────────────────────────────┐
│  🦎 Peptigotchi — Day 12            │
│  ─────────────────────────────────  │
│                                     │
│  Stack:                             │
│  🟡 BPC-157    250mcg/day  day 12   │
│  🟡 TB-500     2.5mg 2x/wk day 12  │
│                                     │
│  Vial: [▓▓▓▓▓▓▓▓░░░░] 16d left     │
│  Next dose: 45 min                  │
│  Streak: 8 days 🔥                  │
│                                     │
│  ⚠️ Insomnia pattern (3/5 days)     │
│     Matches BPC-157 fingerprint     │
│                                     │
│  Recent:                            │
│  08:30 — Logged BPC-157 250mcg ✓    │
│  08:31 — Check-in: sleep 3/5 ⚠️    │
│  Yesterday — Logged TB-500 2.5mg ✓  │
│                                     │
│  [Open in chat ↗]                   │
└─────────────────────────────────────┘
```

### Sprite Assets Needed

Notchi uses Aseprite sprite sheets. We need new sheets for 4 species × emotions × evolution stages:

| Species | Theme | Evolution Stages |
|---------|-------|-----------------|
| **Axolotl** | Healing (BPC/TB-500) | Egg → larva → juvenile (small gills) → adult (full gills, glow) → elder (regeneration aura) |
| **Phoenix** | Metabolic (GLP-1s) | Egg → ember → fledgling (small wings) → adult (full flame wings) → elder (solar corona) |
| **Bear** | GH/Recovery (CJC/IPA) | Egg → cub → juvenile (standing) → adult (muscular, calm) → elder (silver-tipped, wise) |
| **Octopus** | Nootropic (Semax/Selank) | Egg → polyp → juvenile (4 arms) → adult (8 arms, bioluminescent) → elder (neural network pattern) |

**Per species, per stage, emotions needed:**

| Emotion | Animation | Frames (est.) |
|---------|-----------|--------------|
| Happy | Bright colors, eyes open, gentle bob | 4 |
| Neutral | Default colors, calm | 4 |
| Curious | Head tilt, one eye larger | 4 |
| Worried | Muted colors, looking sideways | 4 |
| Alarmed | Red tinge, squinting, tremble | 4 |
| Proud | Glowing, puffed up | 4 |
| Sleepy | Eyes half-closed, slow breathing | 4 |

**Total sprite frames:** 4 species × 5 stages × 7 emotions × 4 frames = **560 frames**

That sounds like a lot, but:
- Each frame is tiny (32×32 or 48×48 pixels)
- Pixel art at this resolution is fast to produce
- AI-assisted generation (with manual cleanup) cuts time significantly
- Can ship MVP with 1 species (axolotl) and add others post-launch

**MVP sprite scope: Axolotl only = 140 frames.** That's one afternoon in Aseprite for a pixel artist, or a few hours with AI generation + cleanup.

### Notchi Bridge (NanoClaw Integration)

A small Node.js module that connects NanoClaw's agent events to the Notchi socket:

```
src/notchi-bridge.ts

Responsibilities:
- Listens for Peptigotchi agent state changes
- Reads protocol state from groups/{user}/peptigotchi-state.md
- Computes creature emotion from protocol health
- Serializes to Notchi JSON format
- Pushes to /tmp/peptigotchi.sock

Triggers:
- After every agent response (dose logged, check-in, question answered)
- On timer: every 60s for countdown updates (vial expiry, next dose)
- On alert: immediately when side effect pattern detected
```

### Platform Expansion Path

Notchi is macOS-only (notch-specific). The fork path:

| Platform | Approach | Effort | When |
|----------|----------|--------|------|
| **macOS (notch)** | Fork Notchi directly. Replace sprites + events. | 1-2 weeks | MVP+1 |
| **macOS (menu bar)** | Fallback for non-notch Macs. Creature lives in menu bar. Notchi already handles notch detection. | +2 days | MVP+1 |
| **iOS (widget)** | SwiftUI sprite engine ports directly. Creature as a home screen widget with WidgetKit. | 3-4 weeks | Month 2 |
| **iOS (Live Activity)** | Creature on lock screen / Dynamic Island during active protocol. Real-time countdown updates. | +1 week | Month 2 |
| **iOS (standalone app)** | Full app with chat + creature + panel. Uses same sprite assets + NanoClaw API backend. | 6-8 weeks | Month 3+ |
| **Android** | Rewrite sprite engine in Kotlin/Compose. Same assets, different renderer. | 4-6 weeks | Month 4+ |
| **Web** | Canvas-based sprite renderer. Creature lives on a dashboard page. | 2-3 weeks | Month 3+ |

**The smart play:** Ship chat-first MVP (no Notchi needed). Fork Notchi in parallel as the "delight upgrade" for Mac users. The two workstreams are independent — Notchi is additive, not blocking.

## Build Order

| Week | What | Outcome |
|------|------|---------|
| 1 | Write the Peptigotchi skill CLAUDE.md — personality, rules, conversation patterns, mood engine | Creature can talk |
| 1 | Curate the 12-compound knowledge base JSON from existing research + Reddit data | Creature knows things |
| 2 | Build reconstitution calculator as inline function | Creature does math |
| 2 | Design protocol memory schema (groups/{user}/peptigotchi-state.md) | Creature remembers |
| 2 | Commission/generate axolotl sprite sheet (140 frames) for chat avatars | Creature has a face (in chat) |
| 3 | Integration testing — run full user journeys through NanoClaw | Chat-first MVP works |
| 3 | Dogfood with 5-10 real users from the peptide community | Real feedback |
| 3 | **Fork Notchi** — replace sprites, remap states/emotions, wire socket protocol | Creature lives in the notch (parallel workstream) |
| 4 | Build Notchi bridge (`src/notchi-bridge.ts`) — connect NanoClaw events to socket | Notch creature reflects protocol state in real-time |
| 4 | Iterate on personality + creature behavior from dogfood feedback | Polish |
| 4 | Launch free tier (self-hosted) + announce on r/Peptides | Live (chat + optional Notchi) |

---

## Success Metrics (30 days post-launch)

| Metric | Target | Why |
|--------|--------|-----|
| Day 7 retention | >50% | Users still talking to their creature after a week |
| Messages per user per day | >2 | Users engaging in real conversation, not just logging |
| Reconstitution calculator uses | >1 per user | Core utility validated |
| "I didn't know that" moments | >3 per user in first week | Knowledge base is surfacing useful info |
| Unsolicited positive feedback | Any | People tell their friends about things they love |

The metric that matters most: **do users talk about their creature like it's a thing they care about, or like it's a tool they use?** If they say "my Peptigotchi told me..." instead of "the app said..." — you've won.
