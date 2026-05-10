---
name: expert-research-v2
description: "Fixed 3-Agent Research Pipeline — Deep Analyst (hypothesis generation) + Devil's Advocate (adversarial validation) + Fact Finder (external fact-checking). Cross-validation matrix minimizes hallucinations. Domain-agnostic, general-purpose."
trigger: manual
tags:
  - research
  - multi-agent
  - expert
  - cross-validation
  - fact-check
  - hallucination-reduction
---

# Fixed 3-Agent Research & Cross-Validation Skill

Three fixed experts perform independent parallel analysis, then the orchestrator synthesizes results through a cross-validation matrix to produce hallucination-minimized answers.

> **Design Rationale** (academic basis):
> - Du et al. (ICML 2024): 3 agents, 2 rounds is cost-optimal
> - A-HMAD (Springer 2025): Heterogeneous role assignment → factual errors **reduced by 30%+**
> - Tool-MAD (2026): RAG + web search + debate → **35% improvement** over base MAD
> - ChatEval (ICLR 2024): Identical roles = sycophancy cascade → **role diversity is essential**
>
> vs `biz-synthesis`: Fixed 3 business-specific → **This skill: domain-agnostic, general-purpose**
> vs `marl-5stage`: Single LLM, 5 roles sequential → **This skill: multi-agent parallel + external source verification**
> vs `biz-sales-mda`: User selects agents → **This skill: fixed 3 agents, just ask a question**

---

## Fixed 3 Agents

| Role | Agent | Model | Core Mission |
|------|-------|-------|-------------|
| **Deep Analyst** | `research-deep-analyst` | sonnet | Auto domain detection + multi-angle hypothesis generation + evidence tagging |
| **Devil's Advocate** | `review-harsh-critic` | opus | Assumption attacks + counterarguments + bias removal + gap detection |
| **Fact Finder** | `research-doc-specialist` | sonnet | External fact gathering via WebSearch/WebFetch + source URLs |

**Role Separation Principles** (based on A-HMAD + Tool-MAD):
1. **Generator ≠ Validator**: Deep Analyst creates hypotheses, Devil's Advocate attacks them
2. **Internal knowledge ≠ External facts**: LLM reasoning (Deep Analyst) and web facts (Fact Finder) are collected separately
3. **Structural critique protection**: Devil's Advocate must never flatter — "must find at least 1 substantive flaw"

---

## Full Pipeline (2-Stage Sequential Structure)

```
User question
    |
[Phase 1] Parallel execution (single response block, 2 simultaneous)
    ├── Deep Analyst: Domain detection + multi-angle analysis + evidence tagging
    └── Fact Finder: WebSearch/WebFetch external fact collection
    |
[Phase 1.5] Sequential execution (Phase 1 results as input)
    └── Devil's Advocate: Receives Analyst's actual analysis + Fact Finder's facts, then launches precise attacks
    |
[Phase 2] Cross-validation matrix (orchestrator directly)
    ├── 2-1. Fact comparison (Analyst claims vs Fact Finder data)
    ├── 2-2. Critique comparison (Analyst claims vs Devil's Advocate attacks)
    └── 2-3. Three-party consensus matrix
    |
[Phase 3] Synthesis + Final answer
```

**Why 2-Stage**: Devil's Advocate must see Analyst's actual analysis + Fact Finder's actual data before attacking — this yields higher critique accuracy. In parallel execution, DA would resort to "attacking conventional wisdom" and produce misguided critiques (per A-HMAD adaptive ordering rationale).

---

## Phase 1: Parallel Research (2 simultaneous calls in a single response block)

**Deep Analyst + Fact Finder are called simultaneously in one response block.** The two agents are independent, so parallel is optimal.

### Agent 1: Deep Analyst (Parallel)

```
Task(subagent_type="research-deep-analyst", run_in_background=True,
  model="sonnet",
  description="Deep Analyst: multi-angle research",
  prompt="Perform an in-depth multi-angle analysis on the question below.

## Question
{user_question}

## Analysis Rules
1. Auto-detect the domain and apply an appropriate analysis framework
2. Present 3-5 key points, each with an evidence tag:
   - [ESTABLISHED]: Widely known fact
   - [REASONING]: Logical inference (state the basis)
   - [UNCERTAIN]: Plausible but needs verification
3. Present a steel-man counterargument for each point
4. Identify at least 2 risks/trade-offs
5. Describe [UNCERTAIN] items specifically enough for Fact Finder to verify

## Response Format
### Domain: [detected domain]
### Framework: [applied analysis framework]

### Key Analysis (3-5 points)
- Point 1: [claim] — [ESTABLISHED/REASONING/UNCERTAIN] — Confidence: HIGH/MED/LOW
  - Counterargument: [counterargument]
- Point 2: ...

### Risks & Trade-offs (2 or more)
### Actionable Recommendations (specific, actionable level)
### Items Needing Verification ([UNCERTAIN] list)")
```

