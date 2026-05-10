---
name: expert-research
description: "Lean single-agent research protocol — fast, web-grounded, hallucination-reduced. ~3x faster than expert-research-v2. Use this for most research questions. Use expert-research-v2 (3-agent pipeline with adversarial Devil's Advocate) only when deep multi-perspective validation is required."
trigger: manual
tags:
  - research
  - multi-perspective
  - fact-check
  - hallucination-reduction
  - lean
  - web-grounded
---

# Lean Research Protocol (expert-research v2)

Fast, grounded research with multi-perspective analysis and hallucination reduction.
Single-agent architecture that replaces the 3-agent v1 pipeline.

> **Design rationale**:
> - v1 (3-agent): Deep Analyst + Fact Finder + Devil's Advocate = ~4 LLM calls, sequential bottleneck on DA
> - v2 (lean): Web grounding + single multi-lens agent + orchestrator synthesis = ~1 LLM call + web search
> - Same hallucination reduction via: external fact grounding + confidence tagging + adversarial self-check
> - **~3x faster, comparable quality for most research questions**
>
> Academic basis (shared with v1):
> - Du et al. (ICML 2024): Multi-perspective analysis improves factual accuracy
> - Tool-MAD (2026): External search + analysis = 35% improvement over pure LLM reasoning
> - Key insight: The value comes from **role separation** (proposer vs critic), not from agent count

---

## When to use

- Domain-agnostic research questions requiring grounded accuracy
- Questions where LLM knowledge alone is insufficient (need web verification)
- "Research this", "Analyze", "What's the best approach for..."
- When speed matters more than maximum rigor

## When to use v1 (expert-research) instead

- Extremely high-stakes decisions worth the extra verification time
- Questions with known high hallucination risk (future events, obscure domains)
- User explicitly requests full 3-agent pipeline or "deep research"

---

## Phase 1: Web Grounding (Orchestrator — no subagent)

The orchestrator directly performs targeted web research to establish a fact base.

### 도구 선택

| 환경 | 검색 도구 | 페이지 조회 도구 |
|------|----------|----------------|
| **Claude Code** (Anthropic 네이티브) | `WebSearch(query)` | `WebFetch(url, prompt)` |
| **non-Anthropic 모델** (MiniMax, Gemini, Qwen, GLM 등) | `mcp__websearch__search_web(query)` | `mcp__websearch__fetch_url(url)` |

> non-Anthropic 모델 사용 시 네이티브 WebSearch/WebFetch가 없으므로 반드시 MCP websearch 도구로 대체할 것.

```
WebSearch("{core topic} {current year} best practice")
  — 또는 mcp__websearch__search_web("{core topic} {current year} best practice")

WebSearch("{core topic} comparison benchmark")
  — 또는 mcp__websearch__search_web("{core topic} comparison benchmark")

(optional) WebSearch("{core topic} risks pitfalls")

-> Extract top 3-5 relevant URLs

WebFetch(url, prompt="Extract key facts, data points, and expert opinions. Include specific numbers.")
  — 또는 mcp__websearch__fetch_url(url)

-> Compile structured fact sheet
```

**Output**: Fact sheet with numbered entries and source URLs.

```
[FACT-1] ... (source: URL)
[FACT-2] ... (source: URL)
[FACT-3] ... (source: URL)
...
```

**Rules**:
- Minimum 2 web searches, maximum 4
- Prefer official docs, peer-reviewed sources, reputable tech blogs
- Include opposing viewpoints if found
- Note contradictions between sources explicitly
- Skip this phase only for purely code-internal questions (use code-index instead)

---

## Phase 2: Multi-Lens Analysis (Single Agent — sonnet)

One agent performs analysis from 3 expert perspectives with built-in self-critique.
All three lenses run sequentially within a single prompt — no inter-agent overhead.

