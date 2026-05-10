---
name: youtuber
description: "Platform-specific workflow command — YouTube Shorts upload + SEO + CVR measurement. Executes ffmpeg, Playwright automation, hashtag strategy directly (no agent delegation). Consider wrapping Playwright steps in a dev-executor agent for cleaner isolation."
---

# YouTube Shorts — Upload & SEO Optimization Skill

## When to Use
- YouTube Shorts 영상 제작 + 업로드 자동화
- SEO 최적화 (제목, 설명, 해시태그, 메타데이터)
- TTPS S phase CVR 채널 검증 (신규 채널도 가능)
- Playwright로 YouTube Studio 자동화

---

## Phase 1 — BGM Mixing (ffmpeg — TTS + BGM 듀얼 트랙)

### 1A. TTS + BGM 믹싱 (권장 방식 — 2026-04-15 확립)

영상에 이미 TTS 오디오가 있는 경우, BGM을 별도 트랙으로 믹싱:

```bash
ffmpeg \
  -i input_video_with_tts.mp4 \
  -i background_music.mp3 \
  -filter_complex \
    "[0:a]volume=1.0[tts]; \
     [1:a]volume=0.15,afade=t=in:st=0:d=1.5,afade=t=out:st=FADEOUT_START:d=2.5[bgm]; \
     [tts][bgm]amix=inputs=2:duration=first,loudnorm=I=-14:LRA=11:TP=-1.5[aout]" \
  -map 0:v \
  -map "[aout]" \
  -c:v copy \
  -c:a aac -b:a 192k \
  -y output_with_bgm.mp4
```

**음량 기준표:**
| 파라미터 | 값 | 이유 |
|---------|-----|------|
| TTS volume | 1.0 (100%) | 나레이션 선명도 유지 |
| BGM volume | 0.15 (15%) | TTS 뒤에 깔리는 분위기용 (0.10~0.20) |
| loudnorm I=-14 | -14 LUFS | YouTube 권장 기준 (EBU R128) |
| FADEOUT_START | 영상길이 - 2.5 | 영상 종료 2.5초 전부터 fade |

**FADEOUT_START 계산:**
```bash
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 input.mp4)
FADEOUT=$(python3 -c "print(max(0, float('$DUR') - 2.5))")
```

### 1B. BGM 소싱 전략

| 방법 | 비용 | 자동화 | 추천 |
|------|------|--------|------|
| Pixabay 큐레이션 (5-10곡 로테이션) | 무료 | Playwright 배치 다운 | 지금 즉시 |
| Stable Audio API (Replicate) | $0.04/곡 | API 1줄 | 스케일 시 |
| YouTube Audio Library | 무료 | 수동 다운로드만 | 대안 |

**Pixabay API에는 음악 엔드포인트가 없음** — Playwright로 다운로드해야 함.
BGM 파일 위치: `assets/background-music.mp3` (또는 `assets/bgm/` 하위 로테이션)

### 1C. 단순 BGM 교체 (TTS 없는 영상)

```bash
ffmpeg -i input_video.mp4 -i background_music.mp3 \
  -c:v copy -map 0:v:0 -map 1:a:0 \
  -af "afade=t=in:st=0:d=1,afade=t=out:st=FADEOUT_START:d=1" \
  -shortest -y output.mp4
```

---

## Phase 2 — YouTube Shorts SEO 최적화

### 제목 (Title)
- **40자 이내** 권장 (모바일 truncation 기준, 핵심 키워드는 앞 20자 내)
- 핵심 키워드 앞에 배치
- 감정/희소성 트리거 포함
- 예: `AI가 그린 화투, 한 장씩 공개 | 300세트 한정`

### 설명 (Description)
- **첫 2줄이 핵심** (더보기 접힘 전 노출)
- 키워드 자연스럽게 포함 (키워드 스터핑 금지)
- 링크, CTA, 해시태그 배치

```
첫 2줄: 핵심 가치 제안 + CTA
---
상세 설명 (선택)
---
[해시태그 5개 — 맨 마지막]
```

### 해시태그 전략
| 규칙 | 이유 |
|------|------|
| **3-5개 최적** | 10개+ = hashtag stuffing → 도달 억제 |
| **#Shorts 첫 번째** | 알고리즘이 Shorts Feed 분류 |
| 나머지 4개: 주제 태그 | 검색 + 추천 알고리즘 |

**예시:**
```
#Shorts #화투 #KoreanArt #AI일러스트 #한정판
```

---

## Phase 3 — Show More 필드 (YouTube Studio)

| 필드 | 중요도 | 설정값 |
|------|--------|--------|
| **Language** | ★★★ 필수 | 한국어 / English (타겟 언어) |
| **Category** | ★★★ 필수 | Film & Animation / People & Blogs |
| Comments | 켜두기 | 참여 신호 = 알고리즘 부스트 |
| License | 기본값 | Standard YouTube License |
| Recording date | 생략 가능 | SEO에 무관 |
| Age restriction | 생략 | 해당 없음 시 |

