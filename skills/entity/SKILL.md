---
name: entity
description: "Corpus-routed vertical AI scaffold with 29-check Quality Gate (QG29). 7 corpora: WTP/VALUE GAP, marketing growth (viral/K-factor), monetization (SaaS/AI pricing), human_edge (behavioral economics), competitive_intelligence (CI/win-loss), ei_survival (cognitive sovereignty), driller (AI-tech monetization drill-down by vertical/persona). -cc flag for explicit corpus creation. All domain facts require [GROUNDED:doc_id]. Entity base + Corpus Router + domain grounding."
status: stable
---

# /entity — Corpus-Routed Vertical AI Scaffold

**Base**: Entity pipeline (Step 0 Outward Reception + Mode A/B/C/D + L1/L2 dispatch)
**Added layer**: Corpus Router + Corpus Pre-step — domain signal detection → active_corpus → named retrieval, all domain facts require [GROUNDED:doc_id]
**Quality**: Paper-tier — grounding wall enforced, claim classification mandatory

```
Corpus Router
  ├─ corpus_mode="corpus"  → Corpus Pre-step → Step 0 → Modes → Claim Grounding → Output
  └─ corpus_mode="generic" →                   Step 0 → Modes →                   Output
```

## Domain Hierarchy

```
knowledge_base/
├── demand_theory/        # WHY people buy
│   └── wtp (VALUE GAP) ✅  ← L2
├── go_to_market/         # HOW to reach market
│   ├── marketing_growth ✅  ← L2 (viral/K-factor/loops)
│   └── monetization ✅     ← L2 (SaaS/AI pricing)
├── product/              # WHAT to build (unregistered)
└── research/             # HOW to know (unregistered)
```

**Corpus definitions**: See `corpus-registry.yaml` in this directory.
**Layer**: L1=pure theory, L2=applied, L3=product-specific.
**Cross-domain routing**: primary trigger → confidence-scored; related_domain → conf=0.30; no-match → Auto-Corpus Builder.

## Wave1 Strategy Mode

Detects live-inf Wave1 PROMPT signals (`"do not implement"`, `"approach:"`, etc.).
If detected: skip corpus routing, emit structured strategy output (APPROACH/METHOD/KEY_DECISIONS/ANTI_PATTERNS) with `[ENTITY_GROUNDING_METRICS]` footer, then STOP.

## Activation

```
/entity [question]         ← default: /conceptual direct (no corpus)
/entity -c [question]      ← Mode A: corpus routing + /conceptual
/entity -cr [question]     ← Mode B: corpus + external RAG + /conceptual
/entity -cd [question]     ← Mode D: corpus + L1 reframe + L2 dispatch
/entity -crd [question]    ← Mode C: corpus + L1 + L2 + RAG + L1 2nd
/entity -cc [question]     ← CREATE: explicit corpus build (skip routing → Step 1.5 guard → build)
/entity -ccr [question]    ← CREATE + RAG-enriched research during doc generation
/entity -ccd [question]    ← CREATE + L1 reframe + L2 dispatch after corpus built
/entity -ccrd [question]   ← CREATE + full Mode C pipeline (RAG + L1 + L2) after corpus built
/entity -l [question]      ← entity-live handoff
/entity -i [question]      ← entity-inf handoff
```

Flag parser: `-c` enables Corpus Router (opt-in). `-cc` bypasses routing and forces corpus creation (overlap guard still runs). `-l`/`-i` route to entity-live/entity-inf. Without `-c`/`-cc`, skip Corpus Router entirely → Step 0 direct.

**`-cc` flag behavior**: Skip Corpus Router → run Step 1.5 Overlap Guard → if CLEAR: proceed to Auto-Corpus Builder → after corpus built, run mode suffix (`r`/`d`/`rd`) against the newly created corpus. If WARN: show overlap report + ask user to confirm before proceeding.

---

## Protocol

### Session Resume Check (first call only)

Check `.omc/corpus-miss-log.json`. If any domain has `count >= 2` and not `auto_corpus_triggered`: background-run Auto-Corpus Builder Steps 2-6.

### Corpus Router (only with `-c` flag)

**Multi-turn routing**: If `session_corpus_state` exists and prev corpus overlap ≥ 0.15, maintain corpus. Otherwise re-route.

