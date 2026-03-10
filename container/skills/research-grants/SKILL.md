---
name: research-grants
description: Competitive grant proposal writing for NIH (R01, R21, R03, K-series, F-series), NSF (CAREER, EAGER, standard), ERC (Starting, Consolidator, Advanced), DOE, DARPA, and Wellcome Trust. Provides agency-specific review criteria, Specific Aims page structure, budget justification templates, and resubmission strategies. Use when asked to write a grant proposal, draft specific aims, prepare a research plan, structure a grant application, write a budget justification, or plan a resubmission strategy.
---

# Research Grants

Specialist in competitive grant proposal writing across major funding agencies. This skill covers the full grant development lifecycle: from ideation and aims development through writing, internal review, and submission. It provides agency-specific guidance on review criteria, formatting requirements, page limits, and scoring rubrics, along with universal grant writing principles that apply across all funders.

Distinct from **peer-review** (which evaluates existing proposals from a reviewer perspective) and **literature-deep-research** (which conducts systematic literature analysis). This skill operates at the proposal construction level, helping investigators build compelling narratives, structure aims, justify budgets, and respond to reviewer critiques on resubmission.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_research-grants_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Drafting...]`
3. **Populate progressively**: Update sections as literature is gathered and narrative is developed
4. **Never show raw tool output**: Synthesize findings into proposal-ready text
5. **Final verification**: Ensure no `[Drafting...]` placeholders remain

## When NOT to Use This Skill

- Reviewing or scoring an existing grant proposal -> use `peer-review`
- Systematic literature review for background section -> use `literature-deep-research`
- Developing a novel hypothesis from data -> use `hypothesis-generation`
- Writing a clinical trial protocol -> use `clinical-trial-protocol-designer`
- FDA regulatory strategy for an IND/NDA -> use `fda-consultant`
- Competitive landscape or market analysis -> use `competitive-intelligence`

## Cross-Reference: Other Skills

- **Reviewing a grant from reviewer perspective** -> use `peer-review`
- **Deep literature search for significance/innovation** -> use `literature-deep-research`
- **Hypothesis development from preliminary data** -> use `hypothesis-generation`
- **Clinical trial protocol design** -> use `clinical-trial-protocol-designer`
- **FDA regulatory pathway and IND strategy** -> use `fda-consultant`
- **Budget benchmarking and competitive analysis** -> use `competitive-intelligence`

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Literature for Significance & Innovation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed by keywords, MeSH terms, author, journal | `query`, `num_results` |
| `fetch_details` | Full article metadata: abstract, authors, journal, DOI, MeSH | `pmid` |

**Grant-specific uses:**
- Build significance section with recent high-impact publications
- Identify gaps in the literature to justify the proposed research
- Find preliminary data from the PI's own publication record
- Survey the field to position the innovation narrative
- Identify potential reviewers based on publication activity in the area

### `mcp__ctgov__ctgov_data` (Clinical Trial Landscape)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search clinical trials by condition, intervention, sponsor | `query`, `status`, `phase`, `limit` |
| `get_study` | Full trial record: design, endpoints, enrollment, sponsor | `nct_id` |

**Grant-specific uses:**
- Demonstrate clinical relevance by citing ongoing trials in the field
- Identify gaps where no trials exist (supporting the need for proposed research)
- Reference trial designs when proposing clinical aims
- Show translational potential of basic science proposals

### `mcp__opentargets__opentargets_data` (Target Validation Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drug` | Search drugs by name across the Open Targets platform | `query`, `size` |
| `get_drug_info` | Drug details: mechanism, indications, linked targets | `drug_id` |
| `get_associations` | Evidence-scored target-disease associations | `target_id`, `disease_id`, `size` |

**Grant-specific uses:**
- Validate therapeutic targets with genetic and genomic evidence
- Strengthen rationale for target-based research proposals
- Identify druggable targets for translational aims
- Support significance by showing disease-gene association scores

### `mcp__biorxiv__biorxiv_data` (Recent Advances & Preprints)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search bioRxiv/medRxiv preprints by keyword | `query`, `limit` |

**Grant-specific uses:**
- Identify cutting-edge findings not yet in PubMed
- Demonstrate awareness of the latest developments in the field
- Find potential competitors whose work may overlap with proposed aims
- Cite preprints for emerging methods or technologies relevant to the approach

---

## Agency-Specific Guidance

### NIH (National Institutes of Health)

#### Grant Mechanisms

