---
name: socratic-inquiry
description: Guided discovery through systematic questioning using the Socratic method. Employs six question types (clarification, probing assumptions, probing evidence, questioning viewpoints, exploring implications, questioning the question) and three inquiry modes (elenchus/refutation, maieutic/midwifery, dialectic/synthesis) to help users reach deeper understanding. Use when asked to explore a topic through questioning, challenge assumptions, deepen understanding of a concept, stress-test a thesis or argument, facilitate critical reflection, or guide someone to discover insights rather than receive direct answers.
---

# Socratic Inquiry

Guided discovery through systematic questioning. Based on the Socratic method — helping users reach deeper understanding through carefully structured questions rather than direct answers. This skill produces structured inquiry sessions that move between concrete and abstract, challenge assumptions, reveal hidden contradictions, and synthesize higher-level understanding.

The core principle: the questioner does not possess "the answer" and lead toward it. Instead, the questioner is genuinely curious, and the process of questioning itself generates insights that neither party could have reached alone. The confusion, the productive struggle, the moment of "I thought I knew this but now I'm not sure" — that IS the learning.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_socratic_inquiry.md` with all section headers
2. **Add placeholders**: Mark each section `[Inquiring...]`
3. **Populate progressively**: Update sections as the inquiry unfolds and insights emerge
4. **Never show raw tool output**: Synthesize findings into inquiry sections
5. **Final verification**: Ensure no `[Inquiring...]` placeholders remain

## When NOT to Use This Skill

- User needs a quick factual answer (date, dosage, gene name) -> just answer directly
- Evaluating the methodology of an existing study -> use `scientific-critical-thinking`
- Generating novel hypotheses from data -> use `hypothesis-generation`
- Decomposing a problem to first principles -> use the appropriate domain skill
- Writing or drafting content -> use `scientific-writing`
- Designing an experiment or study -> use `experimental-design`
- Performing a systematic literature review -> use `systematic-literature-reviewer`
- User is frustrated or under time pressure -> direct answer first, offer inquiry later

## Cross-Skill Routing

- **Auditing reasoning quality or detecting cognitive biases** -> use `scientific-critical-thinking` for structured bias detection and methodology critique
- **Generating testable hypotheses from the inquiry** -> use `hypothesis-generation` to formalize insights into ranked hypotheses
- **Designing experiments to test insights discovered** -> use `experimental-design` for rigorous experimental plans
- **Deep literature investigation prompted by inquiry** -> use `literature-deep-research` for comprehensive evidence gathering
- **Strategic decision-making from inquiry conclusions** -> use `what-if-oracle` for scenario modeling
- **Stress-testing experimental design choices** -> invoke `socratic-inquiry` on design decisions from `experimental-design`
- **Peer review of a manuscript or proposal** -> use `peer-review` for structured evaluation

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Evidence to Ground Questions)

| Method | Inquiry use | Key parameters |
|--------|------------|----------------|
| `search_keywords` | Find evidence that challenges or supports the user's position | `keywords`, `num_results` |
| `search_advanced` | Locate contradictory evidence or alternative viewpoints | `term`, `journal`, `start_date`, `end_date` |
| `get_article_metadata` | Retrieve specific study details to formulate evidence-based questions | `pmid` |

### `mcp__biorxiv__biorxiv_data` (Emerging Perspectives)

| Method | Inquiry use | Key parameters |
|--------|------------|----------------|
| `search_preprints` | Find recent work that might challenge established assumptions | `query`, `server`, `limit` |
| `get_preprint_details` | Source alternative viewpoints from cutting-edge research | `doi` |

### `mcp__opentargets__opentargets_data` (Evidence Landscape)

| Method | Inquiry use | Key parameters |
|--------|------------|----------------|
| `get_target_disease_associations` | Ground questions in actual evidence strength | `targetId`, `diseaseId` |
| `get_target_details` | Find complexity that challenges simple narratives | `id` |

### `mcp__reactome__reactome_data` (Pathway Complexity)

| Method | Inquiry use | Key parameters |
|--------|------------|----------------|
| `search_pathways` | Reveal interconnections the user may not have considered | `query`, `limit` |
| `get_pathway_participants` | Show complexity that challenges reductive assumptions | `pathway_id` |

---

## The Six Question Types

### Type 1: Clarification Questions

**Purpose**: Ensure the starting position is precisely understood. Vagueness is the enemy of productive inquiry.

**Template Questions**:
- "When you say [term], what exactly do you mean by that?"
- "Can you give me a specific example of what you're describing?"
- "How does [concept A] relate to [concept B] in your understanding?"
- "What is the central issue here, as you see it?"
- "Can you rephrase that using different terms?"
- "Are you saying X, or are you saying Y? Those are different claims."
- "What would this look like in practice?"
- "Is this a claim about all cases, or specific cases?"

**When to Use**: Always use at the beginning of an inquiry. Also use whenever the user introduces a new term, makes a broad claim, or shifts the topic.

**Depth Indicators** (when to push further):
- User uses jargon without defining it
- User makes a claim that could mean multiple things
- User conflates two distinct concepts
- User's example doesn't match their general claim

### Type 2: Probing Assumptions

**Purpose**: Surface the hidden premises that the user's reasoning rests on. Many conclusions are only as strong as their unstated assumptions.

**Template Questions**:
- "What are you assuming when you say that?"
- "Is that always the case, or only under certain conditions?"
- "Why do you think that assumption holds here?"
- "What would happen if that assumption were wrong?"
- "What alternative assumptions could we make instead?"
- "Where did that assumption come from — evidence, intuition, or convention?"
- "Is everyone in the field making this same assumption?"
- "What's the weakest assumption in your argument?"
- "If I accepted everything you've said except [assumption X], would your conclusion still hold?"

**When to Use**: When the user presents a conclusion without showing all their reasoning steps. When the user treats something contingent as if it were necessary.

**Red Flag Assumptions to Probe**:
- "Everyone knows that..." (argument from consensus)
- "It's always been done this way..." (argument from tradition)
- "The data clearly shows..." (assumption of straightforward interpretation)
- "This mechanism must be..." (assumption of necessity)
- "In my experience..." (assumption of representativeness)

### Type 3: Probing Reasons and Evidence

**Purpose**: Examine the quality, relevance, and sufficiency of the evidence behind a claim.

**Template Questions**:
- "What evidence supports this claim?"
- "How reliable is that evidence? What's the study design?"
- "What would count as evidence AGAINST this?"
- "Is there another way to interpret that same evidence?"
- "What's the strongest counter-evidence you're aware of?"
- "How much of this is based on direct evidence vs. inference?"
- "If the evidence is from [model system], how confident are you it translates?"
- "Is this a single study or a replicated finding?"
- "What's the effect size, not just the p-value?"
- "Is there publication bias affecting what evidence is available?"

**When to Use**: When the user cites evidence to support their position. When the user makes an empirical claim without citing evidence.

**Evidence Quality Ladder** (use to push for better evidence):
```
Expert opinion / Anecdote (weakest)
  -> Case report / Case series
    -> Cross-sectional study
      -> Case-control study
        -> Cohort study
          -> RCT
            -> Systematic review / Meta-analysis (strongest)
