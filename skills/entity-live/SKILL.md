---
name: entity-live
description: "Standalone bounded swarm loop for Entity domains. Explorer-Reasoner-Auditor cycle with 4D Corpus Quality Oracle. Max 5 iterations. omc-independent. Use when corpus-grounded autonomous iteration is needed."
---

# /entity-live — Bounded Corpus Evolution Loop

**Architecture**: Standalone swarm loop — NOT a /live wrapper.
Explorer(gap probe) → Reasoner(/entity execution) → Auditor(validation) per iteration.
4D Corpus Quality Oracle replaces code oracle. omc-independent.

```
entity-live (Bounded Corpus Evolution Loop, max 5 iterations)
  ├── [STIGMERGY]  Corpus State — docs as pheromone trails
  ├── [SWARM]      Explorer (parallel) + Reasoner (sequential) + Auditor (parallel)
  ├── [4D ORACLE]  grounding_rate + routing_precision + claim_quality + sycophancy_pass
  ├── [EVOLVE]     Gap-driven goal elevation (weakest dimension + weakest doc)
  └── [RESEARCH]   Auto-triggered expert-research on corpus gaps
```

Research basis:
- SwarmSys (arXiv:2510.10047): Explorer→Worker→Validator, pheromone stigmergy
- MAE Proposer-Solver-Judge (arXiv:2510.23595): oracle-free self-improving loop
- EvolveR (arXiv:2510.16079): RAG lifecycle with systematic learning

## Activation

```
/entity-live [question]     ← bounded loop (max 5 iterations)
/entity-live -i [question]  ← route to /entity-inf (unbounded)
```

**Flag parser:**
```python
tokens = args.split()
flags = set()
question_tokens = []
for token in tokens:
    if token.startswith("-"):
        flags.update(c.lower() for c in token[1:] if c.isascii() and c.isalpha())
    else:
        question_tokens.append(token)
question = " ".join(question_tokens)

if 'i' in flags:
    → Skill('entity-inf', args=question)
    → STOP
```

## Configuration

```yaml
max_iterations: 5              # bounded ceiling
plateau_k: 3                   # 3 consecutive all-dim stagnant → converge
epsilon: 0.03                  # quality change threshold per dimension
quality_threshold: 0.70        # MAE 0.7 gate — any dim below → not converged
exploration_rate: 0.15         # SwarmSys epsilon-greedy for Explorer
score_ensemble_n: 3            # ensemble scoring (Sakana AI Scientist-v2)
pareto_convergence: true       # ALL 4 dims must plateau simultaneously
state_dir: ".entity"            # omc-independent state directory
```

## Protocol

### PRE-LOOP: Initialize

**Step 0a — Resume Check:**
```python
if .entity/live-state.json exists:
    state = read(".entity/live-state.json")
    if state.status == "ACTIVE":
        restore(state)  # goal, iteration, quality_history, world_model
        emit: "[RESUME] iter {state.iteration}/{max_iterations} | best={state.best_score:.2f}"
        → skip to Step 0c (World Model load)
    elif state.status in ["CONVERGED", "STOPPED"]:
        → fresh start (clear state)

if question is empty:
    → error: "No active goal. Run /entity-live <question> to start."
```

**Step 0b — Initialize State:**
```python
state = {
    "status": "ACTIVE",
    "root_goal": question,
    "original_goal": question,
    "iteration": 0,
    "evolution_count": 0,
    "best_score": 0.0,
    "best_score_vector": {},
    "quality_history": [],
    "plateau_count": 0,
    "started_at": ISO8601_now()
}
write(".entity/live-state.json", state)
emit: "[START] Goal: {question} | Max iterations: {max_iterations}"
```

**Step 0c — World Model Load:**
```python
if .entity/world-model.json exists:
    world_model = read(".entity/world-model.json")
    emit: "[WORLD MODEL] {len(world_model.tried)} tried, {len(world_model.dead_ends)} dead ends"
else:
    world_model = {
        "tried": [],           # {goal, score_vector, iteration, outcome}
        "dead_ends": [],       # strategies that failed 2+ times
        "known_facts": [],     # confirmed truths
        "pheromone": {},       # doc_id → {strength, flagged}
        "research_cache": []   # cached research findings (cross-iteration)
    }
```

