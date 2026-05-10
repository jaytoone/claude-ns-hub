# Competitive Intelligence Diagnostic Protocol

**Date**: 2026-05-02  **Corpus**: competitive_intelligence  **Doc-ID**: D1
**Status**: auto-generated (Auto-Corpus Builder)

---

## CI Program Diagnostic — 10-Question Protocol

Run this before designing or recommending a CI program. Each answer routes to a different starting point.

### Q1: Current Win Rate Against Named Competitors
- **<20%**: CI program needed urgently, but start with buyer interviews to diagnose root cause before tools
- **20-40%**: CI gap likely in battlecard quality or sales activation, not signal collection
- **>40%**: CI program can be tuned for specific competitor segments, not overhauled

### Q2: Do You Have External Win-Loss Interview Data?
- **No**: Start here before anything else. All other CI is downstream of understanding real decision criteria.
- **Yes, internal CRM only**: Treat as directional only. 85% error rate means plan for external validation.
- **Yes, external third-party**: Proceed to battlecard and positioning analysis.

### Q3: How Many Active Named Competitors?
- **1-2**: Focused battlecard program (2-3 updated monthly)
- **3-7**: Segment by deal stage and ICP; primary + secondary battlecards
- **8+**: Category map required before individual battlecards; risk of CI sprawl

### Q4: Who Owns CI Currently?
- **No owner**: Assign Product Marketing as CI owner before any tool investment
- **Single analyst**: Add cross-functional input loops (Sales weekly, CS monthly)
- **Distributed (PMM + Sales + Product)**: Coordinate with centralized repository (Klue, Confluence, or Notion)

### Q5: Current CI Budget and ARR Stage?
- **Starter (<$1M, <$5k budget)**: G2 + manual competitor monitoring + 5 external buyer interviews/quarter
- **Growth ($1-10M, $10-25k)**: Add Klue or Crayon + quarterly win-loss synthesis
- **Enterprise (>$10M, $50k+)**: Full stack + external win-loss firm + dedicated CI role

### Q6: Are Battlecards Currently Being Used in Deals?
- **No**: Activation problem. Content quality is irrelevant if not integrated in CRM workflow.
- **Sometimes**: Measure adoption rate. <20% = distribution failure; redesign delivery mechanism.
- **Yes (>50% adoption)**: Optimize for freshness and specificity, not creation.

### Q7: What Are Your Top 3 Loss Reasons (from CRM)?
- If reasons are generic ("price", "features", "timing"): CRM data is unreliable → external interviews needed
- If reasons are specific ("lost to [competitor X] on enterprise security requirements"): CRM hygiene is good, use as baseline

### Q8: How Frequently Do You Update Battlecards?
- **Never/annually**: Stale battlecards. Implement monthly refresh cadence minimum.
- **Quarterly**: Acceptable for Growth stage; add automated monitoring triggers for urgent updates.
- **Monthly or event-triggered**: Good. Measure sales adoption, not just production cadence.

### Q9: Do Product and Sales Share CI Findings?
- **No shared process**: Create monthly CI sync (30 min, cross-functional)
- **Ad hoc sharing**: Formalize into structured format (battlecard + product implications + deal impact)
- **Systematic process**: Measure loop closure (does CI insight → product action → win rate change?)

### Q10: What Competitive Move Would Most Hurt You in the Next 90 Days?
- Answer reveals current threat model clarity. Vague answers → need competitor positioning map first.
- Specific answers → CI program can be targeted to monitor that specific signal type.

---

## Gap Pattern Diagnostic

| Gap Pattern | Signal in Conversation | Implication |
|---|---|---|
| `no_win_loss_program` | Win/loss discussed using only CRM data | 85% error rate risk; ground truth missing |
| `tool_before_strategy` | CI tool selection before workflow design | Stack without activation = wasted budget |
| `feature_list_as_ci` | Competitor feature matrix as primary CI output | Positioning/ICP shifts missed; roadmap misaligned |
| `single_owner` | CI program with one person owning all signals | Cross-functional blind spots; CS/Sales signals lost |
| `static_battlecards` | Battlecards mentioned without update cadence discussion | Stale at deal time; sales stops trusting CI |

---

## Recommended Starting Points by Diagnosis

| Situation | First Action | Timeline |
|---|---|---|
| No CI program at all | 5 external buyer interviews (recent losses) | Week 1-2 |
| CI exists but win rate declining | External win-loss audit (10-15 interviews) | Month 1 |
| Good CI but low sales adoption | CRM integration + ≤2-min battlecard redesign | Week 1 |
| Competitor just launched major feature | Emergency battlecard + 3 customer interviews | 48 hours |
| New competitor entering market | Positioning map update + ICP overlap analysis | Month 1 |