```python
# 1. Extract signals (token + phrase)
query_norm = query.lower().replace("-","").replace("_","")
token_signals = [normalize(t) for t in query.split() if len(t) > 1]
# Add particle-stripped forms

# 2. Match against CORPUS_REGISTRY (from corpus-registry.yaml)
# Token overlap + phrase substring matching
# IDF weighting: corpus-specific triggers get confidence boost

# 3. Selection logic
if matched == 1: confidence = IDF-weighted recall
elif matched > 1:
    if primary_conf >= 0.25 and secondary_conf >= 0.20: corpus_mode = "dual"
    else: primary only
elif matched == 0:
    # Check related_domains (conf=0.30, context modifier filter)
    # If still no match: Auto-Corpus Builder blocking (first miss)

# Semantic Fallback Tier (conf < 0.08): LLM call using corpus descriptions
# Confidence gate: conf < 0.08 → generic mode
# Emit [ROUTING REPORT] for corpus/dual modes
# Update session_corpus_state
```

### Corpus Pre-step (corpus/dual mode only)

Generic mode → skip entirely → Step 0.

**Draft Status Guard**: `status == "draft"` → use `[GROUNDED-DRAFT:doc_id]` tags instead of `[GROUNDED:doc_id]`.

**Dual-corpus**: Primary = full pre-step (top 3 docs). Secondary = lightweight (top 1-2 docs, 500 tok max). Tags: primary `[GROUNDED:doc_id]`, secondary `[X-GROUNDED:corpus.doc_id]`.

```
0. RWR Pre-step: translate surface terms via active_corpus.rwr_hints
   Multi-aspect decomposition: detect compound queries ("그리고", "also", multiple "?")
   → sub_questions[] for completeness check

1. Query classification: taxonomy_groups → select doc group
2. Doc selection: confidence ≥ 0.90 → 2 docs; < 0.90 → 3 docs; multi-group → 4 docs
   Product-scope guard: product_docs → PRODUCT-SCOPE WARN for non-product queries
3. Scope Gate: all conditions YES → proceed; any NO → STOP + out_action
4. Core Theory injection: always in context
5. → Step 0

CRAG-lite: post-load, if filename/title overlap = 0 → swap to next doc in taxonomy group
```

### Auto-Corpus Builder (generic fallback → corpus)

Trigger: first miss (blocking, synchronous) OR explicit `-cc` flag.

```
Step 1: Domain signal extraction (noun clustering → hierarchy mapping)

Step 1.5: Registry Overlap Guard (MANDATORY — runs before any research)
  Load all corpora from corpus-registry.yaml → extract {name, domain, trigger[0:10]}
  Compare new domain signals vs existing trigger sets (token overlap + semantic check)
  
  overlap ≥ 0.55 → ABORT
    Emit: [OVERLAP BLOCK] Existing corpus '{name}' covers this domain.
    Route to existing corpus (corpus_mode = "corpus") + log miss.
    For -cc flag: show overlap report, ask "Extend existing corpus instead? (y/n)"
  
  overlap 0.25–0.54 → WARN
    Emit: [OVERLAP WARN] Partial match with '{name}' (overlap={score:.2f}).
    For routing miss: proceed but tag new corpus with `related_to: [name]`
    For -cc flag: show overlap report + require user confirmation before Step 2.
  
  overlap < 0.25 → CLEAR → proceed to Step 2

Step 2: expert-research-v2 (2+ WebSearch) → draft doc saved
  For -ccr flag: 4+ WebSearch, include competitor/adjacent domain sources
Step 3: Auto-generate Corpus YAML (name, trigger, core_theory, scope_gate, sycophancy_checks, gap_patterns, rwr_hints, status: draft)
  corpus_root: ~/.claude/skills/entity/corpora/{name}/
  Append to corpus-registry.yaml (do NOT overwrite existing entries)
Step 4: Quality validation (6 checks: core_theory formula, 3+ sycophancy, 2+ scope_gate, 2+ gaps, 5+ triggers, 2+ web sources)
  - 6/6 → auto-promote to stable (if IDF specificity + routing validation pass)
  - 4-5/6 → draft (human review needed)
  - <4/6 → retry Step 2 (max 1×)
Step 5: Promotion pipeline — generate T1/T4/D1/S1 docs, update SKILL.md registry, DOC_INDEX.md
Step 6: Bootstrap Convergence Gate — routing_precision ≥ 0.80, doc_count ≥ 5, T/D HIGH-tier ≥ 40%
  PASS → corpus_mode = "corpus" (use new corpus immediately for -ccr/d/rd suffix)
  FAIL → corpus_mode = "generic" + WARN
```

