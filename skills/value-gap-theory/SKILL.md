---
name: value-gap-theory
description: "VALUE GAP demand theory diagnostic — L1-L5 identity gap classification, D(WTP) formula, 13-question customer interview, bbaijjim audit, falsification criteria. Use for ANY knowledge/identity product. For Career Mirror specific execution, use /career-mirror-builder."
---

# VALUE GAP Theory — Diagnostic Skill

## When to use
- Diagnosing WTP level of a knowledge/career/identity product idea
- Running customer interviews to find L1-L5 gap level
- Auditing whether a product design risks bbaijjim (dependency trap)
- Deciding which WTP levers to activate
- Evaluating pricing power of identity-adjacent products

## When NOT to use
- B2B SaaS with functional/workflow WTP -> use /wtp-validator
- Commodity or impulse purchase products (out of scope)
- When you need Career Mirror specific execution -> use /career-mirror-builder
- Addictive/compulsive purchase analysis (clinical domain)
- Institutional/procurement purchases (organizational KPI-driven)

---

## CORE THEORY

### D(WTP) Formula (v2)

```
Gap_Intensity = Functional_Gap + Social_Position_Gap

D(WTP)_instantaneous = [Gap_Intensity x Attainability] x [Social_Amplifier]

D(WTP)_sustainable   = D(WTP)_instantaneous x Ethical_Coefficient
```

**Variable definitions:**

- **Functional_Gap**: The functional or epistemological gap that cannot be resolved without the product. Ranges from 0 to 1.0. Higher when the gap is specific and named.
- **Social_Position_Gap**: The gap in social belonging, status, or recognition. Independent from Functional_Gap. L1 products operate primarily on this variable (Functional_Gap near 0).
- **Gap_Intensity**: Sum of the two gap types. This is what drives instantaneous WTP.
- **Attainability**: The degree to which the customer perceives that the product can actually close the gap. Range 0-1.0. If the customer believes "this can't help me," WTP collapses regardless of gap intensity.
- **Social_Amplifier**: Signal transmission coefficient — the degree to which the functional gap is visible to important others. NOT a pure multiplier. For L1, Social_Position_Gap carries the load directly. For L2-L5, Social_Amplifier modulates how much peers see the gap.
- **Ethical_Coefficient**: Range (0, 1]. Lifetime-extractable surplus discount factor. NOT part of the purchase-moment formula. It operates on a longer time scale. Exploitative products: EC near 0 (high instant WTP, collapsing sustainable WTP). Healthy products: EC near 1.0.

**Key insight from v2 revision**: Instantaneous WTP and sustainable WTP are separated. A product can have very high D(WTP)_instantaneous but low D(WTP)_sustainable if its Ethical_Coefficient is low (addictive design, manufactured dependency, gap reproduction).

**Prediction**: Products optimizing D(WTP)_instantaneous while ignoring Ethical_Coefficient will show early high revenue followed by accelerating churn + regulatory risk.

### L1-L5 Gap Hierarchy

| Level | Type | Gap Composition | ICP Condition | WTP Signature |
|---|---|---|---|---|
| L1 | Social Position Gap | Social_Position_Gap > 0, Functional near 0 | Anyone needing belonging/inclusion signals | WTP has ceiling (network saturation) |
| L2 | Commodity Delegation | Functional_Gap begins | Needs functional task outsourcing | Price-sensitive, alternative-aware |
| L3 | Identity Delegation | Identity-threatening Functional_Gap | Professionals with external visibility | "I know I lack something but don't know the path" |
| L4 | Meta-insight (Known Unknown) | Strategic, named Functional_Gap | External visibility + self-gap awareness | "I know what I don't know but not how to fix it" |
| L5 | Meta-insight (Unknown Unknown) + Identity Portability | Unnamed gap + identity portability | External-visibility professionals (employment-agnostic) | "I didn't know I didn't know this" — highest WTP, most price-inelastic |