**Language 설정이 중요한 이유:** YouTube가 해당 언어권 사용자에게 우선 배포.

---

## Phase 4 — Playwright 업로드 자동화 (실제 동작 확인 코드 — 2026-04-15)

### Session 관리
```
세션 우선순위: session-1 idle(about:blank) 확인 → session-2 → session-3 → session-4
browser_tabs(action="list") 로 about:blank 확인
세션 충돌 시: 다음 번호로 즉시 전환 (재시도 금지)
```

### 핵심: 업로드 다이얼로그는 contenteditable div (input 아님)
제목/설명 필드는 `<input>` 또는 `<textarea>`가 **아니라** `contenteditable="true"` div.
`browser_fill` 또는 `browser_type` 불가 → **반드시 `browser_evaluate` + `execCommand` 사용**.

### Step 1 — YouTube Studio 진입 + 만들기 클릭
```javascript
// 로그인 확인: studio.youtube.com 이동 후 URL이 accounts.google.com이면 로그인 필요
browser_navigate("https://studio.youtube.com")

// 만들기 버튼 — button 태그, snapshot에서 ref 확인 후 click
// evaluate로 클릭 (outline 버튼 계열):
browser_evaluate(`() => {
  const btn = document.querySelector('#create-icon')
    || document.querySelector('ytcp-button#create-icon')
    || document.querySelector('[aria-label="만들기"]')
    || document.querySelector('[aria-label="Create"]');
  if(btn) btn.click();
}`)
```

### Step 2 — 동영상 업로드 메뉴 + 파일 선택
```javascript
// snapshot에서 menuitem "동영상 업로드" ref 확인 → click
browser_click(ref="동영상 업로드 menuitem ref")

// 파일 선택 버튼 클릭 → file chooser 활성화
browser_click(ref="파일 선택 button ref")

// 파일 업로드 — 반드시 배열 형식
browser_file_upload(paths=["/절대경로/output.mp4"])

// 업로드 완료 대기 (3초)
browser_wait_for(time=3)
```