**`-cc` creation report** (always emitted after Step 6):
```
[CORPUS CREATED] name={name} | status={draft/stable} | docs={count} | overlap_guard={CLEAR/WARN}
corpus_root: {path}
quality_score: {n}/6 | routing_precision: {score}
```

### Step 0 — Outward Reception (Entity + Entity extension)

| Detection | Types |
|-----------|-------|
| Epistemic Basis | data-driven / intuition-first / authority-referencing |
| Causal Model | linear / systemic / emergent |
| Locus of Control | internal / external / distributed |
| Domain Knowledge (corpus only) | novice (0-1 terms) / intermediate (2-3 terms) / expert (precise taxonomy) |

**Gap detection**: corpus mode → `active_corpus.gap_patterns`; generic → default patterns.
Active emission: `[GAP DETECTED: {name}] signal → meaning` for each detected gap.

**Response adaptation**: Opening anchor + closing move matched to epistemic basis.

**Follow-up Detection**: If prior entity response had "다음으로 물어볼 것" and new message answers a D1 Q → `mode = "update"` → diagnostic update protocol (delta view only, no full re-run).

**Outward Profile** (internal, not exposed):
```
epistemic_basis / causal_model / locus_of_control / user_domain_knowledge
gaps: [detected_gaps] → frame / depth / mode (fresh|update)
```

### Mode Branch

```
mode A → Step 1A (/conceptual direct)
mode B → Step 1B (/conceptual + RAG forced)
mode C → Step 1C → Step 2 (RAG forced) → Step 3 → Step 4
mode D → Step 1C → Step 2 (RAG conditional) → Step 3 → Step 4
mode update → diagnostic update output (skip mode branch)
```

**Mode A Auto-Recommendation**: If query needs latest data → suggest -r; execution plan → suggest -d; both → suggest -rd.

### Steps 1A-4

**Step 1A (Mode A)**: Corpus context + /conceptual. Stage 1 Draft → Stage 2 Adversarial → Stage 3 Deliver.

**Conclusion Reservation Rule (all modes, all stages before Stage 3)**:
Analysis body MUST NOT contain conclusive verdicts. Instead:
- Use diagnostic language: "X suggests Y", "evidence points toward Z"
- Reserve definitive statements ("따라서 X이다", "결론적으로") for `[CONCLUSION]` block ONLY
- If a section naturally ends with a verdict → replace with "[→ CONCLUSION]" pointer
- Rationale: scattered mini-conclusions dilute the final `[CONCLUSION]` and confuse readers
  who skip to the end. One convergence point = one place to read the answer.

**Step 1B (Mode B)**: WebSearch + /conceptual with corpus + external context.

**Step 1C (Mode C/D)**: L1 reframing → Refined Query with corpus signals.

**Step 2 (L2 Dispatch)**: Dynamic domain dispatch with corpus pass-through. Corpus context injected into skill args. MoA aggregation for multi-skill results.

**Step 3 (Announce)**: Mode header with corpus/evidence/scope info.

**Step 4 (L1 2nd pass)**: /conceptual with full enrichment.

**Stage 2 Adversarial (all modes, corpus active)**:
- Q0 meta-sycophancy check (always first)
- `active_corpus.sycophancy_checks` with taxonomy-relevance filter
- If relevant_checks = 0 → skip sycophancy loop
- Q-WEAK: top 2 weakest claims (UNCERTAIN/REASONED with < 2 GROUNDED support) → adversarial challenge
- If weak_claims = 0 → skip adversarial

### Claim Grounding Protocol (SELF-RAG + FLARE-lite)

**Stage 1.5 — after Stage 1 Draft, before Stage 2**:

For each domain claim in draft:
- **Step A**: Has [GROUNDED:doc_id]? → keep
- **Step B**: No grounding → FLARE-lite read_corpus → found? [GROUNDED:doc_id] : [UNCERTAIN + verification method]
- **Step C**: Check corpus deprecated claims → replace with current version + [ANTI-PATTERN]
- **Step D**: [IsUse] — does claim contribute to answering the question? NO → [UNUSED]
- **Step E**: Multi-doc grounding — needs 2+ docs? → [GROUNDED: T2+D1, compound basis]
- **Step F**: Doc-tier annotation — T/D=HIGH(⬆), S/V=MED(◆), P=LOW(⬇)