**Critical L1 resolution**: In v1, Social_Amplifier as a pure multiplier created a paradox: if Gap_Intensity is near 0, D(WTP) should be near 0, yet L1 products extract real WTP. v2 resolves this by separating Gap_Intensity into Functional_Gap + Social_Position_Gap. L1 products operate on Social_Position_Gap alone.

**WTP ordering prediction**: At population level, average WTP follows L1 < L2 < L3 < L4 < L5. Individual variation is permitted, but systematic group-level reversal falsifies the hierarchy (see PHASE 5).

### ICP Criterion: Identity Portability

The v2 theory replaces employment-type exclusion (e.g., "exclude salaried workers") with **identity portability** as the core ICP criterion.

**Definition**: Identity portability = the degree to which a professional's reputation travels independently of their employing institution.

**3-condition test** (all must be met for high L5 WTP potential):

1. **External output exists**: The person has public artifacts (blog, GitHub, portfolio, talks, publications) that carry their name, not their employer's brand.
2. **Reputation is transferable**: If they left their current employer tomorrow, their professional reputation would follow them. Peers in the industry would recognize their work independently.
3. **Failure is personally attributed**: When things go wrong, the consequences attach to the individual's personal brand, not absorbed by the institution.

**Included (high L5 WTP)**: Founders 0-3 years, freelancers, consultants, researchers, developers with public profiles, knowledge workers with external recognition — regardless of employment form.

**Excluded (low L5 WTP)**: Professionals whose identity is opaque to the external market — failure is institutionally attributed, personal brand has no independent existence.

**Key correction from v1**: v1 excluded all salaried workers. v2 includes salaried workers who have identity portability (e.g., Remember/LinkedIn users who are consultants, researchers, or public-output knowledge workers within companies).

### Scope Boundary (when this theory applies)

VALUE GAP applies ONLY when ALL THREE conditions are met:

**In-scope conditions:**

1. **High involvement**: Cognitive effort and psychological engagement in the purchase decision. Pre-purchase comparison/search behavior exists. Post-purchase satisfaction affects self-evaluation. (Zaichkowsky 1985 Personal Involvement Inventory, above median)
2. **Identity-adjacent**: The purchase target connects to the buyer's self-concept. "What kind of person uses this product?" is a meaningful question whose answer relates to the buyer's ideal self. (Belk 1988 Extended Self framework, above median)
3. **Non-monopolistic market**: Alternatives exist. Monopolistic necessities (electricity, water) are governed by price theory and regulation, not identity gaps.

**Concrete in-scope examples**: Career development tools, coaching, professional expression tools, education, health/wellness services, creative tools, high-involvement fashion/luxury, identity-expression products.

**Out-of-scope categories (VALUE GAP does NOT claim primary explanatory status):**

| Category | Why Out-of-Scope | Better Theory |
|---|---|---|
| (A) Low-involvement replenishment | Toilet paper, detergent, gas — triggered by inventory depletion, not identity gap | Standard price theory |
| (B) Impulse purchase | Unplanned convenience-store snacks — no gap recognition process occurs | Stern (1962) impulse buying classification |
| (C) Pure commodity | Undifferentiated raw materials, generic supplies — WTP = supply-demand equilibrium | Commodity pricing, transaction cost |
| (D) Institutional purchase | Org-KPI-driven procurement — identity gap of individual decision-maker is constrained | B2B procurement theory |
| (E) Addictive/compulsive | Gambling, compulsive shopping — neurochemical reward circuits, not identity gap | Clinical psychology, behavioral addiction |

**Boundary decision procedure** for new purchase situations:
1. Involvement test: Pre-purchase search/comparison exists? -> No = Out-of-scope
2. Identity-adjacency test: "What kind of person am I for using this?" is meaningful? -> No = Out-of-scope
3. Alternative existence test: Alternatives exist? -> No (monopoly) = Out-of-scope

All three passed -> In-scope for VALUE GAP.

---

## PHASE 1: ICP QUALIFICATION

Before running interviews or diagnosing gap levels, screen whether the target user qualifies as an ICP for an identity-gap product. This operationalizes the Identity Portability criterion.

### Screening Questions (5 Yes/No)

