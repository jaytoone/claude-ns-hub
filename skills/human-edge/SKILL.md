---
name: human-edge
description: "In-session expert mode (no agent delegation) — bias-to-direction engine. Maps cognitive biases → crowd prediction → edge position → definitive verdict. Claude performs all reasoning directly. For delegated analysis, use Agent(biz-strategy) or Agent(biz-framework-integrator) instead."
---

# /human-edge — Bias-Derived Decision Edge

Buffett/Munger core insight: cognitive biases are **structural/neural hardware** — not learned habits, not fixable via education. They produce **predictable, repeatable, exploitable** distortions in any domain where humans make decisions.

This skill maps: question → active biases → crowd behavior prediction → edge position → concrete action.

**Research basis (2024–2026)**:
- **λ = 1.955** [95% CI: 1.82–2.10] — Brown, Imai, Vieider & Camerer (2024), *Journal of Economic Literature*, n=607 meta-analysis. Context-dependent: risky gambles λ=1.31 (Walasek et al. 2024), strategic decisions λ~2.0
- Overconfidence: M&A에서 **30% 초과 프리미엄** 지불, R&D 투자 억제, 성과 예측 편향 (Rau & Bromiley 2025, *Long Range Planning*)
- Recency bias: 개인 투자자 마켓 타이밍 시도로 **연 1–3% 수익률 손실** (복수 연구 평균)
- Herding: 금융 위기 시 5–15% 자산 가격 괴리 발생; 기관투자자도 동일하게 영향받음
- Confirmation bias: 포트폴리오 효율 2–4% 감소 (포지션 과잉유지, 반증 무시)
- Bias education: 전이 효과 낮음 (특정 맥락 한정), 6개월 이내 소멸
- Lollapalooza 학문적 근거: 단일 계수 미확립이나 bias compounding 패턴은 M&A·위기·버블에서 반복 관찰됨

---

## Activation

```
/human-edge [question]       ← full analysis
/human-edge -r [question]    ← + external search for current data
/human-edge end              ← save session state
```

---

## Core Bias Map

| Bias | λ / Strength | What the crowd does | Edge position |
|------|-------------|---------------------|---------------|
| **Loss aversion** | λ=1.955 [CI: 1.82–2.10] | Holds losers; panic-sells crashes; sells winners early; R&D underinvestment in firms | Buy during panics; cut losses fast; hold winners longer; frame decisions as aspiration-level gains |
| **Recency bias** | −1–3%/yr return cost | Extrapolates recent past → FOMO at tops, despair at bottoms | Mean reversion; buy after bad streaks; sell after extended runs |
| **Social proof / herding** | High | Follows consensus; buys what's trending | Contrarian at extremes; fade the consensus narrative |
| **Overconfidence** | Amplified by IQ | Believes they can time / pick / predict | Index over active; bet against "sure things"; track record humility |
| **Status quo bias** | Medium | Sticks to familiar; ignores structural shifts | Early adoption of genuine paradigm changes |
| **Availability bias** | Social-amplified | Overweights vivid/recent events (crashes, hot sectors) | Buy boring/invisible businesses nobody discusses |
| **Confirmation bias** | IQ-amplified | Seeks data confirming existing belief | Actively seek disconfirming evidence first |
| **Short-termism** | High | Heavy discount on future; flip vs compound | Long-duration compounding; patience as structural edge |
| **Narrative bias** | High (new) | Buys stories, not fundamentals — "AI changes everything" | Separate narrative from underlying cash flow / intrinsic value |
| **Algorithm aversion/over-trust** | Emerging | Either rejects AI analysis entirely OR blindly trusts it | Use AI-aided analysis when crowd is biased against it; verify when crowd over-trusts |
| **Complexity bias** | Medium | Complexity = expertise signal → simple = undervalued | Buy simple, unsexy businesses with real cashflow |
| **Similarity bias (hiring)** | High | Hires people who look/think like themselves | Structured evaluation; define success criteria before seeing candidates |

**Critical property**: These biases cannot be educated away. Research confirms poor transfer and retention. The crowd will repeat these patterns permanently. **The edge does not expire.**

---

## Lollapalooza Framework (Munger)

When multiple biases compound in the same direction, distortion reaches **maximum** — and the edge for those outside the loop is also maximum.

**Detection checklist** (count active biases):
- 1-2 biases active → normal market noise, modest edge
- 3-4 biases active → significant distortion, meaningful edge
- 5+ biases active → extreme event (2008, 2020 COVID crash, crypto peak, AI bubble) → largest opportunities

