---
name: live-inf
description: Infinite autonomous self-evolving loop — no iteration budget, context rotation across sessions, Epistemic State Layer for world model tracking. Terminates only on convergence plateau or explicit user stop.
# Updated: 2026-03-30 — critique-based improvements (P0-P1)
#   P0-2: plateau_k 5→7, score_uncertain_threshold 0.10
#   P1-4: Context Priming with world-model extension
#   P1-5: Progress Log (inherited from omc-live)
#   All other P0/P1 changes inherited from omc-live
#   P2: goal_fidelity 누적 추적, autopilot phase-aware retry, world model GC, context priming 품질 필터, alignment check 명확화
#   P3: Autonomous Skill Router (Step 3e) — world-model-aware routing with skill_routing_history tracking
#   P4: DISPATCH layer inherited from omc-live (DELEGATE/FAN_OUT/AUTOPILOT) — world-model dead-end aware
#   P5: Wave 1 (Step 3f) — Adaptive Strategy Consultation, re-runs on session resume + goal evolution
#       Co-Evolution Feedback loop: Wave 2 outcomes feed back into next Wave 1 (Agent0 arXiv:2511.16043)
# Updated: 2026-04-14 — entity integration (P6)
#   P6: wave1_prompt aligned to APPROACH/METHOD/KEY_DECISIONS/ANTI_PATTERNS format
#       Triggers entity Iter 47/48/49 Wave1 detection → structured response + [ENTITY_GROUNDING_METRICS] footer
#       P6-5 oracle (live/SKILL.md) parses routing_precision + sycophancy_pass from entity footer
#       P6-6: claim_quality → impact dimension (Iter 48 all-corpus [ENTITY_GROUNDING_METRICS] footer)
#       P6-7: oracle-aligned thresholds — grounding_rate ≥0.85, claim_quality ≥0.75 (Iter 49)
#       P6-8: actionability 14th QG check + impact blend = (claim_quality + actionability) / 2 (Iter 51)
#       P6-9: Iter 54 efficiency hardening — confidence-gated doc budget + Q-WEAK grounded-skip
#       P6-10: Iter 55 16th QG recommendation evidence anchoring — [ACTION:][FROM:doc_id], action_anchoring_rate ≥0.80
---

<Purpose>
omc-live-inf is the unbounded version of omc-live. It removes the iteration budget ceiling
and adds two mechanisms that make true infinite execution possible:

1. **Context Rotation**: when context approaches the limit, the full run state is serialized to
   `.omc/infinite-state.json` and a handoff prompt is emitted. The next session resumes exactly
   where the previous one stopped — no progress is lost.

2. **Epistemic State Layer (World Model)**: tracks what has been tried, what is known, and what
   remains uncertain — preventing the agent from re-exploring dead ends across sessions.
   Inspired by Kosmos (arXiv:2511.02824): 200 rollouts, 1,500 papers, 79.4% accuracy.

Architecture position:
  omc-live-inf (Infinite Outer Loop)
    ├── [WORLD MODEL] Epistemic State Layer (.omc/world-model.json)
    ├── [ROTATE] Context Rotation Protocol (session boundary serialization)
    ├── [SCORE] Multi-dimensional evaluator (inherits from omc-live)
    ├── [EVOLVE] Goal elevation engine (inherits from omc-live)
    ├── [ROUTE] Autonomous Skill Router (Step 3e — world-model-aware task-type → skill/agent selection)
    ├── [WAVE1] Adaptive Strategy Consultation (Step 3f — re-runs on session resume + goal evolution)
    └── omc-autopilot (Inner Loop, Phase 0-5)

Relationship to omc-live:
  omc-live-inf IS omc-live with 5 overrides:
    1. max_outer_iterations: ∞  (no budget ceiling)
    2. Context Rotation added  (step 3c — new)
    3. Epistemic State Layer added  (step 0 — new PRE-LOOP step)
    4. Autonomous Skill Router extended  (step 3e — world-model-aware, tracks skill_routing_history)
    5. Wave 1 Adaptive Strategy Consultation  (step 3f — re-run on resume/evolution, co-evolution feedback)
  All other omc-live steps (scoring, alignment, evolution, etc.) are inherited unchanged.

**omc-live vs omc-live-inf — key differences at a glance:**

| Feature | omc-live | omc-live-inf |
|---------|----------|-------------------|
| Max iterations | 5 (configurable) | ∞ (convergence only) |
| Termination | budget OR convergence | convergence OR user-stop |
| Context limit | early handoff (manual restart) | auto-compact (seamless continue); rotation only at 90% emergency |
| World model | none | full epistemic state |
| plateau_k | 3 | 7 (stricter for infinite mode) |
| Skill Router | keyword+LLM | world-model-filtered + routing history |
| Wave 1 | runs once | re-runs on resume + goal evolution |
| Dead end detection | none | yes (max_dead_ends=10) |
| Sessions | 1 | N (unbounded) |
| Use case | bounded tasks, cost-aware | unbounded quality optimization |
</Purpose>

<Use_When>
- Task requires indefinite execution until true convergence — no time box
- User says "live-inf", "infinite loop", "keep going until perfect", "no iteration limit"
- Research-style tasks: optimize until plateau, not until N iterations
- Task is known to require many iterations (>5) to reach high quality
</Use_When>

<Do_Not_Use_When>
- Task has a deadline or cost constraint — use omc-live with max_outer_iterations instead
- Quick fix or single-pass task — use omc-autopilot directly
- User wants manual approval between iterations — use omc-live with lower max_outer_iterations
</Do_Not_Use_When>