**SQ1. "Does your current work output exist publicly under your own name?"**
- Yes: GitHub profile, blog, portfolio site, publications, talk recordings
- No: Only inside company systems, only under team name
- Measures: External visible output existence

**SQ2. "If you left your current company/client tomorrow, could you secure an equivalent opportunity within 3 months?"**
- Yes: High transition confidence = mobility exists
- No: High current-employer dependency
- Measures: Subjective mobility confidence

**SQ3. "In the last 12 months, have you been recognized for your expertise from outside your current organization? (external talks, articles, consulting, headhunter contact, community recognition)"**
- Yes: External market signal generated
- No: Only internal evaluation exists
- Measures: External recognition event occurrence

**SQ4. "Comparing yourself to a peer in your field who is 'doing better,' can you specifically name what they know that you don't?"**
- Yes: Gap awareness activated (L4+ signal)
- No: No comparison target or no gap awareness
- Measures: Unknown-unknown gap pre-awareness

**SQ5. "Do you feel anxiety that continuing your current approach for 2 more years would lead to stagnation?"**
- Yes: Change urgency exists
- No: Satisfied with status quo
- Measures: Change urgency (L4-L5 precondition)

### Threshold

- **3/5+ Yes -> ICP qualified** (proceed to interview)
- **2/5 Yes -> Conditional** (interview to determine, may be L3)
- **1/5 or less -> Not ICP** (current product not relevant for them)

---

## PHASE 2: CUSTOMER INTERVIEW (13 Questions)

**Purpose**: Diagnose which VALUE GAP level (L1-L5) the interviewee occupies, whether they have identity portability, whether unknown-unknown gaps exist.

**Rules**: NEVER use theory language ("gap," "WTP," "level") during the interview. Conduct as a natural context-understanding conversation. Duration: 15-20 minutes.

### Opening (2 minutes)

> "Today, rather than talking about any product, I'd like to first hear about the work you're doing and how things are going. Please speak candidly about the last 3-6 months. There are no wrong answers, and I'm not trying to sell you anything — I'm trying to understand the context of the work you do."

Purpose: Deactivate sales-guard, activate candid mode. DO NOT introduce any product at this stage.

### Level Diagnosis Q1-Q6

**Q1. "How has your work changed compared to a year ago?"**

| Signal | Diagnosis |
|---|---|
| "I've learned a lot" | L1-L2 |
| "What I changed was..." (specific agency) | L3+ |
| "Pretty much the same" | RED: Low urgency |
| Spontaneous mention of dissatisfaction with pace of change | GREEN: L3+ |

---

**Q2. "What takes the most energy in your work right now? Not things you dislike, but things that somehow don't go well for reasons you can't quite pin down."**

| Signal | Diagnosis |
|---|---|
| "Just busy" (vague) | L1-L2 |
| Named recurring friction | L3 |
| "There's a ceiling but it's not visible to others" | GREEN: L4-L5 |
| Can't name it properly, pauses mid-sentence | GREEN: Pre-signal for unknown-unknown |

---

**Q3. "Among people who do the same kind of work, is there someone where you think 'why is that person doing better?' Can you think of a specific case?"**

| Signal | Diagnosis |
|---|---|
| "They're just lucky" | L1-L2, Social Amplifier weak |
| "They seem to know something different" | GREEN: L4, Social Amplifier ON |
| No reference group at all | RED: Low WTP |
| Specific person + delta observation + frustration | GREEN: L4-L5 |

---

**Q4. "By your own standards, do you feel there's a gap between your actual ability and how much external recognition you get?"**

| Signal | Diagnosis |
|---|---|
| "I have the skills but I'm not known" | L3 |
| "I don't know how to make myself known" | GREEN: L4-L5 (indirect unknown-unknown expression) |
| "It feels about right" | RED: No gap awareness |
| Emotional escalation + unprompted example | GREEN: Strong signal |

---

**Q5. "If you keep doing things exactly the same way for 2 more years, how would you feel about that?"**

| Signal | Diagnosis |
|---|---|
| "That would be fine" | RED: No urgency |
| Mild anxiety | L3 |
| Named, specific fear | L4-L5 |
| "I wouldn't feel like myself" type identity-outcome response | GREEN: L5 |