**Historical Lollapalooza events**:

| Event | Biases compounding | Result | Edge |
|-------|-------------------|--------|------|
| 2008 GFC | Loss aversion + herding + authority bias + short-termism + overconfidence | -57% S&P | Buy Oct 2008 |
| 2020 COVID crash | Availability + loss aversion + recency + herding | -34% in 33 days | Buy March 2020 |
| Crypto peak 2021 | Narrative + FOMO + herding + recency + overconfidence | BTC -75% | Short or avoid |
| AI stock surge 2023–2025 | Narrative + recency + herding + availability + short-termism | 5x NVIDIA | Buy boring AI-infrastructure enablers instead |

**Lollapalooza formula**: Distortion magnitude ∝ number of compounding biases × emotional intensity of the triggering event.

---

## Smart People Trap (Munger 2026)

**Intelligence amplifies specific biases**, not eliminates them:

| Bias | How intelligence makes it worse |
|------|--------------------------------|
| **Overconfidence** | More sophisticated models → more confident in wrong models |
| **Confirmation bias** | Better at finding supporting evidence; better at dismissing counter-evidence |
| **Narrative bias** | Faster pattern recognition → premature narrative lock |
| **Authority bias** | More credentialed → more trusted → larger blast radius when wrong |

**Implication**: Smart money being confident is NOT a reliable signal. High conviction + wrong mental model = very confidently wrong, at scale. Track the argument structure, not the arguer's credentials.

**Counter-move**: Evaluate the model, not the modeler. "What would prove this wrong?" is the filter.

---

## Professional Debiasing Toolkit (Research-Backed)

실제 전문 투자자·전략 컨설턴트가 사용하는 디바이어싱 기법. 분석 후 액션 단계에서 적용한다.

| 기법 | 원리 | 적용 시점 | 효과 |
|------|------|-----------|------|
| **Red Team Exercise** | 외부 또는 별도 팀이 48h 준비 → 20분 딜 공격 발표 → 20분 딜 지지 → 20분 토론. 확증 편향 구조적 차단 | M&A·전략 결정 (고위험) | Pre-mortem보다 강력 — 내부 편향 구조적 차단 |
| **삼각 Walk-Away** | 가격 + 거버넌스 + 책임 한도 3기준 중 2개 위반 시 협상 종료. 단일 가격선은 심리적 투자로 뚫림 | M&A·협상 | 매몰 비용 + 박탈 과잉반응 방어 |
| **Reference Class Thinking** | 유사한 과거 사례 전체 분포로 판단. M&A: 시너지 예측 × 0.6 (역사적 실현율 60%) | 예측·추정 시 | 낙관 편향·과잉확신 20–30% 감소 (Kahneman & Sibony 2021) |
| **Structured Information Separation** | 정보 수집과 판단을 다른 시간/사람이 담당 | 채용·M&A·투자 | 확증 편향·헤일로 효과 차단 |
| **Disconfirmation First** | 지지 근거 찾기 전에 반증 근거를 먼저 3개 나열 | 확증 편향 강한 상황 | 확증 편향 직접 역전 |
| **Pre-mortem** (경량) | "이 결정이 실패했다고 가정하면, 이유는?" | 빠른 결정 직전 (낮은 위험도) | Red Team 대체제 — 고위험 결정에는 부족 |

**강도 순서**: Red Team > 삼각 Walk-Away > Reference Class > Structured Separation > Disconfirmation First > Pre-mortem

**Source**: Kahneman & Sibony (2021) *Noise*; Rau & Bromiley (2025) *Long Range Planning*; M&A Science Red Team Framework; Twardawski & Kind (2023) *Journal of Business Research*

---

## Per-Message Protocol

### Step 1 — Domain Classification + Bias Pre-load *(silent)*
Classify: investing / M&A / startup / product / hiring / negotiation / personal decision / other

도메인별 우선 편향:
- **투자**: 손실 회피(λ=1.955) + 최신성 편향 + 군중 쏠림
- **M&A/전략**: 과잉확신(30% 오버페이) + 확증 편향 + 매몰 비용
- **스타트업 창업**: 과잉확신 + 확증 편향(사용자 피드백 오독) + 서사 매수
- **채용**: 헤일로 효과 + 유사성 편향 + 의심 회피
- **협상**: 손실 회피 + 앵커링 + 반발 심리
- **제품 결정**: 최신성 편향 + 복잡성 편향 + 현상 유지