<Autonomy_Contract>
**MANDATORY — live-inf executes fully autonomously. NO user prompting between iterations.**

- After iter N completes (Score + Evolve decided), **immediately** start iter N+1 in the same response turn.
- **NEVER** present "continue / pause / pivot / stop" menus mid-run. That is /live (bounded) behavior, not live-inf.
- **NEVER** ask "should I proceed?" / "다음 뭐 할까요?" / "계속 진행할까요?" / "어떻게 할까요?". Those are bounded-mode patterns.
- Per-iteration output is **a single-line status** (`[LIVE-INF iter N] score={s:.3f} goal={g[:60]}`). No interactive checkpoints.

**Authorized stop conditions (ONLY these end the loop autonomously):**
1. `plateau_count >= plateau_k` (default 7) — genuine convergence
2. `cumulative_fidelity < cumulative_fidelity_min` (0.50) — Goodhart drift forced stop
3. `estimated_context_pct > context_budget_pct` (70%) — emit handoff, save state, STOP
4. User explicit stop in NEW user message: "stop" / "cancel" / "멈춰" / "중단" / "그만"
5. FATAL escalation (Level 3 goal substitution per parent skill) — omc-goal-tree returned Level 3
6. External publish action (biz-autopilot with publish/post/submit/게시/홍보/제출) — USER CONSENT GATE (this is the ONLY authorized interactive pause)

Anything outside those 6 conditions = **continue the loop**. No exceptions.

**Rationale**: live-inf's defining property is unbounded autonomous execution. Interactive checkpointing defeats its purpose and loses the user's implicit authorization granted by `/live -i` invocation. If the user wanted interactive control, they would invoke `/live` (bounded) instead.
</Autonomy_Contract>

<Configuration>
Inherits ALL omc-live configuration. These values are overridden:
- max_outer_iterations: null    (infinite — convergence/user-stop only)
- plateau_k: 7                  (stricter: 7 consecutive below-epsilon iterations to converge)
                                 (raised from 5: LLM scoring variance at 0.05-0.10 makes k=5
                                  still prone to false convergence in infinite mode where
                                  premature termination wastes the unbounded budget.
                                  omc-live default is 3 — infinite mode needs more evidence.
                                  Source: 20260330-omc-live-critique P0-2)
- score_uncertain_threshold: 0.10 (inherited from omc-live P0-2 — gray zone protection applies here too)
- context_budget_pct: 90        (emergency fallback only — auto-compact handles normal context growth)
                                 Raised from 65: Claude Code /compact compresses context automatically,
                                 making 65% rotation unnecessary. 90% is a safety net for edge cases.

Infinite-mode additions:
- rotation_on_resume: true      (on session start, check for infinite-state.json → auto-resume)
- world_model_enabled: true     (enable Epistemic State Layer tracking)
- max_dead_ends: 10             (if world model accumulates 10 dead-end strategies → escalate to user)
- session_id_prefix: "inf"      (prefix for session IDs in infinite-state.json)
- max_escape_attempts: 2        (Novelty Escape: max attempts before declaring true CONVERGED)
                                 Research basis: Novelty Search (Lehman & Stanley);
                                 POET (arXiv:1901.01753); Agent0 (arXiv:2511.16043)
- pareto_convergence: true      (use per-dimension Pareto vector instead of single scalar)
                                 Research basis: NSGA-II multi-objective evolution
                                 plateau only when ALL dimensions stagnant simultaneously
- her_enabled: true             (Hindsight Experience Replay: reuse partial gains as sub-goal hints)
                                 Research basis: Andrychowicz et al. NeurIPS 2017
</Configuration>

<Steps>
## Infinite Outer Loop Execution Protocol

### PRE-LOOP STEP 0 (NEW): Resume or Initialize

**Check for existing infinite run:**
```
if .omc/infinite-state.json exists:
    state = read(.omc/infinite-state.json)
    if state.status == "ROTATING":
        # Previous session hit context limit — resume from exact state
        log: "[INFINITE] Resuming from session {state.session_id}, iteration {state.current_iteration}"
        log: "[INFINITE] Best score so far: {state.best_score:.2f} | Evolution depth: {state.evolution_count}"
        # Restore: root_goal, original_goal, evolution_history, best_score, plateau_count, world_model
        restore_all_state_from(state)
        → Skip PRE-LOOP steps 1-2, go directly to STEP 0b (World Model load)
    elif state.status == "CONVERGED" or state.status == "USER_STOPPED":
        log: "[INFINITE] Previous run is {state.status}. Starting fresh run."
        → Proceed normally (steps 1-2, fresh init)
else:
    → Fresh start: proceed normally (steps 1-2)
```