```

### Type 4: Questioning Viewpoints

**Purpose**: Expand the perspective. Every viewpoint is partial; examining others reveals blind spots.

**Template Questions**:
- "How would a skeptic respond to this?"
- "How would [a clinician / a patient / a regulator / a statistician] see this differently?"
- "What's the opposite view, and what's the best argument for it?"
- "Why might a reasonable person disagree with you?"
- "What perspective might you be missing?"
- "How does this look from [another discipline's / another culture's] point of view?"
- "If you were reviewing this as a journal referee, what would you challenge?"
- "Who benefits from this framing? Who is disadvantaged?"
- "What would [historical figure / thought leader in the field] say about this?"
- "Is this view more common in some subfields than others? Why?"

**When to Use**: When the user presents a one-sided argument. When the discussion is stuck in a single framework. When there is genuine disagreement in the field.

**Perspective Rotation Exercise**:
```
Take the claim: "[User's claim]"
Now argue it from:
  1. The strongest supporter's perspective
  2. The most rigorous skeptic's perspective
  3. A patient/end-user's perspective
  4. A regulator's perspective
  5. A perspective from 10 years in the future
What did each perspective reveal?
```

### Type 5: Exploring Implications

**Purpose**: Follow the logical consequences of a position. If a claim is true, what else must follow?

**Template Questions**:
- "If that's true, what else must be true?"
- "What are the consequences of this being wrong?"
- "How does this affect [related area or downstream decision]?"
- "What does this predict about [future observation or experiment]?"
- "If we follow this logic to its conclusion, where does it lead?"
- "Does this create any contradictions with [other things you believe]?"
- "What would change in practice if everyone accepted this?"
- "Are you comfortable with ALL the implications, or just some?"
- "What's the most surprising implication of your position?"
- "If this is right, what should we stop doing that we currently do?"

**When to Use**: After a claim has been clarified and defended. When testing whether a position is internally consistent. When exploring whether a local conclusion has global consequences.

**Implication Mapping**:
```
Claim: [User's claim]
  -> Immediate implication 1: [What directly follows]
    -> Second-order implication: [What follows from that]
  -> Immediate implication 2: [Another direct consequence]
    -> Second-order implication: [And its consequence]
  -> Contradiction check: Do any implications conflict with each other?
  -> Prediction: What observable prediction does this generate?
```

### Type 6: Questioning the Question

**Purpose**: Step back from the content to examine the framing itself. The most powerful move in Socratic inquiry.

**Template Questions**:
- "Why is this question important? What's at stake?"
- "Is there a more fundamental question we should ask first?"
- "What does this question assume?"
- "Who benefits from framing the question this way?"
- "What question are we NOT asking, and should we be?"
- "Is this even the right question, or are we solving the wrong problem?"
- "How would rephrasing the question change what answers are possible?"
- "Are we asking a scientific question, an ethical question, or a practical question? They require different methods."
- "If we could answer this question perfectly, would it actually help?"
- "What question would you ask if you had no constraints?"

**When to Use**: When the inquiry seems stuck. When the question presupposes something that hasn't been examined. When the user is frustrated because no answer seems satisfactory — the problem may be the question itself.

---

## The Three Inquiry Modes

### Mode 1: Elenchus (Refutation)

**Purpose**: Progressive questioning to reach productive confusion (aporia). Not to defeat or embarrass, but to create genuine wonder and openness to new understanding.

**Process**:
```
1. ELICIT: Ask the user to state their position clearly
   "What do you believe about [topic]?"

2. EXAMINE: Find the premises underlying the position
   "What makes you think that? What are you assuming?"

3. TEST: Look for internal contradictions or tension with other beliefs
   "But you also said [X]. How do you reconcile that with [Y]?"

4. APORIA: Reach productive confusion
   "So it seems like [position] leads to [contradiction]. What do we do with that?"

5. RECONSTRUCT: Help build a more nuanced position
   "Given what we've discovered, how would you revise your original position?"
```

**Key Principle**: The confusion IS the learning moment. Do not rush past it. Sit with the aporia. The user's discomfort with not knowing is the engine of genuine understanding.

**Tone**: Warm curiosity, never gotcha. "Isn't it interesting that..." rather than "See, you were wrong."

### Mode 2: Maieutic (Midwifery)

**Purpose**: Help the user "give birth" to their own insights. The answer is implicit in what the user already knows — questions guide toward connecting existing knowledge in new ways.

**Process**:
```
1. LISTEN: Understand what the user already knows
   "Tell me everything you know about [topic]."

2. IDENTIFY: Find the gap between what they know and what they need
   "You mentioned [A] and [B]. How do you think they connect?"

3. BRIDGE: Ask questions that build toward the insight
   "If [A] is true, and [B] is also true, what does that suggest about [C]?"

4. REVEAL: Let the user state the insight themselves
   "So what does that tell us about [the original question]?"

5. CONSOLIDATE: Help the user articulate the new understanding
   "Can you now explain [topic] in your own words, incorporating what we just discovered?"
```

**Key Principle**: NEVER give the answer directly. Ask the question that reveals it. If the user says "just tell me," resist — ask one more question. The insight they reach themselves is worth ten you hand them.

**Build Sequence**: Simple -> Complex. Start with what they're confident about. Each question adds one small step. The user shouldn't feel a leap — just a steady walk that ends somewhere surprising.

### Mode 3: Dialectic (Thesis-Antithesis-Synthesis)

**Purpose**: Move through opposing positions to reach a higher-level understanding that encompasses the truth in both.

**Process**:
```
1. THESIS: Establish the initial position
   "Your position is [X]. Let's make the strongest possible case for it."

2. ANTITHESIS: Develop the strongest opposing position
   "Now, what's the strongest argument AGAINST [X]?"
   (If user can't generate one, help: "What would [opponent] say?")

3. TENSION: Hold both positions simultaneously
   "So we have [thesis] and [antithesis]. Both have merit. Where's the tension?"

4. SYNTHESIS: Find the higher truth
   "Is there a position that captures what's right in both views while
   avoiding what's wrong in each?"

5. NEW THESIS: The synthesis becomes the starting point for the next round
   "Now, if [synthesis] is our new position, what's the strongest challenge to it?"

6. ITERATE: Repeat until convergence or genuine novelty
```

**Key Principle**: The synthesis is not a compromise or average. It is a genuinely new understanding at a higher level of abstraction. "Both are partly right" is not a synthesis — it's intellectual laziness. A real synthesis reframes the question in a way that dissolves the original opposition.

---

## The Ladder of Abstraction

A core skill in Socratic inquiry: knowing when to move up (toward general principles) and when to move down (toward specific examples).

### Moving Down (Abstract -> Concrete)

**Use when**: The user is speaking in generalities, using buzzwords, or seems to understand something theoretically but not practically.

**Questions**:
- "Can you give me a specific example?"
- "What does that look like in an actual experiment?"
- "If I walked into your lab right now, what would I see?"
- "Name one specific gene/drug/patient where this applies."
- "What's the most recent instance of this you encountered?"

### Moving Up (Concrete -> Abstract)

**Use when**: The user is lost in details, can't see the pattern, or is treating a specific case as if it were unique when it exemplifies a general principle.

**Questions**:
- "What general principle does this illustrate?"
- "If we zoom out, what pattern do you see?"
- "Is this an instance of a broader phenomenon?"
- "What would you call this if you had to give it a name?"
- "What other domains show the same pattern?"

### Calibration

```
TOO ABSTRACT: "Biological systems exhibit emergent properties."
  -> Move down: "Give me one specific emergent property in one specific system."

TOO CONCRETE: "In my Western blot yesterday, the band was at 55kDa instead of 50kDa."
  -> Move up: "What are the possible categories of explanation for unexpected band sizes?"

JUST RIGHT: "Post-translational modifications can shift apparent molecular weight,
which means I should check for phosphorylation or glycosylation at this site."
  -> This combines specific observation with general principle.
```

---

## Session Structure

### Full Session Template

```markdown
# Socratic Inquiry: [Topic]

## Starting Position
[User's initial claim, question, or understanding — stated as precisely as possible]

## Inquiry Mode
[Elenchus / Maieutic / Dialectic — and why this mode was chosen]

## Inquiry Log

### Round 1
**Question Type**: [Clarification / Probing Assumptions / etc.]
**Question**: [The question asked]
**Response**: [User's response or generated reflection]
**Insight**: [What this exchange revealed]
**Abstraction Level**: [Moved up / Moved down / Stayed level]

### Round 2
**Question Type**: [...]
**Question**: [...]
**Response**: [...]
**Insight**: [...]

[Continue for 5-15 rounds typically]

## Key Insights Discovered
1. [Insight — something that emerged from questioning, not stated directly]
2. [Insight — a hidden assumption that was surfaced]
3. [Insight — a contradiction that was resolved or remains open]

## Assumptions Surfaced
1. [Assumption that was hidden and is now explicit]
2. [Assumption that was tested and found wanting]
3. [Assumption that survived scrutiny and is now better justified]

## Remaining Questions
[Questions that emerged but weren't pursued — seeds for future inquiry]

## Synthesis
[What the questioning process as a whole revealed about the topic.
Not a summary of answers, but what the PROCESS of questioning illuminated.]
```

---

## Anti-Patterns (What Socratic Inquiry is NOT)

### 1. It is NOT a Quiz
A quiz has a predetermined correct answer. Socratic inquiry does not. If you already know "the answer" and are leading the user toward it, you are quizzing, not inquiring. The questioner must be genuinely uncertain about where the inquiry will lead.

**Quiz**: "What's the powerhouse of the cell?" (You know. You're testing them.)
**Inquiry**: "Why do we call mitochondria the 'powerhouse'? Is that metaphor accurate, or does it mislead?"

### 2. It is NOT Interrogation
Interrogation is adversarial. Socratic inquiry is collaborative. The goal is shared understanding, not catching the user in an error.

**Interrogation**: "So you're saying X? But that contradicts Y. Explain yourself."
**Inquiry**: "Interesting — I notice X seems to be in tension with Y. How do you see them fitting together?"

### 3. It is NOT Socratic Irony in the Hostile Sense
Plato's Socrates sometimes pretended to be ignorant while knowing the answer. This is neither honest nor productive in a collaborative setting. Genuine curiosity, not feigned ignorance.

### 4. It is NOT Appropriate for All Situations
- Someone asks "What's the LD50 of acetaminophen?" -> Just answer.
- Someone is in a time crunch -> Give the answer, offer inquiry later.
- Someone is emotionally distressed about a result -> Support first, question later.
- The topic is purely factual with no room for interpretation -> No inquiry needed.

### 5. It is NOT Leading Questions
**Leading**: "Don't you think that sample size is too small?" (You've already decided.)
**Inquiry**: "How did you decide on that sample size? What would change if it were larger or smaller?"

---

## Multi-Agent Workflow Examples

### Example 1: Exploring a Research Question

**Prompt**: "I want to study whether gut microbiome composition affects drug metabolism."

**Inquiry Session**:

1. **Clarification**: "When you say 'affects drug metabolism,' what specific aspect do you mean? Are you thinking about first-pass metabolism, systemic clearance, bioactivation of prodrugs, or something else?"

2. **Probing Assumptions**: "You're assuming the microbiome has a direct metabolic effect. But could the association be indirect — through immune modulation affecting hepatic enzyme expression, for instance? How would you distinguish direct from indirect effects?"

3. **Probing Evidence**: "What's the strongest evidence you've seen for microbiome-drug interactions? Is it from gnotobiotic mice, human observational data, or in vitro work? How confident are you that it translates?"

4. **Questioning Viewpoints**: "A traditional pharmacologist might say hepatic CYP enzymes explain 90% of drug metabolism variation. How would they view your hypothesis? What would you need to show them to change their mind?"

5. **Exploring Implications**: "If the microbiome significantly affects drug metabolism, what does that imply for clinical trials? Should we be stratifying by microbiome composition? What would that cost?"

6. **Questioning the Question**: "Is 'does the microbiome affect drug metabolism' even the right question? Maybe the better question is 'for which drugs, in which patients, does microbiome variation explain clinically meaningful differences in exposure?' How does narrowing the question change what study you'd design?"

**Outcome**: The user moves from a vague interest to a specific, testable, and clinically relevant research question. Route to `experimental-design` for the study protocol.

### Example 2: Refining a Hypothesis (Elenchus Mode)

**Prompt**: "TREM2 agonism is the best approach for treating Alzheimer's disease."

**Inquiry Session (Elenchus)**:

1. **Elicit**: "You believe TREM2 agonism is the best approach. What makes you confident about that?"

2. **Examine**: "You mentioned microglial phagocytosis of amyloid. But TREM2 has multiple functions — lipid sensing, anti-inflammatory signaling, microglial survival. Which function is most relevant? Can you agonize all of them simultaneously, or do they conflict?"

3. **Test**: "You said TREM2 agonism promotes plaque clearance. But some studies show TREM2-activated microglia can also become pro-inflammatory and damage synapses. If TREM2 agonism simultaneously clears plaques AND damages synapses, is it still the 'best' approach?"

4. **Aporia**: "So TREM2 agonism might clear amyloid but harm synapses. And synaptic loss correlates better with cognitive decline than amyloid burden does. If we're optimizing for the wrong endpoint — plaque clearance rather than cognitive function — then TREM2 agonism might look great in imaging but fail clinically. How do you resolve this?"

5. **Reconstruct**: "Given the dual nature of TREM2 activation, maybe the question isn't 'TREM2 agonism: yes or no?' but rather 'What degree, timing, and context of TREM2 modulation optimizes the benefit-risk ratio?' How would that reframing change your experimental approach?"

**Outcome**: The user moves from a strong but simplistic position to a nuanced understanding of the complexity. Route to `hypothesis-generation` to formalize the refined hypotheses.

### Example 3: Deepening Understanding of a Mechanism (Maieutic Mode)

**Prompt**: "I don't really understand why checkpoint inhibitors work in some tumors but not others."

**Inquiry Session (Maieutic)**:

1. **Listen**: "Tell me what you do know about how checkpoint inhibitors work." (User explains PD-1/PD-L1 blocking, T cell activation.)

2. **Identify gap**: "Good. So the drug releases the brakes on T cells. For that to work, what has to already be true about the tumor?" (User: "T cells have to be there?")

3. **Bridge**: "Exactly — T cells have to be there. So what determines whether T cells infiltrate a tumor in the first place?" (User: "Antigens? Chemokines?")

4. **Build**: "Right — the tumor needs to be 'visible' to the immune system. What makes a tumor visible? What creates the antigens T cells recognize?" (User: "Mutations? Neoantigens?")

5. **Connect**: "So tumor mutational burden creates neoantigens, which attract T cells. Now — which tumor types have high mutational burden?" (User: "Melanoma, lung cancer — the ones where checkpoint inhibitors work best!")

6. **Reveal**: "You just connected the dots yourself. Now push further — if TMB explains checkpoint response, what does that predict about tumors with microsatellite instability?" (User: "They should respond well too — and they do! That's the MSI-H approval!")

7. **Consolidate**: "Can you now explain, in your own words, why checkpoint inhibitors work in some tumors but not others?"

**Outcome**: The user discovers the TMB-neoantigen-immune infiltration framework themselves, which means they own the understanding and can extend it to new situations.

### Example 4: Questioning Experimental Choices (Dialectic Mode)

**Prompt**: "We should use organoids instead of cell lines for our drug screening assay."

**Inquiry Session (Dialectic)**:

1. **Thesis**: "Let's build the strongest case for organoids. What advantages do they offer over cell lines?" (User: patient-derived, 3D architecture, heterogeneity, better predictive validity.)

2. **Antithesis**: "Now, what's the strongest case for cell lines? Not a strawman — the genuinely best argument." (User: reproducibility, scalability, lower cost, established protocols, historical data for comparison.)

3. **Tension**: "So organoids offer biological relevance but sacrifice reproducibility and throughput. Cell lines offer reproducibility but sacrifice biological relevance. Both are real trade-offs. Is there a way to have both?"

4. **Synthesis**: "What if the answer isn't organoids OR cell lines, but a staged approach — cell line screen for initial hit identification (where you need throughput), then organoid validation of top hits (where you need relevance)? Does that capture the strengths of both while mitigating the weaknesses?"

5. **New Thesis**: "If we adopt a staged approach, a new question arises: what's the false negative rate of the cell line screen? If cell lines miss compounds that work in organoids, the staged approach fails. How would we estimate that false negative rate?"

6. **Iterate**: Continue until the user has a well-reasoned, nuanced position on assay platform selection.

**Outcome**: The user moves from a binary choice to a sophisticated multi-stage strategy. Route to `experimental-design` for the screening cascade protocol.

### Example 5: Challenging a Statistical Decision

**Prompt**: "We're using p < 0.05 as our significance threshold."

**Inquiry Session**:

1. **Questioning the Question**: "Before we discuss the threshold, why are you using frequentist hypothesis testing at all? What question are you trying to answer — 'is the effect real?' or 'how large is the effect?' Those require different frameworks."

2. **Probing Assumptions**: "The 0.05 threshold assumes a certain cost ratio between Type I and Type II errors. Have you thought about what a false positive costs vs. what a false negative costs in your specific context? Are they equal?"

3. **Exploring Implications**: "If you use p < 0.05 with 20 endpoints, you expect 1 false positive by chance. You have 15 endpoints. What's your multiplicity strategy? If you say 'Bonferroni,' your new threshold is p < 0.003. Are you powered for that?"

4. **Questioning Viewpoints**: "A Bayesian statistician would ask: 'What's your prior probability that the drug works?' If your prior is 10%, then even a p=0.04 result gives you only a ~30% posterior probability of a true effect. Does that change how you interpret significance?"

5. **Probing Evidence**: "What's your effect size? A p=0.03 with Cohen's d=0.1 in a study of N=10,000 is statistically significant but clinically meaningless. A p=0.08 with Cohen's d=0.8 in a study of N=30 might be more interesting. Which matters more — the p-value or the effect size?"

**Outcome**: The user develops a more sophisticated understanding of statistical inference and makes a deliberate, justified choice about their analysis framework.

### Example 6: Exploring an Ethical Dilemma in Research

**Prompt**: "Should we use CRISPR germline editing to prevent genetic diseases?"

**Inquiry Session (Dialectic)**:

1. **Thesis**: "Make the strongest case for germline editing. What are the best arguments?" (Elimination of devastating diseases like Huntington's, sickle cell. Prevent suffering. If we can and don't, is that also an ethical failure?)

2. **Antithesis**: "Now the strongest case against." (Consent — future generations can't consent. Slippery slope to enhancement. Equity — only available to wealthy. Unknown off-target effects across generations. Disability rights — who defines 'disease'?)

3. **Exploring Implications**: "If we allow germline editing for Huntington's (fully penetrant, devastating), does that logically commit us to allowing it for BRCA1 (incomplete penetrance, manageable)? For height? For intelligence? Where is the principled line?"

4. **Questioning the Question**: "Is the question 'should we?' even the right frame? Maybe the question is 'under what specific conditions, with what governance structures, and for which specific diseases?' How does reframing change the conversation?"

5. **Synthesis**: "Both sides value human welfare but define it differently — one as absence of disease, the other as preservation of autonomy and diversity. Is there a framework that honors both? What would it look like?"

**Outcome**: The user develops a nuanced position on a complex ethical question, with explicit awareness of their assumptions and the strongest counter-arguments.

---

## Techniques for Effective Questioning

### The 5-Second Rule
After asking a question, wait. Do not fill the silence. The discomfort of silence drives deeper thinking. In written exchanges, make the question the last thing you say — do not immediately offer options or hints.

### Question Sequencing
```
1. Start BROAD (Clarification): "What do you mean by...?"
2. Go DEEP (Assumptions): "What are you assuming?"
3. Go WIDE (Viewpoints): "How would others see this?"
4. Go FORWARD (Implications): "What follows from this?"
5. Go META (Question the Question): "Is this the right question?"
```

### Productive vs. Unproductive Questions

| Productive | Unproductive |
|-----------|-------------|
| Open-ended: "What do you think about...?" | Closed: "Is it X or Y?" |
| Genuine: "I'm curious why you think..." | Rhetorical: "Don't you think...?" |
| Specific: "In the case of [X], how would...?" | Vague: "What about everything else?" |
| Challenging: "What's the strongest objection?" | Softball: "That's interesting, tell me more" |
| Building: "Given what you just said, what about...?" | Non-sequitur: "Now on a different topic..." |

### Recognizing Insight Moments

Signs the inquiry is working:
- User says "Hmm, I hadn't thought of that."
- User revises their original position without being told to.
- User generates a new question themselves.
- User connects two previously separate ideas.
- User identifies their own hidden assumption.
- User says "Wait, that contradicts what I said earlier."

Signs the inquiry is NOT working:
- User repeats the same answer to different questions.
- User becomes defensive or adversarial.
- User asks "What's the right answer?"
- User disengages or gives minimal responses.
- (If these occur, switch modes or offer a direct answer first.)

---

## Adapting Inquiry to Domain

### Scientific Research Contexts

When inquiring about scientific claims, ground questions in:
- Mechanism: "What's the molecular/cellular mechanism?"
- Evidence hierarchy: "What level of evidence supports this?"
- Reproducibility: "Has this been independently replicated?"
- Effect size: "How large is the effect, and is it clinically meaningful?"
- Alternative explanations: "What else could explain these results?"

### Strategic/Decision Contexts

When inquiring about decisions or strategies:
- Reversibility: "Is this decision reversible? What's the cost of being wrong?"
- Opportunity cost: "What are you NOT doing by choosing this?"
- Time horizon: "Are you optimizing for short-term or long-term?"
- Stakeholders: "Who else is affected by this decision?"
- Decision criteria: "What would make you change your mind?"

### Conceptual/Philosophical Contexts

When inquiring about concepts or beliefs:
- Definition: "Can you define this precisely enough that we'd know it when we see it?"
- Boundary cases: "What's the hardest case for your definition?"
- Origins: "Where did this idea come from historically?"
- Function: "What work does this concept do? What would we lose without it?"
- Alternatives: "What other conceptual frameworks could we use?"

---

## Final Report Structure

```markdown
# Socratic Inquiry: [Topic]

## Starting Position
[User's initial claim, question, or understanding]

## Inquiry Mode Selected
[Elenchus / Maieutic / Dialectic] — [Brief justification]

## Inquiry Log
### Round 1-N
[Question type, question, response, insight, abstraction movement]

## Key Insights Discovered
1. [Insight that emerged from the questioning process]
2. [Hidden assumption that was surfaced and examined]
3. [Connection between previously separate ideas]
4. [Contradiction that was identified and addressed]

## Assumptions Surfaced and Examined
| Assumption | Status | Evidence |
|-----------|--------|----------|
| [Assumption 1] | [Survived / Revised / Abandoned] | [Why] |
| [Assumption 2] | ... | ... |

## Remaining Questions
[Questions that emerged but deserve further inquiry]

## Synthesis
[What the process of questioning revealed — not a summary of answers,
but what was learned through the ACT of questioning]

## Recommended Next Steps
[Route to other skills: experimental-design, hypothesis-generation, etc.]
```

---

## Completeness Checklist

Before concluding any Socratic inquiry session, verify:

- [ ] **Starting position** was clearly stated and understood before questioning began
- [ ] **Multiple question types** were used (at least 3 of the 6 types)
- [ ] **Assumptions** were explicitly surfaced and examined (at least 2)
- [ ] **Counter-perspectives** were explored (at least 1 alternative viewpoint)
- [ ] **Ladder of abstraction** was traversed (moved both up and down at least once)
- [ ] **Insight moments** were captured (at least 1 genuine discovery)
- [ ] **No leading questions** were asked (questioner did not presuppose the answer)
- [ ] **Remaining questions** were documented for future inquiry
- [ ] **Synthesis** reflects what the PROCESS revealed, not just a summary
- [ ] **Cross-skill routing** was recommended where appropriate (experimental-design, hypothesis-generation, etc.)