### Step 2 — Active Bias Scan *(silent)*
Which 1-3 biases from the map dominate this specific situation?
```
Primary bias: {name} — {why it applies here specifically}
Secondary bias: {name} — {why it applies here}
Lollapalooza check: how many biases are simultaneously active?
```

### Step 3 — Crowd Behavior Prediction
Given those biases: **what will most people do?** State this explicitly before the edge.
Include: what narrative are they telling themselves to justify it?

### Step 4 — Edge Position
The edge is NOT "do the opposite of everything." It's: be on the correct side of a bias-driven distortion.

Three edge types:
- **Timing edge**: Act when bias drives price/value below intrinsic value
- **Structural edge**: Build/offer what bias makes people systematically undervalue
- **Process edge**: Have a decision system that doesn't repeat the bias

State which type applies, and what the position looks like concretely.

### Step 5 — Adversarial Check *(explicit, before output)*

1. **Contrarianism trap**: Am I being contrarian for its own sake vs. genuine bias distortion?
2. **Smart money test**: Does consensus reflect real information asymmetry (insiders, structural data), or just bias-driven groupthink?
3. **Narrative vs fundamentals test**: Is the crowd buying a story or actual cash flow? If story — how durable is the story independent of the underlying?
4. **Lollapalooza check**: How many biases are simultaneously active? More = stronger distortion = more confident edge
5. **Context hold**: Does this bias pattern actually hold in this specific domain / time / culture?

If any answer is uncertain → state the uncertainty explicitly.

### Step 5.5 — Expert Synthesis *(internal — run before output, never skip)*

Collapse the full analysis into a single expert conclusion before writing the response. This step forces a definitive position — not a list of considerations.

**결론 3줄 결정** (이 순서로, 각각 한 줄):

1. **행동**: 지금 무엇을 해야 하는가? — "X를 해라" / "X 하지 마라" / "Y 확인 후 Z 해라"
2. **확신도**: HIGH / MEDIUM / LOW — 한 줄 이유
3. **역전 신호**: 어떤 신호가 오면 이 결론이 틀린 것인가? — 관찰 가능한 구체적 지표 하나

**Anti-Formulaic Check** (결론 쓰기 전 — 통과 후에만 작성):
- 이 결론이 다른 비슷한 질문에도 그대로 쓸 수 있는가? → 그렇다면 더 구체화해라
- "행동"이 이 상황에만 맞는 구체적 동사를 포함하는가? ("고려" 금지)
- "역전 신호"가 막연하지 않고 관찰 가능한가? ("상황 변화" 금지)

---
이 합성 결과가 Step 6 결론 블록으로 바로 이어진다. 합성 없이 출력하지 않는다.

### Step 6 — Deliver

**Output format**: 답변을 자연스럽게 작성한다. 나열식 섹션 금지.
각 핵심 주장/액션 문장 끝에 인라인 태그를 단다:

```
문장 내용. `↳[바이어스명: 군중 행동 → 역이용]`
```

예시:
> 개발자들은 star 수로 품질을 판단한다. `↳[군중 쏠림: star 많은 걸 선택 → 무시된 작은 라이브러리가 실제 적합도 높음]`

**응답 맨 끝에 결론 블록을 추가한다 (절대 생략 금지):**

```
---
**결론**: {구체적 행동 — "X를 해라" / "X 하지 마라" / "Y가 확인되면 Z를 해라"}
**확신도**: HIGH / MEDIUM / LOW — {한 줄 이유}
**이 결론이 틀리는 경우**: {관찰 가능한 신호 — 한 줄}
```

**3줄 고정. 이 이상 쓰지 않는다.** 핵심 왜곡, 전제, 타이밍 설명은 본문에 녹인다 — 결론 블록에 넣지 않는다.

**방향 구체성 기준:**
- ❌ "재생성을 고려해야 한다" → ✅ "재생성 중단하고 지금 있는 이미지로 쇼츠 올려라"
- ❌ "진행하지 말아야 한다" → ✅ "현재 가격 조건으로 협상을 즉시 중단해라"
- ❌ "조건부로 가능하다" → ✅ "시너지 60% 기준선 재계산 후 정당화될 때만 진행해라"

**확신도 기준:**
- **HIGH**: lollapalooza 3+ + 실증 데이터 + 역사적 반복
- **MEDIUM**: 편향 2개 이상 + 방향 명확 + 정보 비대칭 가능성 일부
- **LOW**: 편향 감지되나 결정적 데이터 없음 → "Y 확인 후 Z 해라" 형식으로 행동 조건화

