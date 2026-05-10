---
name: live
description: Fully autonomous self-evolving outer loop orchestrator — loads past episodes, manages goal tree, drives autopilot inner loops, and continuously redefines goals until no further improvement is possible (self-evolution mode)
# Updated: 2026-03-30 — critique-based improvements (P0-P1)
#   P0-1: evaluator_mode config (self/cross_prompt/oracle_only)
#   P0-2: plateau_k 2→3, score_uncertain_threshold 0.10, gray zone protection
#   P0-3: Extended Auto Oracle (lint/type-check)
#   P1-4: Context Priming (episode-based lesson injection)
#   P1-5: Progress monitoring log (.omc/live-progress.log)
#   P2: goal_fidelity 누적 추적, autopilot phase-aware retry, world model GC, context priming 품질 필터, alignment check 명확화
#   P3: Autonomous Skill Router (Step 3e) — task-type-based skill/agent auto-selection
#       Research: RouteLLM (Berkeley 2024, arXiv:2406.18665), ReAct (Yao et al. 2022),
#       Mixture-of-Agents (Wang et al. 2024, arXiv:2406.04692)
#   P4: DISPATCH Layer (Step 3e) — DELEGATE/FAN_OUT/AUTOPILOT modes, ORCHESTRATOR_MAP
#   P5: 2-Wave Architecture (Step 3f) — Wave 1: expert strategy consultation (once)
#       Wave 2: execution loop seeded by Wave 1 plan
# Updated: 2026-04-14 — domain-aware improvements (P6)
#   P6-1: KEYWORD TABLE — `knowledge` task_type 추가 (corpus/grounding/entity/wtp/domain)
#   P6-2: WAVE1_SPECIALISTS — knowledge: [entity, research-deep-analyst]
#   P6-3: Domain-Aware Oracle — knowledge/research/analysis: grounding rubric (LLM-as-judge)
#          business: hypothesis/evidence rubric. code tooling 없이 oracle 품질 측정
#   P6-4: cross_prompt evaluator role — task_type별 domain-appropriate skeptic (CROSS_PROMPT_ROLES map)
#          기존: 항상 "code reviewer" → 수정: 도메인별 전문가 비평가 역할
#   P6-5: Entity corpus oracle extension — grounding rubric + routing_precision + sycophancy_pass
#          entity corpus signal 감지 시 2개 추가 차원: efficiency(routing) + quality(sycophancy)
#          Research: 20260414-entity-loop-skill-spec.md 4-dim oracle spec (SwarmSys arXiv:2510.10047)
#   P6-6: Entity Iter 48 — claim_quality → impact 차원 추가. entity 13-check Quality Gate footer 파싱.
#          모든 corpus-mode 응답에 [ENTITY_GROUNDING_METRICS] footer 자동 emit (Wave1 전용 → 전체 확장)
#          impact 차원이 synthesis_quality 0.5 fallback → claim_quality 실측값으로 대체
#   P6-8: Entity Iter 51 — actionability 14th QG check. impact = (claim_quality + actionability) / 2 blend
#          actionability: concrete [ACTION:{동작}] recommendations (not vague "consider X")
#   P6-11: Auto Oracle task_type guard — pytest/npm/eslint/typecheck에 task_type in [code,debug,ui] 조건 추가
#          knowledge/research/business 태스크에서 pytest.ini 등 있어도 코드 oracle 실행 안 함
#   P6-12: ORCHESTRATOR_MAP "knowledge" 추가 — knowledge 태스크를 entity에 직접 DELEGATE
#          기존: knowledge → ORCHESTRATOR_MAP 미매칭 → T2<2 skills 시 AUTOPILOT(omc-autopilot) 실행 → dev-bias 재발
#          수정: knowledge: "entity" 명시 → corpus-routed scaffold로 항상 DELEGATE
#          AUTOPILOT fallback 주석 명확화: knowledge는 entity 미설치 시에만 AUTOPILOT
#   Audit checklist (완전 완료 기준 — dev-bias 전수 검사 항목):
#     [✅] pytest/pyproject (831)     [✅] npm test (846)      [✅] eslint (984)
#     [✅] typecheck (989)            [✅] repo-context (583)  [✅] context7 (597)
#     [✅] TDD gate (612)             [✅] WAVE1_SPECIALISTS   [✅] CROSS_PROMPT_ROLES
#     [✅] ORCHESTRATOR_MAP knowledge (476, P6-12)
#   Research: MAE oracle-free scoring (arXiv:2510.23595), SwarmSys (arXiv:2510.10047)
---

<Purpose>
omc-live is the Outer Loop driver that completes the autonomous agent architecture.

**Self-Evolution Mode** (default): The loop does not stop at first success.
After each YES verdict, the system scores the current state, compares against the best known
score, and — if improvement delta exceeds epsilon — elevates the goal to a higher standard and
continues. The loop terminates only when improvement plateaus (convergence) or budget is exhausted.

Architecture position:
  omc-live (Self-Evolving Outer Loop)
    ├── [SCORE] Multi-dimensional evaluator (quality/completeness/efficiency/impact)
    ├── [EVOLVE] Goal elevation engine (redefines goal to next level of excellence)
    ├── [ROUTE] Autonomous Skill Router (Step 3e — task-type → skill/agent selection)
    └── omc-autopilot (Inner Loop, Phase 0-5)
          ├── omc-failure-router (failure classification)
          ├── omc-goal-tree (goal update on Fatal)
          └── omc-episode-memory (save on cleanup)
</Purpose>

<Use_When>
- User wants TRUE end-to-end autonomous execution that persists across multiple autopilot runs
- User says "omc-live", "live mode", "keep going until done", "fully autonomous", "outer loop"
- Task requires multi-session persistence — the goal spans more than one autopilot cycle
- User wants the system to self-correct goals and retry until outer objective is met
</Use_When>

<Do_Not_Use_When>
- Single-task execution that fits in one autopilot run — use omc-autopilot directly
- User wants manual control between iterations — use omc-autopilot + omc-episode-memory separately
- Task is a quick fix or exploration — use ralph or plan skills instead
</Do_Not_Use_When>

<Configuration>
Default limits (override in .omc/live-config.json if needed):
- max_outer_iterations: 5        (total autopilot cycles before forced stop)
- goal_check_model: sonnet       (model used to evaluate outer goal achievement)
- stop_on_fatal_escalation: true (stop if omc-goal-tree returns Level 3 and user declines)

Self-Evolution settings (new):
- evolve_mode: true              (enable self-evolving goal redefinition on YES)
- epsilon: 0.05                  (minimum score improvement to continue evolving; 0.0–1.0)
- plateau_k: 3                   (consecutive iterations below epsilon → declare convergence)
                                 (raised from 2: LLM scoring variance at 0.05-0.10 makes k=2 statistically
                                  unreliable. k=3 requires 3 consecutive below-epsilon iterations.
                                  Source: 20260330-omc-live-critique P0-2)
- max_evolution_depth: 3         (max number of goal evolutions before forced stop)
- score_dimensions: ["quality", "completeness", "efficiency", "impact", "goal_fidelity"]
                                 (evaluation axes; score = average across dimensions, 0.0–1.0 each)
                                 goal_fidelity: semantic alignment between current_goal and original_goal
                                 — prevents Goodhart drift where evolved goals diverge from user intent
- goal_fidelity_min: 0.7         (minimum goal_fidelity to allow goal evolution; below → skip EVOLVE, log WARNING)
- cumulative_fidelity_min: 0.50  (NEW — P2-8: minimum cumulative goal_fidelity across all evolutions)
                                   Per-step minimum is goal_fidelity_min=0.7
                                   Cumulative: product of all per-step fidelities
                                   Example: 0.7 × 0.8 × 0.9 = 0.504 → just passes
                                            0.7 × 0.7 × 0.7 = 0.343 → FAIL → force stop
- min_convergence_score: 0.6     (minimum best_score at convergence; below → CONVERGED_STALE, not success)
- score_ensemble_n: 3            (run SCORE PROMPT N independent times → average; reduces single-call variance)
                                 Research basis: AI Scientist-v2 (Sakana AI, arXiv:2504.08066, ICLR 2025 workshop)
                                 — multi-reviewer ensemble achieves balanced accuracy 69%, F1 > inter-human consistency.
                                 Default 3 (cost-balanced). Set to 1 to disable ensemble.
- exploration_rate: 0.2          (base probability of exploring non-weakest dimension in CANDIDATE_3)
                                 Dynamically adjusted each iteration based on recent score_variance:
                                   score_variance < 0.05 → rate × 1.5  (low variance = stuck → explore more)
                                   score_variance > 0.15 → rate × 0.5  (high variance = unstable → exploit more)
                                   else → rate unchanged
                                 Clamped to [0.05, 0.6]. 0.0 = pure exploitation, 1.0 = full random exploration.
                                 Research basis: Agent0 co-evolution (arXiv:2511.16043, +18-24%);
                                 SSP self-play (arXiv:2510.18821) — exploitation-only leads to local optima
- score_uncertain_threshold: 0.10 (NEW — lowered from implicit 0.15: protect "gray zone" variance 0.10-0.14
                                  from false convergence. At variance 0.10-0.15, plateau_count
                                  increments by 0.5 instead of 1.0. Source: 20260330-omc-live-critique P0-2)
- evaluator_mode: "self"         (NEW — controls how SCORE PROMPT is evaluated.
                                  "self": default — same session self-scoring, identical to current behavior.
                                  "cross_prompt": system prompt reset to skeptical reviewer before scoring.
                                  "oracle_only": auto-oracle results only, LLM scoring disabled — requires oracle.
                                  Source: 20260330-omc-live-critique P0-1, Anthropic Generator/Evaluator separation)
- context_budget_pct: 70         (trigger early handoff when estimated context usage reaches this %)
                                 Research basis: agents consume 4–15× standard chat tokens (Oracle/LangChain 2025);
                                 context exhaustion mid-run leaves codebase in inconsistent state
                                 Anthropic internal testing confirms quality drop-off begins at ~70% utilization.
                                 Note: token estimation uses language/code-aware correction (see Step 3b).

Domain Specialization (optional):
- domain_profile: null           (path to domain profile file, e.g., ".omc/domain-profile.md")
                                 When set, overrides score_dimensions and injects domain scoring oracle.
                                 null = generic mode (default). Set to file path to enable domain mode.
                                 Template: .omc/domain-profile.md (see PRE-LOOP step 2.5 for format)
</Configuration>

<Steps>
## Flag Parsing (FIRST — before any other step)

Parse args before executing any protocol step:

```
args = skill invocation arguments
args_stripped = args.strip()
args_lower = args_stripped.lower()

# -i / --inf flag: route to live-inf (case-insensitive)
if args_lower == "-i" or args_lower == "--inf"
   or args_lower.startswith("-i ") or args_lower.startswith("--inf "):
    stripped_args = args_stripped after removing the leading flag token
                   (e.g., "-i implement X" → "implement X", "-I" → "", "--INF do Y" → "do Y")
    → Skill('live-inf', args=stripped_args)
    → STOP: live-inf handles all remaining execution
```