---

**Q6. "When you say work is going well, what does that mean to you first — money, recognition, or freedom?"**

| Signal | Diagnosis |
|---|---|
| Money first | Functional_Gap dominant (L1-L3) |
| Recognition or autonomy first | GREEN: Social_Position_Gap or identity gap (L4-L5) |
| Only socially correct answers | RED: ICP unclear |

---

### Identity Portability Probe Q7-Q9

**Q7. "Without your current company or clients, if you had to find work starting tomorrow, what would you bring with you?"**

- GREEN: Specific outputs, results, reputation -> High portability (L5 ICP)
- RED: "I'd submit my resume" / references current employer's brand -> Low portability

**Q8. "Do you feel like you're building something under your own name, or building within the place where you currently are?"**

- GREEN: "I want to build under my own name but it's not working out" -> High L5 potential, gap already felt
- RED: "Under my organization's name, and that's fine" -> Low identity portability

**Q9 (optional). "How many people in your industry would you estimate know the work you do?"**

- Low number + dissatisfaction -> Social Amplifier gap activated
- High number + satisfaction -> Social Amplifier already fulfilled, lower marginal WTP from this dimension

---

### Unknown-Unknown Surfacing Q10-Q11

"Do you know what you don't know?" is FORBIDDEN. Use contrast and third-person framing to surface it indirectly.

**Q10. "When you look at someone with a similar background who progressed much faster, what do you think they knew that you didn't?"**

- The interviewee's answer = projection of their own unknown-unknowns
- Specific, reasoned answer -> High gap awareness potential
- "I don't know" (genuinely puzzled) -> Unknown-unknown confirmed

**Q11. "Among things you've solved on your own so far, was there ever a time when you later discovered there was a much faster way?"**

- Retrospective gap recognition activated -> Reduces resistance to current unknown-unknowns
- Multiple specific examples -> Person regularly encounters unknown gaps
- "Not really" -> Either very competent or very unaware

---

### Attainability Check Q12

**Q12. "If that gap could actually be narrowed, do you think it's possible within 6 months?"**

- GREEN: "I think it's possible but I don't know how" -> Attainability latent, activatable
- RED: "My case is kind of special" -> Structural attribution, Attainability low
- YELLOW: "Maybe with the right help" -> Conditional Attainability, product must demonstrate path

---

### Social Amplifier Check Q13

**Q13. "Whether this problem gets solved or not, is there someone around you who would notice?"**

- GREEN: Named specific people (boss, client, community peers) -> Social Amplifier ON
- RED: "Not really" -> Gap invisible to social reference group, WTP low
- Note: If the gap is invisible to others, Social_Amplifier approaches 1.0 (baseline), reducing D(WTP).

---

### Closing (1 minute)

Name the gap using THEIR language, but DO NOT present a solution.

> "Based on what you've shared, it sounds like [specific concern from Q5] and [observation from Q10] might be connected somehow. Would it be okay to talk about that part more sometime?"

Reflect the tension back in the interviewee's own words and name it — NOT a solution. **This moment IS the sale.**

---

### Post-Interview Internal Scoring (do not share with interviewee)

| Signal | Level Assignment |
|---|---|
| Specific future fear named in Q5 | L4-L5 |
| Unprompted peer comparison + delta analysis in Q3 | Social Amplifier ON |
| "Want to build under my own name but..." in Q8 | Identity Portable |
| Retrospective unknown-unknown admission in Q11 | Attainability unlockable |
| No urgency, no reference group, no response in Q5 | Recycle / nurture (not ICP now) |

**Scoring rubric:**

Count GREEN signals across Q1-Q13:

| GREEN Count | Level | Implication |
|---|---|---|
| 0-2 | L1-L2 | Not a target for identity-gap products. Standard functional value proposition needed. |
| 3-5 | L3 | Feels the gap but can't articulate the path. Responds to "how to" framing. Mid-tier WTP. |
| 6-8 | L4 | Can name the gap, seeking precision. Responds to data/benchmarks. High WTP, price < value assessment. |
| 9+ | L5 | Unknown-unknowns confirmed. Responds to gap revelation with intensity. Highest WTP, most inelastic. |

