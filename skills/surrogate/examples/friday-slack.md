# Example: Friday Slack from Senior IC

## Situation

> Friday 6:47 PM. Senior engineer (18mo tenure, key IC on core system) sends Slack:
> *"Hey, can we chat Monday? Just want to discuss my role."*
> No emoji. No prior heads-up. Last 1:1 two weeks ago was normal.

---

## M1 INTAKE
- **signal**: vague meeting request, delayed 2.5 days, "my role" (not "the team" / "project")
- **salience**: Friday-evening timing, flat tone (no softeners), ownership pronoun "my"
- **absent**: no agenda, no emoji, no "no worries" hedge, no mention of topic

## M1.5 SITUATION-TYPE
- **type**: `vague-meeting-request-IC`
- **mode**: `ADV-LEGIBLE`  (counterparty with private info, not full adversary)

## M2 FRAMES
- **activated**: [FN-10, FN-02, FN-03, FN-06, FN-05]
- **meta-frame**: WIN/LOSE (positional — keeping vs losing core IC; Monday 9am negotiating position)
- **surrogate**: none loaded (cold start for this person)

## M3 HYPOTHESES

1. **NULL / base-rate**: Normal career check-in at 18-month tenure.
   - mech: career gravity at mid-tenure
   - falsifier: no recent clarity from last 1:1 → weakens
   - prior: 0.35

2. **POSITIVE (from M2)**: External offer in hand; wants counter/leverage.
   - mech: competing offer; Monday timing = offer-deadline-linked
   - falsifier: no hiring-market signal, no LinkedIn activity → weakens
   - prior: 0.30

3. **Already-decided resignation, Monday is the notice.**
   - mech: decision complete; "discuss my role" softens resignation
   - falsifier: would ask for shorter/later meeting if fully decided
   - prior: 0.15

4. **ADVERSARIAL**: Not about their role — about **someone else** (team conflict, boundary).
   - mech: "my role" framed as role-in-relation, avoids blaming peer
   - falsifier: no recent team friction signals → weakens
   - prior: 0.20 — often missed because anchored on "quit/promo" binary

## M4 LENS EVAL

- **FN-10 ToM**: They chose Friday 6pm → you stress over weekend, they don't perform today. Asymmetric cost-shifting. Implies self-protection (uncomfortable topic OR offer clock). prediction: "info being protected" / conf: 0.7 / evidence: timing+silence / residual: 0.3
- **FN-02 Signaling**: Flat tone is costly signal. "Nothing urgent" would have cost 3 words — omitted deliberately. prediction: "non-routine meeting" / conf: 0.7 / residual: 0.3
- **FN-03 Loss Aversion**: Both sides in loss frame — they fear your reaction, you fear losing them. If you catastrophize, you enter Monday with worse BATNA. prediction: "manage own loss frame first" / conf: 0.8 / residual: 0.2
- **FN-06 Commitment**: Vagueness is not yet binding on their side. Monday is still open ground. prediction: "not committed to a specific outcome yet" / conf: 0.6 / residual: 0.4
- **FN-05 Info Asymmetry**: They have ~48hr private info advantage. Optimal move: shrink the gap before Monday. prediction: "reduce asymmetry via low-cost probe" / conf: 0.7 / residual: 0.3

**conflict register**: FN-10 + FN-02 both point to self-protection; FN-05 suggests time-to-probe. These stack rather than conflict. No averaging needed.

## M5 INTEGRATE

- **weights** (cold start W_hist=0.5 for all):
  - FN-10: 0.27
  - FN-02: 0.28
  - FN-03: 0.21
  - FN-06: 0.15
  - FN-05: 0.18 (normalized)
- **posterior distribution**:
  - H2 (counter-offer leverage): 0.30
  - H1 (career path check-in): 0.25
  - H3 (already-decided resignation): 0.20
  - H4 (team/interpersonal): 0.20
  - other: 0.05
- **uncertainty**: MEDIUM-HIGH — 4 hypotheses all above 0.15; no single dominant
- **preserved conflicts**: none direct (FN stacking was additive); but no consolidation either — leave uncertainty wide

## M6 ACTION

- **recommended**: Tonight (9-11pm, not immediate): *"Sounds good — Monday works. Anything you'd like me to have in mind so I come prepared?"*
- **scored**:
  - EV: positive (preserves all H-branches; no commitment cost)
  - info_value: HIGH (their reply or non-reply cuts hypothesis space ~50%)
  - reversibility: full (zero commitment on your side)
  - opponent-perturbation: neutral-positive (composure signal; counters their cost-shifting without pressing)
- **win/lose positional**: reclaims agenda-setting without seizing it. You enter Monday with information instead of anxiety — position improves regardless of their answer.
- **do NOT**:
  - Call them now (high-pressure; damages relationship even if they stay)
  - Ask "everything okay?" (loss-averse tell; confirms they have leverage)
  - Wait silently to "not look worried" (forfeits the 48hr window)

**Branch plans based on reply**:
- If reveals H2 (offer) → Monday prep = retention package + growth path
- If reveals H4 (team) → Monday prep = facilitation mode, not career framing
- No reply / "let's just chat" → lean H2/H3; prep accordingly

## M7 UPDATE (pending Monday outcome)

- **episode key**: `2026-04-17T18:47`
- **frames to reweight**:
  - If outcome = H1 (career path): down-weight FN-02 for this person (flat affect = baseline noise)
  - If outcome = H2 (offer): up-weight FN-05 for situation-type `vague-meeting-request-IC`
  - If outcome = H4 (team): up-weight FN-08 Emotional/Status (should have been in M2) — reconsider M2 minimum activation
- **surrogate to create**: after Monday, initialize `<name>.json` with observed communication style baseline
