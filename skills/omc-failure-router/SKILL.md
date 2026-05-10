---
name: omc-failure-router
description: Failure classification and propagation router for autonomous agent loops — Transient/Persistent/Fatal triage with oscillation prevention and goal-update escalation
---

<Purpose>
omc-failure-router implements the failure propagation mechanism for autonomous agent loops. It classifies failures into three types (Transient, Persistent, Fatal) and routes them to the appropriate handler — preventing both premature escalation (false Fatal) and infinite oscillation (oscillating Persistent).

Based on Magentic-One dual-loop failure handling (Microsoft 2025) and the Type-1/2/3 failure propagation model derived from MAHRL (arXiv:2411.01184).
</Purpose>

<Use_When>
- When ralph/autopilot hits the same error multiple times and you need to decide: retry, restructure, or abandon?
- When a sub-agent fails and the calling orchestrator needs routing guidance
- User says "it keeps failing", "the same error again", "what should I do with this error"
- When omc-autopilot Phase 3 (QA) cycles are exhausted
- Before declaring "fundamental issue" — classify first, then escalate appropriately
</Use_When>

<Do_Not_Use_When>
- First occurrence of any error — always retry once before classifying
- When the error is clearly environmental (network down, disk full) → fix environment directly
- When user has already decided on the next action explicitly
</Do_Not_Use_When>

<Failure_Classification>
## Three Failure Types

### Type 1: Transient Failure
**Definition**: Error that resolves with simple retry (no strategy change needed)
**Characteristics**:
- Occurred < N times (default N=3)
- Error message varies between occurrences (not identical pattern)
- Related to external state (timing, resource availability, lock contention)
- Examples: flaky test, temporary file lock, import path issue fixed by re-run

**Response**: Retry within current loop. Do NOT escalate. Log occurrence count.

### Type 2: Persistent Failure
**Definition**: Error that requires strategy adjustment at the sub-goal level
**Characteristics**:
- Same error pattern N≥3 times (or 2 times with identical stack trace)
- Error is deterministic given current approach
- Solvable by changing HOW to achieve the sub-goal (not the sub-goal itself)
- Examples: API not available → switch to different API, test framework mismatch → change framework

**Response**:
- Signal parent loop with failure context
- Parent loop: re-decompose sub-goal OR spawn different specialist agent
- Do NOT trigger goal update yet

### Type 3: Fatal Failure
**Definition**: Error that cannot be resolved without changing the goal itself
**Characteristics**:
- Persistent failure has been attempted and sub-goal restructuring also failed
- OR: The sub-goal is provably unachievable given current constraints
- OR: Oscillation detected (see Anti-Oscillation below)
- Examples: Required library doesn't exist for this Python version, spec is self-contradictory

**Response**:
- Save episode via omc-episode-memory (save mode) FIRST
- Trigger omc-goal-tree at Level 2 (augment) or Level 3 (substitute)
- Present to user: failure hypothesis + 3 candidate next steps
</Failure_Classification>

<Steps>
## Classification and Routing Protocol