**Step 0d — Corpus Stigmergy Init:**
```python
# Load current corpus doc quality as pheromone state
# Read from corpus-registry.yaml (entity skill directory)
for corpus_name, corpus_config in CORPUS_REGISTRY.items():
    for doc_id in corpus_config.docs:
        key = f"{corpus_name}.{doc_id}"
        if key not in world_model.pheromone:
            world_model.pheromone[key] = {"strength": 0.5, "flagged": False}

write(".entity/world-model.json", world_model)
emit: "[STIGMERGY] {len(world_model.pheromone)} corpus docs tracked"
```

---

### MAIN LOOP (max 5 iterations)

```
for iteration in 1..max_iterations:
    Step 1: EXPLORER (parallel)  — gap probe + research trigger
    Step 2: REASONER (sequential) — /entity -crd execution
    Step 3: AUDITOR (parallel)   — consensus validation
    Step 4: QUALITY COMPUTE      — 4D oracle scoring
    Step 5: CONVERGENCE CHECK    — Pareto + plateau
    Step 6: EVOLVE or CONVERGE   — goal elevation or termination
    Step 7: STATE UPDATE         — stigmergy + world model + checkpoint
```

---

#### Step 1: EXPLORER — Gap Probe + Research

Explorer identifies the weakest point in corpus quality and generates an improvement question.
Runs as parallel Agent for real swarm behavior (not sequential self-prompting).

```python
# Compute current corpus stats from quality_history
if quality_history:
    latest = quality_history[-1]
    weakest_dim = min(latest, key=latest.get)
    weakest_score = latest[weakest_dim]
else:
    weakest_dim = "grounding_rate"
    weakest_score = 0.0

# Find weakest doc from pheromone state
flagged_docs = [k for k, v in world_model.pheromone.items() if v["flagged"]]
weak_docs = sorted(world_model.pheromone.items(), key=lambda x: x[1]["strength"])[:3]

# Explorer Agent
explorer_result = Agent(
    subagent_type="research-explore",
    prompt=f"""You are the EXPLORER in a corpus quality swarm.

Current corpus quality:
  Weakest dimension: {weakest_dim} = {weakest_score:.2f}
  Flagged docs: {flagged_docs[:5]}
  Weakest docs: {[d[0] for d in weak_docs]}
  Dead ends (DO NOT retry): {[d['goal'][:50] for d in world_model.dead_ends[-3:]]}

Goal: {state.root_goal}

YOUR TASK:
1. Identify the single most impactful corpus gap to address
2. Generate ONE specific improvement question that, when answered via /entity,
   would improve the weakest dimension
3. If the gap requires external knowledge (latest data, academic papers,
   market research), flag it as [RESEARCH-NEEDED]

Output format (STRICT):
GAP_TARGET: <doc_id or "new_topic">
GAP_DIMENSION: <grounding_rate|routing_precision|claim_quality|sycophancy_pass>
IMPROVEMENT_QUESTION: <specific question for /entity -crd>
RESEARCH_NEEDED: <true|false>
RESEARCH_QUERY: <web search query if RESEARCH_NEEDED=true, else "none">
RATIONALE: <why this gap matters most>
"""
)

# Parse explorer output
gap_probe = parse_explorer_output(explorer_result)

# AUTO-RESEARCH TRIGGER (if Explorer flagged research needed)
if gap_probe.research_needed:
    emit: "[RESEARCH] Explorer triggered research: {gap_probe.research_query}"
    research_result = Agent(
        subagent_type="research-deep-analyst",
        prompt=f"""Research this topic for corpus improvement:
Query: {gap_probe.research_query}
Context: We need to improve {gap_probe.gap_dimension} for Entity corpus.
Goal: {state.root_goal}

Use web search to find recent (2024-2026) data, papers, or frameworks.
Return: key findings with citations. Max 500 words."""
    )
    # Cache research for Reasoner context
    world_model.research_cache.append({
        "iteration": state.iteration,
        "query": gap_probe.research_query,
        "findings": research_result.summary[:500]
    })
    emit: "[RESEARCH] Findings cached for Reasoner"

emit: "[EXPLORER] gap={gap_probe.gap_target} dim={gap_probe.gap_dimension} research={gap_probe.research_needed}"
```

---

#### Step 2: REASONER — /entity Execution