Supported flags:
| Flag | Behavior |
|------|----------|
| `-i`, `-I`, `--inf`, `--INF` (case-insensitive) | Route to live-inf (unbounded, convergence-only termination; **NO user prompting between iterations** — see live-inf `<Autonomy_Contract>`) |
| *(none)* | Run live (bounded, max_outer_iterations=5) — interactive choice menus permitted on UNCERTAIN/exhaustion |

Example:
```
/live -i implement X         →  live-inf runs with "implement X" (new goal)
/live -i                     →  live-inf runs with "" (resume mode)
/live implement X            →  live (bounded) runs with "implement X" (new goal)
/live                        →  live (bounded) resumes previous goal
```

---

## Outer Loop Execution Protocol

### PRE-LOOP: Initialize context

1. **Load past episodes** via `omc-episode-memory` (load mode):
   - Invoke `omc-episode-memory` skill in LOAD mode — it handles TF-IDF ranking internally
     (omc-episode-memory uses TF-IDF cosine similarity when ≥5 episodes exist; tag-based fallback otherwise)
   - Inject top 3 relevant episodes into working context
   - Report: "Found N relevant past episodes. Key lessons: [summary]"
   - If no episodes → "Starting fresh. No past experience for this task type."

   **Cross-trajectory recombination** (Research basis: SE-Agent, NeurIPS 2025, +55% SWE-bench):
   - Additionally load up to 3 *failed* episodes with similar task keywords
   - Extract: what strategies were attempted, at which phase they failed, and what partial progress was made
   - Inject as: "Past failure patterns: [strategy X failed at phase N — avoid / try alternative Y]"
   - This recombines failure trajectories into actionable avoidance hints for the current run
   - If no failed episodes → skip silently (no message)

   **Co-evolution input** (Research basis: Agent0, arXiv:2511.16043, +18-24%):
   - From successful episodes: extract "task types where autopilot succeeded" as `success_patterns`
   - Format: "Previously succeeded at: [task_type_1, task_type_2, ...]"
   - Store in working context as `{success_patterns}` — used in Step 6b to calibrate goal elevation
   - Goal elevation targets areas BEYOND current success patterns (avoids trivial repetition)
   - If no successful episodes → `success_patterns = []` (goal elevation unconstrained)

2. **Initialize or load GoalTree** via `omc-goal-tree`:

   **Goal resolution priority** (args vs persisted state):

   | Invocation | Behavior |
   |------------|----------|
   | `Skill('live', args='<any non-empty text>')` | **NEW GOAL** — args 전체를 goal로 사용 (이전 상태 무시). `Goal:` prefix가 있으면 strip. |
   | `/live` 단독 (args 없음) | **RESUME** — goal-tree.json이 있으면 이전 목표 재개 |
   | `/live` 단독 + goal-tree.json 없음 | 에러: "No active goal. Run `/live <task>` to start." |

   **New Goal 처리** (args가 비어있지 않을 때):
   ```
   goal = args.strip()
   if goal.lower().startswith("goal:"):
       goal = goal[5:].strip()   # "Goal:" prefix 제거 (하위 호환)
   ```
   ```json
   {
     "root_goal": "<goal>",
     "original_goal": "<goal>",
     "level": 0,
     "sub_goals": [],
     "evolution_count": 0,
     "evolution_history": [],
     "reward_spec": {"primary_metric": "task completion", "threshold": "all acceptance criteria met"},
     "history": []
   }
   ```
   Note: `original_goal`은 init 시 한 번만 설정 — 이후 goal evolution이 일어나도 덮어쓰지 않음.

   **Resume 처리** (args 없음 + goal-tree.json 존재):
   - goal-tree.json 로드 → 기존 `root_goal`, `evolution_count`, `history` 유지
   - Display: "Resuming: [root_goal] (iter {evolution_count+1}/{max_outer_iterations})"

   Display (new goal): "Outer goal: [root_goal]. Starting iteration 1/{max_outer_iterations}."

2.5. **Load domain profile** (skip if `domain_profile: null`):
   - Read the file at `domain_profile` path (e.g., `.omc/domain-profile.md`)
   - Parse three sections:
     ```
     ## Score Dimensions
     <comma-separated list> → override config score_dimensions for this run
     (goal_fidelity is always appended automatically if not present)

     ## Score Oracle
     <shell command with {output_dir} placeholder, or "none">
     → command to invoke external evaluator; stdout must be parseable key:value lines
     → e.g.: python eval_benchmark.py --output {output_dir}

     ## Convergence Rule  (optional)
     <natural-language stopping rule>
     → e.g.: "Converged if accuracy > 0.90 AND reproducibility_check = PASS"
     → injected verbatim into SCORE PROMPT as additional stopping guidance
     ```
   - Store as `{domain_score_dimensions}`, `{domain_oracle_cmd}`, `{domain_convergence_rule}`
   - Report: "[DOMAIN] Profile loaded: {N} dimensions, oracle={'yes' if cmd else 'none'}"
   - If file not found → log "[DOMAIN] Profile not found at {path} — falling back to generic mode"
     and clear `domain_profile` for this run

3. **Check iteration budget**:
   - Read `.omc/live-state.json` for current_iteration (default 0)
   - If current_iteration >= max_outer_iterations → STOP, report exhaustion, generate handoff

3a. **Iteration Alignment Check** (skip on first iteration; from iteration 2 onwards — P1-2):
   (Research: LlamaFirewall AlignmentCheck arXiv:2505.03574; Goal Drift arXiv:2505.02709 —
    all LLMs exhibit drift in extended runs; drift correlates with context length growth)
   # Alignment Check runs from iteration 2+ because: (FIX-2)
   # - Iteration 1: root_goal == original_goal by definition (no drift possible yet)
   # - Iteration 2+: goal may have evolved from Step 6b in prior iter → drift check needed
   # Exception: if first iteration itself triggers goal evolution (early_evolve flag),
   #            alignment check runs before that evolution is committed.
   Verify `root_goal` still aligns with `original_goal` BEFORE invoking autopilot:
   ```
   ALIGNMENT CHECK PROMPT (1 call, goal_check_model):
   Original user goal: {original_goal}
   Current goal (may be evolved): {root_goal}
   Evolution depth: {evolution_count}

   Rate semantic alignment (0.0 to 1.0):
   1.0 = same intent, just more specific
   0.5 = related but significantly different scope
   0.0 = completely different topic

   Output EXACTLY one line: alignment: 0.XX
   ```
   ```
   if alignment_score < goal_fidelity_min (default 0.7):
       emit: "[ALIGNMENT WARNING] iter {N}: root_goal drifts from original_goal
              (alignment={alignment_score:.2f}).
              Original: '{original_goal[:60]}'
              Current:  '{root_goal[:60]}'"
       → Present to user: "Confirm continue with evolved goal, or revert to original?"
       → Wait for user response (do NOT proceed autonomously on alignment failure)
   else:
       log: "[ALIGNMENT OK] iter {N}: alignment={alignment_score:.2f}"

   # Also check cumulative_fidelity in alignment check (early warning — P2-8):
   if cumulative_fidelity < cumulative_fidelity_min + 0.10:  # within 0.10 of limit
       emit: "[ALIGNMENT WARN] Cumulative fidelity {cumulative_fidelity:.2f} approaching limit {cumulative_fidelity_min}"
   ```
   Note: Catches misalignment BEFORE running an expensive autopilot cycle.
   Detects Goodhart drift that the goal_fidelity gate (Step 6a) catches only AFTER execution.