```
Task(subagent_type="research-deep-analyst",
  model="sonnet",
  description="Multi-lens grounded analysis",
  prompt="Perform a deep, multi-perspective analysis of the question below.
You have web-sourced facts to ground your analysis. Prefer grounded claims over speculation.

## Question
{user_question}

## Web Facts (ground your claims against these)
{phase_1_fact_sheet}

## Analysis Protocol

### LENS 1: Domain Expert
Analyze as a domain specialist. Provide 3-5 key insights.
Tag each claim:
  - [GROUNDED]: Directly supported by web facts above
  - [REASONED]: Logical inference with clear reasoning chain
  - [UNCERTAIN]: Plausible but unverified — flag for user awareness
For each insight, include a steel-man counterargument.

### LENS 2: Devil's Advocate (attack your own Lens 1)
- Which claims are overconfident? Mark [OVERCONFIDENT]
- What's missing from Lens 1? Mark [MISSING]
- Any claims contradicting web facts? Mark [CONFLICT]
- MANDATORY: Find at least 1 substantive flaw. If nothing obvious, look harder.
- Check hidden assumptions that Lens 1 takes for granted.

### LENS 3: Practical Synthesizer (reconcile Lens 1 + Lens 2)
- Confirmed: Lens 1 claim + no Lens 2 critique -> keep, cite source
- Challenged: Lens 2 critique valid -> revise or hedge the claim
- Missing: Lens 2 found gap -> fill with grounded information
- Produce concrete, actionable recommendations

### CONFIDENCE CALIBRATION
Rate overall answer: HIGH (>80%) / MEDIUM (50-80%) / LOW (<50%)
List remaining [UNCERTAIN] items needing further investigation.

## Output Format
### Domain Analysis (3-5 insights with evidence tags)
### Self-Critique (adversarial findings — at least 1 substantive)
### Synthesized Answer (reconciled, actionable)
### Confidence: HIGH/MEDIUM/LOW
### Remaining Uncertainties
### Key Sources (numbered, from web facts)")
```

---

## Phase 3: Synthesis + Quality Gate (Orchestrator)

The orchestrator performs final synthesis and quality check.

### 3-1. Quality Gate (check ALL before output)

- [ ] All [CONFLICT] items resolved or explicitly noted?
- [ ] At least 1 source URL included in final answer?
- [ ] [OVERCONFIDENT] claims revised or hedged?
- [ ] [MISSING] gaps addressed?
- [ ] All internal tags ([GROUNDED], [REASONED], [UNCERTAIN], [CONFLICT], etc.) removed?
- [ ] Answer directly addresses the user's original question?
- [ ] Devil's Advocate critique (Lens 2) is reflected in final answer?

Any "No" -> revise the specific item before outputting.

### 3-2. Final Output Format

```markdown
## [Question Summary]

### Key Answer
[Confirmed insights — highest confidence, grounded in web facts]

### Detailed Analysis
[Multi-perspective synthesized analysis]

### Caveats & Trade-offs
[Revised claims + unresolved tensions from Devil's Advocate lens]

### Recommendations
[Actionable items that survived self-critique]

### Sources
- [Source 1](URL)
- [Source 2](URL)
...

### Further Investigation Needed
[Items that remain uncertain after analysis]
```

---

## Quick Mode (for simple factual questions)

When the question is straightforward and factual:

```
[Phase 1] WebSearch (1-2 queries) -> fact sheet
[Phase 3] Orchestrator direct synthesis (skip Phase 2 agent)
```

- Skip Phase 2 multi-lens agent entirely
- Orchestrator summarizes web facts directly
- ~5x faster than full v2, suitable for simple lookups
- **Do NOT use for complex, nuanced, or high-stakes questions**

---

## v1 vs v2 Comparison

| Aspect | v1 (expert-research) | v2 (lean protocol) |
|--------|---------------------|-------------------|
| Agents | 3 (Analyst + DA + Fact Finder) | 1 (multi-lens) |
| Web search | Fact Finder agent (sonnet) | Orchestrator direct |
| Self-critique | Devil's Advocate (opus, sequential) | Built-in adversarial lens |
| Cross-validation | 3D matrix (elaborate) | Inline confidence + quality gate |
| Speed | ~4 LLM calls + sequential DA | ~1 LLM call + web search |
| Cost | High (opus for DA) | Low (sonnet only) |
| Hallucination reduction | Excellent (structural separation) | Good (grounding + self-critique) |
| Best for | High-stakes, complex | Most research questions |

---

## Documentation (MANDATORY)

Pipeline results MUST be saved as a document. Skipping documentation = pipeline incomplete.

### Save Rules

1. **Path**: `docs/research/[YYYYMMDD]-[topic-summary].md`
2. **Timing**: Before returning final answer to user
3. **DOC_INDEX.md**: Update `docs/DOC_INDEX.md` top table after save
4. **Content**:

```markdown
# [expert-research-v2] {topic summary}
**Date**: {YYYY-MM-DD}  **Skill**: expert-research-v2

## Original Question
{user_question}

## Web Facts
{Phase 1 fact sheet with source URLs}

## Multi-Lens Analysis
### Domain Expert (Lens 1)
{key insights with evidence tags}

### Self-Critique (Lens 2)
{adversarial findings}

### Synthesis (Lens 3)
{reconciled answer}

## Final Conclusion
{Phase 3 output — clean answer presented to user}

## Sources
{URL list}
```
