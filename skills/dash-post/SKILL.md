---
name: dash-post
description: "Utility command (automation) — posts today's git commit log to dash.vidraft.net via Playwright. Single-task automation, not an agent scaffold. Consider migrating to a dev-executor agent task for cleaner separation. Trigger: /dash-post or 'dash에 올려줘'."
---

# dash-post — dash.vidraft.net 일일 작업 자동 포스팅

## Trigger
- `/dash-post`
- "dash에 올려줘"
- "오늘 작업 기록해줘"
- "데일리 워크 포스팅"
- "dash 업데이트"

## Purpose

매 작업 세션 마무리 시, 현재 git 프로젝트의 오늘 커밋 내역을 dash.vidraft.net 해당 프로젝트 항목에 자동으로 기록한다.

---

## 인증 정보

**항상 `~/.claude/env/shared.env`에서 로드** — 절대 하드코딩 금지:

```bash
source ~/.claude/env/shared.env
# $DASH_ID, $DASH_PW 사용 가능
```

Playwright 로그인 시:
```javascript
await p.getByPlaceholder('이름').fill(process.env.DASH_ID);
await p.getByPlaceholder('비밀번호').fill(process.env.DASH_PW);
```

---

## Step 0: 오늘 작업 내역 수집

```bash
# 오늘 날짜 (KST 기준)
TODAY=$(date +%Y-%m-%d)
TODAY_DISPLAY=$(date +%Y%m%d)

# 오늘 커밋 추출 (최신순, 10개 이내)
git log --oneline --since="$TODAY 00:00" --until="$TODAY 23:59" --no-merges | head -10
```

수집 결과를 아래 포맷으로 구성:
```
{TODAY_DISPLAY} 작업 내역:
- {커밋 메시지 1}
- {커밋 메시지 2}
...
```

오늘 커밋이 없으면: `{TODAY_DISPLAY} 작업 내역:\n- 코드 리뷰 / 기타 작업`

---

## Step 1: 프로젝트 → dash 탭 매핑

| 프로젝트 디렉토리 | 탭 | dash 프로젝트명 |
|---|---|---|
| HugwartsBanana / ginigen.ai | ⚙️ 개발/운영 및 프로젝트 | 허그와트 바나나 (ginigen.ai) |
| NodeClaw / node-claw | ⚙️ 개발/운영 및 프로젝트 | NodeClaw |
| OneViral | ⚙️ 개발/운영 및 프로젝트 | OneViral |
| 정부과제 관련 프로젝트 | 🏛️ 정부 지원 과제 | (프로젝트명 일치) |
| 제휴/영업 관련 | 💼 제휴/영업/투자 | (프로젝트명 일치) |

현재 `git remote -v` 또는 디렉토리명으로 프로젝트를 자동 감지한다.

---

## Step 2: Playwright 세션 확보

**CRITICAL**: WSL2 환경에서는 session-1/2/3이 SingletonLock 오류 발생.
**항상 session-4 우선 사용.**

```
1. mcp__playwright-session-4__browser_tabs 로 현재 탭 확인
2. about:blank 또는 dash.vidraft.net 이면 사용 가능
3. 불가 시 session-3 → session-2 → session-1 순으로 시도
```

---

## Step 3: dash.vidraft.net 로그인 (필요 시)

```
URL: https://dash.vidraft.net/
```

현재 페이지가 이미 dash.vidraft.net이고 "👤 장재원"이 보이면 로그인 완료 — skip.

로그인이 필요한 경우 사용자에게 확인 후 진행:
- 아이디/비밀번호는 사용자에게 직접 질문하거나 `.env.hb` 또는 `~/.claude/env/shared.env`에서 참조

---

## Step 4: 프로젝트 탭 이동 및 항목 찾기

```
1. 좌측 메뉴에서 해당 탭 클릭 (Step 1 매핑 기준)
2. 프로젝트 목록에서 프로젝트명 항목 클릭
3. 우측 상세 폼이 열리면 확인
```

**항목이 없는 경우**: "＋ 새 프로젝트" 버튼 클릭 후 신규 생성

---

## Step 5: 폼 필드 업데이트

업데이트할 필드:

| 필드 | 값 | 비고 |
|---|---|---|
| **작성자** | **장재원** | **항상 `장재원` 고정** — 매 포스팅마다 필수 확인/설정 |
| 마감일 | **TODAY** (YYYY-MM-DD) | **항상 오늘 날짜로 덮어씀** — 기존 계약 마감일 무관 |
| 계약시작 | **TODAY** (YYYY-MM-DD) | **항상 오늘 날짜로 덮어씀** |
| 계약종료 | **TODAY** (YYYY-MM-DD) | **항상 오늘 날짜로 덮어씀** |
| 진행단계 | 사용자 입력 또는 현재 값 유지 | "착수/개발/중간점검/납품/완료" 중 명시 시 업데이트 |
| 진행률 | 사용자 입력 또는 추정값 | 기본값: 현재 슬라이더 값 유지; 명시 시 업데이트 |
| 산출물 | 링크가 있으면 입력, 없으면 skip | 사용자가 링크를 제공한 경우만 업데이트 |
| 메모 | Step 0에서 수집한 작업 내역 | **overwrite** — 오늘 내용만 (누적 X) |

