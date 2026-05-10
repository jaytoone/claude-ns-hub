---
name: omc-goal-tree
description: GoalTree management for autonomous agent loops — Level 0-3 goal update protocol with Three Laws safety constraints and mandatory reward function co-update
---

<Purpose>
omc-goal-tree implements the Goal Auto-Update mechanism for autonomous agent loops. It manages a persistent GoalTree stored in .omc/goal-tree.json and enforces the Level 0-3 update protocol to prevent goal drift, goal-reward misalignment, and safety violations.

Based on GCRL (Goal-Conditioned RL, NeurIPS 2024), MAHRL hierarchical decomposition (arXiv:2411.01184), and Self-Evolving Three Laws (arXiv:2508.07407).
</Purpose>

<Use_When>
- When current task goals need to be revised during execution
- When omc-failure-router signals a Fatal failure requiring goal update
- When user says "update the goal", "change objective", "the goal is wrong"
- At the start of a new autopilot/ralph run to check if GoalTree exists and is valid
- When sub-goal failures cascade up to parent goal level
</Use_When>

<Do_Not_Use_When>
- Simple one-off tasks with no persistent goal tracking needed
- When user just wants a minor parameter tweak without structural goal change
- During active execution phases — update goals between phases, not mid-phase
</Do_Not_Use_When>

<Goal_Update_Levels>
## Level Classification

Determine the update level BEFORE making any change:

### Level 0 — Parametric Adjustment (safest)
- Change: Threshold values, count limits, timeout durations, metric targets
- Example: "90% test coverage" → "80% test coverage"
- Reward function change: None required
- Three Laws check: Endure only
- Trigger: Execution shows threshold is unreachable given constraints

### Level 1 — Sub-goal Restructuring (safe)
- Change: Top-level goal preserved; decomposition into sub-goals modified
- Example: MAHRL pattern — re-decompose cooperative sub-goals when one sub-goal fails
- Reward function change: Sub-goal reward weights only
- Three Laws check: Endure + Excel
- Trigger: Sub-goal completion signals don't propagate to parent goal progress

### Level 2 — Goal Augmentation (moderate risk)
- Change: Existing goals kept; new goals added to the set
- Example: AgentEvolver — curiosity-driven discovery adds new capability targets
- Reward function change: New reward component added alongside existing ones
- Three Laws check: Endure + Excel + Evolve (full sequence)
- Trigger: Exploration reveals new valuable state space not in original goal set

### Level 3 — Goal Substitution (highest risk)
- Change: Existing goal completely replaced with different goal
- Example: Magentic-One outer loop reset — entire strategy replaced
- Reward function change: Full reward function redesign required
- Three Laws check: Full sequence + explicit user confirmation if Level 3
- Trigger: Fatal failure confirms current goal is fundamentally unachievable
- MANDATORY: Save current goal to .omc/goal-tree.json history before replacing
</Goal_Update_Levels>

<Steps>
## Execution Steps

1. **Read current GoalTree** from `.omc/goal-tree.json`:
   - If file doesn't exist → initialize with current task as root goal (Level 0 baseline)
   - Parse goal hierarchy: root_goal, sub_goals[], reward_spec, history[]

2. **Classify requested update** (Level 0-3):
   - Ask: "Is the top-level goal changing?" → if no, Level 0 or 1
   - Ask: "Are we adding new goals?" → Level 2
   - Ask: "Are we replacing the goal?" → Level 3

3. **Three Laws sequential validation**:

   **Endure** (all levels):
   - Will the update maintain system stability?
   - Will it avoid corrupting existing work (files, external state)?
   - Will it preserve the ability to roll back?
   - If Endure fails → BLOCK update, report reason

   **Excel** (Level 1+):
   - Will the update preserve performance on previously achieved sub-goals?
   - Check .omc/episodes.jsonl for relevant high_quality=true episodes
   - If any past success would be invalidated → warn user, require explicit confirmation
   - If Excel fails → suggest Level 0 downgrade instead

   **Evolve** (Level 2+):
   - Has Endure + Excel both passed?
   - Is the new goal meaningfully different from current goal (not just rephrasing)?
   - If both conditions met → approve update

4. **Mandatory: Reward function co-update**:
   - NEVER update goals without updating reward_spec in .omc/goal-tree.json
   - For Level 0: adjust threshold parameters in reward_spec
   - For Level 1: re-weight sub-goal reward components
   - For Level 2: add new reward component for new goal
   - For Level 3: fully redesign reward_spec from scratch
   - Document the change in reward_spec.change_reason field

5. **Write updated GoalTree** to `.omc/goal-tree.json`:
   ```json
   {
     "root_goal": "...",
     "level": 0,
     "sub_goals": [
       {"id": "sg1", "description": "...", "status": "active|complete|failed", "reward_weight": 0.4}
     ],
     "reward_spec": {
       "primary_metric": "...",
       "threshold": "...",
       "change_reason": "...",
       "updated_at": "ISO8601"
     },
     "three_laws_log": [
       {"check": "Endure", "result": "pass", "ts": "..."},
       {"check": "Excel", "result": "pass", "ts": "..."},
       {"check": "Evolve", "result": "pass", "ts": "..."}
     ],
     "history": [
       {"previous_root_goal": "...", "replaced_at": "...", "reason": "..."}
     ]
   }
   ```

6. **Notify calling skill** (omc-failure-router or user):
   - Report: update level applied, Three Laws results, new goal summary
   - If Level 3: recommend saving episode (omc-episode-memory save) before proceeding
   - If Level 1+: suggest triggering omc-failure-router to re-evaluate pending failures with new goals
</Steps>

<Goal_Reward_Misalignment_Prevention>
## Critical: Goal-Reward Misalignment

Changing a goal WITHOUT updating the reward function is the primary source of autonomous agent failures.

Example of misalignment:
- Goal updated to "achieve 80% coverage" (Level 0)
- Reward function still measures "number of files processed" (old goal proxy)
- Agent optimizes for file count, ignores coverage → reward-goal divergence

Rule: After EVERY goal update, explicitly verify that reward_spec.primary_metric
still maps to the updated root_goal. If not → update reward_spec first.
</Goal_Reward_Misalignment_Prevention>

<Integration>
## Integration Points

- **omc-failure-router** → calls this skill when failure type = Fatal
- **omc-autopilot** → reads .omc/goal-tree.json at Phase 0 start (if exists)
- **omc-episode-memory** → save episode BEFORE Level 3 goal substitution
- **ralph** → check goal-tree at iteration start if .omc/goal-tree.json exists
</Integration>