Reasoner executes the Explorer's improvement question through entity's full corpus pipeline.
Sequential — needs corpus context from the routing step.

```python
# Build Reasoner prompt with research context if available
research_context = ""
if world_model.research_cache:
    latest_research = world_model.research_cache[-1]
    research_context = f"\n[RESEARCH CONTEXT]\n{latest_research['findings']}"

# Execute /entity -crd (full pipeline: corpus + RAG + L1→L2→L1)
reasoner_result = Skill("entity", args=f"-crd {gap_probe.improvement_question}{research_context}")

# Extract quality signals from entity response
# entity emits [ENTITY_GROUNDING_METRICS] footer with 9 fields
entity_metrics = parse_entity_metrics(reasoner_result)
# Keys: routing_precision, sycophancy_pass, grounding_rate, claim_quality,
#        actionability, action_anchoring, conflict_reconciliation, fast_path, uncertain_ratio

emit: "[REASONER] entity executed | grounding={entity_metrics.grounding_rate:.2f} claims={entity_metrics.claim_quality:.2f}"
```

---

#### Step 3: AUDITOR — Consensus Validation

Auditor evaluates the Reasoner's output independently. Runs as parallel Agent.
Checks for ungrounded claims, sycophancy violations, and extracts corpus improvement deltas.

```python
auditor_result = Agent(
    subagent_type="review-harsh-critic",
    prompt=f"""You are the AUDITOR in a corpus quality swarm.
Evaluate this entity response for corpus grounding quality.

RESPONSE TO AUDIT:
{reasoner_result.summary[:2000]}

ENTITY METRICS (self-reported):
{entity_metrics}

AUDIT CHECKLIST:
1. Count domain claims WITHOUT [GROUNDED:doc_id] tags → ungrounded_count
2. Check: are any [GROUNDED] tags referencing non-existent or deprecated docs?
3. Sycophancy: does the response agree with premises that should be challenged?
4. T4 falsification: are hard claims stated without falsification conditions?
5. Corpus delta: what specific improvements could be made to corpus docs
   based on gaps found in this response?

Output format (STRICT):
UNGROUNDED_CLAIMS: <count>
PHANTOM_REFS: <count of [GROUNDED] tags to non-existent docs>
SYCOPHANCY_FLAGS: <count of unchallenged questionable premises>
T4_VIOLATIONS: <count of hard claims without falsification>
CORPUS_DELTA: <list of specific doc improvements, max 3>
AUDITOR_SCORE: <0.0-1.0 overall quality assessment>
VERDICT: <PASS|NEEDS_IMPROVEMENT|FAIL>
"""
)

audit = parse_auditor_output(auditor_result)
emit: "[AUDITOR] verdict={audit.verdict} score={audit.auditor_score:.2f} ungrounded={audit.ungrounded_claims}"
```

---

#### Step 4: QUALITY COMPUTE — 4D Oracle

Combines entity self-reported metrics with auditor independent assessment.
No code execution — purely from response analysis.

```python
def compute_quality_vector(entity_metrics, audit, ensemble_n=3):
    """4D Corpus Quality Oracle — replaces code oracle (lint/test/typecheck)."""

    # Primary: entity self-reported metrics (from [ENTITY_GROUNDING_METRICS])
    raw = {
        "grounding_rate":    entity_metrics.get("grounding_rate", 0.5),
        "routing_precision": entity_metrics.get("routing_precision", 0.5),
        "claim_quality":     entity_metrics.get("claim_quality", 0.5),
        "sycophancy_pass":   entity_metrics.get("sycophancy_pass", 0.5),
    }

    # Cross-validation: blend with auditor assessment (reduces self-scoring bias)
    # Auditor score moderates entity's self-report
    auditor_weight = 0.3  # 30% auditor, 70% entity self-report
    if audit.verdict == "FAIL":
        auditor_weight = 0.5  # increase auditor influence on failure

    quality_vector = {}
    for dim in raw:
        base = raw[dim]
        # Auditor adjustments
        if dim == "grounding_rate" and audit.ungrounded_claims > 0:
            penalty = min(0.2, audit.ungrounded_claims * 0.05)
            adjusted = base - penalty
        elif dim == "sycophancy_pass" and audit.sycophancy_flags > 0:
            penalty = min(0.2, audit.sycophancy_flags * 0.1)
            adjusted = base - penalty
        elif dim == "claim_quality" and audit.t4_violations > 0:
            penalty = min(0.15, audit.t4_violations * 0.05)
            adjusted = base - penalty
        else:
            adjusted = base

        quality_vector[dim] = max(0.0, min(1.0,
            base * (1 - auditor_weight) + adjusted * auditor_weight
        ))

    total = sum(quality_vector.values()) / len(quality_vector)
    quality_vector["total"] = total

    return quality_vector

qv = compute_quality_vector(entity_metrics, audit)
state.quality_history.append(qv)

emit: "[4D ORACLE] grounding={qv['grounding_rate']:.2f} routing={qv['routing_precision']:.2f} claims={qv['claim_quality']:.2f} sycophancy={qv['sycophancy_pass']:.2f} | total={qv['total']:.2f}"
```