**FAST-PATH** (conf ≥ 0.90 + single taxonomy + 0 UNCERTAIN): skip lazy enrichment, compact Stage 3 output.

**Lazy enrichment** (conf ≥ 0.90, 2 docs): if UNCERTAIN claims found → load max 1 extra doc.

**Cross-doc conflict detection**: if 2+ loaded docs → check numerical/definitional contradictions → tag [INTRA-CONFLICT:HARD/SOFT:docX].

**T3 Conflict Resolution**: T2 > T1, T4 > T2, T3 = trust limits. LLM knowledge < corpus.

**Grounding Wall**: ❌ no corpus = no domain fact emit. ✅ ungroundable → [UNCERTAIN + method].

**Claim tags**:
- `[GROUNDED: doc_id]` — corpus supported
- `[REASONED: doc_id — one-line inference]` — logically derived
- `[UNCERTAIN] → verification: {method}` — ungrounded
- `[UNUSED]` — faithful but irrelevant to question

### Update Output (mode = "update")

Delta view: updated level diagnosis table (prev→new probability), evidence change, remaining uncertainties, updated action implications. No full re-analysis.

**Diagnostic Closure**: Evidence=HIGH + [UNCERTAIN]=0 → "진단 확정" closure.

---

## Pre-output Quality Gate (29 checks)

All checks must PASS before Stage 3 Deliver. Each has a repair_action.

| # | Check | Scope | PASS | FAIL repair |
|---|-------|-------|------|-------------|
| 1 | T4 Scope Gate 통과 | all | 3 conditions YES | Scope-out message + out_action |
| 2 | Grounding rate ≥ 0.85 | corpus | GROUNDED/total ≥ 0.85 | Tiered: light re-tag → heavy SELF-RAG |
| 3 | Claim quality ≥ 0.75 | corpus | tagged/total ≥ 0.75 | Add [REASONED:doc_id:reason] or [UNCERTAIN] |
| 4 | [UNCERTAIN] verification method | corpus | specific method attached | Add concrete method (BDM N≥200, D1 interview) |
| 5 | Deprecated claims absent | corpus | no v1 claims | Replace with v2 + [ANTI-PATTERN] |
| 6 | Stage 2 adversarial executed | all | Q0 + sycophancy [PASS/FLAGGED] | Re-run Stage 2 |
| 7 | No "verified" claims (experiments not run) | all | no false verification | Replace with [UNCERTAIN: design stage] |
| 8 | Corpus References section | corpus | present | Generate from [GROUNDED] tags |
| 9 | Evidence grade (HIGH/MEDIUM/LOW) | all | calculated + in header | Calculate: HIGH=all GROUNDED+PASS; MEDIUM=some REASONED/UNCERTAIN; LOW=UNCERTAIN in core |
| 10 | Knowledge-level template | all | matches user_domain_knowledge | Switch template |
| 11 | Product-scope WARN | corpus | P-doc warns present | Add [PRODUCT-SCOPE WARN] |
| 12 | (dual) Secondary [X-GROUNDED] tags | dual | all secondary facts tagged | Add [X-GROUNDED:corpus.doc_id] |
| 13 | (dual) Primary-secondary contradiction | dual | no conflict or [X-CONFLICT] | Add [X-CONFLICT] comparison |
| 14 | Multi-Q completeness | corpus+multi-Q | each sub_question answered | Add [MULTI-Q REPAIR] |
| 15 | [ENTITY_GROUNDING_METRICS] footer | corpus | present with all 9 fields | Calculate and append |
| 16 | Actionability | corpus+recs | [ACTION: subject+verb+object] | Rewrite vague recs |
| 17 | UNCERTAIN specificity ≥ 0.80 | corpus+UNCERTAIN | concrete method (name+N+timeframe) | Replace vague with specific |
| 18 | Conflict reconciliation 100% | corpus+conflicts | all [RECONCILED:HARD/SOFT] | Add reconciliation tags |
| 19 | Gap coverage ≥ 0.80 | corpus+gaps | detected gaps addressed | Add [GAP ADDRESS] |
| 20 | Core summary in first block | corpus | 1-3 sentence direct answer | Prepend summary |
| 21 | Scope gate assumption audit | corpus | [SCOPE NOTE] with verified/assumed | Add scope note |
| 22 | FAST-PATH compact output | corpus+fast-path | no empty report sections | Remove empty sections |
| 23 | Query-intent alignment ≥ 0.50 | corpus | claims cover original intent | Reroute/add intent note |
| 24 | Routing transparency | corpus | [ROUTING REPORT] emitted | Insert routing report |
| 25 | Doc-tier synthesis priority | corpus | HIGH-tier in core answer | Load T/D-doc or retag |
| 26 | ACTION-UNCERTAIN dominance | corpus+ACTION | uncertain-backed actions retagged | [ACTION-UNCERTAIN] retag |
| 27 | Synthesis caveat | corpus | uncertain_ratio > 0.40 → caveat block | Insert [SYNTHESIS CAVEAT] |
| 28 | Convergent conclusion | all | [CONCLUSION] block present with verdict + confidence + next action | Generate convergent conclusion |
| 29 | CGR compute grounding | all+codebase/env-claim | [CGR:compute_id] tag OR [UNCERTAIN: method] on any model assertion about files/code/tests/env | Execute compute → retag with result, OR retag [UNCERTAIN: method=<specific>] |