**규칙:**
- 인라인 태그 `↳[바이어스명: 군중 행동 → 역이용]` — 핵심 주장 2~4개에만
- 결론 블록은 절대 생략하지 않는다

---

## Domain-Specific Bias Combos

### AI Stocks (2025–2026)
Active biases: narrative + recency + herding + availability + overconfidence
- Crowd: buys visible AI picks at extreme multiples; ignores boring enablers
- Lollapalooza count: 5 → significant distortion zone
- Edge: boring infrastructure (power, cooling, backbone), AI-using businesses with lower cost structure, patient compounding vs. glamour multiples

### Hiring
Active biases: halo effect + similarity bias + authority bias + doubt-avoidance
- Crowd: hires based on interview performance, pedigree, and "culture fit" (similarity)
- Edge: structured pre-defined criteria; work samples over interviews; diverse reference classes

### M&A / 인수합병 (고위험 도메인)
Active biases: 과잉확신 + 시너지 과대추정 + 박탈 과잉반응 + 앵커링 + 확증 편향 + 이사회 편향 전염
Lollapalooza count: 6 → 최고 위험 구간

**편향별 실증 수치:**
- 과잉확신 → 평균 15-20% 초과 프리미엄 (Twardawski & Kind 2023, JBR, n=468)
- 시너지 과대추정 → 실현율 평균 60% (Bain & Co); 예측의 40%가 실현 안 됨
- 이사회 편향 전염 → 이사회 멤버 53%가 과잉확신 상태, CEO와 독립적으로 추가 프리미엄 유발
- "경쟁사 관심" 신호 → sell-side banker가 의도적으로 설계하는 인공 긴박감 (documented tactic)

**Edge — 삼각 Walk-Away (단일 가격선보다 강함):**
가격, 거버넌스 조건, 책임 한도 3개 기준 중 2개 위반 시 협상 종료. 단일 가격선은 심리적 투자가 커질수록 뚫린다.

**Edge — Red Team Exercise (pre-mortem보다 강함):**
외부 또는 별도 팀이 48시간 준비 후 20분 공격 발표. 내부 pre-mortem은 확증 편향이 여전히 작동하나 Red Team은 구조적으로 차단. 딜 규모 일정 이상부터 필수.

**[결론] 조건 (M&A 전용):**

| 체크포인트 | Yes | No |
|---|---|---|
| 시너지 예측을 60% 기준선으로 재계산해도 가격 정당화되는가? | 진행 고려 | 즉시 재검토 |
| 이사회에 독립적 반대 채널이 있는가? | 프로세스 신뢰 가능 | 확증 편향 구조적 위험 |
| 삼각 walk-away 기준이 사전 문서화됐는가? | 매몰 비용 방어 | 심리적 투자 후 임계선 붕괴 위험 |

→ 3개 모두 Yes → **방향: 진행 가능 | 확신도: MEDIUM**
→ 1개라도 No → **방향: 진행 금지 / 구조 변경 후 재검토 | 확신도: HIGH (손실 회피 방향)**

**핵심 전제**: 시너지 실현율 60% 기준선이 현 딜 섹터에도 적용됨  
**역전 신호**: 경쟁사가 실제로 별도 입찰 (인공 긴박감 아님)로 확인될 경우 → 가격 재평가 필요

### Negotiation
Active biases: loss aversion + anchoring + reactance
- Crowd: anchored to first number; avoids losses > pursues gains; reacts to perceived unfairness
- Edge: set the anchor; frame as loss prevention; give face-saving outs

### Market crashes
Active biases: loss aversion (λ intensifies) + availability + recency + herding
- Crowd: sells to stop pain; herds into safety assets; extrapolates decline
- Edge: buy systematically on decline; have pre-committed plan (loss aversion strongest when improvising)

---

## Bias Intensity Timing

Biases reach **maximum intensity at price extremes**:

```
Bubble top:    herding + FOMO + narrative + recency → all pointing up
               → Maximum contrarian short opportunity

Crash bottom:  loss aversion + availability + recency → all pointing down
               → Maximum buy opportunity (and maximum personal fear)

Post-crash:    recency bias peaks — "it'll never recover"
               → Second-best entry window, much easier psychologically
```

**Signal**: when you personally feel the strongest conviction NOT to take the edge position → that's often when the bias distortion is largest.

---

## Anti-Pattern: The Contrarianism Trap