---

## PHASE 3: LEVEL DIAGNOSIS OUTPUT

After completing the interview, synthesize the diagnosis:

### Level Assignment Checklist

1. **Count GREEN signals** from Q1-Q13 signal tables
2. **Check identity portability** from Q7-Q9 (must be positive for L5 assignment)
3. **Check Social Amplifier** from Q3 and Q13 (determines pricing multiplier)
4. **Check Attainability** from Q12 (must be at least conditional for product viability)

### What Each Level Means for Product Design

**L1-L2 (Low gap intensity)**:
- Product must provide tangible functional value (delegation, convenience)
- Pricing: Low ceiling, alternatives matter, commodity comparison shopping expected
- WTP driver: "Does this save me time/effort?" NOT "Does this reveal something about me?"
- Example products: Task automation, basic templates, commodity content

**L3 (Identity-threatening functional gap)**:
- Product should name the gap and provide a clear path
- Pricing: Mid-range, ₩15,000-35,000/month for Korean B2C knowledge services
- WTP driver: "I know something is wrong but I don't know the route to fix it"
- Gap revelation is partially effective (they already feel it vaguely)

**L4 (Meta-insight, known unknown)**:
- Product must provide precision: benchmarks, data-driven diagnosis, specific comparisons
- Pricing: Higher range, ₩39,000-69,000/month. Single reports: ₩100,000-250,000
- WTP driver: "I can name the gap but need precise direction and peer comparison"
- Social Amplifier is active — peer cohort features increase WTP

**L5 (Meta-insight, unknown unknown + identity portability)**:
- Product must REVEAL what the user couldn't see themselves (gap disclosure = sale)
- Pricing: Premium, ₩59,000-99,000/month. Price is not the barrier — trust is.
- WTP driver: "I didn't know I didn't know this" — the shock of revelation
- Requires cohort-based comparison data to make gap disclosure credible, not horoscope

### What This Means for Pricing

D(WTP)_sustainable determines the pricing ceiling. Use the formula:

```
D(WTP)_sustainable = [Gap_Intensity x Attainability] x Social_Amplifier x Ethical_Coefficient

Map to price range:
  D(WTP) < 0.5  -> Sub ₩15,000/month (L1-L2, functional value only)
  D(WTP) 0.5-1.0 -> ₩15,000-35,000/month (L3)
  D(WTP) 1.0-1.5 -> ₩39,000-69,000/month (L4)
  D(WTP) > 1.5  -> ₩59,000-99,000/month (L5)
```

---

## PHASE 4: BBAIJJIM AUDIT

**Definition**: Bbaijjim (dependency) is a structural property of the product-user relationship, not a moral judgment. A product exhibits bbaijjim when, after N usage cycles, the user's ability to achieve the same goal WITHOUT the product has **not increased or has decreased**.

```
Autonomy(t) = Probability of achieving the goal without the product

Healthy product:  dAutonomy/dt > 0  (autonomy increases over time)
Bbaijjim product: dAutonomy/dt <= 0 (autonomy stagnant or declining)
```

### 4 Structural Conditions of Bbaijjim

All four must be simultaneously present for a bbaijjim diagnosis. One alone may not constitute bbaijjim.

1. **Gap Reproduction**: The product regenerates the same or similar gap that it resolves. User feels "solved" but the substantive gap hasn't shrunk.
2. **Alternative Blocking**: Product intentionally blocks or hides independent problem-solving paths.
3. **Escalating Exit Cost**: Cost of leaving increases disproportionately with usage duration (data lock-in, habit formation, sunk identity).
4. **Autonomy Perception Distortion**: User believes they've become more capable, but testing without the product reveals no actual improvement.

### Healthy Retention vs Dependency Retention