| Mechanism | Duration | Budget | Purpose | Career Stage |
|-----------|----------|--------|---------|-------------|
| R01 | 5 years | ~$250K/yr direct | Major research project | Established/New investigator |
| R21 | 2 years | $275K total | Exploratory/developmental | Any |
| R03 | 2 years | $50K/yr direct | Small research grant | Any |
| K08 | 3-5 years | $100K/yr + salary | Mentored clinical scientist | Early career (MD) |
| K23 | 3-5 years | $100K/yr + salary | Mentored patient-oriented | Early career (MD) |
| K99/R00 | 5 years (2+3) | Varies | Pathway to independence | Postdoc -> faculty |
| F31 | Up to 5 years | Stipend + tuition | Predoctoral fellowship | Graduate student |
| F32 | Up to 3 years | Stipend + research | Postdoctoral fellowship | Postdoc |
| P01 | 5 years | Multi-project | Program project grant | Established team |
| U01 | Varies | Varies | Cooperative agreement | Collaborative |
| R34 | 3 years | $450K total | Clinical trial planning | Any |
| UG3/UH3 | 6 years (2+4) | Varies | Milestone-driven clinical | Any |

#### NIH Review Criteria (Scored 1-9, 1 = Exceptional)

| Criterion | Weight | What Reviewers Assess |
|-----------|--------|----------------------|
| **Significance** | ~20% | Does the project address an important problem? Will it improve scientific knowledge or clinical practice? |
| **Investigator(s)** | ~20% | Are the PD/PIs and key personnel suited to the project? Do they have appropriate experience and training? |
| **Innovation** | ~20% | Does the project employ novel concepts, approaches, methodologies, or technologies? |
| **Approach** | ~30% | Is the overall strategy, methodology, and analyses well-reasoned and appropriate? Are potential problems addressed? |
| **Environment** | ~10% | Does the scientific environment contribute to the probability of success? Are institutional support and resources adequate? |

**Additional review considerations (not scored separately):**
- Protections for human subjects
- Inclusion of women, minorities, and children
- Vertebrate animals
- Biohazards
- Resource sharing plan
- Budget and period of support
- Authentication of key biological and/or chemical resources

#### Study Section Selection Strategy

1. Use NIH Reporter to search funded grants similar to your proposal
2. Identify which study sections reviewed those grants
3. Read the study section roster and recent meeting summaries
4. Contact the Scientific Review Officer (SRO) for guidance
5. Consider requesting assignment to a specific study section or IC in your cover letter
6. Avoid study sections where reviewers lack expertise in your methods

#### Specific Aims Page Structure

The Specific Aims page is THE most important page of the entire application. Reviewers form their initial impression here, and many will not read further if the aims page fails to convince them.

**Paragraph 1: The Hook (2-3 sentences)**
Open with the big-picture problem. Establish urgency and importance. Use statistics or striking facts to capture attention. End with a statement of the current state of the field.

```
[Disease/problem] affects [N] people annually and costs $[X] in [healthcare/economic burden].
Current treatments [limitation]. Recent advances in [field] have revealed [opportunity],
but [critical gap remains].
```

**Paragraph 2: The Gap (2-3 sentences)**
Identify what is specifically unknown or unresolved. This is the knowledge gap your proposal will fill. Make the gap feel both important and tractable.

```
However, [specific knowledge gap]. This gap exists because [reason — technical limitation,
understudied population, conflicting evidence]. Without addressing this gap, [consequence
for the field/patients].
```

**Paragraph 3: Long-Term Goal and Objective (1-2 sentences)**
State your long-term research goal and the specific objective of this application. The objective should be achievable within the grant period.

```
The long-term goal of our research program is to [broad vision]. The objective of this
application is to [specific, achievable goal within grant period].
```

**Paragraph 4: Central Hypothesis and Rationale (1-2 sentences)**
State a testable central hypothesis. Provide the rationale (usually preliminary data). Name the conceptual or theoretical framework.

```
Our central hypothesis is that [testable statement]. This hypothesis is based on
[preliminary data / published evidence / theoretical framework] showing that [key finding].
```

**Paragraph 5: Specific Aims (3-4 aims, each 2-3 sentences)**
Each aim should be independent (failure of one does not prevent completion of others). State the aim, the working hypothesis, and the approach in brief.

```
Aim 1: [Action verb] [what you will do]. We hypothesize that [testable prediction].
We will [brief approach] using [key methods]. Expected outcome: [what you will learn].

Aim 2: [Action verb] [what you will do]. Building on [Aim 1 or preliminary data],
we will test the hypothesis that [prediction]. We will [approach].

Aim 3: [Action verb] [what you will do]. We will [approach] to determine whether
[prediction]. This aim will [how it integrates with others].
```

**Paragraph 6: Impact Statement (2-3 sentences)**
Describe the expected outcomes and their significance. How will this work advance the field? What is the translational potential?

```
This work is expected to [primary outcome], which will [impact on the field].
These results will be significant because [why it matters]. This contribution will be
significant because it is expected to [vertically advance the field / shift current
paradigms / provide foundation for future work].
```

