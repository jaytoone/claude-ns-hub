---
name: CL/Kool WTP Postmortem & Reusable Methodologies
description: CL(CommentLens) + Kool killed items — failure analysis + reusable WTP validation infrastructure and outreach methods for future items
type: project
---

## CL/Kool Kill Record (2026-04-04)

### Kool (YouTube Shorts script service)
- **Kill date**: 2026-04-03
- **Kill reason**: Structural competitors (Jasper $49/mo, Copy.ai free) make 49-300만/mo pricing unjustifiable
- **Viability score**: 2/10
- **Lesson**: "what you can build" bias — built product before validating competitive position

### CommentLens (YouTube comment intelligence for beauty brands)
- **Kill date**: 2026-04-04
- **Kill reason**: 32 cold emails, 10 days, 0 replies. WTP signal = none
- **Breakdown**: delivery 68.8%, open 12.5% (below 15-25% benchmark), reply 0%, wtp_responded 1건 (no conversion)
- **Lesson**: Low deliverability (Brevo + paintpoint.co.kr domain) was a primary issue; product message may also lack urgency

**Why:** Both items failed at the "does anyone care enough to respond?" stage, not at the product stage.
**How to apply:** Future items should validate reply rate before building infrastructure.

---

## Reusable Methodologies (carry forward to next item)

### 1. Cold Email Infrastructure (Brevo SMTP)
- **Script**: `kool/send-cl-outreach.js` — nodemailer + Brevo SMTP + pg DB tracking
- **Pattern**: Layer structure (HOOK → EMPATHY → VALUE → SOCIAL → CTA)
- **Tracking**: pixel open + redirect click + DB status update (sent/delivered/opened/visited/wtp_responded)
- **Caution**: Brevo + custom domain deliverability was ~69%. Consider warming domain or using different SMTP for next item
- **Reuse**: Script structure is item-agnostic. Change email array + subject/body templates

### 2. WTP Events DB (wtp_events table)
- **Schema**: `{id, type, payload(jsonb), ip, ua, created_at}`
- **POST API**: `wtp-dashboard/src/app/api/outreach/track-visit/route.ts`
- **Use**: Any Fake Door / survey / CTA click can post to this table
- **Reuse**: Fully generic. Change `type` field per experiment

### 3. Fake Door Landing Pattern
- **Kool**: `kool/landing/variant-a/index.html` — pricing buttons → waitlist modal with plan tracking
- **CL**: `comment-lens/src/app/pricing/page.tsx` — 3 plans + waitlist modal
- **Pattern**: Pricing button click → modal with email capture → wtp_events POST
- **Reuse**: Copy HTML structure, change copy/pricing

### 4. LinkedIn DM Outreach (Playwright)
- **Method**: Playwright session-4, manual SingletonLock removal for session recovery
- **Pattern**: Search → Visit profile → "Connect" → "Add a note" → custom message → Send
- **Result**: 8 DMs sent to K-beauty marketers
- **NOTABLE**: 1 interview request accepted (김송희, in-house marketer) — only LinkedIn produced action signal
- **Lesson**: LinkedIn DM > cold email for B2B outreach in Korea market. Even with 노쇼, the acceptance itself = higher engagement than 32 cold emails combined
- **Reuse**: Playwright automation script pattern; session management (check browser_tabs, clear SingletonLock)

### 5. Van Westendorp Interview Prep
- **Guide**: `docs/cl-vw-interview-guide.docx` — v3 with hidden purposes per question
- **Survey backup**: `wtp-dashboard/public/cl-survey.html` — 10-question form posting to wtp_events
- **Pattern**: VW 4 questions (too cheap / cheap / expensive / too expensive) + role/method/cost context questions
- **Reuse**: VW questions are product-agnostic. Change Q4 (usefulness framing) and Q5-Q8 price anchors per product

### 6. Sample Report as Sales Tool
- **CL**: `docs/cl-sample-report.html` — Korean, inline request form, deployed to Vercel static
- **Pattern**: Real data analysis → branded PDF/HTML → attach to outreach → CTA inside report
- **Reuse**: For any data/analysis product, create 1 real sample → use as lead magnet

### 7. Community Posting (CreativeBox, disquiet.io, Kakao OpenChat)
- **CreativeBox**: SmartEditor2 API — `oEditors.getById['wr_content'].setContents(body)`
- **disquiet.io**: ProseMirror — `execCommand('insertText')` + textbox ref
- **Result**: Low engagement from community posts. disquiet = ghost town signal
- **Lesson**: verification-gated platforms (Reddit) > open platforms (disquiet) for signal quality

---

## Key Signal: LinkedIn > Cold Email for Korea B2B

LinkedIn DM 8건 중 인터뷰 승인 1건 (12.5% acceptance) vs Cold email 32건 중 reply 0건 (0%).
이 차이가 의미하는 것: 한국 B2B 시장에서 LinkedIn이 cold email보다 채널로서 강력하다.
다음 아이템에서 LinkedIn DM을 primary outreach channel로 사용할 것.