| Dimension | Healthy Retention | Dependency Retention |
|---|---|---|
| Return motivation | Discovering new frontier | Unresolved same gap |
| Feeling when leaving | Achievement of "graduation" | Anxiety, loss, fear |
| Capability after stopping | Maintained or improved | Regressed |
| Recommendation reason | "I learned X here" | "I can't function without it" |
| Gap direction | New gap > old gap (frontier moved) | Old gap recycled |

### 13-Item Checklist

Score each item: YES (healthy) = 0, NO (risk) = 1.

**Gap Direction Indicators (5 items):**

| # | Item | YES = Healthy | NO = Risk |
|---|---|---|---|
| GA-1 | Cohort gap reduction: After 6 months, users' core gap score decreased vs onboarding? | Gap actually closing | Gap reproduction suspected |
| GA-2 | Churned user success rate: Users who left achieved their goal at similar rate to active users? | Capability transferred (healthy graduation) | Product is the bottleneck |
| GA-3 | Renewal motivation change: Renewal reason is "want to learn new things" vs "feel I have to continue"? | "New frontier" motivation dominant | "Anxiety/habit" motivation dominant |
| GA-4 | Closed gap recycling: Product does NOT re-display gaps the user already closed? | No recycling | Artificial gap reproduction |
| GA-5 | Upward mobility rate: 20%+ of paid users reset goals to higher-tier outcomes within 6 months? | Frontier expansion working | Stuck on same goal |

**User Autonomy Indicators (5 items):**

| # | Item | YES = Healthy | NO = Risk |
|---|---|---|---|
| AU-1 | Independent execution test: 60%+ of users say "I can do it without the product" (quarterly survey, 1-5 Likert, avg 3.5+)? | Capability transfer successful | Product dependency formed |
| AU-2 | Deliberation time preserved: Product provides minimum 24h deliberation time before payment/upgrade decisions? | Autonomy preserved | Impulse purchase inducement |
| AU-3 | Information transparency: Product explains how it works AND guides how to achieve the same result without the product? | No alternative blocking | Alternative blocking present |
| AU-4 | Data portability: User can fully export their data in standard formats (CSV, JSON)? | Limited exit cost | Escalating exit cost |
| AU-5 | Habit vs intent ratio: 50%+ of daily logins are "intentional goal-driven" (vs habitual checking)? | Intentional use dominant | Habit loop formed |

**Social Amplification Indicators (3 items):**

| # | Item | YES = Healthy | NO = Risk |
|---|---|---|---|
| SA-1 | Identity expression outside product: 70%+ of users can describe their expertise WITHOUT mentioning the product name? | Identity amplification (healthy) | Identity replacement (danger) |
| SA-2 | Social comparison direction: Product uses more "here's where you could go" (upward goal) than "you're falling behind" (downward comparison)? | Healthy motivation | FOMO exploitation, shame-based retention |
| SA-3 | Community graduation celebration: Product treats user "graduation" (goal achieved, leaving) positively? | Healthy lifecycle acknowledged | Leaving framed as failure |

### Scoring

| Score (total NO count) | Judgment | Action |
|---|---|---|
| 0-4 | **Safe** (healthy) | Maintain current design. Quarterly re-check. |
| 5-8 | **Watch** (caution) | Build improvement roadmap for flagged items. Re-check in 6 weeks. |
| 9-13 | **Restructure** (redesign required) | Redesign core product loop. Consider halting launch. |

### Mandatory Redesign Triggers (regardless of score)

These patterns trigger IMMEDIATE redesign even if total score is low:

- **Trigger 1 — Autonomy reversal**: AU-1 = NO AND GA-1 = NO -> User becoming less capable AND gap not shrinking. Worst combination.
- **Trigger 2 — Artificial gap loop**: GA-4 = NO AND GA-3 = NO -> Re-selling already-solved problems while retaining through anxiety.
- **Trigger 3 — Identity hijacking**: SA-1 = NO AND AU-4 = NO -> User's professional identity is trapped inside the product with no escape.

### Ethical_Coefficient Proxy Calculation

Convert checklist score to Ethical_Coefficient:

```
Ethical_Coefficient_proxy = (13 - bbaijjim_score) / 13

Safe (0-4):        EC approximately 0.77 - 1.00
Watch (5-8):       EC approximately 0.46 - 0.69
Restructure (9-13): EC approximately 0.00 - 0.38
```

Plug this proxy into D(WTP)_sustainable formula to estimate long-term WTP potential.

### 5 Design Principles for Healthy High-WTP Products

1. **Frontier Expansion (Gap Escalator)**: Each session closes 1 gap and reveals 1 new gap at a higher level. Not artificial reproduction — new gaps visible because user has grown.
2. **Graduation Architecture**: Explicit graduation conditions exist. "When all 5 divergence points are closed, you graduate this tier." Paradoxically, graduation design INCREASES D(WTP)_sustainable because it builds trust.
3. **Meta-Transparency**: Explain how the product works to the user. Users who understand the mechanism use more intentionally, stay longer, and recommend more.
4. **Counter-Intuitive Capability Transfer**: Teach users to succeed WITHOUT the product. This keeps Ethical_Coefficient near 1.0 while INCREASING Gap_Intensity (users who grow can see higher-level gaps). Mathematically: higher EC x higher Gap = higher D(WTP)_sustainable.
5. **Social Contribution Path**: After 6+ months, offer users a "contributor role." Contributors confirm their own growth while boosting community Social_Amplifier. Giving > receiving for identity strength.

**Must pass bbaijjim audit before moving to pricing/GTM.**

---

## PHASE 5: FALSIFICATION CHECK

VALUE GAP theory specifies conditions under which it should be considered WRONG. Based on Lakatos' MSRP (hard core vs protective belt) and Popper's falsificationism.

### Hard Core Propositions (if ANY is falsified, the theory loses its unique explanatory power)

**HC-1: Identity gap = root of WTP**
> In high-involvement identity-adjacent purchases, WTP is proportionally (monotonically increasing) related to perceived identity gap intensity.
- Falsified if: Pearson r < 0.15 (or negative) between gap intensity and WTP, p < 0.05, N >= 200, using 3+ independent gap measurement tools.

**HC-2: Gap disclosure = purchase trigger**
> The moment a potential buyer recognizes their identity gap is the core trigger for purchase conversion. High-involvement purchase does not occur without gap recognition.
- Falsified if: 40%+ of high-involvement buyers (purchase > ₩50,000) report no gap experience at purchase time AND cannot reconstruct one retroactively.

**HC-3: Hierarchical gap structure**
> Identity gaps form qualitatively distinct levels (L1-L5) where higher levels systematically produce higher WTP at population level.
- Falsified if: Population mean WTP order shows L5 < L3 or L4 < L2 across 2+ independent samples. Critical test: L5 WTP must exceed L3 WTP even AFTER gap disclosure for L5 subjects.

**HC-4: Sustainability separation**
> Instantaneous WTP and sustainable WTP are separable constructs. Unethical gap exploitation maximizes the former while systematically degrading the latter.
- Falsified if: Exploitative products maintain high WTP for 5+ years without churn increase, regulation, or reputation damage (in competitive markets).

### Key Falsification Conditions

| # | Condition | Tests | What It Would Mean |
|---|---|---|---|
| F-1 | No correlation between gap intensity and WTP | BDM auction + self-discrepancy scale, N>=200 | Theory's core equation is empty |
| F-2 | 40%+ buyers had no gap at purchase time | Post-purchase interview within 24h, N>=100 | "Gap disclosure = sale" is false |
| F-3 | L-level hierarchy reversal | Within-subject WTP across L2-L5 products | L1-L5 classification is arbitrary tags |
| F-4 | Social visibility has no WTP effect | 2x2 factorial: public/private x high/low gap | Social_Amplifier doesn't exist |
| F-5 | Exploitative products sustain WTP long-term | 5-year ARPU comparison, 10 exploitative vs 10 healthy | Sustainable/instantaneous split unnecessary |
| F-6 | VALUE GAP works outside its stated scope | Apply to low-involvement purchases, outperforms price theory | Scope claim is wrong (precision falsification) |
| F-7 | Gap-WTP relationship doesn't replicate cross-culturally | Same instruments in 3+ cultures, r < 0.10 in 2+ | Theory is Korea-specific, not universal |