#### Research Strategy Structure (R01)

| Section | Pages | Focus |
|---------|-------|-------|
| **Significance** | ~1 page | Importance of the problem, rigor of prior research, how the project will improve knowledge/practice |
| **Innovation** | 0.5-1 page | Novel concepts, approaches, methods, or technologies; how project challenges existing paradigms |
| **Approach** | 8-9 pages | Preliminary data, research design, methods for each aim, expected outcomes, potential problems and alternative strategies, timeline, rigor and reproducibility |

**Approach section structure per aim:**
1. Rationale and hypothesis
2. Preliminary data supporting feasibility
3. Experimental design (variables, controls, sample size)
4. Methods (detailed protocols)
5. Expected outcomes and interpretation
6. Potential problems and alternative approaches
7. Rigor and reproducibility considerations

#### NIH Biosketch and Personal Statement

The personal statement (within the biosketch) should:
- Explain why you are the right person for this project
- Describe relevant experience and expertise
- Reference 1-4 publications that demonstrate your qualifications
- For K-awards: articulate career development goals and how this award advances them

#### Human Subjects and Vertebrate Animals

**Human subjects (if applicable):**
- Justification for involvement of human subjects
- Inclusion enrollment report (planned enrollment by sex/gender, race, ethnicity)
- Protection of human subjects (risks, adequacy of protections, data safety)
- Inclusion of women, minorities, children (or justification for exclusion)

**Vertebrate animals (if applicable):**
- Description of procedures
- Justification for use of animals
- Minimization of pain and distress
- Method of euthanasia (must be AVMA-approved)

---

### NSF (National Science Foundation)

#### Grant Mechanisms

| Mechanism | Duration | Budget | Purpose |
|-----------|----------|--------|---------|
| Standard Grant | 3 years | Varies by directorate | Core research |
| CAREER | 5 years | $400K-$800K total | Early career (tenure-track) |
| EAGER | 2 years | $300K max | High-risk exploratory |
| RAPID | 1 year | $200K max | Urgent research opportunity |
| Collaborative | 3-5 years | Varies | Multi-institution |

#### NSF Review Criteria (Two Criteria Only)

**Intellectual Merit:** Potential to advance knowledge; creative, original, or transformative concepts; well-reasoned plan with mechanism to assess success; PI qualifications; adequate resources.

**Broader Impacts:** Advancing discovery while promoting teaching/training/learning; broadening participation of underrepresented groups; enhancing research/education infrastructure; broad dissemination; benefits to society.

#### NSF Proposal Structure

| Section | Pages | Content |
|---------|-------|---------|
| Project Summary | 1 page | Overview, Intellectual Merit, Broader Impacts (each labeled separately) |
| Project Description | 15 pages | Introduction, background, proposed research, broader impacts, timeline |
| References Cited | No limit | Complete bibliographic citations |
| Biographical Sketch | 3 pages | Professional preparation, appointments, products, synergistic activities |
| Budget Justification | 3 pages | Detailed justification for all budget categories |
| Data Management Plan | 2 pages | How data will be managed, shared, and preserved |
| Facilities & Equipment | No limit | Available resources |
| Mentoring Plan | 1 page | Required if postdocs are funded |

#### Broader Impacts: What Counts

Broader impacts must be genuine and well-integrated, not an afterthought. Strong examples:

| Category | Examples |
|----------|---------|
| **Education** | Course development, curriculum integration, student mentoring, REU supplements |
| **Outreach** | K-12 programs, public lectures, museum exhibits, citizen science |
| **Diversity** | Recruiting underrepresented students, partnering with MSIs/HBCUs, mentoring programs |
| **Infrastructure** | Shared instruments, databases, software tools, community resources |
| **Society** | Policy briefs, industry partnerships, public health impact, environmental sustainability |
| **Dissemination** | Open-source software, public datasets, workshops, textbooks |

#### NSF Data Management Plan

Must address:
1. Types of data produced (experimental, observational, computational, etc.)
2. Data and metadata standards
3. Policies for access and sharing (including timeline)
4. Policies for re-use and redistribution
5. Plans for archiving and preservation (minimum 3 years post-award)

---

### ERC (European Research Council)

#### Grant Types

| Grant | Eligibility | Duration | Budget |
|-------|------------|----------|--------|
| Starting Grant (StG) | 2-7 years post-PhD | 5 years | Up to 1.5M EUR |
| Consolidator Grant (CoG) | 7-12 years post-PhD | 5 years | Up to 2.0M EUR |
| Advanced Grant (AdG) | Established leaders | 5 years | Up to 2.5M EUR |
| Synergy Grant (SyG) | 2-4 PIs jointly | 6 years | Up to 10M EUR |
| Proof of Concept (PoC) | Existing ERC grantees | 1.5 years | Up to 150K EUR |

