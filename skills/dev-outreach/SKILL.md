---
name: dev-outreach
description: Developer community outreach skill for OSS/side project promotion. Covers channel selection, content generation, and execution across HN, Dev.to, GitHub issues, disquiet.io, TLDR AI, GeekNews, and more. Works standalone or as a sub-skill within /live.
---

# dev-outreach — Developer Community Outreach Skill

## Trigger
- `/dev-outreach`
- "홍보해줘", "채널 홍보", "outreach"
- /live sub-goal: "홍보 채널 실행"

## Purpose

오픈소스/사이드 프로젝트를 개발자 커뮤니티에 홍보한다.
채널별 특성에 맞는 콘텐츠를 생성하고, Playwright MCP로 직접 게시까지 실행한다.

---

## Step 0: 프로젝트 컨텍스트 수집

실행 전 아래 정보를 파악한다:

```
PROJECT_NAME: (예: CTX)
ONE_LINER: (예: LLM-free code context loader)
KEY_METRIC: (예: 5.2% tokens, R@5=1.0 dependency recall)
GITHUB_URL: (예: https://github.com/jaytoone/CTX)
ARTICLE_URL: (있으면) Dev.to / 블로그 포스트 URL
TARGET_AUDIENCE: (예: coding agent 개발자, RAG 엔지니어)
LANGUAGE: ko | en | both
```

`docs/marketing/` 폴더가 있으면 기존 자료 먼저 확인:
```bash
ls docs/marketing/ 2>/dev/null
```

---

## Step 1: 채널 선택 (즉시 실행 가능 우선순위)

### Tier 1 — 즉시, karma/karma 제한 없음

| 채널 | 도달 범위 | 방법 | 계정 필요 |
|------|---------|------|---------|
| **Dev.to** | 글로벌 개발자 | 블로그 포스트 | 필요 (be2jay67 등) |
| **GitHub issues** | 관련 repo 팔로워 | 기존 이슈 댓글 | 필요 |
| **disquiet.io** | 국내 인디 개발자 | 로그 포스팅 | 필요 (be2jay67@gmail.com) |
| **TLDR AI** | 50만+ 구독자 | 이메일 제출 | 없음 (ai@tldr.tech) |

### Tier 2 — 조건부 실행

| 채널 | 조건 | 방법 |
|------|------|------|
| **Hacker News Show HN** | karma ≥ 1 (신규 계정 가능), 단 Show HN은 karma 필요 | 일반 링크로 먼저 제출 가능 |
| **GeekNews** | 계정 필요 (nave94), 타이밍 중요 | 직접 제출 |
| **Reddit** | 서브레딧별 karma 제한 있음 | 기존 토론 스레드 댓글 우선 |
| **continue.dev Discord** | 계정 필요 | Discord MCP 또는 수동 |

### Tier 3 — 장기 채널

| 채널 | 설명 |
|------|------|
| **Hacker Newsletter** | hackernewsletter.com — HN 포스트가 충분히 업보트 되면 자동 선정 |
| **Last Week in AI** | GitHub PR로 제출 |
| **Twitter/X thread** | 계정 있으면 스레드 형태로 |

---

## Step 2: 채널별 콘텐츠 템플릿

### 2-A. Dev.to 포스트

제목 패턴: `[PROJECT]: I built a [ONE_LINER] that [KEY_ACHIEVEMENT]`

구조:
```
## The Problem
[왜 만들었는지 — 기존 솔루션의 문제점]

## How It Works
[핵심 메커니즘 2-3가지]

## Results
[구체적 수치: before/after 비교]

## Quick Start
pip install [package] / npx [tool] 등

## Links
GitHub / Demo / Docs
```

### 2-B. GitHub Issues 댓글

타겟: 관련 repo의 "context window", "file selection", "wrong files" 등 키워드가 있는 이슈

```
Yeah, this is the root issue most people don't talk about.

[Pain point 공감 1-2문장]

I ran into this building [PROJECT_NAME] — built a classifier that routes queries
to the right retrieval strategy before loading files:
- [TRIGGER_TYPE_1] → [STRATEGY_1]
- [TRIGGER_TYPE_2] → [STRATEGY_2]

Results: [KEY_METRIC]

[ARTICLE_URL]

Happy to discuss the approach if helpful.
```

**탐색 쿼리:**
```
site:github.com [repo] "context window" OR "wrong files" OR "file selection"
```

### 2-C. Hacker News