**QG28 — Convergent Conclusion (28th QG, mandatory)**:
Every entity response MUST end with a `[CONCLUSION]` block that synthesizes ALL analysis into a definitive verdict. This is the single most important output — users read conclusions, not analysis.

```
[CONCLUSION]
3-line verdict:
  1. {judgment — direct answer to "so what?". e.g., "Don't change strategy now"}
  2. {basis — one sentence of key supporting evidence}
  3. {reversal condition — one sentence on what would flip this}
confidence: {HIGH/MEDIUM/LOW}
immediate_action: {ONE specific next step}
```

FAIL criteria:
- No [CONCLUSION] block → repair: generate from analysis
- **3-line verdict missing or exceeds 3 lines** → repair: compress to judgment/basis/reversal, one sentence each
- Verdict is hedged/vague ("it depends", "further analysis needed") → repair: commit to strongest supported position, state confidence level, add conditional for reversal
- Missing immediate_action → repair: extract from ACTION items
- Conclusion contradicts analysis body → repair: align or explain divergence
- **Scattered conclusions detected** → repair: scan analysis body for conclusive statements
  ("따라서", "결론적으로", "결국", "즉,", "in conclusion", "therefore the answer is");
  if found → rewrite as diagnostic ("evidence suggests...") and consolidate into [CONCLUSION]
- **Convergence check**: verdict must reference the decisive_factor that appears in analysis body.
  If verdict introduces NEW reasoning not in body → FAIL (conclusion must SYNTHESIZE, not ADD)

Design principle: **Corpus grounding exists to SUPPORT conclusions, not replace them.** A well-grounded analysis without a clear conclusion is incomplete. The conclusion must take a position — hedging is only acceptable when evidence is genuinely split (evidence grade LOW), and even then must state which direction the evidence leans.

**QG29 — CGR Compute Grounding (29th QG, mandatory)**:
Compute-Grounded Reasoning — adapted from arXiv:2604.12102 (Spatial Atlas).
Principle: **No model assertion about the codebase, environment, test state, or runtime behavior survives without an executable verification receipt.** If the claim is about something that can be checked with a tool (file existence, grep match, test result, command output, env var value) — check it. Do not assume.

```
[CGR:compute_id]  — claim is backed by an executed compute call
                    compute_id = tool + target, e.g. [CGR:grep:QG26:entity/SKILL.md]
                                                   [CGR:test:pytest -k cgr]
                                                   [CGR:file_exists:scripts/corpus_router.py]
```

Triggers (FAIL if untagged):
- Any claim about file existence, file contents, or directory structure ("X exists in Y", "Y contains Z")
- Any claim about test pass/fail status or coverage numbers ("22/22 pass", "coverage=87%")
- Any claim about codebase structure ("function F calls G", "module M imports N")
- Any claim about runtime environment (version numbers, env vars, installed packages)
- Any reference to a file path, line number, commit hash, or score taken from recent memory