---

#### Step 5: CONVERGENCE CHECK — Pareto

```python
def check_convergence(quality_history, plateau_k=3, epsilon=0.03, quality_threshold=0.70):
    DIMS = ["grounding_rate", "routing_precision", "claim_quality", "sycophancy_pass"]

    # MAE 0.7 gate: any dimension below threshold → not converged
    latest = quality_history[-1]
    below_threshold = [d for d in DIMS if latest[d] < quality_threshold]
    if below_threshold:
        return "IMPROVE", below_threshold

    # Need at least plateau_k iterations to judge
    if len(quality_history) < plateau_k:
        return "CONTINUE", []

    # Pareto convergence: ALL dimensions stagnant for plateau_k iterations
    recent = quality_history[-plateau_k:]
    stagnant_dims = []
    for d in DIMS:
        values = [r[d] for r in recent]
        if max(values) - min(values) < epsilon:
            stagnant_dims.append(d)

    if len(stagnant_dims) == len(DIMS):
        return "CONVERGED", stagnant_dims
    else:
        improving = [d for d in DIMS if d not in stagnant_dims]
        return "EVOLVE", improving

convergence_status, details = check_convergence(state.quality_history)
```

---

#### Step 6: Decision Branch

```python
if convergence_status == "CONVERGED":
    # Check quality gate
    if qv["total"] >= quality_threshold:
        → CONVERGED_SUCCESS (see Post-Loop)
    else:
        → CONVERGED_STALE (see Post-Loop)

elif convergence_status == "IMPROVE":
    # Below MAE 0.7 threshold on some dimensions
    emit: "[IMPROVE] Below threshold on: {details}"
    # Goal stays the same — focus on weak dimensions
    state.root_goal = f"Improve {details[0]} (currently {qv[details[0]]:.2f} → target ≥ 0.70) for: {state.original_goal}"
    → continue to Step 7 → next iteration

elif convergence_status == "EVOLVE":
    # Some dimensions improving — elevate goal
    emit: "[EVOLVE] Improving dims: {details}"
    weakest_dim = min(DIMS, key=lambda d: qv[d])
    weakest_doc = min(world_model.pheromone.items(), key=lambda x: x[1]["strength"])

    # Goal elevation
    state.root_goal = f"Deepen {weakest_dim} (currently {qv[weakest_dim]:.2f}) via {weakest_doc[0]}: {state.original_goal}"
    state.evolution_count += 1

    # Goal fidelity check (inherited from live-inf)
    # Fidelity = semantic alignment between evolved goal and original goal
    # If goal drifts too far → freeze evolution, keep original goal
    # Simple heuristic: if evolution_count > 3 → warn
    if state.evolution_count > 3:
        emit: "[FIDELITY WARN] {state.evolution_count} evolutions — checking drift"
        # Reset to original goal direction
        state.root_goal = f"Further improve corpus quality for: {state.original_goal}"

    → continue to Step 7 → next iteration

elif convergence_status == "CONTINUE":
    # Not enough data yet
    → continue to Step 7 → next iteration
```

---

#### Step 7: State Update