1. **Exogenous Failure Pre-Check** (MANDATORY — runs BEFORE any classification):

   Check if the error is caused by the external environment (not by the agent's logic or approach).
   If yes → route directly to environment-fix handler, bypassing Reflexion.

   **Exogenous failure patterns** (match against error_message):
   ```
   HTTP_5XX:      "HTTP 5[0-9][0-9]" | "502 Bad Gateway" | "503 Service" | "504 Gateway"
   TIMEOUT:       "Connection timed out" | "Read timeout" | "Request timeout" | "ETIMEDOUT"
   PERMISSION:    "Permission denied" | "Access denied" | "EACCES" | "403 Forbidden"
   DISK:          "No space left on device" | "ENOSPC" | "disk full"
   NETWORK:       "Connection refused" | "ECONNREFUSED" | "Name or service not known"
   RATE_LIMIT:    "429 Too Many Requests" | "rate limit exceeded" | "quota exceeded"
   ```

   **If exogenous match found**:
   - Log: `{"ts": "...", "pattern": "...", "route": "exogenous", "category": "<HTTP_5XX|TIMEOUT|...>"}`
   - Return immediately with environment-fix guidance:
     ```
     EXOGENOUS FAILURE DETECTED
     Category: {category}
     Action: Fix the environment before retrying — do NOT generate Reflexion.
     Suggested fix:
       HTTP_5XX    → Wait and retry, or check service health status
       TIMEOUT     → Increase timeout config, check network/firewall
       PERMISSION  → Check file/API permissions, run with correct credentials
       DISK        → Free disk space, clean temp files
       NETWORK     → Check DNS, firewall rules, service endpoint
       RATE_LIMIT  → Add delay between requests, reduce batch size
     ```
   - Do NOT increment occurrence_count for exogenous failures
   - Do NOT classify as Type 1/2/3 — exogenous failures are not agent logic failures

   **If no exogenous match** → continue to Step 2.

2. **Collect failure context**:
   ```
   - error_message: exact error text
   - error_type: syntax | type | runtime | test | build | dependency | logic
   - occurrence_count: how many times has this identical pattern appeared?
   - phase: which autopilot/ralph phase did this occur in?
   - sub_goal_id: which sub-goal was being attempted?
   ```

3. **Read failure history** from `.omc/failure-history.json`:
   - If file doesn't exist → create it, initialize counters to 0
   - Look up current error_pattern (normalize: strip line numbers, memory addresses)
   - Get: total_occurrences, last_strategy_tried, backoff_level

3. **Classify** (decision tree):
   ```
   occurrence_count < 3 AND error varies?
     → Type 1 (Transient): retry
   occurrence_count >= 3 AND same pattern?
     → Check: has sub-goal restructuring been tried?
       No → Type 2 (Persistent): restructure sub-goal
       Yes → Check: did restructuring also fail >= 2 times?
              Yes → Type 3 (Fatal): escalate to goal update
              No  → Type 2 (still trying restructuring)
   oscillation_detected (see below)?
     → Force Type 3 regardless of count
   ```

4. **Anti-Oscillation check** (MANDATORY before any retry):
   - Read `.omc/failure-history.json` for current error pattern
   - If `oscillation_count >= 2`: this pattern has caused outer loop reset before
   - Oscillation = same error → outer loop reset → same error again
   - If oscillation detected → FORCE Type 3, add `"oscillation": true` to history entry
   - Apply exponential backoff before any Type 2 retry: wait_iterations = 2^backoff_level (max 32)

5. **Execute routing**:

   **Type 1 — Retry**:
   - Log: `{"ts": "...", "pattern": "...", "type": 1, "action": "retry", "count": N}`
   - Return: "Retry recommended. Occurrence N/3."

   **Type 2 — Restructure + Reflexion**:
   - Log: `{"ts": "...", "pattern": "...", "type": 2, "action": "restructure", "backoff_level": N}`
   - Apply backoff: skip backoff_level iterations before next attempt

   **Reflexion Loop** (MANDATORY for every Type 2 classification):
   Generate a structured reflection paragraph using the following prompt internally:
   ```
   REFLEXION PROMPT:
   Error pattern: {normalized_error}
   Error type: {error_type}
   Occurrences: {occurrence_count}
   Sub-goal attempted: {sub_goal_id}
   Approach used so far: {last_strategy_tried}

   Generate a Reflexion paragraph (3-5 sentences):
   1. WHY this approach failed (root cause hypothesis)
   2. WHAT assumption was wrong
   3. WHAT different approach should be tried next
   4. HOW to verify the new approach worked

   Be concrete and specific to the error. Do NOT restate the error — analyze it.
   ```

   Save reflection to `.omc/failure-history.json` under this entry's `reflexion` field:
   ```json
   "reflexion": {
     "text": "<generated paragraph>",
     "generated_at": "ISO8601",
     "next_strategy": "<extracted concrete next action>"
   }
   ```

   **Inject reflexion into next attempt**: Prepend to the sub-goal's execution prompt:
   ```
   ## Reflexion from Previous Attempt
   {reflexion.text}
   → Next strategy: {reflexion.next_strategy}
   ```

   - Return: "Persistent failure classified. Reflexion generated. Recommend: [next_strategy]"
   - Fallback suggestions by error_type (if reflexion generation fails):
     - dependency: "Try alternative library / pin version / use stdlib instead"
     - test: "Check test framework config / try different test runner"
     - build: "Verify build tool version / check for missing config files"
     - logic: "Review algorithm approach / consider different data structure"

   **Type 3 — Goal Update**:
   - Call `omc-episode-memory` (save mode) first
   - Call `omc-goal-tree` with Level 2 or 3 based on severity:
     - Level 2 if: goal is partially achievable (some sub-goals succeeded)
     - Level 3 if: goal is fundamentally unachievable (core assumption violated)
   - Generate handoff document:
     ```
     ## Failure Handoff Report
     Error pattern: {normalized_error}
     Occurrences: {N} (including {restructuring_attempts} restructuring attempts)
     Root cause hypothesis: {LLM reasoning about why this is fatal}

     Recommended next steps:
     1. {concrete action A}
     2. {concrete action B}
     3. {concrete action C — conservative fallback}
     ```
   - Return handoff document to user

6. **Update `.omc/failure-history.json`**:
   ```json
   {
     "patterns": {
       "{normalized_error_hash}": {
         "occurrences": N,
         "type_classified": 1|2|3,
         "last_action": "retry|restructure|goal_update",
         "backoff_level": N,
         "oscillation_count": N,
         "first_seen": "ISO8601",
         "last_seen": "ISO8601",
         "reflexion": {
           "text": "<generated reflection paragraph>",
           "generated_at": "ISO8601",
           "next_strategy": "<concrete next action extracted from reflection>"
         }
       }
     }
   }
   ```
   Note: `reflexion` field is populated only for Type 2 classifications. Null for Type 1/3.
</Steps>

<Anti_Oscillation_Detail>
## Oscillation Prevention

Oscillation pattern:
1. Inner Loop fails → Outer Loop resets → Inner Loop fails again with same error
2. Without damping, this can repeat indefinitely

Detection:
- Track per-error-pattern: how many times has outer loop reset been triggered?
- If oscillation_count >= 2 → force Type 3, never re-trigger Type 2

Exponential backoff for Type 2:
- backoff_level 0: no wait (first restructuring attempt)
- backoff_level 1: skip 2 inner loop iterations before retry
- backoff_level 2: skip 4 iterations
- backoff_level 3: skip 8 iterations
- Max: backoff_level 5 = skip 32 iterations → if still failing → force Type 3

Reset backoff_level to 0 only when a DIFFERENT error pattern appears (sign of progress).
</Anti_Oscillation_Detail>

<Integration>
## Integration Points

- **omc-autopilot Phase 3** → call this skill when QA cycle hits "same error 3 times"
  instead of just stopping — classify first, route appropriately
- **ralph** → call this skill at each retry decision point (same error N times)
- **omc-goal-tree** → called by this skill for Type 3 failures (Level 2 or 3)
- **omc-episode-memory** → called by this skill BEFORE Type 3 goal update trigger
</Integration>

<Autopilot_Integration_Patch>
## omc-autopilot Phase 3 Replacement

Replace the current Phase 3 stop condition:
```
OLD: "Stop early if the same error repeats 3 times (indicates a fundamental issue)"

NEW: "When same error repeats 3 times → call omc-failure-router to classify:
  - Type 1 → continue retrying (up to 5 cycles total)
  - Type 2 → pause, apply restructuring suggestion, retry
  - Type 3 → escalate: save episode, update goal tree, generate handoff report"
```
</Autopilot_Integration_Patch>