3b. **Context budget check** (P2-3):
   Estimate context tokens consumed so far using language/code-aware correction.
   Naive `total_chars / 4` has ±30% error: Korean ~1.5 chars/token, code ~0.35 chars/token,
   English prose ~0.75 chars/token. Mixing these without correction causes systematic
   under-estimation (Korean-heavy sessions trigger handoff too late).

   ```
   # Token estimation with content-type correction
   session_text = [all messages + tool outputs in current context]
   total_chars  = len(session_text)

   korean_chars = count of chars in Unicode range AC00-D7A3 (Hangul syllables)
   code_chars   = chars inside ``` blocks or indented code (heuristic: lines starting with 4+ spaces)
   other_chars  = total_chars - korean_chars - code_chars

   korean_ratio = korean_chars / total_chars   (default 0 if total_chars == 0)
   code_ratio   = code_chars   / total_chars

   # Weighted harmonic mean of chars-per-token by content type
   chars_per_token = (1.5  * korean_ratio) \
                   + (0.35 * code_ratio)   \
                   + (0.75 * (1 - korean_ratio - code_ratio))

   estimated_tokens     = total_chars / chars_per_token
   estimated_context_pct = (estimated_tokens / context_window_size) * 100
   # context_window_size: use 200_000 for Claude (Sonnet/Opus), else 128_000
   ```

   ```
   if estimated_context_pct > context_budget_pct (default 70):
       log: "[CONTEXT] Approaching limit (~{estimated_context_pct:.0f}%, korean={korean_ratio:.0%}, code={code_ratio:.0%}). Triggering early handoff."
       → Save live-state.json, generate handoff report → STOP
   ```

   **Fallback**: if character counting is unavailable, use `total_chars / 4` (original naive estimate)
   and add +10% safety margin to compensate for under-estimation bias.

3d. **Context Priming** (NEW — P1-4, Source: 20260330-omc-live-critique):
   Injects key lessons from episode memory into autopilot context
   to counteract auto-compact information loss. Runs after 3b, before autopilot.
   ```
   if current_iteration > 1:
       # Quality-filtered episode retrieval (improved from P1-4 — FIX-3):
       relevant = load_episodes(
           query=root_goal,
           top_k=3,
           min_quality=0.6,         # existing
           max_age_iterations=20,   # NEW: ignore episodes older than 20 iterations
           exclude_outcome=["stale"] # NEW: exclude CONVERGED_STALE episodes
       )
       # If fewer than 2 results with filters: relax max_age to 50, keep min_quality=0.6
       if len(relevant) < 2:
           relevant = load_episodes(query=root_goal, top_k=3, min_quality=0.6, max_age_iterations=50)
       failed_patterns = [e.failure_pattern for e in relevant if e.outcome == "failure"]
       success_patterns = [e.key_decision for e in relevant if e.outcome == "success"]

       context_primer = f"""
   [CONTEXT PRIMER — iter {current_iteration}]
   Goal: {root_goal}
   Forbidden strategies (failed before): {failed_patterns[:3]}
   Proven approaches (worked before): {success_patterns[:2]}
   Current best score: {best_score:.2f} | Weak dimension: {min_dimension}
   """
       # This primer is prepended to the autopilot task prompt
       autopilot_prompt_prefix = context_primer
       emit: "[CTX PRIME] Injected {len(failed_patterns)} failure patterns, {len(success_patterns)} success patterns"

       # Skill Patch Injection (arxiv:2604.00901 — Evolving Orchestration):
       # Load experience-based patches from .omc/skill-patches/ and append to context_primer.
       # Patches evolve skill behavior without modifying SKILL.md files directly.
       from pathlib import Path
       patch_dir = Path(".omc/skill-patches")
       if patch_dir.exists():
           patches_injected = []
           patch_lines = []
           for patch_file in sorted(patch_dir.glob("*.json")):
               patch_data = json.loads(patch_file.read_text())
               skill_name = patch_data.get("skill_name", patch_file.stem)
               if patch_data.get("success_patterns"):
                   patch_lines.append(f"[{skill_name}] Proven: {'; '.join(patch_data['success_patterns'][:2])}")
               if patch_data.get("failure_patterns"):
                   patch_lines.append(f"[{skill_name}] Avoid: {'; '.join(patch_data['failure_patterns'][:2])}")
               if patch_data.get("parameter_adjustments"):
                   patch_lines.append(f"[{skill_name}] Adjust: {'; '.join(patch_data['parameter_adjustments'][:2])}")
               patches_injected.append(skill_name)
           if patch_lines:
               context_primer += "\n[SKILL PATCHES — experience-based prompt evolution]\n"
               context_primer += "\n".join(patch_lines)
               emit: f"[SKILL PATCH] Injected {len(patches_injected)} patch(es): {patches_injected}"
   ```

3e. **Autonomous Skill Router** (NEW — P3, Research: RouteLLM arXiv:2406.18665; ReAct Yao 2022; MoA arXiv:2406.04692):
   Classifies the current goal's task type and injects relevant skill/agent recommendations
   into the autopilot context. Runs AFTER Step 3d (Context Priming), BEFORE Step 4 (omc-autopilot).

   **Keyword Classification Table** (task_type only — NO hardcoded skills):
   ```
   TASK TYPE  │ TRIGGER KEYWORDS
   ───────────┼──────────────────────────────────────────────────────
   research   │ research, investigate, find, study, explore, survey
   code       │ implement, build, add, create, write, refactor
   debug      │ debug, error, fail, crash, broken, fix, bug
   review     │ review, check, verify, audit, quality, inspect
   plan       │ plan, design, architect, structure, strategy
   analysis   │ statistic, metric, data, result, measure, benchmark
   business   │ business, market, gtm, growth, revenue, customer
   ui         │ ui, frontend, design, component, page, interface
   security   │ security, auth, vulnerability, permission, OWASP
   knowledge  │ corpus, grounding, claim, entity, doc, knowledge, domain, wtp, canon
   ```
   Note: skill selection is NEVER done from this table — always from live available_skills via T2.
   The table only provides task_type classification for the T2 prompt context.

   **Routing Protocol (2-tier):**
   ```
   # PRE-STEP: Extract available_skills from session context
   # Claude Code injects the full installed skills list via <system-reminder> at every turn.
   # Read it from context — no tool call needed; it is already in Claude's working memory.
   #
   # available_skills = [all skill names visible in current <system-reminder> skills block]
   # This list is the GROUND TRUTH of what is actually installed and callable right now.
   available_skills = <read from session system-reminder skills list>

   # TIER 1 — Keyword classification only (zero cost — determines task_type, NOT skills)
   task_text = (root_goal + " " + last_autopilot_summary + " " + min_dimension).lower()

   task_type = None
   for t, keywords in KEYWORD_TABLE.items():
       if any(kw in task_text for kw in keywords):
           task_type = t
           break   # first match wins

   # TIER 2 — Dynamic LLM skill selection from live available_skills (ALWAYS runs)
   # T1 provides task_type hint; T2 selects actual skills from available_skills.
   # If T1 matched: T2 uses task_type as context. If not: T2 classifies on its own.
   #
   # TIER 2 PROMPT (inline, single LLM call):
   # ─────────────────────────────────────────
   # Goal: {root_goal}
   # Task type (pre-classified): {task_type or "unknown — classify yourself"}
   # Task types available: research | code | debug | review | plan | analysis | business | ui | security
   # Available skills in this session:
   #   {available_skills[:40]}   ← capped at 40 to stay within token budget
   #
   # Instructions:
   # 1. If task_type is "unknown", classify the goal into ONE task type above.
   # 2. From available_skills ONLY, select up to 3 most relevant skills for this task type.
   #    You MUST only select names that appear verbatim in the available_skills list above.
   #    Do NOT invent skill names. If uncertain, select the most general-purpose skill available.
   #
   # Output (STRICT):
   # task_type: <type>
   # selected: <skill1>, <skill2>, <skill3>
   # ─────────────────────────────────────────
   task_type, dynamic_selected = <run TIER 2 PROMPT inline>

   # Validate: all selected skills must be in available_skills (hallucination guard)
   selected_skills = [s for s in dynamic_selected if s in available_skills]
   routing_tier = "T1+T2" if task_type else "T2-only"

   # TIER 3 — Fallback: available_skills[:3] if T2 returned nothing (rare — LLM total failure)
   if not selected_skills:
       selected_skills = available_skills[:3]   # any real skill beats phantom name
       routing_tier = "T3-fallback"
       log: "[SKILL ROUTER] T3 fallback — T2 returned no valid skills"

   # INJECT into context primer (extending Step 3d output)
   context_primer += f"""
   [SKILL ROUTER — iter {current_iteration} | {routing_tier}]
   Task type: {task_type}
   Invoke these skills via Skill tool if relevant to this iteration:
   {chr(10).join(f"  - {s}" for s in selected_skills[:3])}
   """
   emit: "[SKILL ROUTER] type={task_type} | skills={selected_skills[:3]} | tier={routing_tier}"
   ```

   **Execution contract:**
   - If the goal clearly spans multiple types (e.g. "research + implement"), include top match from each.
   - Never invoke skills that are already part of the standard omc-live loop (omc-episode-memory, omc-goal-tree, omc-autopilot, omc-failure-router).
   - If routing produces no match and Tier 2 is uncertain: skip router, continue to autopilot as normal.

   **DISPATCH Layer** (P4 — replaces "RECOMMENDATIONS" passive injection):
   ```
   # ORCHESTRATOR MAP: task_type → dedicated orchestrator skill
   # When a task_type has an orchestrator, omc-live DELEGATES directly — skips omc-autopilot.
   ORCHESTRATOR_MAP = {
       "business":  "biz-autopilot",       # 6-phase biz cycle (researcher/marketer/content-writer/sales/ops)
       "research":  "expert-research-v2",   # 3-agent research pipeline
       "review":    "omc-code-review",      # code review skill
       "plan":      "omc-plan",             # planning skill
       "security":  "omc-security-review",  # security review
       "analysis":  "omc-analyze",          # analysis skill
       "knowledge": "entity",               # corpus-routed vertical AI scaffold (P6-12)
       # code / debug / ui → no orchestrator → AUTOPILOT mode (omc-autopilot)
   }

   # DISPATCH MODE DECISION
   def determine_dispatch_mode(task_type, selected_skills):
       if task_type in ORCHESTRATOR_MAP:
           # Verify orchestrator skill actually exists in available_skills
           orch = ORCHESTRATOR_MAP[task_type]
           if orch in available_skills:
               return "DELEGATE", orch
       if len(selected_skills) >= 2 and task_type not in ["code", "debug", "ui"]:
           return "FAN_OUT", selected_skills[:2]
       return "AUTOPILOT", None

   dispatch_mode, dispatch_target = determine_dispatch_mode(task_type, selected_skills)
   emit: "[DISPATCH] mode={dispatch_mode} | target={dispatch_target}"

   # USER CONSENT GATE — required before any external publish/post action
   # Fire ONLY when: dispatch_target is biz-autopilot AND goal contains publish/post keywords
   if dispatch_mode == "DELEGATE" and any(kw in root_goal.lower()
       for kw in ["publish", "post", "submit", "게시", "홍보", "제출"]):
       emit: "[CONSENT] About to execute external publish action via {dispatch_target}."
       emit: "         Confirm: Y=proceed / N=skip external publish / S=stop loop"
       wait_for_user_consent()   # pause here; resume on Y

   if dispatch_mode == "DELEGATE":
       # Invoke the orchestrator skill directly — omc-autopilot is SKIPPED this iteration
       result = invoke Skill(name=dispatch_target, args=root_goal + "\n\nContext:\n" + context_primer)
       autopilot_summary = result.summary or f"Delegated to {dispatch_target}. Goal: {root_goal[:60]}"
       last_outcome = result.outcome or "success"
       last_phase_reached = f"delegated:{dispatch_target}"
       → skip Step 4, proceed directly to Step 5 (increment counter)

   elif dispatch_mode == "FAN_OUT":
       # Spawn specialist agents in parallel, synthesize results
       results = []
       for skill_name in dispatch_target:
           r = invoke Skill(name=skill_name, args=root_goal)
           results.append(r)
       autopilot_summary = "FAN_OUT: " + " | ".join(r.summary[:40] for r in results)
       last_outcome = "success" if all(r.outcome != "failure" for r in results) else "partial"
       last_phase_reached = f"fan_out:{','.join(dispatch_target)}"
       → skip Step 4, proceed directly to Step 5

   else:  # AUTOPILOT
       # Standard omc-autopilot path (code/debug/ui tasks).
       # knowledge/research/business reach here ONLY IF orchestrator skill unavailable AND selected_skills < 2.
       context_primer += f"""
   [SKILL ROUTER — iter {current_iteration} | {routing_tier}]
   Task type: {task_type}
   Suggested skills (call via Skill tool if helpful):
   {chr(10).join(f"  - {s}" for s in selected_skills[:3])}
   """
       → proceed to Step 4 (omc-autopilot) as normal
   ```

---

### WAVE 1: Strategy Phase (runs ONCE per omc-live invocation)

3f. **Wave 1 — Expert Strategy Consultation** (P5 — 2-Wave Architecture):
   Wave 1 runs ONCE at the start of a fresh omc-live run to produce an optimized
   execution plan before any implementation begins. Wave 2 (Steps 4+) is seeded with
   this plan. On resume (live-state.json exists), Wave 1 is skipped and the saved plan
   is loaded directly.

   ```
   # Check if Wave 1 already completed (resume guard)
   if live_state.get("wave1_complete"):
       wave1_plan = live_state["wave1_plan"]
       emit: "[WAVE1 LOADED] Resuming with existing strategy plan"
       → skip to WAVE 2 (Step 4)

   # ── Wave 1 Execution ──────────────────────────────────────────
   emit: "[WAVE1 START] Consulting specialist agents for: {root_goal[:60]}"

   # WAVE 1 SPECIALIST MAP (task_type → strategy agents to call in parallel)
   # These agents produce PLAN/STRATEGY, not implementation.
   WAVE1_SPECIALISTS = {
       "business":  ["biz-researcher", "biz-marketer"],          # ICP + channel strategy
       "research":  ["expert-research-v2"],                       # 3-agent research pipeline
       "code":      ["research-explore", "ops-planner"],          # codebase recon + approach
       "debug":     ["ops-debugger"],                             # root cause analysis
       "review":    ["review-harsh-critic"],                      # adversarial assessment
       "plan":      ["ops-planner"],                              # structured planning
       "analysis":  ["research-deep-analyst"],                    # hypothesis generation
       "security":  ["sec-reviewer"],                             # threat model
       "ui":        ["research-explore"],                         # pattern discovery
       "knowledge": ["entity", "research-deep-analyst"],           # corpus grounding + synthesis
   }

   # Select specialists (fallback: first 2 from available_skills if map empty)
   specialists = WAVE1_SPECIALISTS.get(task_type, [])
   specialists = [s for s in specialists if s in available_skills]
   if not specialists:
       specialists = [s for s in available_skills if s not in
           ["omc-live", "omc-live-inf", "omc-autopilot",
            "omc-episode-memory", "omc-goal-tree", "omc-failure-router"]][:2]

   # ── Repo Context Injection (code/debug/ui tasks only) ─────────────────────
   # auto-index.py (SessionStart hook) ensures mcp__code-search__ is always indexed.
   # Inject repo-aware context BEFORE specialist fan-out so Wave 1 plan is codebase-grounded.
   if task_type in ["code", "debug", "ui"]:
       repo_hits = mcp__code-search__search_code(query=root_goal, top_k=5)
       if repo_hits:
           repo_context_block = "[REPO CONTEXT — existing patterns]\n"
           for hit in repo_hits:
               repo_context_block += f"  {hit.file}:{hit.line} — {hit.snippet[:100]}\n"
           context_primer += "\n" + repo_context_block
           emit: "[REPO CTX] {len(repo_hits)} relevant code snippets injected from indexed codebase"
       else:
           emit: "[REPO CTX] No relevant snippets found — proceeding without repo context"

   # ── Library Docs Injection (context7 MCP) ─────────────────────────────────
   # If root_goal mentions a known library/framework, fetch current docs via context7.
   # Prevents hallucinated API usage that breaks in Phase 3 QA.
   if task_type in ["code", "debug", "ui"]:
       lib_keywords = ["react", "next", "prisma", "fastapi", "pytest", "typescript",
                       "tailwind", "express", "django", "sqlalchemy", "pydantic"]
       detected_libs = [lib for lib in lib_keywords if lib in root_goal.lower()]
       if detected_libs:
           for lib in detected_libs[:2]:  # max 2 (cost guard)
               lib_id = mcp__plugin_context7_context7__resolve-library-id(libraryName=lib)
               if lib_id:
                   docs = mcp__plugin_context7_context7__query-docs(context7CompatibleLibraryID=lib_id, topic=root_goal, tokens=3000)
                   context_primer += f"\n[LIBRARY DOCS — {lib}]\n{docs[:800]}"
           emit: "[CTX7] Library docs injected: {detected_libs[:2]}"

   # ── TDD Gate (code tasks only) ─────────────────────────────────────────────
   # omc-tdd writes tests before Phase 2 execution → Phase 3 QA has a concrete target.
   # Only runs on first iteration (evolution_count==0) to avoid re-testing evolved goals.
   if task_type == "code" and evolution_count == 0:
       tdd_result = invoke Skill(name="omc-tdd", args=root_goal)
       if tdd_result and tdd_result.tests_written:
           context_primer += f"\n[TDD] Tests pre-written: {tdd_result.tests_written} test(s). Autopilot must pass them."
           emit: "[TDD] {tdd_result.tests_written} test(s) written — Phase 2 will target these"
       else:
           emit: "[TDD] Skipped or no tests produced — proceeding without TDD gate"

   # ── Fan-out: call all specialists in parallel (each gets root_goal + context_primer)
   WAVE1_PROMPT = f"""
   You are a strategy consultant. Do NOT implement anything.
   Analyze this goal and produce a structured strategy plan only.

   Goal: {root_goal}
   Context: {context_primer}

   Output format (STRICT):
   APPROACH: <1-2 sentences — overall method>
   METHOD: <step-by-step approach, 3-5 steps>
   KEY_DECISIONS: <2-3 critical choices that will determine success>
   ANTI_PATTERNS: <2-3 common mistakes to avoid>
   RECOMMENDED_TOOLS: <specific skills/agents to use in Wave 2>
   CONSTRAINTS: <hard limits or non-negotiables>
   """

   wave1_outputs = []
   for specialist in specialists:
       result = invoke Skill(name=specialist, args=WAVE1_PROMPT)
       wave1_outputs.append({"specialist": specialist, "output": result.summary})
       emit: "[WAVE1] {specialist} → done"

   # Synthesize: merge all specialist outputs into single wave1_plan
   SYNTHESIS_PROMPT = f"""
   Merge these specialist strategy outputs into a single coherent execution plan.
   Resolve conflicts by favoring the most conservative/safe approach.

   Specialist outputs:
   {json.dumps(wave1_outputs, indent=2)}

   Produce a unified plan with these fields:
   - approach: single best approach
   - method: ordered steps
   - key_decisions: merged decisions
   - anti_patterns: all anti-patterns (deduplicated)
   - recommended_tools: merged tool recommendations
   - constraints: all constraints
   """
   wave1_plan = synthesize(SYNTHESIS_PROMPT)  # single LLM call

   # Persist to live-state.json
   live_state["wave1_complete"] = true
   live_state["wave1_plan"] = wave1_plan
   live_state["wave1_specialists"] = specialists
   save_live_state()

   emit: "[WAVE1 COMPLETE] Strategy plan ready. Entering Wave 2 execution."
   emit: "  Approach: {wave1_plan['approach']}"
   emit: "  Specialists consulted: {specialists}"
   ```

   **Wave 1 → Wave 2 handoff** (inject plan into all subsequent iterations):
   ```
   # Prepend wave1_plan to context_primer for every Wave 2 iteration
   wave1_context_block = f"""
   [WAVE 1 STRATEGY PLAN — do not override, use as execution guide]
   Approach: {wave1_plan['approach']}
   Method:
   {wave1_plan['method']}
   Key Decisions: {wave1_plan['key_decisions']}
   Anti-patterns to avoid: {wave1_plan['anti_patterns']}
   Recommended tools: {wave1_plan['recommended_tools']}
   Constraints: {wave1_plan['constraints']}
   """
   context_primer = wave1_context_block + context_primer
   ```

   **Wave 1 budget**: max 2 specialist calls per task_type (cost guard).
   If token estimate > 20% of context_budget → use only top-1 specialist.

---

### WAVE 2: Execution Loop (seeded by Wave 1 plan)

4. **Execute one autopilot cycle** (AUTOPILOT dispatch_mode only — skipped for DELEGATE/FAN_OUT):
   - Invoke `omc-autopilot` with current goal context from GoalTree
   - Pass episode context as additional instructions to Phase 0
   - Track: which phase completed, outcome (success/failure/partial)

   **Post-execution extraction** (required — used by Steps 6a, 6b):
   After autopilot completes, extract and store in working context:
   - `autopilot_summary`: 2–4 sentence summary of what was built/changed this iteration
     (derive from autopilot's final status message or Phase 5 cleanup report)
     If autopilot produces no summary → generate from git diff: "Modified: [file list]. Goal: [root_goal]."
   - `autopilot_output_dir`: the working directory where autopilot produced its output
     (default: current project root; override if autopilot wrote to a subdirectory)
   - `validator_results`: test/lint results from autopilot Phase 4
     (derive from autopilot's validator output; if Phase 4 not reached → "N/A — phase_4 not executed")

5. **Increment iteration counter** in `.omc/live-state.json`:
   ```json
   {
     "current_iteration": N,
     "last_outcome": "success|failure|partial",
     "last_phase_reached": "phase_N",
     "started_at": "ISO8601"
   }
   ```

5a. **Checkpoint commit** (rollback point — MANDATORY after every iteration):

   Run after live-state.json is written:
   ```bash
   git add -u   # tracked files only — avoids staging untracked secrets (.env, credentials)
   git commit -m "omc-live iter {N}/{max_outer_iterations}: {last_outcome} | goal_v{evolution_count}: {root_goal[:60]}"
   ```

   **Commit message format**:
   ```
   omc-live iter 2/5: success | goal_v1: implement auth with JWT and refresh tokens
   omc-live iter 3/5: partial | goal_v1: implement auth with JWT and refresh tokens
   omc-live iter 4/5: success | goal_v2: add rate limiting and audit logging to auth
   ```

   **Failure handling** (non-blocking — never abort the loop on commit failure):
   ```
   if git not available OR no changes to commit:
       log: "[CHECKPOINT] iter {N} — no commit (no git / no changes)"
       continue normally
   if git commit fails:
       log: "[CHECKPOINT] iter {N} — commit failed: {error}"
       continue normally (do NOT abort the outer loop)
   ```

   **Rollback usage** (user reference — shown in CONVERGED_STALE and Handoff reports):
   ```
   # List all omc-live checkpoints
   git log --oneline | grep "omc-live iter"

   # Rollback to specific iteration
   git checkout <commit-hash>

   # View diff between iterations
   git diff <hash-N> <hash-N+1>
   ```

5b. **Progress Log** (NEW — P1-5, Source: 20260330-omc-live-critique):
   Records per-iteration status to `.omc/live-progress.log` for long-running monitoring.
   ```
   progress_entry = {
       "iteration": current_iteration,
       "timestamp": ISO8601_now(),
       "score": current_score,
       "score_vector": current_scores,
       "goal": root_goal[:80],
       "outcome": last_outcome,
       "plateau_count": plateau_count,
       "elapsed_sec": elapsed_since_start
   }
   append_jsonl(".omc/live-progress.log", progress_entry)

   # Also emit a one-line summary to stdout (visible in terminal):
   emit: f"[LIVE iter {current_iteration}] score={current_score:.3f} ({last_outcome}) | goal={root_goal[:60]}"
   ```

---

### POST-LOOP: Evaluate and decide

6. **Evaluate outer goal achievement** (structured judgment — prevents hallucination):

   Use the following prompt template with goal_check_model (default: sonnet):
   ```
   JUDGMENT PROMPT:
   Outer goal: {root_goal}
   Reward spec: {reward_spec.primary_metric} — threshold: {reward_spec.threshold}
   Autopilot outcome this iteration: {last_outcome}
   Phase reached: {last_phase_reached}
   Validator results (if Phase 4 ran): {validator_results}

   Answer with EXACTLY one of:
   - YES   → outer goal fully achieved, all acceptance criteria met
   - NO    → outer goal not yet achieved, specific gap: [what remains]
   - UNCERTAIN → cannot determine from available evidence, reason: [why]

   Do not use any other format.
   ```

   **Output Parser** (MANDATORY — applied before branching):
   ```
   PARSE RULES:
   1. Strip leading/trailing whitespace from model response
   2. Take only the first line if multi-line
   3. Extract first token (space-separated), uppercase it
   4. Match starts-with: "YES" | "NO" | "UNCERTAIN" (case-insensitive)
      - "YES, but..." → YES
      - "NO - specific gap..." → NO
      - "UNCERTAIN because..." → UNCERTAIN
   5. If first token does NOT start with any of these → PARSE FAILURE:
      - Log: {"ts": "...", "event": "parse_failure", "raw_output": "<first 200 chars>"}
      - Default to UNCERTAIN
      - Set uncertain_reason = "Judgment output did not start with YES|NO|UNCERTAIN. Raw: [first 100 chars]"
   ```

   Process response (after parsing):
   - **YES** → proceed to SCORE step (Step 6a) — do NOT immediately stop
   - **NO** → proceed to NOT YET branch, include "specific gap" in GoalTree Level 1 update
   - **UNCERTAIN** (including parse failures) → human escalation required (see below)

6a. **[SELF-EVOLUTION] Score current state** (only when evolve_mode=true AND YES verdict):

   **Auto Oracle Detection** (runs BEFORE domain oracle check, if `domain_oracle_cmd` is null):
   ```
   # Self-scoring problem: LLM evaluating own work has systematic bias.
   # Solution: auto-detect standard project tooling → use as ground truth oracle.
   # Detected oracle scores replace LLM scoring for measurable dimensions.

   auto_oracle_scores = {}

   # Python projects (code/debug/ui 태스크에만 실행 — knowledge/research/business는 domain oracle로 처리)
   if task_type in ["code", "debug", "ui"] and ("pytest.ini" OR "pyproject.toml" OR "setup.cfg" exists in project root):
       result = shell("python3 -m pytest --tb=no -q 2>&1")
       # Parse: "N passed" → test_pass_rate = N_passed / N_total
       # Parse: "Total coverage: XX%" → coverage = XX / 100
       if parsed_successfully:
           auto_oracle_scores["test_pass_rate"] = N_passed / N_total   # 0.0–1.0
           auto_oracle_scores["coverage"] = coverage_pct / 100         # 0.0–1.0
           # Map to score_dimensions:
           #   completeness ← test_pass_rate  (tests passing = task completeness)
           #   impact       ← coverage        (coverage = real-world impact of test quality)
           oracle_scores = auto_oracle_scores
           log: "[AUTO ORACLE] pytest: {N_passed}/{N_total} passed, coverage={coverage_pct:.1f}%"
           log: "[AUTO ORACLE] mapped → completeness={test_pass_rate:.2f}, impact={coverage:.2f}"

   # Node.js / TypeScript projects (code/debug/ui 태스크에만 실행)
   elif task_type in ["code", "debug", "ui"] and ("package.json" exists AND "scripts.test" in package.json):
       result = shell("npm test --silent 2>&1 | tail -5")
       if parsed_successfully (test summary found):
           auto_oracle_scores["test_pass_rate"] = N_passed / N_total
           oracle_scores = auto_oracle_scores
           log: "[AUTO ORACLE] npm test: {N_passed}/{N_total} passed"

   # No tooling found
   elif task_type in ["knowledge", "research", "analysis"]:
       # Domain-Aware Quality Oracle: grounding-based LLM-as-judge rubric
       # Reference: MAE oracle-free scoring (arXiv:2510.23595) — structured rubric without external ground truth
       #            SwarmSys corpus-native oracle (arXiv:2510.10047) — pheromone trace signal strength

       # Entity corpus signal detection (P6-entity):
       # When goal/output context suggests entity corpus routing, extend rubric with corpus-native metrics.
       # Research: 20260414-entity-loop-skill-spec.md — 4-dim oracle spec:
       #   grounding_rate (≥0.85), routing_precision (≥0.80), claim_quality (≥0.75), sycophancy_pass (≥0.90)
       # Strong signals (single match sufficient — entity-specific vocabulary)
       ENTITY_STRONG_SIGNALS = ["entity", "routing_precision", "corpus-routed", "[grounded:",
                               "corpus_mode", "active_corpus", "sycophancy_pass"]
       # Weak signals (require 2+ matches to avoid false positives on academic text)
       ENTITY_WEAK_SIGNALS = ["corpus", "wtp", "value gap", "canon", "grounding_rate"]
       context_lower = (root_goal + " " + autopilot_summary).lower()
       strong_hits = sum(1 for s in ENTITY_STRONG_SIGNALS if s in context_lower)
       weak_hits = sum(1 for s in ENTITY_WEAK_SIGNALS if s in context_lower)
       is_entity_corpus = strong_hits >= 1 or weak_hits >= 2

       base_rubric_dims = """
       - grounding_rate: fraction of domain claims backed by cited sources or explicit reasoning (vs bare assertions)
       - claim_quality: precision and falsifiability of claims (vague/hedged → low; specific/testable → high)
       - coverage_depth: does the output address all aspects of the goal, not just surface-level?
       - synthesis_quality: are multiple perspectives integrated coherently, or just listed?"""

       entity_rubric_dims = """
       [ENTITY CORPUS EXTENSION — only if corpus-routing was active]
       - routing_precision: fraction of queries that matched a registered corpus (vs fell back to generic mode)
                            (1.0 = all queries routed to correct corpus, 0.0 = all generic fallback)
       - sycophancy_pass: fraction of sycophancy check gates that returned PASS
                          (1.0 = all checks passed, 0.0 = all flagged — sycophancy detected)""" if is_entity_corpus else ""

       base_output_format = """
       Output format (STRICT, one line each):
       grounding_rate: 0.XX
       claim_quality: 0.XX
       coverage_depth: 0.XX
       synthesis_quality: 0.XX"""

       entity_output_format = """
       routing_precision: 0.XX
       sycophancy_pass: 0.XX""" if is_entity_corpus else ""

       GROUNDING_RUBRIC = f"""
       Evaluate the quality of this output on the following dimensions (0.0–1.0 each):
       {base_rubric_dims}
       {entity_rubric_dims}
       {base_output_format}
       {entity_output_format}

       Output to evaluate:
       {autopilot_summary}

       Goal: {root_goal}
       """
       rubric_result = LLM(GROUNDING_RUBRIC, model=goal_check_model)
       for line in rubric_result.split("\n"):
           if ":" in line:
               k, v = line.split(":", 1)
               try:
                   auto_oracle_scores[k.strip()] = float(v.strip())
               except ValueError:
                   pass  # skip non-numeric lines
       # Map to score_dimensions:
       #   grounding_rate + claim_quality → quality
       #   coverage_depth                 → completeness
       #   synthesis_quality              → impact
       #   routing_precision              → efficiency   (entity corpus only)
       #   sycophancy_pass                → quality (blended)  (entity corpus only)
       oracle_scores = {
           "quality":      (auto_oracle_scores.get("grounding_rate", 0.5) + auto_oracle_scores.get("claim_quality", 0.5)) / 2,
           "completeness": auto_oracle_scores.get("coverage_depth", 0.5),
           "impact":       auto_oracle_scores.get("synthesis_quality", 0.5),
       }
       if is_entity_corpus and "routing_precision" in auto_oracle_scores:
           oracle_scores["efficiency"] = auto_oracle_scores["routing_precision"]
           log: "[DOMAIN ORACLE entity] routing_precision={oracle_scores['efficiency']:.2f}"
       if is_entity_corpus and "sycophancy_pass" in auto_oracle_scores:
           # Blend sycophancy_pass into quality: higher weight (direct anti-hallucination signal)
           oracle_scores["quality"] = (oracle_scores["quality"] + auto_oracle_scores["sycophancy_pass"]) / 2
           log: "[DOMAIN ORACLE entity] sycophancy_pass={auto_oracle_scores['sycophancy_pass']:.2f} → quality blended"
       if is_entity_corpus and "claim_quality" in auto_oracle_scores:
           # Iter 48: entity emits claim_quality in all corpus-mode responses (not just Wave1)
           # claim_quality = fraction of claims with evidence tags → direct proxy for actionable impact
           impact_base = auto_oracle_scores["claim_quality"]
           # Iter 51: blend with actionability if present (14th Quality Gate check)
           if "actionability" in auto_oracle_scores and auto_oracle_scores["actionability"] >= 0:
               oracle_scores["impact"] = (impact_base + auto_oracle_scores["actionability"]) / 2
               log: "[DOMAIN ORACLE entity] impact = (claim_quality={impact_base:.2f} + actionability={auto_oracle_scores['actionability']:.2f}) / 2 = {oracle_scores['impact']:.2f} (Iter 51)"
           else:
               oracle_scores["impact"] = impact_base
               log: "[DOMAIN ORACLE entity] claim_quality={oracle_scores['impact']:.2f} → impact (Iter 48, no actionability)"
       log: "[DOMAIN ORACLE] knowledge/research rubric → quality={oracle_scores['quality']:.2f}, completeness={oracle_scores['completeness']:.2f}, impact={oracle_scores['impact']:.2f}{' | entity_corpus=True' if is_entity_corpus else ''}"

   elif task_type == "business":
       BUSINESS_RUBRIC = f"""
       Evaluate this business analysis output on the following dimensions (0.0–1.0 each):
       - hypothesis_validity: are the market/customer hypotheses grounded and falsifiable?
       - actionability: are the recommendations specific and executable (not generic advice)?
       - evidence_quality: are claims backed by data, frameworks, or cited precedents?
       - risk_coverage: does the output identify key risks and counter-arguments?

       Output format (STRICT):
       hypothesis_validity: 0.XX
       actionability: 0.XX
       evidence_quality: 0.XX
       risk_coverage: 0.XX

       Output: {autopilot_summary}
       Goal: {root_goal}
       """
       rubric_result = LLM(BUSINESS_RUBRIC, model=goal_check_model)
       for line in rubric_result.split("\n"):
           if ":" in line:
               k, v = line.split(":", 1)
               auto_oracle_scores[k.strip()] = float(v.strip())
       oracle_scores = {
           "quality":      (auto_oracle_scores.get("hypothesis_validity", 0.5) + auto_oracle_scores.get("evidence_quality", 0.5)) / 2,
           "completeness": auto_oracle_scores.get("actionability", 0.5),
           "impact":       auto_oracle_scores.get("risk_coverage", 0.5),
       }
       log: "[DOMAIN ORACLE] business rubric → quality={oracle_scores['quality']:.2f}, completeness={oracle_scores['completeness']:.2f}, impact={oracle_scores['impact']:.2f}"

   else:
       log: "[AUTO ORACLE] No standard test tooling detected — falling back to LLM scoring"

   # Extended Oracle Detection (NEW — P0-3, Source: 20260330-omc-live-critique):
   # Expand deterministic oracle coverage beyond test_pass_rate and coverage.
   # Lint errors and type errors are objective, measurable quality signals.

   if task_type in ["code", "debug", "ui"] and ("eslint" or ".eslintrc*" exists in project):
       oracle["lint_errors"] = "npx eslint . --format json | jq '.[].errorCount' | awk '{s+=$1} END {print s}'"
       auto_oracle_scores["lint_score"] = max(0, 1.0 - lint_errors / 10)
       log: "[AUTO ORACLE] lint: {lint_errors} errors → lint_score={lint_score:.2f}"

   if task_type in ["code", "debug", "ui"] and ("mypy" or "pyright" or "tsconfig.json" exists):
       # Python: mypy . --json 2>&1 | python -c 'import sys,json; ...; print(len(data["errors"]))'
       # TypeScript: npx tsc --noEmit 2>&1 | grep -c "error TS"
       auto_oracle_scores["type_score"] = max(0, 1.0 - type_errors / 5)
       log: "[AUTO ORACLE] type-check: {type_errors} errors → type_score={type_score:.2f}"

   # Oracle-to-dimension mapping (clarified — P0-3):
   # test_pass_rate     → completeness (what was asked, delivered)
   # coverage           → completeness (code paths covered)
   # lint_score         → quality      (code style correctness)  ← NEW
   # type_score         → quality      (type safety)              ← NEW
   # build_success      → impact       (deployable artifact)

   # Auto oracle overrides domain_oracle_cmd if both exist:
   # domain_oracle_cmd takes priority when explicitly set in domain_profile
   ```

   **Domain Oracle** (run FIRST if `domain_oracle_cmd` is set; overrides auto-oracle):
   ```
   if domain_oracle_cmd is not null:
       oracle_output = shell(domain_oracle_cmd.replace("{output_dir}", autopilot_output_dir))
       # Parse key:value lines from stdout:
       oracle_scores = {}  # e.g., {"accuracy": 0.87, "f1": 0.91}
       for line in oracle_output.split("\n"):
           if ":" in line → parse as key: float_value
       # Map oracle keys → score_dimensions (exact name match; unmapped dims → LLM fallback)
       log: "[ORACLE] scores={oracle_scores}"
       # For dimensions with oracle values: use as ground truth (skip LLM scoring for those dims)
       # For remaining dimensions (e.g., goal_fidelity): still run LLM SCORE PROMPT
   ```
   If oracle exits non-zero → log "[ORACLE] command failed (exit {code}) — falling back to full LLM scoring"

   **SCORE PROMPT construction** (dimension list is dynamic):
   ```
   if domain_oracle_cmd is set AND oracle succeeded:
       llm_dims = score_dimensions - oracle_scores.keys()  # exclude oracle-covered dims
       oracle_ground_truth_block = "\n".join(f"{k}: {v}" for k,v in oracle_scores.items())
   else:
       llm_dims = score_dimensions  # all dims → LLM
       oracle_ground_truth_block = "(no oracle)"
   # goal_fidelity is always included in llm_dims (never oracle-scored)
   if "goal_fidelity" not in llm_dims: llm_dims.append("goal_fidelity")
   ```
   **Evaluator Mode** (NEW — P0-1, Source: 20260330-omc-live-critique):
   ```
   # evaluator_mode == "cross_prompt":
   # Before running SCORE PROMPT, replace the system prompt with a domain-appropriate skeptic role:
   CROSS_PROMPT_ROLES = {
       "code":      "You are a skeptical external code reviewer who was NOT involved in writing this code. Your job is to find flaws, not validate work. Be conservative with scores.",
       "debug":     "You are a skeptical external code reviewer who was NOT involved in debugging this. Find remaining issues. Be conservative.",
       "ui":        "You are a skeptical UX critic who did not design this UI. Find gaps, inconsistencies, accessibility issues. Be conservative.",
       "knowledge": "You are a skeptical domain expert who did NOT write this analysis. Find ungrounded claims, logical gaps, circular reasoning. Be conservative with grounding scores.",
       "research":  "You are a skeptical peer reviewer who did NOT conduct this research. Find unsupported claims, missing sources, overconfident conclusions. Be conservative.",
       "analysis":  "You are a skeptical data scientist who did NOT run this analysis. Find hidden assumptions, sample size issues, causation-correlation conflations. Be conservative.",
       "business":  "You are a skeptical investor who did NOT develop this business strategy. Find unvalidated hypotheses, missing risk analysis, wishful thinking. Be conservative.",
       "plan":      "You are a skeptical project manager who did NOT create this plan. Find missing dependencies, unrealistic timelines, unaddressed risks. Be conservative.",
       "review":    "You are an adversarial reviewer. Your goal is to find every possible flaw. Be harsh.",
       "security":  "You are a skeptical security auditor. Assume the implementation is broken until proven otherwise. Be conservative.",
   }
   # Default fallback (unknown task_type):
   # "You are a skeptical external expert who was NOT involved in this work. Find flaws. Be conservative."
   # This approach does not fully eliminate self-evaluation bias, but perspective
   # shifting partially mitigates it by framing the LLM as adversarial reviewer.
   # Reference: Anthropic Generator/Evaluator separation pattern
   # (anthropic.com/engineering/harness-design-long-running-apps)

   # evaluator_mode == "oracle_only":
   # Skip LLM SCORE PROMPT entirely. Use only auto_oracle / domain_oracle scores.
   # Dimensions without oracle coverage → score = 0.5 (neutral default).
   # Only viable when oracle covers the majority of dimensions.

   # evaluator_mode == "self" (default):
   # Current behavior — same session scores its own work.
   ```

   Run this scoring prompt (llm_dims only) with goal_check_model:
   ```
   SCORE PROMPT:
   Original user goal: {original_goal}
   Current goal (may be evolved): {root_goal}
   Current state description: {autopilot_summary}
   Evolution depth so far: {evolution_count} / {max_evolution_depth}

   {oracle_ground_truth_block}
   (Dimensions above are already scored by external oracle — treat as ground truth, do not re-score.)

   Rate the CURRENT STATE on the REMAINING dimensions only (0.0 to 1.0):
   {llm_dims — one bullet per dim with description}
   - goal_fidelity: how semantically aligned is current_goal with original_goal?
     (1.0 = identical intent, 0.0 = completely different topic)
     Consider: does the evolved goal still serve the user's original need?
   {domain_convergence_rule_block|default:""}

   Output format (STRICT — one line per LLM-scored dimension, then total):
   {llm_dims_output_lines}
   goal_fidelity: 0.XX
   total: 0.XX
   (total = average of ALL dimensions including oracle-scored ones)
   ```

   **Oracle merge rule** (when `domain_oracle_cmd` is set):
   ```
   final_scores = oracle_scores  # ground truth from external evaluator
   for dim in score_dimensions:
       if dim not in oracle_scores:
           final_scores[dim] = llm_scores[dim]  # LLM fallback for unmapped dims
   final_scores["goal_fidelity"] = llm_scores["goal_fidelity"]  # always LLM
   current_score = average(final_scores.values())
   log: "[SCORE] oracle={oracle_scores}, llm_fallback={llm_fallback_dims}, total={current_score:.2f}"
   ```

   **Score Parser** (Ensemble mode — research basis: Sakana AI Nature 2026):
   Run SCORE PROMPT `score_ensemble_n` times independently (default 3):
   ```
   scores = []
   for i in 1..score_ensemble_n:
       response_i = call SCORE PROMPT (identical prompt, independent call)
       parse total_i, goal_fidelity_i from response_i
       scores.append({total: total_i, goal_fidelity: goal_fidelity_i})

   current_score = average(scores[].total)
   current_goal_fidelity = average(scores[].goal_fidelity)
   score_variance = stdev(scores[].total)

   if score_variance > 0.15:
       # P1-1: Adaptive re-sampling (Research: false plateau prevention — DA CRITICAL finding)
       log: "[SCORE] High variance ({score_variance:.2f}) — re-running with 2× ensemble"
       scores = []  # reset
       for i in 1..(score_ensemble_n * 2):
           response_i = call SCORE PROMPT (identical prompt, independent call)
           parse total_i, goal_fidelity_i from response_i
           scores.append({total: total_i, goal_fidelity: goal_fidelity_i})
       current_score = average(scores[].total)
       current_goal_fidelity = average(scores[].goal_fidelity)
       score_variance = stdev(scores[].total)

       if score_variance > 0.15:  # still high after double-sampling
           log: "[SCORE UNCERTAIN] iter {N}: variance={score_variance:.2f} persists after 2× ensemble"
           score_uncertain_flag = true   # plateau_count will NOT increment this iteration
           # Rationale: uncertain scores cannot reliably signal plateau convergence
   ```
   - On parse failure in any single call → skip that call, average remaining
   - If ALL calls fail → default score = 0.5, default goal_fidelity = 1.0, log parse error
   - Store `current_score`, `current_goal_fidelity`, `score_variance` in `.omc/live-state.json`
   - If `score_ensemble_n: 1` → single-pass (legacy mode, no averaging)

   **Self-Evaluation Bias Note** (research-grounded, 2025):
   Empirical studies show Claude-based evaluators tend to *under*score their own outputs
   (-7.4% vs human baseline) rather than inflate. This means:
   - Ensemble averaging further stabilizes the conservative bias without correcting it
   - High variance across ensemble calls = signal that the task quality is genuinely ambiguous
   - Cross-model diversity is NOT needed for bias correction (research shows p=0.12 non-significant);
     ensemble of same model reduces variance without the cost of cross-model coordination.

   **Preferred scoring hierarchy** (reduces self-scoring bias):
   ```
   1. domain_oracle_cmd (explicit)   → highest trust (external, deterministic)
   2. auto_oracle (pytest/npm test)  → high trust (deterministic, objective)
   3. LLM SCORE PROMPT               → fallback only (subjective, bias-prone)
   ```
   LLM scoring should cover ONLY non-measurable dimensions (goal_fidelity, quality aesthetics).
   Measurable dimensions (test_pass_rate, coverage, build_success) MUST use oracle or auto-oracle.

   **Goal Fidelity Gate** (applied before EVOLVE decision):
   ```
   if current_goal_fidelity < goal_fidelity_min (default 0.7):
       emit WARNING: "[WARN] Goal drift detected: fidelity={current_goal_fidelity:.2f} < {goal_fidelity_min}"
       → skip EVOLVE even if delta >= epsilon
       → treat as plateau (plateau_count += 1)
       → if plateau_count >= plateau_k → CONVERGED check
   ```

   **Compute improvement delta**:
   ```
   delta = current_score - best_score   (best_score from live-state.json, default 0.0)

   if current_score > best_score:
       best_score = current_score   (update best)
       plateau_count = 0            (reset — genuine improvement found)
   elif delta >= epsilon:
       plateau_count = 0            (improvement above threshold — reset)
   else:
       if score_uncertain_flag:
           log: "[SCORE UNCERTAIN] Skipping plateau_count increment — score not reliable this iteration"
           # Uncertain scores cannot reliably signal plateau; skip to prevent premature convergence
       else:
           # Gray zone protection (NEW — P0-2, Source: 20260330-omc-live-critique):
           # score_uncertain_threshold logic (FIX-1 — clarification comment):
           # > 0.15  → plateau_count unchanged (too noisy to trust any signal)
           # 0.10-0.15 → plateau_count += 0.5  (weak signal: some evidence of stagnation, but uncertain)
           # < 0.10  → plateau_count += 1.0    (clear signal: reliable low-variance measurement)
           # This is intentional: gray zone gives "half vote" toward convergence,
           # preventing both premature convergence AND infinite non-convergence.
           if score_variance > score_uncertain_threshold:  # 0.10
               if score_variance > 0.15:
                   plateau_count += 0  # full uncertain — skip increment (existing behavior)
               else:
                   plateau_count += 0.5  # gray zone (0.10-0.15) — half increment (NEW)
               emit: "[SCORE] gray zone variance={score_variance:.2f} → plateau_count += 0.5 → {plateau_count}"
           else:
               plateau_count += 1           (increment ONLY when improvement < epsilon)
       # NOTE: regression (current_score < best_score) also hits this branch
       # but best_score is NOT updated — we keep the historical best
       if current_score < best_score:
           emit WARNING: "[WARN] Score regression: {current_score:.2f} < best {best_score:.2f}"
   ```

   **Decide: CONVERGED or EVOLVE?**
   ```
   if plateau_count >= plateau_k:             → CONVERGED (check min_convergence_score)
   if evolution_count >= max_evolution_depth: → CONVERGED (depth limit, check min_convergence_score)
   if delta >= epsilon AND budget remains:    → EVOLVE (continue with elevated goal)
   if delta < epsilon (plateau_count < plateau_k): → continue loop (same goal, wait for plateau)
   ```

   **Cost-aware convergence** (research-grounded, FACT-6):
   Track iteration cost alongside quality. Add to live-state.json:
   ```json
   "cost_history": [
     {"iteration": 1, "phase_reached": "phase_4", "relative_cost": 1.0},
     {"iteration": 2, "phase_reached": "phase_5", "relative_cost": 1.3}
   ]
   ```
   If `delta / relative_cost < epsilon` (diminishing returns per unit cost), treat as
   low-priority EVOLVE — still evolve, but note in report: "marginal improvement per cost."
   This prevents wasteful iterations that improve quality by 0.01 at 3x compute cost.

6b. **[SELF-EVOLUTION] Elevate goal** (when decision = EVOLVE):

   **Progressive tree-search** (Research basis: AI Scientist-v2, Nature 2026, arXiv:2504.08066):
   Generate 3 candidate evolved goals in parallel, then prune to the best 1 before executing.

   Run this goal evolution prompt:
   ```
   GOAL EVOLUTION PROMPT:
   Original goal: {root_goal}
   Current achievement: goal met at score {current_score:.2f}
   Score breakdown: quality={q}, completeness={c}, efficiency={e}, impact={i}
   Weakest dimension: {min_dimension} = {min_score:.2f}
   Past successful strategies (from episodes): {success_patterns}
   Past failure patterns (from loaded episodes — may be empty on first evolution): {failure_patterns|default:"none"}
   Current run failure patterns (this session so far): {current_run_failures|default:"none"}

   The current goal has been achieved. Generate 3 DISTINCT candidate next-level goals.
   Requirements for each:
   - Build directly on what was accomplished (do not restart)
   - CANDIDATE_1, CANDIDATE_2: target the weakest dimension specifically
   - CANDIDATE_3: exploration branch — see below for exploration_rate logic
   - Be concrete and measurable
   - Each must explore a DIFFERENT direction (not variations of the same idea)

   Output format (STRICT — 3 candidates):
   CANDIDATE_1:
   EVOLVED_GOAL: <one sentence>
   RATIONALE: <one sentence>
   DIRECTION: <which score dimension this targets>

   CANDIDATE_2:
   EVOLVED_GOAL: <one sentence>
   RATIONALE: <one sentence>
   DIRECTION: <which score dimension this targets>

   CANDIDATE_3:
   EVOLVED_GOAL: <one sentence>
   RATIONALE: <one sentence>
   DIRECTION: <which score dimension this targets>
   ```

   **Exploration branch for CANDIDATE_3** (P2-1 — Research: Agent0 arXiv:2511.16043, SSP arXiv:2510.18821):
   ```
   # Adaptive exploration_rate — adjust based on recent score_variance before rolling:
   effective_exploration_rate = exploration_rate  # base value (default 0.2)
   if score_variance < 0.05:
       effective_exploration_rate = min(exploration_rate * 1.5, 0.6)
       log: "[EXPLORE] Low variance ({score_variance:.2f}) — boosting exploration to {effective_exploration_rate:.2f}"
   elif score_variance > 0.15:
       effective_exploration_rate = max(exploration_rate * 0.5, 0.05)
       log: "[EXPLORE] High variance ({score_variance:.2f}) — reducing exploration to {effective_exploration_rate:.2f}"

   if evolution_count >= 1 AND random_roll() < effective_exploration_rate:
       # 20% probability: override CANDIDATE_3 to explore beyond weakest dimension
       explore_dim = first dimension from score_dimensions NOT already targeted in evolution_history
       if all dimensions targeted → explore a NEW sub-goal scope not in goal tree
       Replace CANDIDATE_3 generation instruction with:
           "Generate a goal that explores {explore_dim} or a wholly new scope,
            NOT the weakest dimension ({min_dimension}).
            This is the exploration branch — surprise is allowed."
       log: "[EVOLVE] Exploration branch activated — CANDIDATE_3 targets {explore_dim}"
   ```
   Prevents pure exploitation trap (weakest-dimension-always → local optimum after 2-3 evolutions).

   **Look-ahead pruning** (replaces 1-sentence assessment — Research: AI Scientist-v2 arXiv:2504.08066):
   ```
   For each CANDIDATE_i, score on 3 axes WITHOUT executing autopilot:

   LOOK-AHEAD PROMPT (1 call, all 3 candidates in same prompt):
   Remaining iterations: {max_outer_iterations - current_iteration}
   Current score breakdown: {score_breakdown}
   evolution_history: {evolution_history[-3:]}  # last 3 goals

   For each candidate goal below, rate (0.0–1.0):
   - dimension_fit: how directly does this goal improve {min_dimension}?
   - novelty: how distinct is this from previous evolution_history goals? (1.0 = completely new direction)
   - feasibility: achievable within {remaining_iterations} autopilot cycle(s)?

   CANDIDATE_1: {candidate_1_goal}
   CANDIDATE_2: {candidate_2_goal}
   CANDIDATE_3: {candidate_3_goal}

   Output (STRICT):
   C1: dimension_fit=0.XX novelty=0.XX feasibility=0.XX
   C2: dimension_fit=0.XX novelty=0.XX feasibility=0.XX
   C3: dimension_fit=0.XX novelty=0.XX feasibility=0.XX

   look_ahead_scores[i] = dimension_fit * 0.5 + novelty * 0.3 + feasibility * 0.2
   winner = argmax(look_ahead_scores)
   log: "[EVOLVE] Look-ahead scores: C1={:.2f} C2={:.2f} C3={:.2f} → winner=C{N}"

   If all scores < 0.4 → log "[EVOLVE] All candidates weak — requesting regeneration (1× retry)"
     Retry once with stronger instruction: "Generate more ambitious, distinct goals"
     If retry still weak → take C1, log "[EVOLVE] Forced selection — no strong candidate found"
   If all 3 are similar (novelty < 0.2 for all) → take C1, log "[EVOLVE] Low diversity in candidates"
   ```

   Use selected candidate's EVOLVED_GOAL as the new `root_goal`.

   **Apply evolved goal**:
   - Parse `EVOLVED_GOAL:` line → new `root_goal`

   ```
   # Cumulative fidelity tracking (NEW — P2-8):
   # Prevent gradual goal drift through multiple evolution steps
   new_goal_fidelity = evaluate_fidelity(new_goal, original_goal)
   cumulative_fidelity *= new_goal_fidelity  # running product since run start

   if cumulative_fidelity < cumulative_fidelity_min:  # 0.50
       emit: "[DRIFT ALERT] Cumulative fidelity {cumulative_fidelity:.2f} < {cumulative_fidelity_min}"
       emit: "  Goal has drifted too far from original. Forcing alignment correction."
       → Do NOT evolve to new_goal
       → Reset root_goal toward original_goal with constraint:
         "Return to core intent: {original_goal}. Keep improvements from iter {N} but realign."
       → cumulative_fidelity = max(0.5, cumulative_fidelity)  # partial reset
       plateau_count = 0  # reset plateau — this is a forced correction, not stagnation
   else:
       root_goal = new_goal
       emit: "[EVOLVE] Cumulative fidelity: {cumulative_fidelity:.2f} (threshold: {cumulative_fidelity_min})"

   # Also expose in world model (if world_model is active):
   # world_model.cumulative_fidelity = cumulative_fidelity
   ```

   - Update `.omc/goal-tree.json`:
     ```json
     {
       "root_goal": "<evolved goal>",
       "evolution_history": [
         {"iteration": N, "goal": "<previous goal>", "score": X.XX, "rationale": "..."}
       ]
     }
     ```
   - Increment `evolution_count` in live-state
   - Report: `[EVOLVE iter {N}] Score: {current_score:.2f} (+{delta:.2f}). New goal: {evolved_goal}`
   - Go to Step 4 (run another autopilot cycle with elevated goal)

7. **Branch on evaluation result**:

   **CONVERGED** (self-evolution complete — plateau or depth limit reached):

   First, check quality gate:
   ```
   if best_score >= min_convergence_score (default 0.6):
       → CONVERGED_SUCCESS
   else:
       → CONVERGED_STALE (quality insufficient)
   ```

   **Failure taxonomy extraction** (Research basis: Symbolic Learning AI Open 2025 — run on BOTH CONVERGED branches):
   Before saving episodes, scan `score_history` and iteration outcomes to extract failure patterns:
   ```
   failure_patterns = []
   for each iteration where outcome == "failure" OR score < (best_score - 0.1):
       classify as one of:
       - Tier 1 (execution): coding error, tool failure, phase timeout → log only, do NOT store as pattern
       - Tier 2 (strategy): same approach failed N≥2 times → add to failure_patterns[]
         format: {"pattern": "strategy X repeatedly failed", "count": N, "phase": "phase_N"}
       - Tier 3 (principle): cross-domain generalizable lesson → add to failure_patterns[] with flag
         format: {"pattern": "...", "generalizable": true, "domain": "..."}

   # Tier 2/3 patterns only stored if count >= 2 (prevents noise from one-off failures)
   ```
   Append `failure_patterns` to `.omc/goal-tree.json` before saving to episodes.
   These patterns are loaded in PRE-LOOP Step 1 (cross-trajectory recombination) on next run.

   **CONVERGED_SUCCESS**:
   - Run failure taxonomy extraction (above)
   - **Zettelkasten episode linking** (P2-2 — Research: A-MEM NeurIPS 2025, arXiv:2502.12110):
     Before saving, identify related past episodes (compare against last 10):
     For each past episode summary: "Same problem domain as current run?" (yes/no, 1 LLM call)
     Add `"related_episodes": [<episode_ids of matching episodes>]` to current episode metadata.
     Builds a knowledge graph of experiences — richer cross-trajectory recombination on future runs.
   - **State compliance check** (P1-3 — DA MAJOR: cost_history is spec fiction in real deployments):
     After writing live-state.json, verify required fields exist:
     `["current_iteration", "best_score", "score_history", "cost_history", "current_goal_fidelity"]`
     For each missing field → insert default value + log: "[STATE] Inserted missing field: '{field}'"
   - Call `omc-episode-memory` (save) with outcome=success, high_quality=true
   - Delete `.omc/live-state.json`
   - Report convergence summary:
     ```
     omc-live CONVERGED after {N} iterations ({evolution_count} goal evolutions)
     Final goal: {root_goal}
     Best score: {best_score:.2f} / 1.00
     Score trajectory: {iter1=score, iter2=score, ...}
     Convergence reason: plateau for {plateau_k} iterations / depth limit reached
     Evolution history:
       v0: {original_goal} → score {s0:.2f}
       v1: {evolved_goal_1} → score {s1:.2f}
       ...
     Episodes saved: yes (.omc/episodes.jsonl)
     ```

   **CONVERGED_STALE** (converged but quality below threshold):
   - Run failure taxonomy extraction (above) — especially important here as STALE = high failure signal
   - Call `omc-episode-memory` (save) with outcome=partial, high_quality=false
   - Preserve `.omc/live-state.json` (do NOT delete — resume candidate)
   - Report stale convergence:
     ```
     ## omc-live CONVERGED_STALE — Quality Below Threshold
     Best score achieved: {best_score:.2f} / min required: {min_convergence_score:.2f}
     Iterations: {N} | Evolutions: {evolution_count}
     Final goal: {root_goal}

     The system converged but could not reach minimum quality.
     Possible causes: task too difficult, goal too broad, inner loop limitations.

     Rollback options (git checkpoints available):
       git log --oneline | grep "omc-live iter"
       git checkout <best-iter-hash>   # restore best iteration state

     Next steps:
     1. Adjust task scope and re-run /omc-live
     2. Lower min_convergence_score in .omc/live-config.json
     3. Inspect episodes for root cause: .omc/episodes.jsonl
     4. Rollback to best iteration above and continue manually
     ```

   **ACHIEVED (evolve_mode=false)** (classic termination — outer goal met, no evolution):
   - Call `omc-episode-memory` (save) with outcome=success, high_quality=true
   - Delete `.omc/live-state.json`
   - Report completion summary with stats:
     ```
     omc-live COMPLETE after {N} iterations
     Outer goal: {root_goal}
     Stats: {successes} success, {failures} failure, {partials} partial
     Iteration breakdown: {iter1=outcome, iter2=outcome, ...}
     Episodes saved: yes (.omc/episodes.jsonl)
     ```

     *Stats extraction* (from `.omc/goal-tree.json` history):
     - Count outcomes by iterating through `history[]` array
     - Format breakdown as: "iter1=outcome, iter2=outcome, ..." (max 10 shown)
     - If history empty → show "first run" instead

   **NOT YET** (more iterations needed):
   - Check: current_iteration < max_outer_iterations?
     - YES →
       ```
       # Phase-aware failure handling (NEW — P2-7):
       # Instead of always doing GoalTree Level 1 update on failure,
       # adapt the response based on which autopilot phase failed.

       if outcome == "failure":
           failed_phase = extract_failed_phase(autopilot_summary)  # from summary text

           if failed_phase == "phase_3_implementation":
               # Implementation failed → change approach strategy
               next_action = "GoalTree L1 update with explicit strategy constraint:
                              'Try different implementation approach than: {last_strategy}'"
           elif failed_phase == "phase_4_verification":
               # Tests/verification failed → relax or clarify verification criteria
               next_action = "GoalTree L1 update: 'Clarify acceptance criteria.
                              Current criteria may be ambiguous. Add intermediate checkpoints.'"
           elif failed_phase == "phase_2_planning":
               # Planning failed → simplify goal scope
               next_action = "GoalTree L1 update: 'Narrow scope. Break into smaller subtasks.'"
           else:
               # Unknown phase or phase_5 (cleanup) → standard retry
               next_action = "GoalTree L1 update (standard)"

           emit: "[RETRY] Phase {failed_phase} → {next_action}"
           # Note: extract_failed_phase uses keyword matching on autopilot_summary
           # (e.g., "implementation error" → phase_3, "test failed" → phase_4)
           # Returns "unknown" if summary unavailable (autopilot crash)
       ```
       Update GoalTree Level 0/1 with "specific gap" from judgment → go to Step 4
     - NO  → FORCE STOP (budget exhausted):
               Save episode (outcome=partial)
               Generate structured handoff report (see below)

   **UNCERTAIN** (judgment cannot determine achievement):
   - Save current state to `.omc/live-state.json` (outcome=uncertain)
   - Present to user:
     ```
     ## omc-live: Human Input Required
     Cannot autonomously determine if outer goal was achieved.
     Reason: {uncertain_reason}

     Current state:
     - Goal: {root_goal}
     - Iteration: {N}/{max}
     - Last outcome: {last_outcome}
     - Stats: {successes} success, {failures} failure so far

     Please respond:
     Y → goal achieved, complete and clean up
     N → goal not achieved, continue loop
     S → stop here, generate handoff report
     ```
   - Wait for user response; do NOT continue autonomously

   **FATAL ESCALATION** (omc-goal-tree returned Level 3):

   "Level 3" definition: omc-goal-tree classifies goal changes into 4 levels:
   ```
   Level 0: parameter tweak (threshold, timeout, etc.) — no escalation
   Level 1: sub-goal restructure (decomposition change) — auto-apply
   Level 2: goal expansion (new sub-goals added) — auto-apply + log
   Level 3: goal substitution (root_goal category change) — REQUIRES user approval
             Example: "write tests" → "rewrite the module" = Level 3
   ```
   Note: Level 3 is semantically distinct from max_evolution_depth.
   - max_evolution_depth: limits voluntary self-evolution cycles
   - Level 3: triggers on involuntary Fatal failure → omc-goal-tree upgrade

   Handling:
   - Present to user: "Goal fundamentally changed (Level 3). New goal: [new_goal]. Continue? [Y/N]"
   - If stop_on_fatal_escalation=true AND user not responding → save + stop
   - If approved → reset iteration counter (NOT evolution_count), continue with new goal

---

### STOP CONDITIONS (any of these ends the loop)

| Condition | Action |
|-----------|--------|
| **CONVERGED_SUCCESS**: plateau OR depth limit + best_score >= min_convergence_score | Save episode (success, high_quality), report convergence summary |
| **CONVERGED_STALE**: plateau OR depth limit + best_score < min_convergence_score | Save episode (partial), preserve state, report stale warning |
| Outer goal achieved (evolve_mode=false) | Save episode (success), clean up, report |
| max_outer_iterations reached | Save episode (partial), generate handoff |
| Same Fatal failure 2x (oscillation) | Force stop, escalate to user |
| User says "stop" / "cancel" | omc-cancel, save episode |
| Level 3 goal substitution without approval | Stop, report new goal for next session |

**Evolution flow decision tree**:
```
YES verdict
  └─► evolve_mode?
        ├── false → ACHIEVED (classic stop)
        └── true  → Score current state (Step 6a)
                      └─► delta >= epsilon AND budget remains?
                            ├── yes → Elevate goal (Step 6b) → continue loop
                            └── no  → plateau_count += 1
                                        └─► plateau_count >= plateau_k?
                                              ├── yes → CONVERGED (stop)
                                              └── no  → continue loop (same goal, retry)
