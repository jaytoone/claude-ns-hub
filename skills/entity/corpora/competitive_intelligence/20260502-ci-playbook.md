# Competitive Intelligence Playbook — B2B SaaS

**Date**: 2026-05-02  **Corpus**: competitive_intelligence  **Doc-ID**: S1
**Status**: auto-generated (Auto-Corpus Builder)

---

## 90-Day CI Program Launch Playbook

### Month 1: Foundation

**Week 1-2: Win-Loss Foundation**
1. Pull last 20 closed/lost deals from CRM
2. Identify external win-loss interview provider OR design internal interview script (use neutral third-party language)
3. Conduct 5 buyer interviews (recent losses, 3-6 months post-decision)
4. Output: Loss reason taxonomy (real decision criteria, not CRM codes)

**Week 3-4: Signal Infrastructure**
1. Set up automated monitoring for top 3 competitors:
   - G2 review alerts (free)
   - Google Alerts for competitor name + "pricing" / "announces"
   - LinkedIn job posting tracker (manual or Klue)
2. Create competitor profile docs (1-pager per competitor: ICP, pricing, messaging, differentiators)
3. Assign CI owner (Product Marketing recommended)

### Month 2: Battlecards

**Week 5-6: Battlecard Creation**
1. Create 2-3 battlecards for highest-frequency competitors in deals
2. Format: ≤2 min read, deal-stage specific (discovery / demo / close)
3. Content per battlecard:
   - Why buyers choose us (from win-loss data)
   - Why buyers choose them (from win-loss data)
   - Key objection handles (3-5 most common)
   - Pricing positioning (ours vs theirs in deal context)
   - Landmines to plant (questions that reveal their weaknesses)

**Week 7-8: Activation Integration**
1. Load battlecards into CRM (Salesforce, HubSpot) as deal-stage triggered resources
2. Train sales team: 30-min session, focus on objection handles
3. Measure adoption: track battlecard views per deal cycle

### Month 3: Feedback Loop

**Week 9-10: Sales Feedback Collection**
1. Weekly: Slack channel where reps post competitive mentions from calls
2. Add "Competitive Factor" field to CRM opportunity (text field, not picklist)
3. Tag deals with competitor encountered

**Week 11-12: Refresh + Cadence**
1. Update battlecards from 30 days of sales feedback
2. Run second wave of 5 buyer interviews
3. Establish monthly CI sync (cross-functional: PMM + Sales + Product + CS)
4. KPI baseline: win rate against each named competitor

---

## Battlecard Template

```markdown
# vs [Competitor Name]  |  Updated: [Date]

## Why We Win
- [Reason 1 — from buyer interviews]
- [Reason 2]
- [Reason 3]

## Why They Win
- [Reason 1 — from buyer interviews, be honest]
- [Reason 2]

## Top 3 Objections + Handles
1. "[Their claim]" → "[Our response]"
2. "[Their claim]" → "[Our response]"
3. "[Their claim]" → "[Our response]"

## Trap Questions (plant in discovery)
- "How do you handle [their known weakness]?"
- "What happens when [their limitation scenario]?"

## Pricing Context
[One sentence on how to position price relative to theirs]

## When to Walk Away
[Situations where this competitor genuinely beats us — don't fight unwinnable deals]
```

---

## Maturity-Matched Tool Stack

### Starter (<$1M ARR, <$5k/year)
- G2 / Capterra review monitoring (free alerts)
- Google Alerts (free)
- BuiltWith for tech stack signals (freemium)
- Manual quarterly competitor website review
- 5 external buyer interviews/quarter (internal script)

### Growth ($1-10M ARR, $10-25k/year)
- Klue or Crayon (~$12-18k/year) for automated monitoring
- Semrush for SEO/content competitive signals (~$3-5k)
- Win-loss survey tool (Typeform + Calendly) (~$1-2k)
- 10-15 external buyer interviews/quarter

### Enterprise (>$10M ARR, $50k+/year)
- Klue Enterprise + Gong integration for deal-level CI
- 6sense for intent data overlay
- External win-loss firm (Cascade Insights, Primary Intelligence) ($20-40k/year)
- Dedicated CI analyst or Senior PMM

---

## ROI Measurement Framework

| Metric | Measurement Method | Target |
|---|---|---|
| Win rate vs named competitors | CRM filtered by competitor field | +5-15% year 1 |
| Battlecard adoption | CRM resource view tracking | >50% of reps, >30% of deals |
| CI cycle time | Time from competitive event → battlecard update | <7 days |
| Sales satisfaction with CI | Quarterly survey | >7/10 NPS |
| Interview coverage | Deals with external buyer interview / total losses | >20% |