### Competing Theory Check

When diagnosing a product/user, check which theory fits BETTER:

| Situation | VALUE GAP Predicts | JTBD Predicts | Mental Accounting Predicts | SDT Predicts |
|---|---|---|---|---|
| "Discover your hidden weakness" vs "Streamline your work" framing, same product | Gap-disclosure framing = 2-3x higher WTP | Same WTP (same job) | Same WTP (same function) | Weakness framing REDUCES WTP (competence threat) |
| Group coaching (same-industry peers) vs individual coaching | Group higher WTP (Social Amplifier) | Individual higher (more customized job resolution) | Same WTP | Group higher (relatedness), but VALUE GAP predicts same-industry group only |
| "You're already great" expert feedback | WTP for self-improvement products DECREASES | WTP unchanged (job still incomplete) | WTP unchanged | WTP unchanged or increases |
| High vs low identity portability, same product | High portability = higher WTP | No difference (same job) | No difference (same income) | High portability = higher WTP (autonomy), but different mechanism |

**Decision rule**: If JTBD or SDT explains the observed pattern better (run the distinguishing experiments above), VALUE GAP may not be the right framework for this product/user.

### Protective Belt (modifiable without killing the theory)

These aspects CAN be revised without falsifying the core:
- PB-1: Whether Social_Amplifier is multiplicative, additive, or threshold (must produce new prediction when revised)
- PB-2: Whether Attainability is linear, U-shaped, or threshold
- PB-3: Whether there are exactly 5 levels or 3, 7, or a continuum
- PB-4: How Ethical_Coefficient changes over time (linear, exponential, step function)
- PB-5: The specific components of identity portability

---

## OUTPUT FORMAT

When completing a VALUE GAP diagnostic, produce this structured output:

```
## VALUE GAP Diagnostic — [Product/Idea Name]
Date: YYYY-MM-DD

### ICP Qualification: [PASS/FAIL/CONDITIONAL] (N/5 screening questions)
### Gap Level: L[N] — [type name]
### D(WTP) Estimate:
  - Gap_Intensity: [value] (Functional [X] + Social_Position [Y])
  - Attainability: [value]
  - Social_Amplifier: [value]
  - D(WTP)_instantaneous: [calculated]
  - Ethical_Coefficient: [estimated]
  - D(WTP)_sustainable: [calculated]
  - Price range: [derived from D(WTP)_sustainable]

### Bbaijjim Risk Score: [N/13] — [Safe/Watch/Restructure]
  - Mandatory triggers active: [None / Trigger 1/2/3]

### Theory Applicability: [IN_SCOPE/OUT_OF_SCOPE]
  - High involvement: [Y/N]
  - Identity adjacent: [Y/N]
  - Non-monopolistic: [Y/N]

### Competing Theory Fit: [VALUE GAP / JTBD / Mental Accounting / SDT / other]
  - Distinguishing prediction: [which experiment would decide]

### Interview Signals (if interview conducted)
  - GREEN signals: [count] — key responses: [list]
  - Identity portability: [high/low] — evidence: [Q7-Q9 responses]
  - Social Amplifier: [active/inactive] — evidence: [Q3, Q13]
  - Unknown-unknowns: [confirmed/absent] — evidence: [Q10-Q11]

### Product Implications
  - What product design follows from this diagnosis
  - Which WTP levers to activate
  - Key risks to watch

### Next Step
  [interview more / build MVP / apply /career-mirror-builder / use /wtp-validator instead / theory does not apply]
```

---

## INTEGRATION

- Use BEFORE /wtp-validator to determine if VALUE GAP or standard WTP applies
- Use BEFORE /career-mirror-builder to confirm Career Mirror ICP hypothesis
- Use standalone for non-Career-Mirror identity products
- If bbaijjim audit fails (score 9+), do NOT proceed to pricing/GTM — redesign product core first
- If falsification check suggests JTBD or SDT fits better, switch frameworks