#### ERC Evaluation Criteria

**Panel evaluation focuses on two dimensions:**

1. **PI Excellence (50%)**
   - Track record relative to career stage
   - Intellectual capacity and creativity
   - Commitment to the project (time allocation)

2. **Project Quality (50%)**
   - Groundbreaking nature and ambition
   - Novelty and feasibility of methodology
   - Clarity and achievability of objectives
   - Potential for high impact

#### ERC Proposal Structure

**Part B1 — Extended Synopsis (5 pages)**
- State of the art and objectives
- Methodology
- Resources (including team composition)

**Part B2 — Full Scientific Proposal (15 pages)**
- Scientific approach and key methodology
- Timeline and milestones
- Host institution and resources
- PI's CV, publication list, funding track record
- Ethical issues (if applicable)

#### ERC Tips

- Emphasize high-risk, high-gain nature of the research
- Demonstrate the project is "frontier research" (not incremental)
- Show strong publication record relative to career stage
- PI must commit significant time (typically 50%+ for StG/CoG)
- Host institution guarantee letter is required
- Portability: the grant can move with the PI to another institution

---

### DOE (Department of Energy)

Key offices: BES (materials, chemistry, $200K-$500K/yr), BER (climate, genomics, $200K-$400K/yr), ASCR (HPC, algorithms, $200K-$500K/yr), ARPA-E (transformational energy tech, $500K-$5M total). Align with FOA priorities, emphasize energy relevance and technology transfer, partner with national labs when possible. ARPA-E proposals must be truly disruptive.

---

### DARPA (Defense Advanced Research Projects Agency)

Mechanisms: BAAs (specific programs), SBIR/STTR (small business), Young Faculty Award (early career), Director's Fellowship (by invitation). Focus on revolutionary capability, not incremental improvement. Articulate the military/national security "so what." Include concrete metrics and go/no-go decision points. Phase structure: concept -> prototype -> demonstration. White paper often required before full proposal.

---

### Wellcome Trust

#### Key Schemes

| Scheme | Purpose | Duration | Budget |
|--------|---------|----------|--------|
| Discovery Research | Curiosity-driven biomedical | 5-8 years | Up to 3M GBP |
| Career Development Awards | Mid-career researchers | 8 years | Up to 1.5M GBP |
| Senior Research Fellowships | Established researchers | 5 years | Up to 2.5M GBP |
| Collaborative Awards | Team science | 5 years | Up to 5M GBP |

#### Wellcome Proposal Tips

- Strong emphasis on open science and data sharing
- Research must address questions in health and biomedical science
- Wellcome values diversity and expects inclusive research practices
- Budget flexibility: Wellcome funds what is needed (no artificial caps on many schemes)
- Institutional support letter required
- Impact beyond academia is valued (public engagement, policy, clinical translation)

---

## Universal Grant Writing Principles

### Problem-Solution Narrative Structure

Every successful grant tells a story with this arc:

1. **The problem exists and matters** (Significance)
2. **Current solutions are inadequate** (Gap)
3. **We have a promising new approach** (Innovation)
4. **We can execute it** (Approach + Investigator + Environment)
5. **Success will change the field** (Impact)

### Preliminary Data Requirements

| Grant Type | Preliminary Data Expectation |
|-----------|----------------------------|
| R01 | Substantial: proof of concept, feasibility of key methods, initial results |
| R21 | Moderate: conceptual framework, some feasibility data |
| R03 | Minimal: published literature supporting rationale |
| K-series | Relevant to career development plan; shows research potential |
| F-series | Minimal; focus on training potential and mentor's track record |
| NSF Standard | Moderate: preliminary results or published work supporting approach |
| CAREER | Strong: publications demonstrating expertise and initial findings |
| ERC StG | Relative to career stage; strong publication record is key |

### Presenting Preliminary Data

- Include figures with proper labels, legends, and statistical annotations
- Reference figures in the text ("As shown in Figure 1...")
- Explain what the data shows AND what it means for the proposed work
- Acknowledge limitations of preliminary data
- Use preliminary data to demonstrate feasibility, not to tell the whole story

### Writing Specific, Measurable Milestones

**Weak:** "We will characterize the protein."

**Strong:** "By Month 12, we will have determined the crystal structure of Protein X at 2.0 A resolution or better, identified at least 3 key binding-site residues by mutagenesis, and measured binding affinity (Kd) for 5 candidate ligands using ITC."

Each milestone should specify:
- What will be accomplished
- By when (month or year)
- How success will be measured (quantitative criteria)
- What constitutes a go/no-go decision point

### Alternative Approaches for Risky Aims

For every aim, address:
1. **What could go wrong** (technical failures, negative results)
2. **How you will know** (decision criteria for pivoting)
3. **What you will do instead** (specific alternative methods or approaches)
4. **Why the alternative is viable** (evidence or reasoning)

