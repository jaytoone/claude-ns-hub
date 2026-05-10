---
name: intent-clarifier
description: "Intent Clarification Skill — Runs immediately after Node 1 entry at all complexity levels. Extracts 3 layers using 5 Whys + JTBD + Golden Circle frameworks: surface request -> root intent -> meta value. Prioritizes internal reasoning (minimize questions), uses AskUserQuestion only when confidence < 0.7. Outputs intent analysis block at the top of the response."
trigger: manual
tags:
  - intent
  - clarification
  - all-complexity
  - node-1
  - 5whys
  - jtbd
---

# Intent-Clarifier: Multi-Framework Intent Clarification Protocol

Runs immediately after Node 1 entry at **all complexity levels**. Extracts what the user didn't say (root intent) and what exceeds expectations (meta value) beyond what the user said (surface request).

---

## Philosophical Foundation

> "People don't know what they want. If I had asked the focus group, they would have said they wanted a faster horse." — Henry Ford
> "The customer doesn't buy a drill — they buy a hole." — Theodore Levitt (JTBD archetype)
> "Start with Why." — Simon Sinek, Golden Circle

---

## Applied Frameworks

| Framework | Source | Core Question | Use in This Skill |
|-----------|--------|---------------|-------------------|
| **5 Whys** | Sakichi Toyoda, 1930s (Toyota TPS) | "Why do you want X?" x repeat | Symptom → root cause drill-down |
| **JTBD** | Clayton Christensen, 2003 | "What Job are you hiring for?" | Feature request → life problem conversion |
| **Golden Circle** | Simon Sinek, 2009 | Why → How → What reverse reconstruction | Direction alignment, value reframing |
| **Pain/Gain Map** | Osterwalder, Value Proposition Design | Current pain vs desired outcome | Expanding the solution space |
| **Ladder of Inference** | Chris Argyris, 1970s | What data led to this conclusion? | Extracting hidden assumptions/biases |

---

## Step 1: Capture the Surface Request

Summarize the request as a 1-line active sentence:
```
The user wants to [verb + object].
```

Additional identification:
- **Request type**: Implementation / Fix / Investigation / Review / Other
- **Stated constraints**: Time / Technology / Budget, etc.
- **Ambiguity points**: Unclear terms, undefined scope, conflicting conditions

---

## Step 2: 5 Whys — Root Intent Drill-Down

```
Surface request → W1 → W2 → W3 → [W4 → W5]
```

**Rules**:
- If each answer stays at "technical implementation," dig one level deeper
- If the answer reaches "business purpose" or "user emotion," terminate early
- Maximum 5 rounds, early termination when confident

**Example**:
```
Request: "Add a spinner to the button"
W1: Why? → Need to show loading is in progress
W2: Why show it? → Users double-click causing errors
W3: Why double-click? → Slow response, users don't know if click registered
Root: Lack of user feedback → Trust erosion → Duplicate submissions → Errors
```

---

## Step 3: JTBD Lens — Job Identification

**3 Job Types**:
```
Functional Job: [the functional outcome to actually achieve]
  e.g.) "Want to verify code without deploying"

Emotional Job: [the anxiety/desire this request aims to resolve]
  e.g.) "Want to leave work without worrying about production incidents"

Social Job: [what to demonstrate to team/organization]
  e.g.) "Want to prove development speed to the lead"
```

**Hiring Formula**:
```
The user, in [situation], through [surface request], is trying to achieve [functional Job],
and truly wants to resolve [emotional Job].
```

---

## Step 4: Golden Circle — Reverse Reconstruction

```
WHY  (purpose): Why is this needed? [5 Whys endpoint]
HOW  (method):  How will it be achieved? [currently proposed approach]
WHAT (result):  What specifically will be built? [surface request]
```

**Reconstruction value**: Verify whether WHAT (surface) is the best approach for WHY (purpose). If a better WHAT exists, propose it as meta value.

---

## Step 5: Meta Value Synthesis

Complete the 3 layers:

```
[Surface Request] → What the user explicitly stated (X)
[Root Intent]     → What was identified via 5 Whys + JTBD (Y)
[Meta Value]      → What truly resolves Y beyond X (Z)
```

**Meta Value Generation Principles**:
- Implementing X alone fulfills the request — but not knowing Y means X may be replaced later
- Z includes X or achieves X more effectively
- Z is something the user didn't expect but upon hearing it, responds "that's exactly it"

---

## Step 6: Confidence Assessment + Clarification Decision

**Confidence Calculation**:
```
base: 0.5
+ 0.2  Request includes specific context (code, error messages, screenshots)
+ 0.1  Domain pattern match (existing project context)
+ 0.1  WHY is clearly inferred 2+ levels deep
+ 0.1  JTBD emotional Job successfully identified
```

**Branch**:
```
Confidence >= 0.7 → Output intent analysis block and proceed directly (skip AskUserQuestion)
Confidence < 0.7  → AskUserQuestion on only 1-2 key uncertainty points
                  → After receiving answer, re-run from Step 2
```

---

## Step 7: Intent Analysis Block Output (Top of Response)

Output the following block in **collapsed format (>)** at the start of every response:

```markdown
> **Intent Analysis** (5 Whys + JTBD)
> - Request: "[surface request 1-line summary]"
> - Root Intent: [5 Whys endpoint — business/emotional level]
> - Job: [Functional Job] / [Emotional Job]
> - Meta Value: [what's missed by just implementing X + better approach Z]
> - Confidence: 0.X (>=0.7 proceed directly, <0.7 ask then re-analyze)
```

**Only when meta value exists**, include an additional suggestion in the body:
```markdown
> ⚡ **Additional Suggestion**: Beyond implementing X, also addressing Z would [specific reason]. Let me know if you'd like to proceed.
```

---

## Application Example

**Input**: "Create a calc_stats function in smoke_util.py"

```
Step 1 — Surface: The user wants to create a calc_stats function.
Step 2 — 5 Whys:
  W1: Why? → Need statistical calculations
  W2: Why needed? → To summarize training metrics
  W3: Why summarize? → To quickly detect anomalies in logs
  Root: Ensuring training monitoring reliability
Step 3 — JTBD:
  Functional: Summarize batch metrics in one call
  Emotional: Want to immediately detect if loss diverges during training
Step 4 — Golden Circle:
  WHY: Training anomaly detection → rapid intervention
  HOW: Summary statistics function
  WHAT: calc_stats(mean/std/min/max)
Step 5 — Meta Value:
  Surface: 1 calc_stats function
  Meta: Including anomaly detection threshold + warning output would fully achieve the monitoring objective
Confidence: 0.7 (project context clearly ML training) → Proceed directly
```

Output:
```
> **Intent Analysis** (5 Whys + JTBD)
> - Request: "Create calc_stats function"
> - Root Intent: Quick summary for training metric anomaly detection
> - Job: Batch statistics summary / Resolve anxiety about missing training divergence
> - Meta Value: Adding anomaly threshold check beyond mean/std/min/max would fully achieve monitoring objective
> - Confidence: 0.7 → Proceed directly
```