### Step 3 — 제목/설명 입력 (execCommand 방식 필수)
```javascript
// 제목 입력 — contenteditable div, aria-label로 선택
browser_evaluate(`() => {
  const el = document.querySelector('[aria-label="동영상을 설명하는 제목 추가(채널을 멘션하려면 @ 입력)"]');
  if(el) {
    el.focus();
    // 기존 내용 지우기
    const sel = window.getSelection();
    sel.selectAllChildren(el);
    sel.deleteFromDocument();
    // 텍스트 입력
    document.execCommand('insertText', false, '제목 텍스트');
  }
}`)

// 설명 입력 — 동일 패턴
browser_evaluate(`() => {
  const el = document.querySelector('[aria-label="시청자에게 동영상에 대해 설명해 주세요(채널을 멘션하려면 @ 입력)"]');
  if(el) {
    el.focus();
    const sel = window.getSelection();
    sel.selectAllChildren(el);
    sel.deleteFromDocument();
    document.execCommand('insertText', false, \`설명 첫줄\n두번째줄\n\n#Shorts #태그1 #태그2\`);
  }
}`)
```

### Step 4 — 아동용 여부 (필수 — 미선택 시 다음 비활성)
```javascript
// "아니요, 아동용이 아닙니다" 선택
browser_evaluate(`() => {
  const radios = document.querySelectorAll('tp-yt-paper-radio-button');
  const notKids = Array.from(radios).find(r =>
    r.getAttribute('name') === 'VIDEO_MADE_FOR_KIDS_NOT_MFK'
    || r.textContent?.includes('아니요')
  );
  if(notKids) notKids.click();
}`)
```

### Step 5 — 다음 → 다음 → 공개 → 게시
```javascript
// 다음 버튼 (세부정보 → 동영상 요소)
browser_evaluate(`() => {
  const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent?.trim() === '다음');
  if(btn && !btn.disabled) btn.click();
}`)
// 대기 1초 후 동영상 요소 → 다시 다음 클릭 (동일 코드)
// 검토 단계 → 다시 다음 클릭

// 공개 상태 단계: "공개" 라디오 선택
browser_evaluate(`() => {
  const radios = document.querySelectorAll('tp-yt-paper-radio-button');
  const pub = Array.from(radios).find(r =>
    r.textContent?.includes('공개')
    && !r.textContent?.includes('비공개')
    && !r.textContent?.includes('일부')
  );
  if(pub) pub.click();
}`)

// 게시 버튼
browser_evaluate(`() => {
  const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent?.trim() === '게시');
  if(btn && !btn.disabled) btn.click();
}`)
// 완료: "게시된 동영상" 팝업에서 동영상 링크 확인
```

### Step 6 — 업로드 후 SEO 추가 설정 (카테고리 + 언어)
업로드 다이얼로그에서는 카테고리/언어 설정 불가 → 게시 후 편집 페이지에서 설정.

```javascript
// 편집 페이지 직접 이동 (videoId는 게시 완료 팝업 링크에서 추출)
browser_navigate("https://studio.youtube.com/video/{videoId}/edit")
browser_wait_for(time=3)

// "자세히 보기" 버튼 클릭 (고급 설정 펼치기)
browser_evaluate(`() => {
  const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent?.trim() === '자세히 보기');
  if(btn) btn.click();
}`)
browser_wait_for(time=2)

// 동영상 언어 선택 (ytcp-form-select → trigger 클릭 → tp-yt-paper-item 선택)
browser_evaluate(`() => {
  const selects = document.querySelectorAll('ytcp-form-select');
  const langSel = Array.from(selects).find(s => s.textContent?.includes('동영상 언어'));
  if(langSel) {
    const trigger = langSel.querySelector('[role="button"], button, .trigger');
    if(trigger) trigger.click();
  }
}`)
browser_wait_for(time=1)
browser_evaluate(`() => {
  const kr = Array.from(document.querySelectorAll('tp-yt-paper-item'))
    .find(el => el.textContent?.trim() === '한국어');
  if(kr) kr.click();
}`)

// 카테고리 선택 (#category → trigger 클릭 → tp-yt-paper-item)
browser_evaluate(`() => {
  const cat = document.querySelector('#category');
  if(cat) {
    const trigger = cat.querySelector('[role="button"], button, .trigger');
    if(trigger) trigger.click();
  }
}`)
browser_wait_for(time=1)
browser_evaluate(`() => {
  const scitech = Array.from(document.querySelectorAll('tp-yt-paper-item'))
    .find(el => el.textContent?.includes('과학') || el.textContent?.includes('Science'));
  if(scitech) scitech.click();
}`)

// 저장
browser_evaluate(`() => {
  const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent?.trim() === '저장');
  if(btn && !btn.disabled) btn.click();
}`)
```

### 주의사항
- `browser_file_upload` paths: **배열** 형식 `["path"]` (string 오류)
- 제목/설명: `browser_fill` / `browser_type` **불가** — contenteditable div → `execCommand` 사용
- 아동용 미선택 시 "다음" 버튼 비활성화됨 — 반드시 선택 필요
- 카테고리/언어는 업로드 다이얼로그가 아닌 **편집 페이지**에서 설정
- `tp-yt-paper-item` 드롭다운은 클릭 후 1초 대기 필요 (렌더링 지연)
- 진행 중 탭 닫으면 업로드 취소 → `browser_tabs`로 확인
- 로그인 안 된 경우 accounts.google.com 리다이렉트 → 수동 로그인 필요

---

## Phase 4.5 — Traffic Link + Pinned Comment (게시 후 즉시)

### 트래픽 목적지 우선순위 (채널 단계별)
| 채널 단계 | 1순위 | 2순위 | 제외 |
|---------|-------|-------|------|
| <100 구독 | YouTube 구독 CTA | 기술 증명 링크 (HF/GitHub) | 외부 제품 링크 |
| 100-1K | 구독 + 기술 링크 | 관련 롱폼 영상 링크 | 무관한 제품 |
| 1K+ | 제품/서비스 링크 | 기술 링크 | — |

**핵심: Shorts 설명란 클릭률은 극도로 낮음** ("...더보기" 눌러야 보임).
고정 댓글이 더 가시적 → 핵심 링크는 고정 댓글에 배치.

### 설명란 템플릿 (글로벌/영어)
```
[1줄 hook — 영상 핵심 주장 반복]

[모델/제품명] — [핵심 기술 1줄 설명]
[벤치마크 수치 | 비교 대상 수치]
Hardware: [GPU] / [소요 시간]

Model card: [HuggingFace 또는 GitHub 링크]
Built with [플랫폼명].

Subscribe — next: [다음 영상 예고].

#Shorts #[주제태그1] #[주제태그2] #[주제태그3] #[주제태그4]
```

### 고정 댓글 템플릿
```
[시청자 궁금증 자극 질문]? Full details:
[증명 링크 — HuggingFace/GitHub/논문]

Next video: [예고]. Subscribe so you don't miss it.
```

### Playwright 고정 댓글 자동화
```javascript
// Step 1: 영상 페이지 이동 (studio 아님)
browser_navigate("https://www.youtube.com/shorts/{VIDEO_ID}")

// Step 2: 댓글 패널 열기 (2초 대기 후)
browser_evaluate(`() => {
  return new Promise(resolve => {
    setTimeout(() => {
      const btn = Array.from(document.querySelectorAll('button'))
        .find(b => b.getAttribute('aria-label')?.includes('댓글'));
      if(btn) { btn.click(); resolve('opened'); }
    }, 2000);
  });
}`)

// Step 3: "댓글 추가..." 클릭 → 입력 → 제출
browser_evaluate(`() => {
  return new Promise(resolve => {
    const ph = document.querySelector('#simplebox-placeholder');
    if(ph) ph.click();
    setTimeout(() => {
      const input = document.querySelectorAll('[contenteditable="true"]');
      const el = input[input.length - 1];
      el.focus();
      document.execCommand('insertText', false, 'COMMENT_TEXT_HERE');
      setTimeout(() => {
        const submit = Array.from(document.querySelectorAll('button'))
          .find(b => b.textContent?.trim() === '댓글' && !b.disabled);
        if(submit) submit.click();
        resolve('posted');
      }, 500);
    }, 1500);
  });
}`)

// Step 4: 고정 — 댓글 3-dot 메뉴 → "고정" → 확인
browser_evaluate(`() => {
  return new Promise(resolve => {
    setTimeout(() => {
      const panel = document.querySelector('ytd-engagement-panel-section-list-renderer');
      const comment = panel?.querySelector('ytd-comment-thread-renderer');
      const menu = comment?.querySelector('#action-menu button');
      if(menu) menu.click();
      setTimeout(() => {
        const pin = Array.from(document.querySelectorAll('tp-yt-paper-item'))
          .find(m => m.textContent?.includes('고정'));
        if(pin) pin.click();
        setTimeout(() => {
          const confirm = Array.from(document.querySelectorAll('button'))
            .find(b => b.textContent?.trim() === '고정');
          if(confirm) confirm.click();
          resolve('pinned');
        }, 1000);
      }, 1000);
    }, 2000);
  });
}`)
```

---

## Phase 5 — CVR 측정 (TTPS S Phase)

### Shorts 알고리즘 특성
- **구독자 기반 아닌 콘텐츠 기반 배포** → 신규 채널도 검증 가능
- 첫 배포: 소규모 샘플 → CTR/참여율 기준 확장 여부 결정
- 기존 구독자 채널은 초기 노출 우선 제공 (속도 차이, 방향성 동일)

### CVR 측정 기준 (72시간 기준)

| 지표 | 기준 | 판단 |
|------|------|------|
| **Loop rate** | **1.5x+ 재생 → 알고리즘 "extraordinary value"** | 가장 강력한 신호 |
| Swipe-away rate | 낮을수록 좋음 (첫 1초가 결정) | 나쁘면 배포 중단 |
| 조회수 | 500+ (신규) / 2000+ (기존 채널) | 배포 시작 확인 |
| **저장율** | **5%+ → S phase 통과** | 구매 의향 프록시 |
| 좋아요율 | 3%+ | 참여 신호 |
| 댓글 | 키워드 확인 | "어디서 사요?" = WTP 신호 |
| 평균 시청 완료율 | 80%+ (Shorts 목표) | 재배포 결정 기준 |

### TTPS S → T 피드백 루프
```
저장율 5%+ → 텀블벅 링크 설명란 추가 → CVR 수집
저장율 5% 미만 → 제목/해시태그 수정 or T(타겟) 재검토
댓글에서 "어디서 사요?" 등장 → WTP 확인 → 즉시 텀블벅 오픈
```

---

## 체크리스트

### 업로드 전
- [ ] ffprobe로 오디오 트랙 확인
- [ ] 영상 길이 60초 이하 (Shorts 조건)
- [ ] 해상도 9:16 (1080x1920)

### 업로드 시
- [ ] 제목 30자 이내, 키워드 앞 배치
- [ ] 해시태그 5개, #Shorts 첫 번째
- [ ] 아동용: "아니요" 선택 (필수 — 미선택 시 다음 버튼 비활성)
- [ ] 공개 상태: 공개 선택 후 게시
- [ ] 게시 후 편집 페이지에서 Language / Category 설정

### 게시 직후 (Phase 4.5)
- [ ] 설명란에 기술 증명 링크 (HuggingFace/GitHub) 포함 확인
- [ ] 설명란 마지막에 "Subscribe — next: [예고]" CTA
- [ ] 고정 댓글 작성 + 고정 (Playwright 자동화 가능)
- [ ] BGM 적용 여부 확인 (TTS 100% + BGM 15% + loudnorm -14 LUFS)

### 업로드 후 (72시간)
- [ ] "Stayed to watch" 비율 확인 (YouTube Studio → Content → Shorts)
- [ ] 조회수 확인
- [ ] 저장율 5%+ 여부
- [ ] 댓글 키워드 모니터링
- [ ] S→T 피드백 신호 추출