Example:
```
Potential Problem: Protein X may not crystallize under standard conditions.
Alternative Approach: If crystallization fails after screening 1,000 conditions
(3 months), we will pursue cryo-EM single-particle analysis, for which we have
established protocols (see Preliminary Data, Figure 3). Our institutional cryo-EM
facility has successfully resolved structures at 3.2 A for similar-sized complexes.
```

### Budget Justification

#### Personnel

| Role | Justification Must Include |
|------|--------------------------|
| PI | % effort, specific leadership responsibilities, expertise |
| Co-PI/MPI | % effort, complementary expertise, specific aim responsibilities |
| Postdoc | % effort, specific experimental responsibilities, training component |
| Graduate student | % effort, specific project tasks, training plan |
| Technician | % effort, technical skills, specific methods they will perform |
| Biostatistician | % effort, statistical analysis plan, interim analysis responsibilities |

#### Equipment (>$5,000 per item)

- Justify why the equipment is essential
- Explain why existing institutional equipment is insufficient
- Provide cost quotes from vendors
- Describe how equipment will be maintained and who will operate it

#### Supplies

- Group by category (reagents, animals, cell lines, computing)
- Provide per-unit costs and quantities
- Tie expenses to specific aims
- Include cost escalation for multi-year budgets (typically 3%/year)

#### Travel

- Justify each trip (conferences for dissemination, collaborator visits, field work)
- Name specific conferences if possible
- Include domestic and international separately
- Typical: 1-2 conference trips per year per key personnel

#### Subcontracts / Consortium

- Justify why the work cannot be done in-house
- Describe the subcontractor's unique expertise or resources
- Include a letter of support from the subcontract PI
- Budget for both direct costs and F&A at the subcontractor's negotiated rate

### Letters of Support Strategy

| Letter Type | From Whom | What It Should Say |
|------------|-----------|-------------------|
| Collaborator | Named collaborator | Specific commitment (effort, resources, methods, data) |
| Consultant | Expert advisor | Willingness to advise, relevant expertise, availability |
| Resource access | Core facility director | Confirmation of access, capacity, priority, cost structure |
| Data/sample access | Cohort PI or biobank | Confirmation of data/sample availability and sharing terms |
| Institutional | Department chair/dean | Space, startup, protected time, mentoring (especially for K-awards) |

---

## Resubmission Strategies

### NIH A1 Resubmission

NIH allows one resubmission (A1) after an unfunded initial submission (A0). The resubmission must include a 1-page Introduction addressing reviewer concerns.

#### Introduction Page Format

```
INTRODUCTION TO REVISED APPLICATION

This revised R01 application, "[Title]," addresses the critiques raised by the
reviewers of the original submission ([application number], reviewed [date],
percentile: [X]%).

We thank the reviewers for their constructive feedback. Major revisions include:
(1) [summary of change 1], (2) [summary of change 2], and (3) [summary of change 3].

Reviewer 1 Concerns:
[Concern 1]: "[Brief quote or paraphrase]"
Response: [What we changed and why. Reference specific page/section in the revised
application.] (See Approach, p. X)

[Concern 2]: "[Brief quote or paraphrase]"
Response: [What we changed. Include new data if applicable.] (See Significance, p. X;
new Figure Y)

Reviewer 2 Concerns:
[Continue point-by-point...]

Reviewer 3 Concerns:
[Continue point-by-point...]

Panel Discussion Points:
[Address any concerns raised during panel discussion that were not in individual
reviews.]
```

#### Point-by-Point Response Guidelines

| Do | Don't |
|----|-------|
| Address every critique, even minor ones | Ignore or dismiss any reviewer comment |
| Thank reviewers for constructive feedback | Be defensive or argumentative |
| Describe specific changes made | Give vague responses ("we have addressed this") |
| Reference page numbers in revised application | Leave reviewers searching for changes |
| Include new preliminary data if it addresses a concern | Pad with irrelevant new data |
| Explain respectfully if you disagree with a critique | Simply say "we disagree" without rationale |
| Bold or italicize changed text in the Research Strategy | Make reviewers guess what changed |

#### Strategic Aim Restructuring

When a resubmission requires significant revision:

1. **Dropped aim:** Remove the aim reviewers found weakest; redistribute effort
2. **Merged aims:** Combine two aims if reviewers felt scope was too broad
3. **New aim:** Add an aim if reviewers identified a critical gap in the approach
4. **Reordered aims:** Lead with the strongest aim (backed by the most preliminary data)
5. **Reduced scope:** If reviewers said "too ambitious," narrow focus and deepen each aim

### NSF Resubmission