```python
# 7a — Pareto vector update
pareto_improved = False
for dim in DIMS:
    if qv[dim] > state.best_score_vector.get(dim, 0.0):
        state.best_score_vector[dim] = qv[dim]
        pareto_improved = True

if pareto_improved:
    state.plateau_count = 0
else:
    state.plateau_count += 1

# 7b — Best score update
if qv["total"] > state.best_score:
    state.best_score = qv["total"]

# 7c — Stigmergy update (pheromone trails)
if gap_probe.gap_target in world_model.pheromone:
    p = world_model.pheromone[gap_probe.gap_target]
    p["strength"] = 0.7 * p["strength"] + 0.3 * qv["grounding_rate"]
    p["flagged"] = qv["grounding_rate"] < 0.70

# 7d — World model update
world_model.tried.append({
    "goal": state.root_goal,
    "score_vector": qv,
    "iteration": state.iteration,
    "outcome": convergence_status
})
# Dead end detection: same approach failed 2+ times
if convergence_status == "IMPROVE" and state.plateau_count >= 2:
    world_model.dead_ends.append({"goal": state.root_goal[:100], "score": qv["total"]})

# 7e — Corpus delta suggestions (from Auditor)
if audit.corpus_delta:
    emit: "[CORPUS DELTA] Suggested improvements:"
    for delta in audit.corpus_delta[:3]:
        emit: f"  - {delta}"

# 7f — Persist state
state.iteration += 1
write(".entity/live-state.json", state)
write(".entity/world-model.json", world_model)

# 7g — Progress log
append_jsonl(".entity/progress.log", {
    "iteration": state.iteration,
    "timestamp": ISO8601_now(),
    "score_vector": qv,
    "goal": state.root_goal[:80],
    "convergence": convergence_status,
    "plateau_count": state.plateau_count
})

emit: f"[ITER {state.iteration}/{max_iterations}] total={qv['total']:.3f} ({convergence_status}) | goal={state.root_goal[:60]}"

# 7h — Budget check
if state.iteration >= max_iterations:
    → BUDGET_EXHAUSTED (see Post-Loop)
```

---

### POST-LOOP: Termination

**CONVERGED_SUCCESS** (all 4 dims plateaued + above threshold):
```
emit: """
entity-live CONVERGED after {N} iterations ({evolution_count} goal evolutions)
Goal: {original_goal}
Final quality vector:
  grounding_rate:    {qv.grounding_rate:.2f}
  routing_precision: {qv.routing_precision:.2f}
  claim_quality:     {qv.claim_quality:.2f}
  sycophancy_pass:   {qv.sycophancy_pass:.2f}
  total:             {qv.total:.2f}
Score trajectory: {quality_history summary}
Corpus deltas suggested: {total_deltas}
"""
state.status = "CONVERGED"
write(".entity/live-state.json", state)
```

**CONVERGED_STALE** (plateaued but below threshold):
```
emit: """
## entity-live CONVERGED_STALE — Quality Below Threshold
Best total: {best_score:.2f} / required: {quality_threshold:.2f}
Below-threshold dims: {below_dims}
Iterations: {N} | Evolutions: {evolution_count}

Possible causes: corpus docs insufficient, goal too broad, domain gaps.

Next steps:
1. Run /entity-inf for unbounded iteration
2. Manually improve flagged corpus docs: {flagged_docs}
3. Add new corpus docs for weak dimensions
"""
state.status = "STALE"
write(".entity/live-state.json", state)
```

**BUDGET_EXHAUSTED** (max_iterations reached without convergence):
```
emit: """
## entity-live Budget Exhausted ({max_iterations} iterations)
Goal: {original_goal}
Best score: {best_score:.2f}
Quality trajectory: {summary}

To continue: run /entity-inf (unbounded) or /entity-live again (resumes from state)
"""
state.status = "ACTIVE"  # keep state for resume
write(".entity/live-state.json", state)
```

---

## State Files

```
.entity/
  live-state.json       # iteration counter, goal, quality history
  world-model.json      # tried strategies, dead ends, pheromone, research cache
  progress.log          # per-iteration JSONL progress
```

## Anti-patterns

- Do NOT route to /live or /live-inf — this is a standalone loop
- Do NOT invoke omc-autopilot, omc-goal-tree, omc-episode-memory, omc-failure-router
- Do NOT run code oracles (lint, test, typecheck) — use 4D Corpus Quality Oracle
- Do NOT auto-modify corpus docs — emit CORPUS DELTA suggestions only
- Do NOT ask user mid-loop "continue?" — fully autonomous until convergence or budget