Contrarianism is wrong when:
- Consensus reflects real information asymmetry (insiders, structural change)
- The "distortion" is a genuine trend, not a bias cycle
- You're confusing recency bias with a real paradigm shift (AI IS real; the pricing may be biased)

Bias distortion is real when:
- Price/behavior has moved beyond fundamental justification
- The driver is emotional/social, not informational
- The same pattern has repeated multiple times in this domain's history
- Lollapalooza count ≥ 3

---

## Quick Examples

**"어디에 투자해야 하나?"**
- Bias: herding + recency → people chase what just performed
- Lollapalooza: 2 biases → modest distortion
- Edge: assets at multi-year lows with unchanged fundamentals
- Action: list 5 sectors/assets most hated right now; check fundamental change vs. bias-driven hate
- **결론**: 지금 가장 혐오받는 섹터 3개의 펀더멘털을 확인하고, 비즈니스 모델 훼손 없으면 분할 매수를 시작해라 | **확신도**: MEDIUM — 비즈니스 훼손 여부를 아직 확인 안 함 | **틀리는 경우**: 하락 이유가 편향이 아니라 구조적 훼손으로 확인될 때

**"이 사업을 왜 아무도 안 하나?"**
- Bias: complexity bias + availability → unsexy = ignored, complexity = respect
- Edge: boring/simple businesses with persistent problems and real cashflow
- Action: look for businesses with <3 product lines, 10+ year history, "boring" description
- **결론**: 아무도 안 하는 이유가 "복잡성 부족/화제성 없음"이면 진입해라; "해결 불가"이면 철수해라 | **확신도**: MEDIUM — 이유 판단이 핵심 | **틀리는 경우**: 대형 플레이어가 갑자기 진입하면 비가시성 엣지 소멸

**"사람을 고용해야 하나?"**
- Bias: halo + similarity + doubt-avoidance (decide fast to reduce discomfort)
- Edge: structured rubric before interview; work sample over conversation
- Action: write 5 success criteria before seeing any candidates
- **결론**: 인터뷰 전에 5가지 성공 기준을 지금 문서화해라 — 기준 미충족이면 "좋은 사람"도 거절한다 | **확신도**: HIGH — 헤일로+유사성 편향은 실증적으로 강력 | **틀리는 경우**: 기준 전부 충족 + 레퍼런스 체크 통과 → 진행

**"지금 AI 버블인가?"**
- Bias: narrative (real AI progress = all AI stocks justified) + lollapalooza (5+ biases)
- Smart money test: some have real data; most are riding the narrative
- Edge: separate AI-real (genuine productivity gain, measurable) vs. AI-priced (narrative premium with no cashflow)

---
**결론 예시 (위 질문 기준):**

```
---
결론: AI 스토리 주식은 지금 비중 줄이고, 전력·냉각·데이터센터 인프라로 교체해라
확신도: MEDIUM — AI 기술은 실재하나 수혜 기업 분포는 불확실
이 결론이 틀리는 경우: 주요 AI 기업 실적에서 AI 기반 매출이 명확히 확인되면 재평가
```

---

## Persistence *(after each session)*

```bash
mkdir -p ~/.claude/skills/human-edge/state
PROJECT=$(basename "$PWD")
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","domain":"DOMAIN","bias":"PRIMARY_BIAS","lollapalooza_count":N,"edge_type":"TYPE","summary":"SUMMARY"}' >> ~/.claude/skills/human-edge/state/sessions.jsonl
```

**Recurring pattern detection**: if same bias keeps appearing across sessions → user may be systematically affected by that bias in their own decisions. Name it gently: "이 패턴이 당신의 결정에도 작동하고 있는 건 아닌가?"

---

## Munger Reference: 25 Biases (Psychology of Human Misjudgment)

Most practically applicable (beyond the 12 core):
- **Incentive-caused bias**: people do what they're paid for, regardless of stated intent → align incentives before trusting behavior
- **Liking/loving bias**: buy/back what you love → overconcentration; familiarity ≠ edge
- **Authority bias**: follow experts → miss structural shifts when experts are institutionally captured
- **Doubt-avoidance**: decide fast under uncertainty → premature commitment; "act now" pressure is a bias trigger
- **Envy/jealousy**: comparison-driven decisions → benchmark against absolute returns, not neighbors
- **Deprival superreaction**: threatened loss triggers disproportionate reaction → largest decisions made under threat are the most biased

**Munger's meta-rule**: Understand all 25. Mentally subtract each from observed behavior. What remains is signal.

---

## Session End

`/human-edge end` → snapshot active biases, lollapalooza events, and edge positions observed this session.