**일반 링크 제출 (karma 0도 가능):**
```
Title: [PROJECT_NAME]: [ONE_LINER] ([KEY_METRIC])
URL: [ARTICLE_URL or GITHUB_URL]
```
- 제목 80자 이하 필수
- "Show HN:" prefix는 karma 필요 — 신규 계정은 제거 후 제출

**Show HN (karma 축적 후):**
```
Title: Show HN: [PROJECT_NAME] – [ONE_LINER] ([KEY_METRIC])

Body:
I built [PROJECT_NAME], a [ONE_LINER].

The problem: [기존 솔루션의 한계]

How it works: [핵심 메커니즘]

Numbers:
- [METRIC_1]
- [METRIC_2]

Install: [INSTALL_CMD]
GitHub: [GITHUB_URL]

Happy to discuss the [TECHNICAL_ASPECT] in comments.
```

### 2-D. disquiet.io 로그 (한국어)

```
[PROJECT_NAME]을/를 만들었습니다.

[PROBLEM_KO — 개발자가 겪는 문제 1-2문장]

[PROJECT_NAME]은 [MECHANISM_KO]:
- [TRIGGER_1_KO]
- [TRIGGER_2_KO]
- [TRIGGER_3_KO]

결과:
- [METRIC_1_KO]
- [METRIC_2_KO]
- [METRIC_3_KO]

GitHub: [GITHUB_URL]
[INSTALL_CMD]
```

⚠️ **중복 게시 방지**: 버튼 클릭 후 페이지 반응 없어도 1회만 클릭. GraphQL deleteLog mutation으로 삭제 가능:
```javascript
// 인증 후 실행
fetch('https://api.disquiet.io/graphql', {
  method: 'POST',
  headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}`},
  body: JSON.stringify({ query: `mutation { deleteLog(id: LOG_ID) }` }),
  credentials: 'include'
})
// React key로 ID 확인: document.querySelectorAll('[class*="cursor-pointer"]')
//   → __reactFiber key값이 로그 ID
```

### 2-E. TLDR AI 뉴스레터 이메일

수신: `ai@tldr.tech`

제목: `[PROJECT_NAME]: [ONE_LINER] — [KEY_METRIC]`

본문:
```
Hi TLDR AI team,

I'd like to submit a link for consideration:

Title: [TITLE]
URL: [URL]

Description: [2-3문장 요약 — 문제/솔루션/수치]

GitHub: [GITHUB_URL]

Thanks,
[NAME]
```

Gmail 자동화: session-3 (be2jay67@gmail.com 로그인 상태 유지 가능)

### 2-F. GeekNews (geek.news)

- 계정: nave94 (2026-04-07 이후 제출 권장 — 신규 계정 페널티 완화 대기)
- 제목: `[PROJECT_NAME]: [ONE_LINER] ([KEY_METRIC])` — 영어 권장
- URL: GitHub 또는 Dev.to 아티클

---

## Step 3: Playwright MCP 실행 순서

```
1. 세션 확인: browser_tabs (session-1 ~ session-4)
2. 로그인 상태 확인: user_id 포함 URL (tally.so/?user_id=XXXXX)
3. 채널별 순서: disquiet.io → Gmail(TLDR) → HN → GeekNews
4. 완료 후 live-state.json channels_completed 업데이트
```

---

## Step 4: /live 통합

`channels_completed` / `channels_pending` 필드를 `.omc/live-state.json`에 추가하여 진행 상태 추적:

```json
{
  "channels_completed": [
    "Dev.to post (URL)",
    "GitHub [repo] #[issue] comment",
    "HN submission (URL)",
    "disquiet.io log",
    "TLDR AI newsletter email"
  ],
  "channels_pending": [
    "HN Show HN (karma buildup needed)",
    "GeekNews (날짜 조건)"
  ]
}
```

**SCORE 평가 기준 (/live 내부):**
- quality: 콘텐츠 품질 (기술적 정확성, 구체적 수치 포함)
- completeness: 완료된 채널 수 / 전체 가용 채널 수
- efficiency: 중복/실수 없이 1회 성공
- impact: 예상 도달 개발자 수 (HN=최대, TLDR=50만+)
- goal_fidelity: 원래 홍보 목적과의 일치도

---

## 참고: 계정 정보 위치

- disquiet.io: be2jay67@gmail.com (Google OAuth) — session-3 로그인 유지
- HN: jaytoone / CTXproj2026! — https://news.ycombinator.com/user?id=jaytoone
- GeekNews: nave94 — 2026-04-07 이후 사용
- Gmail: be2jay67@gmail.com — session-3

계정 정보는 `.omc/live-state.json`의 `channels_pending` 필드에 메모 보관.