- No formal resubmission mechanism (submit as a new proposal)
- Address previous review feedback in the Project Description
- Contact the program officer to discuss reviewer concerns before resubmitting
- Significant revision expected between submissions

### ERC Resubmission

- Can resubmit to the next call (typically one year later)
- Must substantially revise the proposal
- Panel feedback (if provided) should guide revisions
- No formal response-to-reviewers document, but changes should be evident

---

## Common Mistakes

| Category | Mistake | Fix |
|----------|---------|-----|
| **Conceptual** | Too many aims (5+) | Limit to 3-4 focused, independent aims |
| **Conceptual** | Aims that are sequential/dependent | Restructure so each aim stands alone |
| **Conceptual** | Hypothesis-free aims ("we will characterize...") | Frame each aim around a testable hypothesis |
| **Writing** | Methods-heavy, significance-light | Lead with WHY (significance), then HOW (methods) |
| **Writing** | Jargon-laden opening paragraph | Write the hook for an educated non-specialist |
| **Writing** | Passive voice throughout | Use active voice: "We will..." not "It will be..." |
| **Writing** | No topic sentences | Start each paragraph with a clear claim or transition |
| **Technical** | No alternative approaches | Include Plan B for each risky experiment |
| **Technical** | Missing power analysis | Include sample size justification with effect size and alpha/beta |
| **Technical** | No rigor and reproducibility plan | Address biological variables, authentication, blinding, randomization |
| **Strategic** | Wrong study section | Research membership, read chartered description, contact SRO |
| **Strategic** | Ignoring reviewer expertise | Write for a knowledgeable but non-expert audience |
| **Strategic** | No cover letter with assignment requests | Always request specific IC and study section |
| **Budget** | Unrealistic timelines | Match scope to funding level and duration |
| **Budget** | Overstaffed or understaffed | Justify every person and their effort level |
| **Budget** | Missing budget escalation | Include 3% annual increases for supplies and salary |
| **Format** | Exceeding page limits | Strictly adhere; reviewers will not read excess pages |
| **Format** | Tiny fonts or narrow margins | Use NIH-required fonts (11pt Arial, Palatino, etc.) and 0.5" margins |
| **Format** | Missing required sections | Use the agency checklist; missing sections can trigger administrative withdrawal |

---

## 5-Phase Grant Development Workflow

### Phase 1: Ideation (8-12 Weeks Before Deadline)

**Objectives:** Define the research question, identify the funding mechanism, survey the landscape.

**Tasks:**
1. Identify the knowledge gap and frame the central question
2. Search funded grants on NIH Reporter / NSF Award Search to assess competition
3. Survey the literature for recent advances and gaps

```
mcp__pubmed__pubmed_data(method: "search", query: "TOPIC review OR meta-analysis", num_results: 20)
   -> Identify state of the art and unresolved questions

mcp__biorxiv__biorxiv_data(method: "search", query: "TOPIC novel approach", limit: 10)
   -> Find cutting-edge work not yet peer-reviewed
```

4. Select the appropriate funding mechanism (R01 vs R21 vs CAREER, etc.)
5. Draft preliminary Specific Aims (version 1)
6. Identify potential collaborators and core facilities
7. Contact program officer to discuss fit (NIH/NSF)

**Deliverable:** Draft Specific Aims page (version 1), target mechanism and IC/directorate identified.

### Phase 2: Planning (6-8 Weeks Before Deadline)

**Objectives:** Outline the full proposal, gather preliminary data, plan the budget.

**Tasks:**
1. Revise Specific Aims based on mentor/colleague feedback (version 2)
2. Outline each section of the Research Strategy / Project Description
3. Gather and format preliminary data (figures, tables)
4. Draft the experimental design for each aim
5. Identify and contact letter-of-support writers
6. Begin budget preparation with grants office

```
mcp__pubmed__pubmed_data(method: "search", query: "PI_NAME TOPIC", num_results: 10)
   -> Compile PI's relevant publications for biosketch and preliminary data citations

mcp__ctgov__ctgov_data(method: "search_studies", query: "TOPIC", status: "RECRUITING", limit: 20)
   -> Map ongoing clinical work to position the proposal
```

7. Complete required training (human subjects, responsible conduct of research)
8. Draft the data management / resource sharing plan

**Deliverable:** Full outline with preliminary data figures, budget draft, letters of support requested.

### Phase 3: Writing (4-6 Weeks Before Deadline)

**Objectives:** Draft all sections, iterate on the aims page, integrate feedback.

**Tasks:**
1. Write the Significance section first (sets the narrative frame)
2. Write the Innovation section (what is new about your approach)
3. Write the Approach section aim by aim:
   - Rationale and hypothesis
   - Preliminary data
   - Experimental design and methods
   - Expected outcomes
   - Potential problems and alternatives
   - Timeline and milestones