```

---

### HANDOFF REPORT FORMAT (on forced stop)

```
## omc-live Handoff Report
Outer goal: {root_goal}
Iterations completed: {N}/{max}
Final state: {last_outcome}

Progress achieved:
- {list of completed sub-goals}

Remaining:
- {list of incomplete sub-goals}

Root cause of incompletion:
- {LLM reasoning}

Recommended next steps:
1. {action A — continue with updated goal}
2. {action B — restructure approach}
3. {action C — reduce scope}

Resume command: /omc-live (will load episodes + goal-tree automatically)
```
</Steps>

<State_Files>
## Persistent State Files

| File | Purpose | Lifecycle |
|------|---------|-----------|
| `.omc/episodes.jsonl` | Execution history (all runs) | Never deleted by omc-live |
| `.omc/goal-tree.json` | Current GoalTree + evolution history | Preserved between iterations; deleted on convergence |
| `.omc/live-state.json` | Iteration counter + evolution state | Deleted on convergence; preserved on partial/failure |
| `.omc/failure-history.json` | Per-error backoff counters | Managed by omc-failure-router |
| `.omc/live-progress.log` | Per-iteration JSONL progress log (NEW — P1-5) | Append-only; never deleted |

**live-state.json schema** (full):
```json
{
  "current_iteration": 0,
  "last_outcome": "success|failure|partial|uncertain",
  "last_phase_reached": "phase_N",
  "started_at": "ISO8601",
  "best_score": 0.0,
  "current_score": 0.0,
  "current_goal_fidelity": 1.0,
  "score_variance": 0.0,
  "plateau_count": 0,
  "evolution_count": 0,
  "score_history": [
    {"iteration": 1, "score": 0.72, "goal_fidelity": 1.0, "goal_version": 0, "score_variance": 0.05},
    {"iteration": 2, "score": 0.81, "goal_fidelity": 0.85, "goal_version": 1, "score_variance": 0.02}
  ],
  "cost_history": [
    {"iteration": 1, "phase_reached": "phase_4", "relative_cost": 1.0},
    {"iteration": 2, "phase_reached": "phase_5", "relative_cost": 1.3}
  ]
}
```
**Compliance**: All required fields MUST be present. Missing fields are filled with defaults and logged (see P1-3 compliance check in CONVERGED_SUCCESS).

**goal-tree.json evolution extension**:
```json
{
  "root_goal": "<current goal (may be evolved)>",
  "original_goal": "<user's initial task description>",
  "evolution_history": [
    {"iteration": N, "goal": "<prev goal>", "score": 0.XX, "rationale": "..."}
  ],
  "level": 0,
  "sub_goals": [],
  "reward_spec": {"primary_metric": "...", "threshold": "..."},
  "history": []
}
```
</State_Files>

<Integration_Map>
## Full System Integration (Self-Evolving Mode)

```
/omc-live "task description"
    │
    ├─[PRE]──► omc-episode-memory (load) → inject past lessons
    ├─[PRE]──► omc-goal-tree (init/load) → set outer goal
    │
    ├─[LOOP]─► omc-autopilot (inner loop)
    │               │
    │               ├── Phase 3 failure → omc-failure-router
    │               │       ├── Transient → retry
    │               │       ├── Persistent → restructure
    │               │       └── Fatal → omc-episode-memory(save) → omc-goal-tree(update)
    │               │
    │               └── Phase 5 → omc-episode-memory (save)
    │
    ├─[EVAL]─► Judgment: YES / NO / UNCERTAIN
    │               │
    │               ├── NO → GoalTree Level 1 update → loop again
    │               ├── UNCERTAIN → human escalation
    │               └── YES → [SCORE] multi-dimensional scoring (Step 6a)
    │                             │
    │                             ├── delta >= epsilon → [EVOLVE] goal elevation (Step 6b)
    │                             │       └── goal-tree updated → loop again (elevated goal)
    │                             │
    │                             └── delta < epsilon for plateau_k → CONVERGED
    │
    └─[END]──► omc-episode-memory (save, high_quality) + live-state cleanup
               + convergence summary with score trajectory + evolution history
```
</Integration_Map>

<Resume>
## Resume After Interruption

If omc-live was cancelled or failed mid-run:
1. `.omc/live-state.json` preserves iteration count and last outcome
2. `.omc/goal-tree.json` preserves current goal state
3. `.omc/episodes.jsonl` preserves all past episodes

Simply run `/omc-live` again (without arguments) to resume:
- omc-live will detect existing live-state.json
- Load GoalTree and continue from last known state
- Use past episodes to avoid repeating mistakes

**Cron monitoring for long-running external jobs** (works in `/live` standalone too):

```python
# Within an autopilot iteration, when you launch a long job:
cron_id = CronCreate(
    cron="*/15 * * * *",   # interval: 5m/<30min, 15m/<2h, 30m/<8h
    prompt="Check job: [command to check log for DONE/ERROR]. If DONE: report result, CronDelete this job.",
    recurring=True
)
live_state["active_cron_monitors"] = live_state.get("active_cron_monitors", []) + [cron_id]
```

See `live-inf` SKILL.md → "Cron Monitoring Integration" for full pattern details.
</Resume>