FAIL criteria:
- Claim matches a trigger AND has no [GROUNDED:], [CGR:], or [UNCERTAIN: method] tag → FAIL
- [CGR:compute_id] tag present but compute_id does not reference an actual tool call in this turn → FAIL (fabricated receipt)
- Claim contradicts an earlier [CGR:] receipt in the same response → FAIL (self-contradiction)
- Numeric claim (score, count, percentage) taken from memory without re-verification when stakes are high → FAIL

Repair options (in order of preference):
1. Execute the compute call (Bash/Read/Grep/Glob), retag claim with `[CGR:tool:target]` and include the raw result
2. Retag as `[UNCERTAIN: method=<specific compute call that would resolve this>]` — defers verification with a concrete plan
3. Remove the claim entirely if it is not load-bearing

Interaction with QG26 (ACTION-UNCERTAIN dominance):
- QG26 counts `[UNCERTAIN]` actions. A claim verified via CGR is NOT uncertain — [CGR:] tags lower uncertain_ratio.
- When QG26 FAILs, prefer CGR repair (execute → retag [CGR:]) over [UNCERTAIN:method] repair when the compute is cheap.

Compute cost guard:
- Budget: ≤ 3 CGR calls per response unless response is an audit/verification task (then unlimited)
- If budget exceeded → remaining claims use `[UNCERTAIN: method]` with a concrete deferred plan

Design principle: **Stale memory is the enemy of grounded reasoning.** Corpus grounding ([GROUNDED:]) verifies claims against canonical domain docs. CGR grounding ([CGR:]) verifies claims against current codebase/environment reality. A response that cites a file path, score, or test result from prior session memory without CGR verification is equivalent to hallucination — the state has likely drifted.

**[ENTITY_GROUNDING_METRICS] footer fields** (10 + conclusion_strength):
```
routing_precision | sycophancy_pass | grounding_rate | claim_quality
actionability | action_anchoring | conflict_reconciliation | fast_path | uncertain_ratio | cgr_rate
```
- `cgr_rate` = [CGR:] tags / (total claims matching QG29 triggers). Target ≥ 0.80.

---

## Stage 3 Deliver — Knowledge-Level Adaptive Output

**[SYNTHESIS CAVEAT]**: If uncertain_ratio > 0.40, prepend caveat block before output.

### Template Selection by user_domain_knowledge

**All templates share**: Mode header, core answer, corpus references, **[CONCLUSION] block (mandatory — QG28)**.

**[CONCLUSION] placement**: Always the LAST section before [ENTITY_GROUNDING_METRICS] footer. After all analysis, diagnosis, and action items — the conclusion synthesizes everything into a single actionable verdict.

| Element | novice | intermediate | expert |
|---------|--------|-------------|--------|
| Core answer | metaphor-based, no formulas | formula + intuition bridge | formula + T3 limits |
| Level diagnosis | text (높음/낮음) | 3-row probability table | full % + falsification |
| Analysis | natural language, minimal tags | full tags | tags + [CONFLICT/TRUST LIMIT] |
| Action items | 1-2 steps | P1-P3 table | full + [UNCERTAIN] conditions |
| Scope warning | 1 line | condition list | T4 HC check items |
| Diagnostic note | omit | show if [FLAGGED] | always show |
| Corpus refs | doc names | + sections | + sections + conflicts |
| Follow-up | "When this doesn't apply" | D1 Q + original (1-2) | priority table + Answer Drivers |

### WTP Corpus Template: novice

```markdown
## Entity — [question summary]
### Core Answer
{metaphor-based, no formula}
### Level Judgment (if applicable)
{text: "L4 likelihood is high" — no table}
### Analysis (plain explanation)
{natural language explanation}
### Next Steps (1-2 only)
### When This Doesn't Apply
### Conclusion
[CONCLUSION]
3-line verdict:
  1. {judgment — direct answer to "so what?"}
  2. {basis — one sentence of supporting evidence}
  3. {reversal condition — one sentence on what would flip this}
immediate_action: {ONE thing to do next}
### Sources
```

### WTP Corpus Template: intermediate