**작성자 처리 규칙** (MANDATORY):
- 모든 dash-post 작업에서 **작성자 필드는 반드시 `장재원`으로 설정**한다.
- 신규 프로젝트 등록 시: 작성자 = `장재원`으로 입력
- 기존 프로젝트 업데이트 시: 작성자 필드 값을 확인하고 `장재원`이 아니면 `장재원`으로 교체
- Playwright 예시:
  ```javascript
  await p.getByLabel('작성자').fill('장재원');
  // 또는 getByPlaceholder/getByRole로 해당 입력 선택
  ```

> **⚠️ 날짜 필드 처리 원칙**: dash-post는 **데일리 보고** 도구다.
> 마감일/계약시작/계약종료는 프로젝트의 실제 계약 기간과 무관하게
> **반드시 오늘 날짜(TODAY)로 덮어쓴다**. 기존 값(예: 2026-06-30)을 유지하지 말 것.

**진행단계 처리 규칙**:
- 사용자가 "착수/개발/중간점검/납품/완료" 중 명시하면 해당 버튼 클릭
- 명시 없으면: 기존 값 유지

**진행률 처리 규칙**:
- 사용자가 "진행률 X%"를 명시하면 해당 값으로 슬라이더 업데이트
- 명시 없으면: 기존 값 유지 (슬라이더 변경 안 함)
- 신규 프로젝트 등록 시: 기본값 0% (당일 착수 기준)

**산출물 처리 규칙**:
- 사용자가 링크(URL)를 제공한 경우: 산출물 필드에 입력
- 링크가 없으면: 산출물 필드 변경하지 않음 (skip)

```javascript
// 진행률 슬라이더 업데이트 예시 (browser_evaluate)
const slider = document.querySelector('input[type="range"]');
const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
nativeSetter.call(slider, progressValue);  // 0~100 정수
slider.dispatchEvent(new Event('input', { bubbles: true }));
```

**메모 처리 규칙**:
- **오늘 작업 내역만 덮어씀** (overwrite) — 기존 메모에 누적하지 않음
- 각 날짜의 데일리 보고는 독립적: 이전 날짜 내용은 삭제하고 오늘 내용만 기록

```javascript
// 메모 overwrite 예시 — 누적 아님!
const today_entry = `${TODAY_DISPLAY} 작업 내역:\n${commits.map(c => `- ${c}`).join('\n')}`;
const newMemo = today_entry;  // 기존 메모 무시, 오늘 내용만
```

---

## Step 6: 저장 및 검증

```
1. "💾 저장" 버튼 클릭
2. alert 발생 시: 누락 필드 확인 후 채워서 재시도
3. 저장 후 프로젝트 카드에서 날짜가 TODAY로 반영됐는지 스냅샷으로 확인
```

---

## Step 7: 완료 보고

```
dash.vidraft.net 포스팅 완료
- 프로젝트: {프로젝트명}
- 탭: {탭명}
- 작성자: 장재원
- 마감일: {TODAY}
- 진행단계: {진행단계} (변경 없으면 "유지")
- 진행률: {진행률}%
- 산출물: {링크 또는 "없음"}
- 작업 내역: {커밋 수}건 기록
```

---

## 오류 패턴 및 대응

| 오류 | 원인 | 대응 |
|---|---|---|
| "계약종료 필수" alert | 계약종료 필드 비어있음 | TODAY 값으로 채우고 재저장 |
| "계약시작 필수" alert | 계약시작 필드 비어있음 | TODAY 값으로 채우고 재저장 |
| "마감일 필수" alert | 마감일 필드 비어있음 | TODAY 값으로 채우고 재저장 |
| SingletonLock 오류 | session-1/2/3 WSL2 버그 | session-4로 전환 |
| 로그인 페이지 | 세션 만료 | 사용자에게 로그인 여부 확인 요청 |
| 프로젝트 항목 없음 | 신규 프로젝트 | "＋ 새 프로젝트" 로 신규 생성 |

---

## 설정 파일 (선택)

프로젝트별 dash 매핑을 커스텀하려면 `~/.claude/dash-post-config.json` 생성:

```json
{
  "projects": {
    "HugwartsBanana": {
      "tab": "개발/운영 및 프로젝트",
      "name": "허그와트 바나나 (ginigen.ai)"
    },
    "NodeClaw": {
      "tab": "개발/운영 및 프로젝트",
      "name": "NodeClaw"
    }
  },
  "playwright_session": "session-4",
  "date_fields": ["deadline", "contractStart", "contractEnd"]
}
```

설정 파일이 없으면 Step 1 하드코딩 매핑 사용.