**ESC (force-interrupt) recovery** — check for dirty state on every resume:
```
# Detect if previous session was interrupted mid-iteration (ESC / crash)
git_status = shell("git status --porcelain")
live_state = read(.omc/live-state.json) if exists else null

if git_status contains unstaged/uncommitted changes
   AND live_state.last_outcome is null (iteration started but never completed):
    emit: "[INFINITE WARN] Dirty state detected — previous session may have been interrupted mid-run."
    emit: "  Uncommitted changes exist. Options:"
    emit: "  (A) git stash → discard partial work from interrupted iteration"
    emit: "  (B) git add -u && git commit -m 'wip: interrupted at iter {N}' → save partial work"
    emit: "  (C) Continue anyway — partial work will be included in next iteration"
    → Wait for user input (do NOT proceed autonomously on dirty state)
```
Note: ESC mid-autopilot is safe for the infinite loop state files (they're only updated after autopilot completes),
but the working directory may have partial code changes. Always resolve before resuming.

**STEP 0b: Load World Model** (always — fresh or resumed):
```
if .omc/world-model.json exists:
    world_model = read(.omc/world-model.json)
    log: "[WORLD MODEL] Loaded: {len(world_model.tried_strategies)} tried strategies, {len(world_model.dead_ends)} dead ends"
else:
    world_model = {
        "tried_strategies": [],    # list of {goal, score, iteration, outcome}
        "dead_ends": [],           # strategies that failed ≥2 times
        "known_facts": [],         # confirmed truths about the codebase/task
        "uncertain": [],           # things tried but with unclear outcome
        "dimensions_explored": {}, # {dimension_name: max_score_achieved}
        "skill_routing_history": [],# list of {skill, iteration, score_delta, task_type} — Step 3e
        "her_hints": [],           # HER partial gains — set by Step 6b
        "best_score_vector": {}    # {dimension: best_score} — Pareto tracking
    }
    write(.omc/world-model.json, world_model)
    log: "[WORLD MODEL] Initialized fresh world model"
```

---
### PRE-LOOP (inherited from omc-live, steps 1-2.5)

Steps 1, 2, 2.5 execute exactly as in omc-live.
Exception: if resuming from STEP 0 → skip steps 1-2 (state already restored).

---
### LOOP STEPS (inherited from omc-live, steps 3-6b)

Steps 3, 3a, 3b, 3d, 4, 5, 5a, 5b, 6, 6a, 6b execute exactly as in omc-live.
(3d = Context Priming, 5b = Progress Log — both NEW in P1-4/P1-5)

**CRITICAL: Step 6 → 6b Flow** (prevents premature termination):
```
Step 6: Judgment
  → YES: proceed to Step 6a (do NOT terminate — infinite mode continues)
  → NO: loop back to Step 4

Step 6a: SCORE
  → Calculate current_score, min_dimension
  → ALWAYS proceed to Step 6b (even on first YES)

Step 6b: Pareto + World Model + EVOLUTION DECISION
  → Pareto check (Step 6b section 1):
    - Any dimension improved? → plateau_count = 0, continue loop
    - All dims stagnant? → plateau_count += 1

  → Evolution decision:
    - plateau_count < plateau_k (7) → EVOLVE
      * Generate 3 candidate goals (omc-live Step 6b)
      * Prune to best 1
      * Update root_goal, evolution_count++
      * Loop to Step 3 (iteration N+1)

    - plateau_count >= plateau_k → NOVELTY ESCAPE
      * Attempt maximally novel goal (max 2 attempts)
      * If escape succeeds → reset plateau_count, loop to Step 3
      * If escape fails → CONVERGED

ASSERTION: Goal achievement (Step 6 YES) ≠ run termination in infinite mode.
Termination ONLY when plateau_k consecutive stagnant iterations.
```

**❌ PROHIBITED PATTERNS (enforce strictly — do NOT violate):**
```
1. ❌ Declaring CONVERGED/CONVERGED_SUCCESS mid-loop when plateau_count < plateau_k
   - High score alone (even 0.95+) is NOT a termination condition
   - Only termination trigger: plateau_count >= 7 OR user_stop signal

2. ❌ Asking the user "계속 진화시킬까요?" or any continuation question
   - Infinite mode is fully autonomous — the user does NOT decide each iteration
   - Only 3 valid human interaction points:
       (A) Dirty state on resume (Step 0 ESC recovery)
       (B) Dead-end escalation (max_dead_ends=10 reached)
       (C) User sends "stop"/"done"/"converge now" in chat
   - Any other mid-loop question = protocol violation

3. ❌ Treating "task complete / document saved" as convergence
   - Completion of a deliverable → EVOLVE the goal upward (more depth, new angle, validation)
   - Research tasks: after first synthesis → evolve toward empirical validation, cross-domain,
     or application-specific elaboration — never stop at first draft

4. ❌ Skipping EVOLVE when plateau_count < plateau_k
   - If score improved this iteration → plateau_count = 0 → MUST generate evolved goal → MUST loop
   - No exception for "the document looks good enough"
```

**✅ CORRECT FLOW after high-score iteration (e.g., score=0.90 on iter 1):**
```
score improved (0.0 → 0.90) → plateau_count = 0
→ Step 6b: EVOLVE
  * Generate 3 candidate next goals (deeper depth / new angle / validation / application)
  * Select best 1
  * evolution_count++
→ iter 2 starts automatically — NO user question
```

**Overrides and additions within inherited steps:**

**Step 3: Check iteration budget** — OVERRIDE:
```
# No max_outer_iterations check — infinite mode has no ceiling
# Only check for convergence and user_stop signal:
if .omc/infinite-stop.txt exists:
    log: "[INFINITE] User stop signal detected. Initiating graceful shutdown."
    → write final state, proceed to CONVERGED_SUCCESS flow
```

**Step 3c (NEW): Context Check** (runs AFTER step 3b, before autopilot):
```
# Claude Code has /compact auto-compression — context is NOT a hard ceiling.
# Auto-compact kicks in automatically and the session continues uninterrupted.
# Therefore: DO NOT rotate on context size alone. Just keep looping.
#
# Only trigger rotation (emergency fallback) at 90% — rare edge case where
# auto-compact failed or is disabled.

# Language/code-aware token estimation (±10% vs naive chars/4 at ±30%)
korean_chars = count of chars in Unicode range AC00-D7A3
code_chars   = chars inside ``` blocks or lines with 4+ leading spaces
other_chars  = total_chars - korean_chars - code_chars

total_chars  = len(full session text)
korean_ratio = korean_chars / total_chars
code_ratio   = code_chars   / total_chars

chars_per_token = (1.5  * korean_ratio) \
                + (0.35 * code_ratio)   \
                + (0.75 * (1 - korean_ratio - code_ratio))

# Fallback if character counting unavailable: naive + 10% safety margin
# estimated_tokens = total_chars / 4 * 1.10

estimated_tokens      = total_chars / chars_per_token
model_context_limit   = 200_000  # Claude; use 128_000 for other models
estimated_context_pct = estimated_tokens / model_context_limit * 100

if estimated_context_pct < 90:
    # NORMAL PATH: auto-compact will handle any pressure → continue looping
    log: "[CTX] {estimated_context_pct:.0f}% (korean={korean_ratio:.0%}, code={code_ratio:.0%}) — auto-compact available, continuing"
    → proceed to autopilot (no rotation needed)

else:
    # EMERGENCY FALLBACK (90%+): auto-compact not working — serialize and rotate
    log: "[CTX WARN] {estimated_context_pct:.0f}% (korean={korean_ratio:.0%}, code={code_ratio:.0%}) — emergency rotation triggered"
    state = {
        "status": "ROTATING",
        "session_id": "{session_id_prefix}-{timestamp}",
        "current_iteration": current_iteration,
        "root_goal": root_goal,
        "original_goal": original_goal,
        "evolution_count": evolution_count,
        "evolution_history": evolution_history,
        "best_score": best_score,
        "plateau_count": plateau_count,
        "score_variance": score_variance,
        "score_history": score_history,
        "cost_history": cost_history,
        "world_model_path": ".omc/world-model.json",
        "last_autopilot_summary": autopilot_summary,
        "rotated_at": ISO8601_now()
    }
    write(.omc/infinite-state.json, state)
    emit: """
    [INFINITE LOOP — EMERGENCY ROTATION]
    Context at {estimated_context_pct:.0f}% (korean={korean_ratio:.0%}, code={code_ratio:.0%}) (auto-compact may be disabled).
    Session {state.session_id} | Iteration {current_iteration} | Best: {best_score:.2f}

    TO RESUME: run `/live-inf` in a new Claude Code session.
    """
    → STOP current session
```

**Step 3d (NEW): Context Priming — World Model Extension** (P1-4, Source: 20260330-omc-live-critique):
Inherits the base Context Priming from omc-live (Step 3d) and extends it with world-model data.
Runs after Step 3c (Context Check), before autopilot.
```
# Base context priming is inherited from omc-live Step 3d.
# Infinite-mode extends the context_primer with world-model intelligence:

if world_model.dead_ends:
    context_primer += f"\nDead-end strategies to avoid: {[d['goal'][:50] for d in world_model.dead_ends[-3:]]}"
if world_model.her_hints:
    context_primer += f"\nPartial gains to build on: {[h['dim'] + ':+' + str(h['delta']) for h in world_model.her_hints]}"

emit: "[CTX PRIME infinite] world-model enrichment: {len(world_model.dead_ends)} dead-ends, {len(world_model.her_hints)} HER hints"
```

**Step 3e (OVERRIDE): Autonomous Skill Router — World-Model-Aware** (P3, inherits from omc-live Step 3e):
Extends the base omc-live Skill Router with world-model routing history.
Runs AFTER Step 3d (Context Priming), BEFORE Step 4 (omc-autopilot).
```
# ── 1. Inherit base routing from omc-live Step 3e
# (Tier 1 keyword match → Tier 2 dynamic LLM + available_skills → Tier 3 fallback)
# Run base routing first to get task_type + selected_skills.
# NOTE: Tier 2 already passes available_skills from system-reminder to LLM (see omc-live Step 3e).
#       omc-live-inf inherits this dynamic discovery behavior automatically.

# ── 2. World-model routing history filter
# Skip skills that have been tried repeatedly with low score improvement
if world_model.skill_routing_history:
    for skill in selected_skills[:]:
        history = [h for h in world_model.skill_routing_history if h["skill"] == skill]
        if len(history) >= 3:
            recent_scores = [h["score_delta"] for h in history[-3:]]
            if all(delta < 0.05 for delta in recent_scores):
                selected_skills.remove(skill)
                log: "[SKILL ROUTER∞] Skipping {skill} — 3x low-delta in world model history"

# If filtering removed all candidates → fall back to base routing without filter
if not selected_skills:
    log: "[SKILL ROUTER∞] All candidates filtered — reverting to base routing"
    # re-run base routing (ignore history this iteration)

# ── 3. DISPATCH (P4 — overrides passive injection, inherits ORCHESTRATOR_MAP from omc-live)
# omc-live-inf uses the same DISPATCH layer but adds world-model dead-end awareness.

ORCHESTRATOR_MAP = {
    "business":  "biz-autopilot",
    "research":  "expert-research-v2",
    "review":    "omc-code-review",
    "plan":      "omc-plan",
    "security":  "omc-security-review",
    "analysis":  "omc-analyze",
    "knowledge": "entity",           # corpus-routed vertical AI scaffold (P6-12 sync)
}

# Dead-end guard: don't re-delegate to the same orchestrator that failed recently
if task_type in ORCHESTRATOR_MAP:
    orch = ORCHESTRATOR_MAP[task_type]
    dead_end_key = f"delegate:{orch}"
    if world_model.dead_ends.get(dead_end_key, 0) >= 2:
        log: "[DISPATCH∞] {orch} is a dead-end (2+ failures) — falling back to FAN_OUT or AUTOPILOT"
        dispatch_mode = "AUTOPILOT"
    elif orch in available_skills:
        dispatch_mode = "DELEGATE"
        dispatch_target = orch
    else:
        dispatch_mode = "AUTOPILOT"
        dispatch_target = None

# USER CONSENT GATE (publish/post actions only)
if dispatch_mode == "DELEGATE" and any(kw in root_goal.lower()
    for kw in ["publish", "post", "submit", "게시", "홍보", "제출"]):
    emit: "[CONSENT∞] About to publish via {dispatch_target}. Y=proceed / N=skip / S=stop"
    wait_for_user_consent()

if dispatch_mode == "DELEGATE":
    result = invoke Skill(name=dispatch_target, args=root_goal + "\n\nContext:\n" + context_primer)
    autopilot_summary = result.summary or f"Delegated to {dispatch_target}. Goal: {root_goal[:60]}"
    last_outcome = result.outcome or "success"
    last_phase_reached = f"delegated:{dispatch_target}"
    # Update world model routing history
    world_model.skill_routing_history.append({
        "skill": dispatch_target, "iteration": current_iteration,
        "score_delta": 0  # filled after SCORE step
    })
    → skip Step 4, proceed to Step 5

elif dispatch_mode == "FAN_OUT":
    results = []
    for skill_name in selected_skills[:2]:
        r = invoke Skill(name=skill_name, args=root_goal)
        results.append(r)
    autopilot_summary = "FAN_OUT∞: " + " | ".join(r.summary[:40] for r in results)
    last_outcome = "success" if all(r.outcome != "failure" for r in results) else "partial"
    → skip Step 4, proceed to Step 5

else:  # AUTOPILOT — code/debug/ui or dead-end fallback
    context_primer += f"""
[SKILL ROUTER∞ — iter {current_iteration} | {routing_tier}]
Task type: {task_type}
Suggested skills (world-model filtered): {', '.join(selected_skills[:3])}
Past routing: {len(world_model.skill_routing_history)} records tracked
"""
    emit: "[SKILL ROUTER∞] type={task_type} | mode=AUTOPILOT | skills={selected_skills[:3]}"
    → proceed to Step 4 (omc-autopilot)
```

**Step 3f (NEW — Wave 1 OVERRIDE): Adaptive Strategy Consultation**

Inherits Wave 1 from omc-live (Step 3f) with infinite-mode adaptations.
Runs AFTER Step 3e (Skill Router), BEFORE Step 4 (autopilot / DISPATCH target).

```
# ── Re-run conditions (infinite-mode differs from omc-live's "run once")
wave1_complete = infinite_state.get("wave1_complete", false)
wave1_evolution_count = infinite_state.get("wave1_evolution_count", -1)

should_run_wave1 = (
    not wave1_complete                              # first run of fresh session
    OR is_session_resume                            # ALWAYS re-run on context rotation resume
    OR evolution_count > wave1_evolution_count      # goal evolved since last Wave 1
)

if not should_run_wave1:
    wave1_plan = world_model.get("wave1_plan", "")
    if wave1_plan:
        context_primer += f"\n[WAVE 1 PLAN (cached)]\n{wave1_plan}"
        emit: "[WAVE1∞] Using cached plan (evolution_v{wave1_evolution_count}, resume_safe=true)"
    → skip to Step 4

emit: "[WAVE1∞] Running Wave 1 — reason: {'resume' if is_session_resume else 'evolution' if evolution_count > wave1_evolution_count else 'fresh start'}"

# ── Specialist map (same as omc-live)
WAVE1_SPECIALISTS = {
    "business": ["biz-researcher", "biz-marketer"],
    "research":  ["expert-research-v2"],
    "code":      ["research-explore", "ops-planner"],
    "debug":     ["ops-debugger"],
    "review":    ["omc-code-review"],
    "plan":      ["omc-plan"],
    "analysis":  ["omc-analyze"],
    "security":  ["omc-security-review"],
    "ui":        ["dev-designer"],
}
specialists = [s for s in WAVE1_SPECIALISTS.get(task_type, ["omc-analyze"])
               if s in available_skills]

# ── World-model dead-end filter (∞-specific):
# Don't fan-out to specialists that have failed as delegates 2+ times
filtered_specialists = []
for s in specialists:
    dead_end_key = f"wave1:{s}"
    if world_model.dead_ends.get(dead_end_key, 0) >= 2:
        log: "[WAVE1∞] Skipping {s} — 2+ dead-ends in world model"
    else:
        filtered_specialists.append(s)

if not filtered_specialists:
    log: "[WAVE1∞] All specialists filtered by dead-ends — using omc-analyze fallback"
    filtered_specialists = ["omc-analyze"] if "omc-analyze" in available_skills else []

# ── Co-Evolution Feedback injection (P0 — Agent0 arXiv:2511.16043):
# Feed prior Wave 2 outcomes BACK into this Wave 1 prompt.
# Prevents Wave 1 from issuing the same strategy that Wave 2 already proved ineffective.
co_evolution_feedback = world_model.get("wave1_feedback", [])[-5:]  # last 5 feedback entries
co_evolution_block = ""
if co_evolution_feedback:
    co_evolution_block = "\n".join(
        f"- Iteration {fb['iteration']}: {fb['strategy']} → {fb['outcome']} | dim={fb['weak_dim']}"
        for fb in co_evolution_feedback
    )
    emit: "[WAVE1∞] Co-evolution: injecting {len(co_evolution_feedback)} Wave 2 feedback entries"

# ── Fan-out: call each specialist in parallel
wave1_results = []
for spec in filtered_specialists[:2]:  # max 2 specialists (cost control)
    # Note: Output format (STRICT) with KEY_DECISIONS/ANTI_PATTERNS enables entity Wave1 detection
    # in entity Iter 47+ — entity responds with structured APPROACH/METHOD/KEY_DECISIONS/ANTI_PATTERNS
    # and appends [ENTITY_GROUNDING_METRICS] (routing_precision, sycophancy_pass) for P6-5 oracle.
    wave1_prompt = f"""
You are a strategy consultant. Do NOT implement anything.
Goal: {root_goal}
Task type: {task_type}
Current score: {current_score:.2f} | Weakest dimension: {min_dimension}
Evolution depth: {evolution_count}

{f"[CO-EVOLUTION FEEDBACK — from prior iterations]:\n{co_evolution_block}" if co_evolution_block else ""}

Output format (STRICT):
APPROACH: <overall method — 1-2 sentences>
METHOD: <step-by-step approach, 3-5 steps>
KEY_DECISIONS: <2-3 critical choices that will determine success>
ANTI_PATTERNS: <2-3 common mistakes to avoid>
RECOMMENDED_TOOLS: <specific skills/agents to use in Wave 2>
CONSTRAINTS: <hard limits or non-negotiables>
"""
    result = invoke Skill(name=spec, args=wave1_prompt)
    wave1_results.append({
        "specialist": spec,
        "summary": result.summary or result[:300]
    })
    log: "[WAVE1∞] {spec} → done"

# ── Synthesize
if len(wave1_results) > 1:
    synthesis_parts = [f"[{r['specialist']}]: {r['summary']}" for r in wave1_results]
    wave1_plan = "Wave 1 Strategy:\n" + "\n\n".join(synthesis_parts)
else:
    wave1_plan = wave1_results[0]["summary"] if wave1_results else "(Wave 1 produced no output)"

# ── Persist to world_model (rotation-resilient — survives context rotation)
world_model["wave1_plan"] = wave1_plan
world_model["wave1_evolution_count"] = evolution_count
write(.omc/world-model.json, world_model)

# ── Persist to infinite-state.json (resume guard)
infinite_state["wave1_complete"] = true
infinite_state["wave1_evolution_count"] = evolution_count
write(.omc/infinite-state.json, infinite_state)

# ── Inject into context_primer for this Wave 2 iteration
context_primer += f"""
[WAVE 1 STRATEGY — iter {current_iteration} | evolution_v{evolution_count}]
{wave1_plan}
"""
emit: "[WAVE1∞] Strategy ready ({len(wave1_results)} specialists consulted) — injected into context"
```

**Wave 2 → Wave 1 feedback update** (runs in Step 6b after each autopilot outcome):
```
# After each Wave 2 iteration completes, record its outcome in world_model.wave1_feedback
# This is the Co-Evolution feedback loop: Wave 2 teaches Wave 1 what NOT to recommend.

new_feedback = {
    "iteration": current_iteration,
    "strategy": wave1_plan[:100],          # truncated plan reference
    "outcome": last_outcome,               # success / partial / failure
    "score_delta": current_score - prev_score,
    "weak_dim": min_dimension,
    "evolution_count": evolution_count
}
world_model.setdefault("wave1_feedback", []).append(new_feedback)

# Trim to last 20 entries (cost control)
if len(world_model["wave1_feedback"]) > 20:
    world_model["wave1_feedback"] = world_model["wave1_feedback"][-20:]

write(.omc/world-model.json, world_model)
log: "[WAVE1∞ FEEDBACK] iter {current_iteration}: outcome={last_outcome} delta={score_delta:.3f} | feedback_count={len(world_model['wave1_feedback'])}"
```

---

**Step 5a: Git Checkpoint** — MANDATORY in infinite mode (stronger than omc-live):
```
# Infinite loop runs indefinitely — every iteration MUST be committed.
# ESC interrupt between iterations leaves dirty state; committed checkpoints allow safe rollback.
git add -u
git commit -m "live-inf iter {N}/∞: {last_outcome} | goal_v{evolution_count}: {root_goal[:60]}"

# If commit fails (nothing to commit / git unavailable):
log: "[CHECKPOINT] iter {N} — no commit ({reason})"
continue  # non-blocking

# Rollback any iteration:
# git log --oneline | grep "live-inf iter"
# git checkout <hash>   ← restore to that iteration's state
```
**Why mandatory here**: without checkpoints, ESC mid-run leaves the codebase in an unknown state
across potentially N sessions. Each git commit is the only reliable rollback point.

**Step 6b: Goal Evolution** — ADDITION (world model update + Pareto + HER):

```
# ── 1. Pareto vector tracking (Research: NSGA-II multi-objective)
# Track per-dimension bests independently — not just total average.
# A run is truly converged only when ALL dimensions stagnant simultaneously.

pareto_improved = false
for dim in score_dimensions:
    if current_scores[dim] > world_model.best_score_vector.get(dim, 0.0):
        world_model.best_score_vector[dim] = current_scores[dim]
        pareto_improved = true

if pareto_improved:
    plateau_count = 0
    log: "[PARETO] dim improvement → plateau reset | vector={world_model.best_score_vector}"
else:
    plateau_count += 1
    log: "[PARETO] all dims stagnant (plateau={plateau_count}/{plateau_k})"

# ── 2. World model update
world_model.tried_strategies.append({
    "goal": previous_root_goal,
    "score": current_score,
    "score_vector": current_scores,   # per-dim breakdown
    "iteration": current_iteration,
    "outcome": "evolved",
    "weak_dim": min_dimension
})

if not pareto_improved:
    world_model.uncertain.append({
        "goal": previous_root_goal,
        "score": current_score,
        "reason": "all dims below epsilon"
    })

world_model.dimensions_explored[min_dimension] = max(
    world_model.dimensions_explored.get(min_dimension, 0),
    current_score
)

# ── 2.5. Skill routing history update (P3 — feeds Step 3e filter)
if selected_skills_this_iter:   # set by Step 3e before autopilot
    score_delta = current_score - prev_score
    for skill in selected_skills_this_iter:
        world_model.skill_routing_history = world_model.get("skill_routing_history", [])
        world_model.skill_routing_history.append({
            "skill": skill,
            "iteration": current_iteration,
            "score_delta": score_delta,
            "task_type": task_type_this_iter,
        })
    log: "[SKILL ROUTER∞] Recorded routing: {selected_skills_this_iter} | delta={score_delta:.3f}"

# ── 3. HER: Hindsight Experience Replay (Research: Andrychowicz NeurIPS 2017)
# Extract partial achievements even from stagnant iterations.
# "What DID improve this iteration?" → treat as a stepping-stone sub-goal.

her_sub_goals = []
for dim in score_dimensions:
    dim_delta = current_scores[dim] - world_model.best_score_vector.get(dim, 0.0)
    if dim_delta > 0:   # this dim improved even if total didn't
        her_sub_goals.append({
            "dim": dim,
            "delta": dim_delta,
            "sub_goal": f"Consolidate and extend the {dim} improvement from iter {current_iteration}"
        })

if her_sub_goals:
    # Inject highest-delta sub_goal as a hint for GOAL EVOLUTION PROMPT
    world_model.her_hints = sorted(her_sub_goals, key=lambda x: -x["delta"])[:2]
    log: "[HER] Partial gains found: {[h['dim'] for h in world_model.her_hints]} → injected as hints"
else:
    world_model.her_hints = []

write(.omc/world-model.json, world_model)
log: "[WORLD MODEL] Updated: {len(tried_strategies)} strategies tracked"

# ── 3.5. World Model garbage collection (NEW — P2-9, omc-live-inf only):
# Prevent tried_strategies from growing unboundedly in long runs.

GC_THRESHOLD = 50  # trigger GC when tried_strategies > 50 entries

if len(world_model.tried_strategies) > GC_THRESHOLD:
    # Sort by (score DESC, iteration DESC) — keep recent high-quality entries
    sorted_strategies = sorted(
        world_model.tried_strategies,
        key=lambda x: (x["score"], x["iteration"]),
        reverse=True
    )
    # Keep top-20 by score + last-10 by recency (union)
    top_by_score = sorted_strategies[:20]
    last_by_recency = sorted(world_model.tried_strategies, key=lambda x: x["iteration"], reverse=True)[:10]
    to_keep = {s["goal"]: s for s in top_by_score + last_by_recency}.values()

    # Archive pruned entries to world-model-archive.jsonl
    pruned = [s for s in world_model.tried_strategies if s not in to_keep]
    append_jsonl(".omc/world-model-archive.jsonl", pruned)

    world_model.tried_strategies = list(to_keep)
    world_model.gc_count = world_model.get("gc_count", 0) + 1
    emit: "[GC] World model pruned: {len(pruned)} entries archived → {len(to_keep)} retained"

# ── 4. Dead end check
if count(uncertain where score < 0.5) >= max_dead_ends (default 10):
    emit: "[INFINITE WARN] {max_dead_ends} low-score strategies. Escalating to user."
    → Human escalation: present world model summary, ask for new direction
```

---
### PRE-TERMINATION GUARD (runs BEFORE any CONVERGED declaration)

Before declaring any termination state, verify ALL of the following. If any check fails → abort
termination, reset to loop continuation:

```
TERMINATION CHECKLIST:
  [ ] plateau_count >= plateau_k (7)?          # MUST be true — not just "score is high"
  [ ] escape_attempts >= max_escape_attempts?  # Novelty Escape was tried and failed
  [ ] NO user question was asked this session? # Mid-loop questions are a protocol violation
  [ ] current_iteration > 1?                  # Single-iteration runs cannot converge
      (Exception: user_stop signal — can terminate at any iteration)

If any box is unchecked → DO NOT terminate → generate evolved goal → continue loop.

COMMON FALSE TERMINATION PATTERNS (reject these):
  ✗ "Score is 0.90+ so the task is done" → WRONG: score is irrelevant to termination
  ✗ "The document looks complete" → WRONG: always evolve toward deeper/broader/validated
  ✗ "I asked the user and they said it's good" → WRONG: asking is a protocol violation
  ✗ "Research task is inherently one-shot" → WRONG: always iterate (validation, cross-domain, etc.)
```

---
### POST-LOOP: Convergence / User Stop (inherits from omc-live step 7)

Step 7 (CONVERGED_SUCCESS / CONVERGED_STALE / BUDGET_EXHAUSTED) executes as in omc-live,
with one addition:

```
# Mark infinite-state.json as complete
state.status = "CONVERGED"  # or "USER_STOPPED"
state.final_score = best_score
state.total_iterations = current_iteration
state.total_sessions = rotation_count + 1
write(.omc/infinite-state.json, state)

log: "[INFINITE COMPLETE] {state.status} | {total_iterations} iterations across {total_sessions} sessions"
log: "[INFINITE] World model: {len(tried_strategies)} strategies, {len(dead_ends)} dead ends"
```

**Infinite-mode termination conditions** (replaces budget exhaustion):
```
USER_STOPPED:    .omc/infinite-stop.txt exists
                 OR user sends "stop", "done", "converge now" in chat
                 → immediate graceful shutdown

NOVELTY ESCAPE:  plateau_count >= plateau_k   (triggered BEFORE declaring CONVERGED)
                 → attempt escape with maximally novel goal (see below)
                 → only declare CONVERGED if escape also fails

CONVERGED:       Novelty Escape exhausted (escape_attempts >= max_escape_attempts=2)
                 AND best_score >= min_convergence_score (0.6)

STALE:           Novelty Escape exhausted
                 AND best_score < min_convergence_score (0.6)
                 → CONVERGED_STALE

ESCALATED:       dead_end count >= max_dead_ends (10)
                 → human provides new direction, loop resets with new original_goal
```

**Novelty Escape Protocol** (Research: Novelty Search arXiv:cs/0609leware Lehman & Stanley;
 POET open-ended learning arXiv:1901.01753; Agent0 co-evolution arXiv:2511.16043):
```
# When plateau_count >= plateau_k, DO NOT immediately stop.
# Try to escape by generating a goal that is behaviorally distant from all tried strategies.
# World model's tried_strategies serves as the novelty archive.

max_escape_attempts: 2   (add to Configuration; after 2 failed escapes → true CONVERGED)

NOVELTY ESCAPE PROMPT:
Original goal: {original_goal}
Tried strategies so far (world model):
  {tried_strategies_summary}     ← list of past goals + score_vectors + weak_dims
Dimensions already well-explored:
  {world_model.dimensions_explored}
HER hints (partial gains from last iteration):
  {world_model.her_hints}        ← inject partial gains as stepping stones

The system has plateaued. Generate ONE escape goal that is:
1. Maximally DIFFERENT in approach/technique from all tried strategies above
2. Aligned with original_goal (goal_fidelity ≥ 0.7)
3. Targets a dimension NOT yet well-explored (low score in dimensions_explored)
4. If HER hints exist: build on those partial gains as a jumping-off point

Output EXACTLY:
escape_goal: <new goal>
escape_rationale: <why novel and likely to unlock improvement>
novelty_axis: <which neglected dimension this targets>

# Novelty validation — reject if too similar to past:
if escape_goal overlaps ≥ 50% with any tried_strategy approach:
    log: "[NOVELTY ESCAPE] Too similar — regenerating (1 retry allowed)"
    → re-run prompt once

# Execute escape:
root_goal = escape_goal
plateau_count = 0
escape_attempts += 1
world_model.tried_strategies[-1]["outcome"] = "escaped"
log: "[NOVELTY ESCAPE] Attempt {escape_attempts}/{max_escape_attempts}: {escape_goal}"
→ continue loop from Step 3 with new goal

# If escape iteration also plateaus:
if escape_attempts >= max_escape_attempts AND plateau_count >= plateau_k:
    → CONVERGED (genuine — novelty escape exhausted)
```

---
### State Files

```
.omc/
  infinite-state.json    ← primary session bridge (rotation + resume)
  world-model.json       ← epistemic state (persists across all sessions)
  world-model-archive.jsonl  ← archived tried_strategies from GC (NEW — P2-9)
  goal-tree.json         ← inherited from omc-live
  live-state.json        ← inherited from omc-live (per-iteration)
  episodes.jsonl         ← inherited from omc-live (episode memory)
  live-progress.log     ← per-iteration JSONL progress log (NEW — inherited from omc-live P1-5)
  infinite-stop.txt      ← user creates this file to signal graceful stop
                            content: any text (e.g., "user requested stop")
```

**User stop signal** (alternative to in-chat message):
```bash
# To stop the infinite loop after current iteration completes:
echo "stop" > .omc/infinite-stop.txt
```

---
### World Model Schema (.omc/world-model.json)

```json
{
  "tried_strategies": [
    {
      "goal": "Implement calculator with add/subtract",
      "score": 0.82,
      "iteration": 1,
      "outcome": "evolved",
      "weak_dim": "impact"
    }
  ],
  "dead_ends": [
    {
      "goal": "Add visual UI without backend changes",
      "score": 0.41,
      "reason": "below epsilon improvement after 2 attempts"
    }
  ],
  "known_facts": [],
  "uncertain": [],
  "dimensions_explored": {
    "quality": 0.85,
    "completeness": 0.88,
    "efficiency": 0.79,
    "impact": 0.72
  },
  "skill_routing_history": [
    {"skill": "omc-tdd", "iteration": 3, "score_delta": 0.12, "task_type": "code"},
    {"skill": "research-explore", "iteration": 4, "score_delta": 0.02, "task_type": "research"}
  ],
  "her_hints": [],
  "best_score_vector": {"quality": 0.85, "completeness": 0.88, "efficiency": 0.79, "impact": 0.72},
  "wave1_plan": "Synthesized Wave 1 strategy text — persisted for context rotation resilience",
  "wave1_evolution_count": 1,
  "wave1_feedback": [
    {
      "iteration": 3,
      "strategy": "biz-researcher: focus on developer pain points...",
      "outcome": "partial",
      "score_delta": 0.04,
      "weak_dim": "impact",
      "evolution_count": 1
    }
  ]
}
```

---

## Cron Monitoring Integration (for long-running external jobs)

When live-inf launches a job that takes hours, use CronCreate to monitor it between iterations instead of blocking the loop with polling.

```python
cron_id = CronCreate(
    cron="*/N * * * *",   # interval based on job duration (5m/<30min, 15m/<2h, 30m/<8h)
    prompt="""Check job: [SSH or local command to check LOG_PATH for DONE/ERROR].
If DONE: report result, send popup via notify script, CronDelete this job.""",
    recurring=True
)
world_model["active_cron_monitors"] = world_model.get("active_cron_monitors", []) + [cron_id]
```

**API Error Recovery**: If API rate-limits hit, use `csk-retry` or switch to `lsk` (local model, no limits). Cron monitors run independently of API state.

</Steps>