4. Finalize the Specific Aims page (version 3+)
5. Write the Project Summary / Abstract
6. Complete the biosketch with personal statement
7. Prepare all other required documents (facilities, equipment, budget justification)

```
mcp__opentargets__opentargets_data(method: "get_associations", target_id: "TARGET", disease_id: "DISEASE", size: 10)
   -> Strengthen significance with genetic evidence for target-disease link
```

**Deliverable:** Complete draft of all proposal sections.

### Phase 4: Internal Review (2-3 Weeks Before Deadline)

**Objectives:** Get critical feedback from 3+ colleagues, revise thoroughly.

**Review Strategy:**
1. **Domain expert** (1-2 reviewers): Evaluate scientific rigor, approach, feasibility
2. **Non-expert scientist** (1 reviewer): Evaluate clarity, significance narrative, accessibility
3. **Grants specialist** (if available): Evaluate compliance, formatting, completeness
4. **Mentor** (for K/F awards): Ensure alignment with career development plan

**What to ask reviewers to assess:**
- Is the significance clear and compelling?
- Is the central hypothesis testable and well-supported?
- Are the aims independent and feasible within the timeline?
- Are alternative approaches adequate?
- Is the budget appropriate for the scope?
- Would you fund this proposal? Why or why not?

**Deliverable:** Revised proposal incorporating all reviewer feedback.

### Phase 5: Finalization (1 Week Before Deadline)

**Objectives:** Polish, format, compliance check, submit.

**Tasks:**
1. Final proofread (grammar, typos, consistency)
2. Verify all page limits are met
3. Check font, margins, and formatting requirements
4. Ensure all references are complete and correctly formatted
5. Verify all required documents are included (use agency checklist)
6. Confirm letters of support have been received
7. Upload to eRA Commons / Research.gov / submission portal
8. Submit 24-48 hours before the deadline (system overload is common on deadline day)
9. Confirm receipt of submission and check for errors/warnings

**Deliverable:** Submitted proposal with confirmation receipt.

---

## Analysis Templates

### Template 1: Specific Aims Page (NIH)

```
# Specific Aims

[HOOK: 2-3 sentences establishing the problem and its importance]

[GAP: 2-3 sentences identifying what is unknown]

The long-term goal of [our/my] research program is to [broad vision]. The objective
of this application, which is [the next step / the first step] toward attainment of
that goal, is to [specific objective]. Our central hypothesis is that [testable
statement]. This hypothesis has been formulated on the basis of [preliminary data /
published evidence] showing [key finding]. The rationale for the proposed research
is that [why this work needs to be done now], which will [expected outcome / benefit].

We are well prepared to pursue this work because [relevant expertise, preliminary
data, resources]. Guided by strong preliminary data, we will test our central
hypothesis and accomplish the objective of this application by pursuing the following
specific aims:

Aim 1: [Action verb] [what]. [Hypothesis]. [Brief approach]. [Expected outcome].

Aim 2: [Action verb] [what]. [Hypothesis]. [Brief approach]. [Expected outcome].

Aim 3: [Action verb] [what]. [Hypothesis]. [Brief approach]. [Expected outcome].

[IMPACT: 2-3 sentences]. The proposed research is [significant/innovative] because
[reason]. This contribution will be significant because it is expected to [advance
the field / shift current paradigms / provide new understanding]. Ultimately, this
work will [broader impact on health / science / society].
```

### Template 2: Budget Justification

```
# Budget Justification

## Senior/Key Personnel
[PI Name], PhD, Principal Investigator ([X]% effort, [Y] calendar months)
Dr. [Name] will provide overall scientific direction, supervise trainees, analyze
data, and prepare manuscripts. Expertise in [area] is essential for [aspects].

[Co-I Name], MD/PhD, Co-Investigator ([X]% effort)
Dr. [Name] will [responsibilities]. Expertise in [area] is critical for Aim [N].

## Other Personnel
[Postdoc Name], Postdoctoral Fellow (100% effort) — experimental work for Aims [N-N].
Graduate Research Assistant (50% effort) — [specific tasks] under Aims [N-N].

## Equipment (>$5,000): [Equipment] — $[cost]. [Why needed, which aims].
## Supplies — $[total/year]: Grouped by aim with per-item costs.
## Travel — $[total/year]: [Conference] for dissemination; [collaborator visit].
## Consortium — [Institution] ($[total]): [Contribution, why external, letter of support].
```

### Template 3: Research Strategy Outline (R01)