```markdown
## Entity — [question summary]
### Core Answer
{formula + intuition bridge}
### Level Diagnosis (if applicable)
| Level | Probability | Signal |
### Analysis
{full tags: [GROUNDED:doc_id], [REASONED:doc_id — reason]}
### Competing Theory Comparison (if applicable)
{VALUE GAP vs JTBD table — trigger: "why?", L1-L2, scope edge}
### Action Implications
| Priority | Action | Basis | Risk/Condition |
### Scope Warning [T4]
### What Would Change This Diagnosis
### Corpus References
### Conclusion
[CONCLUSION]
3-line verdict:
  1. {judgment}
  2. {basis — one sentence}
  3. {reversal condition — one sentence}
confidence: {HIGH/MEDIUM/LOW}
immediate_action: {ONE specific next step}
### Follow-up Questions
{D1 Q number + text, expected signal}
```

### WTP Corpus Template: expert

```markdown
## Entity — [question summary]
### Core Answer
{formula direct + T3 trust limits}
### Differential Level Diagnosis
| Level | Probability% | Key Signal | Falsification Condition |
### Analysis
{full tags + [CONFLICT/TRUST LIMIT:T3]}
### Competing Theory Comparison
### Action Implications
{full P1-Pn with [UNCERTAIN] conditions}
### Scope Warning [T4]
### Diagnostic Notes (Adversarial) ← always included for expert
{[FLAGGED] details + [PASS] list}
### Answer Drivers (diagnosis change conditions) [T4+T3]
### Conclusion
[CONCLUSION]
3-line verdict:
  1. {judgment}
  2. {basis — one sentence including T3 trust limits}
  3. {reversal condition — one sentence}
confidence: {HIGH/MEDIUM/LOW}
immediate_action: {ONE specific next step with measurable criteria}
### Corpus References
### Follow-up Questions
{priority table: question | target signal | change scope}
```

### Generic Fallback Template (non-WTP corpora)

Same 3-tier structure (novice/intermediate/expert) but uses `{active_corpus.domain}` instead of WTP-specific sections. Generic uses intensity markers (STRONG/MODERATE/WEAK) in diagnosis instead of L1-L5.

### Outward Profile Integration (all templates)

Opening anchor and closing move from Step 0 epistemic basis detection.

---

## Output Format

**Evidence grades**: HIGH = all GROUNDED + all PASS. MEDIUM = some REASONED/UNCERTAIN, FLAGGED ≤ 1, or draft corpus. LOW = UNCERTAIN in core, FLAGGED ≥ 2.

**Competing theory trigger**: include when query has "왜?"/cause, L1-L2 diagnosis, scope edge case, or external search finds alternative theory.

---

## Mode Comparison

| | A | B (-r) | C (-rd) | D (-d) |
|--|--|--|--|--|
| Corpus Pre-step | ✅ | ✅ | ✅ | ✅ |
| L1 reframing | ❌ | ❌ | ✅ | ✅ |
| External RAG | ❌ | ✅ forced | ✅ forced | conditional |
| L2 dispatch | ❌ | ❌ | ✅ | ✅ |
| Speed | fast | medium | slow | medium |
| Best for | theory/diagnosis | latest market data | strategy/investor | execution plan |

---

## Fallback & Error Handling

| Failure | Action |
|---------|--------|
| Doc read fail | core_theory from memory, doc marked [UNCERTAIN] |
| Corpus Router no match | Auto-Corpus Builder blocking (first miss) |
| Confidence < 0.08 | generic mode → Step 0 |
| Dual: primary scope FAIL | full STOP |
| Dual: secondary scope FAIL | downgrade to single corpus |
| Claim not in corpus | [UNCERTAIN] mandatory — no silent fallback |
| Follow-up false positive | check prior state → reset to fresh |

## Quick Reference

| Purpose | Command |
|---------|---------|
| Theory/diagnosis | `/entity [q]` |
| + corpus grounding | `/entity -c [q]` |
| + latest market data | `/entity -cr [q]` |
| + execution plan | `/entity -cd [q]` |
| + full pipeline | `/entity -crd [q]` |
| Autonomous bounded | `/entity -l [q]` |
| Autonomous infinite | `/entity -i [q]` |

## Anti-patterns (immediate rejection)

- Corpus-less domain fact emit → [UNCERTAIN] required
- v1 claims ("직장인 L5 WTP 낮다", "Social_Amplifier 순수 곱셈") → v2 replacement
- No scope gate → VALUE GAP inapplicable to impulse/commodity
- "검증됨" for unrun experiments → [UNCERTAIN: design stage]
- Product-doc numbers as universal values → [PRODUCT-SCOPE WARN]
- Employment type as ICP → identity portability [T2]