### Agent 3: Fact Finder (Parallel)

```
Task(subagent_type="research-doc-specialist", run_in_background=True,
  model="sonnet",
  description="Fact Finder: web search verification",
  prompt="Use WebSearch and WebFetch to collect the latest facts and data on the question below.
You must retrieve information from actual web sources, not LLM knowledge.

## Question
{user_question}

## Collection Targets
1. Latest information from official docs/blogs (prioritize 2025-2026)
2. Benchmarks, statistics, comparison data
3. Expert opinions/technical blogs (source URL required)
4. Related GitHub issues, Stack Overflow answers, and other community consensus
5. Collect opposing views/critical perspectives in a balanced manner

## Source Authority Ranking (apply to all collected facts)
Tag each fact with its source tier:
- [S1] Peer-reviewed paper / official spec / primary dataset → highest trust
- [S2] Official vendor blog / well-known technical publication → high trust
- [S3] Community blog / Stack Overflow accepted answer / GitHub issue → medium trust
- [S4] Unattributed blog / forum post / social media → low trust (include only if no S1-S3 available)
When two sources conflict: prefer S1 > S2 > S3 > S4. State the conflict explicitly.

## Response Format
### Collected Facts (each with source URL)
- [FACT-1] ... (source: URL)
- [FACT-2] ... (source: URL)
...

### Latest Trends (2025-2026)
...

### Conflicting Information (if any)
- Claim A: ... (source: URL)
  vs Claim B: ... (source: URL)

### Community Consensus (if any)
...")
```

---

## Phase 1.5: Devil's Advocate (Based on Phase 1 results — Sequential call)

**Called after both Deep Analyst + Fact Finder results from Phase 1 have arrived.** DA must see actual analysis and actual facts to achieve high critique accuracy.

### Agent 2: Devil's Advocate (Sequential)

```
Task(subagent_type="review-harsh-critic",
  model="opus",
  description="Devil's Advocate: evidence-based critique",
  prompt="Below are the Deep Analyst's analysis results and the Fact Finder's collected external facts.
Read both results and attack the weaknesses in the Analyst's analysis.
Prioritize claims that conflict with Fact Finder data.

## Original Question
{user_question}

## Deep Analyst Analysis Results
{analyst_result}

## Fact Finder Collected Facts
{fact_finder_result}

## Critique Rules (structural protection — absolutely no flattery)
1. Review each of the Analyst's key points one by one
2. Mark claims that conflict with Fact Finder data with [FACT-CONFLICT] tag
3. Rate each critique by severity: CRITICAL (core premise collapses) / MAJOR (significant flaw) / MINOR (improvable)
4. You MUST find at least 1 CRITICAL or MAJOR critique — if none found after 2 rounds of deeper analysis, write: "NONE_FOUND: [rationale why this analysis is genuinely robust]" and continue (do not block the pipeline)
5. Mark claims the Analyst tagged [ESTABLISHED] that are actually questionable with [OVERCONFIDENT] tag
6. Mark perspectives or risks the Analyst missed with [MISSING] tag
7. Mark suspicious Analyst claims not covered by Fact Finder with [DOUBT] tag

## Response Format
### Critique per Analyst Analysis Point
- Point 1: [agree/disagree/conditional] — Reason: ...
  - [FACT-CONFLICT] / [OVERCONFIDENT] / [MISSING] (where applicable)
- Point 2: ...

### Overall Critique (by severity)
- CRITICAL: [critique] — Reason: ... — Basis: [Fact Finder FACT-n or logical flaw]
- MAJOR: [critique] — Reason: ...
- MINOR: [critique] — Reason: ...

### Hidden Assumptions (premises the Analyst did not state explicitly)
- Assumption 1: ... — Why it's risky: ...

### [DOUBT] Items (need additional verification)
- [DOUBT] [suspicious claim] — Why suspicious: ...

### Alternative Perspectives
[viewpoints or counterexamples the Analyst did not consider]")
```

---

## Phase 2: Cross-Validation Matrix (Performed directly by the orchestrator)

Once all 3 results from Phase 1 + Phase 1.5 have arrived, the orchestrator creates a **3-dimensional cross-validation matrix**.

### 2-1. Fact Comparison (Deep Analyst vs Fact Finder)

Compare each of the Deep Analyst's claims against Fact Finder results:

```
| Analyst Claim | Evidence Tag | Fact Finder Verification | Verdict |
|---------------|-------------|-------------------------|---------|
| Claim 1: "..." | [ESTABLISHED] | FACT-3: "..." (source: URL) | CONFIRMED |
| Claim 2: "..." | [REASONING] | No related facts | UNVERIFIED |
| Claim 3: "..." | [UNCERTAIN] | Conflicts with FACT-1 | CONTRADICTED |
```

Verdict criteria:
- **CONFIRMED**: Matches Fact Finder data → Include in final answer (with source)
- **CONTRADICTED**: Conflicts with Fact Finder data → Exclude or state "conflicting views exist"
- **UNVERIFIED**: Cannot be verified → Mark as "requires expert opinion or independent verification"

### 2-2. Critique Comparison (Deep Analyst vs Devil's Advocate)

Apply Devil's Advocate critiques against the Deep Analyst's analysis:

```
| DA Critique | Severity | Analyst Response | Resolution |
|------------|----------|-----------------|------------|
| Critique 1: "..." | CRITICAL | Not mentioned in analysis | VALID → Include as warning in final answer |
| Critique 2: "..." | MAJOR | Partially addressed in Point 3 | PARTIAL → Needs supplement |
| Critique 3: "..." | MINOR | Already mentioned as counterargument | ADDRESSED → Keep existing analysis |
```

Resolution criteria:
- **VALID**: Substantive flaw the Analyst missed → Reflect as warning/caveat in final answer
- **PARTIAL**: Partially addressed → Supplement and reflect
- **ADDRESSED**: Already addressed → Keep existing analysis
- **OVERREACH**: Critique is excessive (Realist Check applied) → Ignore

### 2-3. Three-Party Consensus Matrix

```
| Topic | Deep Analyst | Devil's Advocate | Fact Finder | Consensus Level |
|-------|-------------|-----------------|-------------|----------------|
| Topic 1 | Agree (HIGH) | Conditional disagree | CONFIRMED | STRONG |
| Topic 2 | Claim X | CRITICAL critique | CONTRADICTED | REJECT |
| Topic 3 | [UNCERTAIN] | [DOUBT] | No related facts | UNRESOLVED |
```

Consensus levels:
- **CONFIRMED-STRONG**: Analyst claim + Fact Finder confirmed + DA no/weak critique → Highest confidence
- **STRONG**: 2/3 support → High confidence (minority view also recorded)
- **CONTESTED**: Analyst claim exists but DA has CRITICAL/MAJOR critique → Medium confidence (state trade-offs)
- **REJECT**: Fact Finder CONTRADICTED + DA CRITICAL → Exclude
- **UNRESOLVED**: Cannot verify + opinions divided → "Further investigation needed"

### 2-4. [UNCERTAIN] + [DOUBT] Tag Cross-Processing

- Analyst's `[UNCERTAIN]` + DA's `[DOUBT]` = same item → **High suspicion** → Attempt matching in Fact Finder results
- Analyst's `[UNCERTAIN]` + Fact Finder CONFIRMED = → Confidence upgraded, remove tag
- DA's `[DOUBT]` + Fact Finder CONTRADICTED = → Remove that claim

---

## Phase 3: Synthesis — Final Answer Generation

Compose the final answer based on the cross-validation matrix.

### Synthesis Rules

1. **CONFIRMED-STRONG items first** → Backbone of the core answer
2. **STRONG items** → Include in main analysis
3. **CONTESTED items** → Include as "This is the mainstream view, but [DA critique] exists" (cite DA critique explicitly)
4. **REJECT items** → Remove or state "may not be factually accurate"
5. **UNRESOLVED items** → Place in separate "Further Verification Needed" section
6. **Facts with sources** → Include URLs inline or as footnotes
7. **Remove ALL internal tags** ([ESTABLISHED], [REASONING], [UNCERTAIN], [DOUBT], FACT-n, etc.)

### Output Format

```markdown
## [Question Summary]

### Core Answer
[Based on CONFIRMED-STRONG + STRONG — highest confidence content]

### Detailed Analysis
[Deep Analyst's unique insights that passed verification]

### Caveats and Trade-offs
[CONTESTED items — present both sides with Devil's Advocate critiques]

### Actionable Recommendations
[Recommendations that passed cross-validation]

### Reference Sources
- [Source 1](URL)
- [Source 2](URL)
...

### Further Investigation Needed
[UNRESOLVED items — things that cannot be confirmed at this time]
```

---

## Quality Gate (Pre-synthesis check)

Verify before returning the synthesis to the user:

- [ ] Have REJECT items been removed/flagged in the final answer?
- [ ] Is at least 1 source URL included?
- [ ] Have all internal tags ([ESTABLISHED], [DOUBT], FACT-n, etc.) been removed?
- [ ] Are Devil's Advocate critiques shown alongside CONTESTED items?
- [ ] Are perspectives from 2+ of the 3 agents reflected?
- [ ] Were Devil's Advocate CRITICAL critiques not ignored?

If any answer is No → Rewrite the synthesis.

---

## Lightweight Mode: Quick Research

**Use Lightweight Mode when ALL of the following are true:**
1. Question is factual/lookup (not analytical, evaluative, or requires synthesis)
2. Single domain (not cross-disciplinary)
3. High-quality official sources likely available (S1/S2)
4. No decision with significant consequences depends on this answer

**Use Full Mode (default) when ANY of the following:**
- Question involves trade-offs, comparisons, or "best approach" judgments
- Conflicting community opinions are likely
- Answer will inform architecture, security, or business decisions
- Question has a strong prior belief that needs adversarial validation

When speed matters and Lightweight Mode criteria are met:

```
[Phase 1] 2 parallel (Deep Analyst + Fact Finder)
[Phase 2] Simplified fact comparison (orchestrator directly)
[Phase 3] Synthesis
```

- Skip Devil's Advocate → 1.5x speed
- Hallucination suppression relies on fact comparison alone
- **Do NOT use for complex questions** — risk of bias without critique

---

## Comparison with Existing Skills

| Aspect | expert-research (v2) | biz-synthesis | biz-sales-mda | marl-5stage |
|--------|---------------------|--------------|---------------|-------------|
| Domain | **General-purpose** | Business only | User-selected | General-purpose |
| Agents | **Fixed 3** | Fixed 3 types + critic | User-selected 3 | 1 (5 roles) |
| Role Design | Proposer+Adversary+Grounder | Analysis+Critique | Debate | Sequential verification |
| WebSearch | **Fact Finder dedicated** | None | None | None |
| Fact-checking | **CONFIRMED/CONTRADICTED** | Critique only | Cross-critique | S4 Verifier |
| Anti-flattery | **Structural protection** (DA mandatory critique) | None | Round separation | Temperature control |
| Hallucination suppression | 3D cross-validation + external sources | Critique only | 3R debate | 5-stage internal verification |
| Source inclusion | **URLs included** | None | None | None |

---

## Design Rationale: Why These 3 Agents

### 1. Deep Analyst (Proposer)
- Fulfills the **MoA Proposer** + **A-HMAD logical reasoning agent** role
- Maintains the benefits of dynamic expert selection via auto domain detection, consolidated into a single agent
- Evidence tags ([ESTABLISHED/REASONING/UNCERTAIN]) serve as anchor points for cross-validation

### 2. Devil's Advocate (Adversary)
- **A-HMAD**: Adding an adversarial agent reduces factual errors by 30%+
- **IUI 2024**: Devil's Advocate is most effective at preventing overconfidence
- **ICLR 2025**: Structurally forced critique is essential to prevent sycophancy cascade
- Uses Opus model: Critique quality determines overall pipeline accuracy

### 3. Fact Finder (Grounder)
- **Tool-MAD (2026)**: External search + debate → 35% improvement over base MAD
- Separating LLM reasoning (Agent 1+2) from external facts (Agent 3) is the key to hallucination suppression
- Source URLs ensure the final answer is verifiable

### Why Not Have a Separate Synthesizer Agent
- ChatEval's Summarizer is 1 of 3 agents → only 2 agents actually do analysis
- All 3 agents are used as "analysis labor," while synthesis is performed directly by the orchestrator (main Claude)
- The orchestrator can see all 3 results, making it optimal for cross-validation

---

## Documentation Obligation (MANDATORY)

After pipeline execution, **agent responses and final conclusions must be saved as a document**. Skipping documentation means the pipeline is considered **incomplete**.

### Saving Rules

1. **Save path**: `docs/research/[YYYYMMDD]-[topic-summary].md` (project docs folder)
2. **Save timing**: **Just before** returning the final answer to the user
3. **DOC_INDEX.md update**: After saving, register in the top table of `docs/DOC_INDEX.md`
4. **Save content**:

```markdown
# [expert-research] {topic summary}
**Date**: {YYYY-MM-DD}  **Skill**: expert-research

## Original Question
{user_question}

## Agent Response Summary
### Deep Analyst
{Analyst key points + evidence tag summary}

### Fact Finder
{Collected facts + source URL list}

### Devil's Advocate
{CRITICAL/MAJOR critique summary}

## Cross-Validation Matrix
{Phase 2 consensus matrix — CONFIRMED/CONTESTED/REJECT/UNRESOLVED}

## Final Conclusion
{Phase 3 synthesis answer in full}

## Reference Sources
{Fact Finder URL list}
```