```
# Research Strategy

## A. Significance

### A.1 Importance of the Problem
[Paragraph on disease burden, prevalence, unmet need, societal impact]

### A.2 Rigor of Prior Research
[Paragraph critically evaluating existing literature — what is known, quality
of evidence, gaps, conflicting findings]

### A.3 How This Project Will Improve Knowledge
[Paragraph on expected advances and how they will change the field]

## B. Innovation

### B.1 Novel Concepts
[How the central hypothesis challenges existing paradigms]

### B.2 Novel Approaches
[New methods, technologies, or interdisciplinary approaches]

### B.3 Novel Application
[Applying existing tools in new contexts or combinations]

## C. Approach

### C.0 Preliminary Data
[Figures and text demonstrating feasibility and supporting the hypothesis]
- Figure 1: [Description]
- Figure 2: [Description]
- Table 1: [Description]

### C.1 Aim 1: [Full aim statement]

#### C.1.1 Rationale
[Why this aim is needed; hypothesis]

#### C.1.2 Experimental Design
[Variables, controls, conditions, sample size with power analysis]

#### C.1.3 Methods
[Detailed protocols for each experiment]

#### C.1.4 Expected Outcomes
[What results are expected; how they will be interpreted]

#### C.1.5 Potential Problems and Alternative Approaches
[What could go wrong; Plan B]

### C.2 Aim 2: [Full aim statement]
[Same subsection structure as Aim 1]

### C.3 Aim 3: [Full aim statement]
[Same subsection structure as Aim 1]

### C.4 Timeline and Milestones

| Milestone | Aim | Quarter | Go/No-Go Criteria |
|-----------|-----|---------|-------------------|
| [milestone] | 1 | Q1-Q4 | [measurable criterion] |
| [milestone] | 2 | Q4-Q8 | [measurable criterion] |
| [milestone] | 3 | Q8-Q16 | [measurable criterion] |

### C.5 Rigor and Reproducibility
[Biological variables, authentication of key resources, blinding,
randomization, statistical methods, data management]
```

---

## Multi-Agent Workflow Examples

**"Write an R01 Specific Aims page for a cancer immunotherapy project"**
1. Research Grants (this skill) -> Draft the Specific Aims page with hook, gap, hypothesis, 3 aims, and impact statement
2. Literature Deep Research -> Systematic review of recent immunotherapy advances for the Significance section
3. Hypothesis Generation -> Refine the central hypothesis based on preliminary data

**"Prepare an NSF CAREER proposal on machine learning for climate modeling"**
1. Research Grants (this skill) -> Structure the 15-page Project Description with Intellectual Merit and Broader Impacts
2. Literature Deep Research -> Survey the ML-for-climate literature landscape
3. Competitive Intelligence -> Analyze funded NSF awards in this area to identify white space

**"Resubmit an NIH R01 that scored in the 30th percentile"**
1. Research Grants (this skill) -> Draft the 1-page Introduction addressing all reviewer critiques point-by-point
2. Peer Review -> Evaluate the revised proposal from a reviewer's perspective before resubmission
3. Literature Deep Research -> Gather new references to strengthen the Innovation section

**"Write a budget justification for a multi-site clinical trial grant"**
1. Research Grants (this skill) -> Draft the budget justification with personnel, equipment, supplies, travel, and subcontracts
2. Clinical Trial Protocol Designer -> Ensure the budget aligns with the trial protocol requirements
3. FDA Consultant -> Assess IND requirements that may affect budget (regulatory costs, DSMB, etc.)

**"Develop an ERC Starting Grant proposal for a structural biology project"**
1. Research Grants (this skill) -> Structure the Part B1 (5-page synopsis) and Part B2 (15-page proposal)
2. Literature Deep Research -> Build the state-of-the-art section with systematic literature coverage
3. Hypothesis Generation -> Develop the groundbreaking hypothesis that justifies ERC-level funding

---

## Completeness Checklist

- [ ] Funding mechanism identified and matched to project scope, budget, and PI career stage
- [ ] Specific Aims page drafted with hook, gap, long-term goal, objective, hypothesis, aims, and impact
- [ ] Each aim has a testable hypothesis, clear methods, expected outcomes, and alternative approaches
- [ ] Significance section establishes the problem, critiques prior research, and articulates the advance
- [ ] Innovation section identifies novel concepts, approaches, or applications
- [ ] Approach section includes preliminary data, detailed methods, power analyses, and timeline
- [ ] Budget justified for all categories (personnel, equipment, supplies, travel, subcontracts)
- [ ] Letters of support identified and requested from all collaborators and core facilities
- [ ] Biosketch and personal statement prepared for all key personnel
- [ ] Human subjects, vertebrate animals, and other compliance sections addressed (if applicable)
- [ ] Data management / resource sharing plan completed per agency requirements
- [ ] Formatting verified: page limits, font, margins, required sections present
- [ ] Internal review completed by 3+ colleagues (domain expert, non-expert, grants specialist)
- [ ] For resubmission: Introduction page addresses all reviewer critiques point-by-point
- [ ] Submission portal tested and proposal uploaded 24-48 hours before deadline
