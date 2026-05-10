# Competitive Intelligence — Falsification Criteria

**Date**: 2026-05-02  **Corpus**: competitive_intelligence  **Doc-ID**: T4
**Status**: auto-generated (Auto-Corpus Builder)

---

## Hard Constraints (HC) — Sycophancy Guard

### HC-1: More Tools ≠ Better CI
**Violation signal**: Recommending a CI tool stack without asking about current workflow and ownership structure.
**Why it fails**: Tool stacking without strategy produces noise, not intelligence. The 3-layer CI architecture (Collect → Analyze → Activate) must exist as a process first — tools are accelerators, not foundations.
**Correct response**: Diagnose current CI maturity stage (Starter/Growth/Enterprise) → recommend budget-matched tools → workflow design first.

### HC-2: Internal CRM Loss Data Is Not Ground Truth
**Violation signal**: Citing CRM "loss reasons" as evidence of why deals are lost, or designing CI programs that rely primarily on CRM data.
**Why it fails**: ~85% of internal loss reason data is wrong. Sales reps mark "price" or "product gap" to avoid uncomfortable conversations. Real decision criteria emerge only from external buyer interviews in a safe-space context.
**Correct response**: External win-loss program with third-party interview provider, or at minimum structured post-decision surveys with anonymized responses.

### HC-3: CI Is Not One Person's Job
**Violation signal**: Assigning CI entirely to a single analyst or competitive intelligence specialist.
**Why it fails**: Single-owner CI creates cross-functional blind spots. Product, marketing, sales, and customer success each hold CI signals the analyst never sees. Win-rate impact requires CI integration across all four functions.
**Correct response**: CI program owner (often Product Marketing) + designated inputs from Product (roadmap signals), Sales (deal feedback), CS (churn signals), Marketing (positioning response).

### HC-4: Real-Time Monitoring Is Enterprise Tier, Not Default
**Violation signal**: Recommending real-time competitor monitoring tools (Klue Compete Agent, Crayon) for Starter-stage companies (<$1M ARR).
**Why it fails**: Real-time monitoring generates noise volume that Starter-stage companies lack bandwidth to process. Signal-to-noise ratio collapses. Budget better spent on 5 external buyer interviews.
**Correct response**: Match CI investment to ARR maturity. Starter: manual quarterly review + G2 monitoring. Growth: Klue/Crayon + monthly win-loss. Enterprise: full real-time stack.

### HC-5: Competitive Feature Lists Are Vanity CI
**Violation signal**: Treating feature parity tables as the primary output of a CI program.
**Why it fails**: Buyers rarely decide on feature lists. Decision criteria from win-loss data show: relationship (seller quality), trust (case studies/references), pricing clarity, and perceived risk dominate. Feature gaps matter only when they hit must-have buyer criteria.
**Correct response**: Feature matrix weighted by buyer decision criteria from win-loss interviews. Unweighted feature lists create false urgency for product roadmap.

### HC-6: Annual Competitive Audit Is Not Sufficient
**Violation signal**: Recommending annual-only competitive review cadence.
**Why it fails**: B2B SaaS competitors change pricing, packaging, and ICP targeting quarterly. Annual reviews miss competitive moves that affect live deals. Battlecards built from annual audits are stale at deal time.
**Correct response**: Weekly automated monitoring → monthly battlecard refresh → quarterly positioning audit → annual strategic market map.

### HC-7: AI-Powered CI Does Not Replace Buyer Interviews
**Violation signal**: Citing AI CI tools (Klue Compete Agent, etc.) as sufficient for understanding deal loss reasons.
**Why it fails**: AI tools excel at signal collection (website changes, pricing pages, job posts). They cannot interview buyers. The 85% CRM data error rate is a human behavior problem, not a data collection problem — it requires human conversation to solve.
**Correct response**: AI tools for Layer 1 (signal collection) + external buyer interviews for Layer 2 (win-loss analysis). Neither substitutes for the other.

---

## Scope Gate Violations

CI framework does NOT apply when:
1. **No active competitors exist** → use category creation playbook instead
2. **B2C consumer context** → consumer CI requires entirely different signal types (social listening, ad tracking, review sites, not deal-level win-loss)
3. **Goal is customer discovery, not competitive positioning** → JTBD/customer interview frameworks are primary

---

## Falsification Conditions

The competitive intelligence framework prediction fails if:
- Win-rate does NOT improve after implementing external win-loss program → investigate sales execution quality (CI is not the bottleneck)
- Battlecard adoption rate < 20% despite quality content → distribution/workflow problem, not content problem
- CI program cost > win-rate-lift revenue impact → ROI negative; downscale tool stack to maturity-matched level
