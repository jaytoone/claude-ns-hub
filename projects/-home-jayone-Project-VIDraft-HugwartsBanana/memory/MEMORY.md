# MEMORY.md - HugwartsBanana 프로젝트

## Feedback
- [playwright-before-commit](feedback_playwright_before_commit.md) — 구현 완료 후 Playwright 검수 먼저, 커밋 여부 질문은 그 다음

## 현재 상태 (2026-04-27) — v1.23.411
- **최신 커밋**: v1.23.411 — 자동화 스튜디오 패널/텍스트 크기 확대 (w-44→w-52, w-52→w-60)
- **진행 중**: 크레딧 환불 시스템 버그 수정 (refund_credits RPC + processRefund + generate-nano-banana-pro + 버튼 debounce)
- **고객 케이스**: sunkhs09@gmail.com — 4/15 FAL API 오류로 6회 실패, 미환불 1회 → +6 바나나 지급 완료

## 현재 상태 (2026-04-24) — v1.23.408
- **최신 커밋**: v1.23.408 — Discord AccountSettings 연동 버튼 + 결제 후 메타데이터 자동 동기화
- **v1.23.407**: WTP/고객인터뷰 모달 닫기 버그 수정 (PSMSurveyModal + LowCreditAlertModal backdrop onClick 패턴)
- **v1.23.406**: 스토리보드 크레딧 환불 누락 수정 (imageUrls 빈 배열 guard + externalImages 빈 배열 guard)
- **다음 pending**: @pro Discord Linked Roles 역할 설정 (Discord 서버 어드민 UI)

## 현재 상태 (2026-04-20) — Discord 커뮤니티 + Linked Roles
- **Discord 서버**: Hugwarts Banana (guild_id=1495635630506508318, invite=discord.gg/Z7wG5skk)
- **채널 10개**: INFO/SHOWCASE/COMMUNITY 카테고리 (welcome, announcements, image/video/automation-creations, general, feedback, help)
- **Discord App** (v1.23.401 커밋): Client ID 1495673244802613359, Linked Roles URL 설정, Bot token 생성
- **5개 metadata 등록**: has_paid(bool)/purchased_credits/credits_spent/account_age_days/country_code
- **Vercel env**: DISCORD_CLIENT_ID/SECRET/BOT_TOKEN/METADATA_SERVICE_KEY 4개 production 등록 완료
- **결제 전략**: 현재 SevenZero(KR)+PayPal 유지, 향후 Paddle 전환 고려 (MoR, 글로벌 VAT 자동 처리)
- **다음**: @pro 역할 Linked Roles 설정 → UI Link Discord 버튼 → 결제 webhook 후킹
- [live-decision 2026-04-21]: Discord 아이콘 적극 활용 — MessageCircle(lucide 일반) → 공식 Discord 브랜드 SVG 아이콘 + FAQ 페이지 Discord 섹션 추가, 사용자 지시 "utilize the discord icon more actively on the pages where linking to discord"
- [**STRATEGIC PIVOT** 2026-04-21]: Discord의 primary purpose = **대화 가능한 공간 + HB 문화 형성 + 정보/서비스 교환** (사용자 원문: "talkable place, making hb cultures/exchange service or other related informations"). 모네타이제이션/리텐션은 **derivative effect** (파생 효과), primary 아님. 이전 분석(identity-status-conversion loop)은 부차적 재프레이밍 필요. Strategy 초점: conversational culture seeding → emergent exchange → derivative retention/monetization
- [live-decision 2026-04-21]: Discord 활성화 실행 - "engage people to link to discord + notice them to use it" 지시. 원칙: notice-not-coerce (배너는 1회성 dismissable, 강제 아님), doorway-not-turnstile (링크 진입 독려 OK, 가입 강요 NO). v1: 홈피드 상단 Discord 배너 (logged-in + not-linked 유저만, +10 바나나 유인, localStorage dismiss 영구)

## 현재 상태 (2026-03-11)
- **최신 버전**: v1.23.249 (커밋됨) — 자동화 스튜디오 전 스텝 w-44 좌측 사이드바 패턴 통일
- **사이드바 레이아웃**: Step1 화면비율/Step2 목표길이+예시주제/Step3 음성선택/Step4 이미지모델+품질/Step6 BGM모드+볼륨 → 각 스텝 좌측 w-44 amber 선택 사이드바
- **Step3Voice button 중첩 버그**: 음성선택 외부 `<button>` → `<div>` 교체 (HTML 유효성)
- **Playwright 세션**: session-1/2/3 SingletonLock (WSL2 버그), session-4 사용 중
- **미커밋 파일**: problem.txt, .swarm/hnsw.index (인덱스 파일, 커밋 불필요)

## 현재 상태 (2026-03-10)
- **자동 정지 오탐 버그 수정** (DB 직접 수정, 미커밋):
  - `detect_and_flag_abuse`: `SELECT INTO` 변수 순서 스왑 버그 수정 (자동환불 스킵 로직 복구)
  - `auto_refund_audio_video_on_failure`: `prevent_double_refund=FALSE` 시 abuse 플래그 제거 → RETURN NEW (Edge Function + DB 트리거 이중 경로 충돌 오탐 방지)
  - 오탐 정지된 3명 복구: hair9555@gmail.com, a01086844868@gmail.com, whodnjsdl2@gmail.com
- **최신 버전**: v1.23.237 (피드 숨기기 기능)
- **DashboardPage.tsx**: CreditBoostBanner + ReferralModal 제거 (uncommitted)

## 현재 상태 (2026-03-09)
- **최신 버전**: v1.23.221 (커밋 예정) — 프로모 카드 디자인 개선 + design-preview 페이지 추가
- **v1.23.221**: 프로모 카드 border 제거 → shadow + 흰 배경 (RoulettePromoCard, ExpiryNoticeCard, DailyStreakCalendar, CommunityFeed isPromo wrapper)
- **v1.23.220**: 피드 카드 개선 (border→shadow, rounded-2xl, hover lift, accent bar 3px)
- **design-preview 페이지**: `src/app/[lang]/design-preview/page.tsx` — `localhost:3000/ko/design-preview`
- **최신 버전 이전**: v1.23.207 (채팅 응답속도 개선)
- **채팅 라우팅 정확도 개선** (v1.23.206): AI tool call 경로에서 keyword override 제거 → LLM 판단 신뢰
- **채팅 응답속도 개선** (v1.23.207):
  - SSE 스트리밍: `conversationType=chat` 시 `streamChat()` → 첫 글자 ~200ms (기존 3-5s 전체 대기)
  - routeToService/consultExperts: serviceRedirect 있으면 스킵 (불필요한 추가 LLM 호출 제거)
  - logRecommendation/recordServiceUsage: fire-and-forget으로 전환
  - chatStore.ts: SSE 파싱 + `updateMessageContent` 액션 추가
- **ErrorBoundary 수정**: `render()`가 `hasError=true`일 때 `null` 반환하도록 수정 → global-error.js 전파 방지
  - 근본 원인: `return this.props.children` 무조건 반환 → 자식 재throw → 상위 전파 → "문제가 발생했습니다" 페이지
  - 관리자 대시보드 접근 에러 원인 (현재 production에서도 정상이나 방어적 수정)
- **Playwright MCP 버전 고정**: `@0.0.48` (`~/.claude/plugins/.../playwright/.mcp.json`) — v0.0.68 WSL2 SingletonLock 버그 회피
  - 원인: v1.59 alpha에서 Linux Chrome 싱글톤 에러(`"Invalid URL"`) 처리 누락
  - Claude Code 재시작 시 적용 / 플러그인 업데이트 후 재고정 필요

## v1.23.203~204 Directors + chat/message 수정 (커밋됨, Playwright 검수 완료)
- **v1.23.203**: `DirectorsGenerator.tsx` — `frameNumber: regenerateFrame` → `frameIndex: regenerateFrame - 1` (1-indexed→0-indexed 변환)
  - 근본 원인: UI select option `value={i+1}` (1-based), 백엔드 `frameIndex` (0-based) 불일치
  - directors-generate Edge Function이 항상 "frameIndex가 필요합니다" 에러 반환하던 버그 수정
- **v1.23.204(=202)**: `chat/message/route.ts` — dead code 제거 (executeGeneration, unused imports 등, -394 lines)
- **v1.23.201**: `directors-generate` Edge Function `max_tokens: 2048→4096` — JSON 절단(7984 chars) 수정

## 이전 상태 (2026-03-06)
- **최신 버전**: v1.23.199 (커밋됨, Vercel production 배포 완료 www.ginigen.ai)
- **훅 상태**: PreToolUse, PostToolUse 모두 비활성화 (빈 배열, 사용자 요청)

## v1.23.193 Automation Studio UX Fixes (커밋됨, Playwright 검수 완료)
- **Fix 1**: `loadUserProjects` — 빈 프로젝트(Step1, scriptCuts/scriptText 없음) 자동 삭제
- **Fix 2**: Step4/Step5 "저장하고 다음 단계" 버튼 — `completedCount < images/videos.length` 조건 강화
- **Fix 3**: Step5Videos useState 초기화 — 항상 `imagesData` 기준으로 초기화 후 `videosData` 오버레이 → 복귀 시 전체 컷 표시
- **일관성 체이닝 토글**: Step4Images에 `consistencyChaining` toggle (OFF=회색/ON=파란색), ON시 이전 컷 imageUrl을 imageInput으로 전달 (1→2→3...)
- **문서**: `docs/AUTOMATION-STUDIO-UX-FIXES.md` 생성, `docs/DOC_INDEX.md` 업데이트

## v1.23.186 피드 확대 클릭 + 슬라이드 프리로딩 (커밋+배포 완료)
- **확대 버튼**: isVideoType/isCardtoonVideoCard/isShortformVideoCard/isShorttoonVideoCard/cardtoon이미지/storyboard/shorttoon/shortform/videoedit 래퍼에 `absolute top-2 left-2 z-20/30 Maximize2` 버튼 추가 → `setSelectedDetailItem(item)`
- **상세 모달 업데이트**: series_images_paths/media_urls 타입에 CardtoonImageViewer/StoryboardImageViewer/ShorttoonImageViewer/ShortformImageViewer 렌더링
- **슬라이드 프리로딩**: 4개 뷰어(Cardtoon/Storyboard/Shorttoon/Shortform)에 N±1 hidden img 프리로딩 추가

## v1.23.185 홈피드 비디오 저데이터 최적화 (커밋+배포 완료)
- `VideoPlayer.tsx`: `poster?: string` prop 추가 + `preload` 기본값 `'none'`
- `CommunityFeed.tsx`: `preload="none"` + `poster={item.original_image_path}` (피드+프로모)

## v1.23.165 복수 그룹 가입 + 프로모 크레딧 모달 (커밋됨)
- DB: `user_group_memberships(user_id, group_id PK)` 테이블 생성 + 기존 49건 마이그레이션
- DB: `join_group_via_code(p_user_id, p_referral_code)` 함수 - 그룹별 ALREADY_IN_GROUP 체크 + referred_by 첫 회만 설정
- route.ts: `referred_by` 단일 체크 → `user_group_memberships` 그룹별 체크 + `join_group_via_code` 호출
- `CreditChargeSuccessModal`: `amountPaid` optional(기본0), 0이면 결제금액 행 숨김
- `page.tsx`: 프로모 성공 + 로그인 → `CreditChargeSuccessModal` 표시 (`showPromoCreditModal` state)
- `PromoCodeInput`: `ALREADY_IN_GROUP` / `ALREADY_REFERRED` → `already_used` 상태 처리

## v1.23.163 group_referral 코드 invalid 버그 수정 (커밋됨)
- route.ts: `promoData.error` early return이 group_referral_codes 체크 전에 실행되던 버그
- `INVALID_CODE` / `CODE_NOT_FOUND` 에러는 early return 제외, group 체크 통과 후 처리
- YGI4X5, KSRQFO 등 group_referral 코드가 "유효하지 않은 코드"로 표시되던 문제 해결

## v1.23.157 채팅 버튼 모바일 최적화 (커밋됨, Playwright 검수 완료)
- GlobalFloatingButtons.tsx: `right-16 md:right-20` → `right-6 sm:right-24` (History 버튼과 열 일치)
- ChatModal.tsx: `isMobile` state 추가 (window.innerWidth < 640), 모바일 바텀 시트 모드
  - 모바일: `inset-x-0 bottom-0 rounded-t-2xl`, slide-up 애니메이션, `max-h-88vh`
  - 데스크톱: 기존 `bottom-6 right-6 sm:right-24 rounded-2xl` 유지
  - resize handle: `{!isMobile && ...}` 조건부, 모바일 드래그 힌트 바 추가
- useResizable.ts: SSR 가드 추가 (`typeof window !== 'undefined'`) - `getSavedSize` + `saveSize` 양쪽
  - 근본 원인: Next.js 서버 컴포넌트에서 localStorage 접근 시도 → `ReferenceError: localStorage is not defined`

## v1.23.156 GlobalFloatingButtons 전역 채팅 버튼 (커밋됨)
- GlobalFloatingButtons.tsx 신규: `usePathname` + `useAuth` 기반, 관리자 페이지(`/admin`) 자동 제외
- layout.tsx: `<GlobalFloatingButtons />` 추가 (SurveyManager 다음, 전역 렌더링)
- CommunityFeed.tsx: 중복 플로팅 버튼 JSX 제거 (ChatBottomBar + scrollTop)

## v1.23.155 이중 환불 버그 수정 (커밋 + Supabase 배포 완료)
- **이중 환불 현황**: 131명 영향, 33,452 크레딧 피해 (2025-09 ~ 2026-03)
- **근본 원인**: 프론트 수동 환불(related_id=NULL) + DB Trigger 자동 환불(related_id=transformationId) → prevent_double_refund가 다른 ID 비교 → 둘 다 통과
- **fix 1**: generate-video-multi catch 블록에 creditCharged 플래그 + 자동 환불 추가 (FAL API 제출 실패 시 미환불 버그)
- **fix 2**: refund-credit에 generationId optional 파라미터 추가 (실제 ID 있으면 사용, 없으면 randomUUID)
- **fix 3**: CompleteVideoGenerator에 currentTransformationId 변수 추가 → catch 블록에서 refund-credit에 실제 ID 전달
- **배포**: supabase functions deploy refund-credit + generate-video-multi (project: rteypbamkblsxhgbqwbf)

## stop hook 주요 수정 이력
- **서버 감지**: lsof → ss+python3 (WSL2에서 lsof -sTCP:LISTEN이 빈 결과 반환하는 버그)
- **로그인 판단**: snapshot 자동 분석 → 사용자에게 "Playwright 브라우저에 현재 로그인이 되어 있나요?" 먼저 질문
- **bash 이스케이프**: python3 -c "..." 안의 따옴표는 반드시 \" 로 이스케이프 (미이스케이프 시 SyntaxError)

## 채팅 라우팅 검증 완료 (chaos test 42/42)
- scripts/chaos-routing-test.mjs: 자동화 스튜디오 6개 시나리오 추가 (36→42)
- 전체 통과율: 100% (42/42) - 이미지/비디오/음악/오디오/자동화/콘텐츠 모든 카테고리
- service_redirect 응답 검증: svc_automation→automation-studio, prompt_hint 포함

## v1.23.154 채팅 라우팅 3개 버그 수정 (커밋됨)
- KEYWORD_SERVICE_MAP: 자동화 키워드 11개 추가 (자동화하고/파이프라인 등)
- serviceTabMap.ts: svc_automation → automation-studio 매핑 추가
- route.ts: context.selected_service 레거시 직접생성 경로 → service_redirect로 교체
- AutomationStudio + Step2Script: useChatPromptHint 추가 (초기 주제 자동 주입)

## v1.23.153 채팅 라우팅 100% 수정 (커밋됨)
- route.ts: keyword override(Fix1) + keyword fallback(Fix2)
- useChatPromptHint hook 신규: 5개 서비스 컴포넌트에 적용 (image/video/music/shortform/simplevideo)

## v1.23.152 Step1 AI 스타일 패널 디자인 통일 (커밋됨)
- AutomationStudio.tsx: 참조이미지 패널 purple/blue → yellow/orange 계열로 변경

## v1.23.151 자동화 스튜디오 이모지 제거
- Step5Videos.tsx:414,421 - `🎯`, `📌` → 텍스트 (Kling/MiniMax 모델 설명)
- Step6Render.tsx:1033 - `🎨` → 텍스트 (자막 스타일 프리셋 레이블)

## v1.23.150 AI 스타일 분석 Step4 → Step1 이동
- AutomationStudio Step1Settings: 참조이미지 업로드 + AI분석 UI 추가 (보라색 카드)
- types.ts: AutomationProject + UpdateProjectInput에 `referenceStylePrompt?: string` 추가
- AutomationDB.ts: settings JSONB에 referenceStylePrompt 병합 저장 (별도 DB 컬럼 불필요)
- Step4Images.tsx: AI분석 섹션 제거 → project.referenceStylePrompt + stylePreset prompt 합쳐서 prefix로 초기화
- 프롬프트 순서: `referenceStylePrompt, stylePreset.prompt, base`

## v1.23.143 자동화 TTS 피드 숨김 수정 (커밋 + 배포 + E2E 검증 완료)
- Step3Voice.tsx: audio-tts invoke에 `isPrivate: true` 추가 (main loop + handleRegenerateCut 2곳)
- 근본 원인: isPrivate 기본값 false → show_in_feed=true → 자동화 TTS 나레이션이 홈피드 노출
- BGM(Step6Render)은 이미 `isPrivate: true` 있었음
- E2E 검증: www.ginigen.ai에서 TTS 생성 → DB id=88247fb2: show_in_feed=f, is_private=t 확인
- stop-playwright-detect.sh v3.2.0: show_in_feed/is_private/isPrivate 변경 시 DB 검증 스텝 자동 추가

## v1.23.142 Step6Render BGM state lifting (커밋됨)
- BgmMode type: 로컬 정의 제거 → useAutomationPipeline에서 import
- BGM state (bgmMode/bgmUrl/bgmVolume/bgmTracks) → props로 이동 (useAutomationPipeline 관리)

## v1.23.141 채팅 → 서비스 페이지 이동 (커밋됨)
- chat/message/route.ts: 최종 응답 객체에 `service_redirect: serviceRedirect` 추가
- ChatMessage.tsx: ServiceRedirectCard import + 렌더링 추가 (`message.service_redirect` 조건부)
- ServiceRedirectCard.tsx: 신규 (이전 세션) - tabChange CustomEvent 발행, promptHint localStorage 5분 저장
- src/lib/chat/serviceTabMap.ts: 신규 (이전 세션) - 17개 서비스 svc_* → tabId 매핑
- stop-playwright-detect.sh: HEAD~1..HEAD fallback 추가 (커밋 후에도 훅 발동하도록 수정)

## v1.23.136 프로젝트 이름 식별 문제 수정
- handleCreateProject: 기본이름 `프로젝트 MM/DD HH:mm` (날짜+시간, 분 단위 고유)
- saveScript: 스크립트 주제 첫 25자로 프로젝트 이름 자동 업데이트 (기본이름 패턴일 때만)
- 프로젝트 목록: 스크립트 첫줄 40자 부제목 + MM/DD HH:MM 시간 표시

## v1.23.135 BGM 합성 수정 + AI 2트랙 선택 UI
- ffmpeg_worker.py: amix `normalize=0` 추가, `-shortest` 제거, ffprobe 오디오 스트림 확인
- ffmpeg_worker.py: `AutomationMergeResponse.bgm_applied: bool = False` 필드 추가
- Step6Render.tsx: `bgmTracks` state + AI 생성 트랙 선택 UI (bgmTracks.length > 1 조건)
- Step6Render.tsx: handleRender 응답 `data.bgm_applied === false` 시 경고 표시

## v1.23.132~134 BGM 기능 (커밋됨)
- v1.23.132: Railway ffmpeg_worker.py BGM mixing (amix 필터, bgm_url/bgm_volume 파라미터)
- v1.23.133: Step6Render.tsx handleGenerateBgm 버그 2개 수정
- v1.23.134: bgmVolume<1이면 20으로 보정 + bgmUrl/bgmVolume DB 저장 완성
- AI 음악 생성: FAL.ai MiniMax Music v2 (`fal-ai/minimax-music/v2`)
- Edge Function 체인: audio-music-generate → audio-music-submit → audio-music-status

## v1.23.126 analyst role + 신규 유저 탭 분리 (커밋됨)
- analyst role 신규 추가: types/index.ts, verifyAdminOrAnalyst (apiAuth.ts)
- DB migration: users_role_check ('user','admin','analyst','pro')

## v1.23.113 피드 카테고리 재설계 (커밋됨)
- 드롭다운 3개 → flat 탭 6개 (전체|이미지|영상|스토리|웹툰·카드|음악·음성)

## DB 결과물 URL 컬럼 매핑
- audio_video_generations: `output_urls` JSONB[0] (music/tts/voice_clone), `video_url` (lipsync)
- storyboard_generations: `merged_video_url`, `frames[0].image_url`
- simplevideo_generations: `video_url` / videoedit_generations: `output_video_url`
- transformations: `series_images_paths[0]` (cardnews/cardtoon/shortform/shorttoon)

## DB 주요 패턴
- user_feedback CHECK: 'sean_ellis_test','exit_survey','feature_request','bug_report','general','onboarding_survey'
- users.role CHECK: 'user','admin','analyst','pro'
- automation_projects: show_in_feed, is_private, script_cuts JSONB (audioUrl/audioDuration per cut)

## 자동화 파이프라인 핵심 아키텍처
- Step3Voice → `audio-tts` Edge Function (per-cut 순차 호출, 컷당 2 banana)
- Step4Images → `generate-nano-banana-pro` (컷당 3~5 banana)
- Step5Videos → `generate-video-multi` (컷당 10~16 banana)
- Step6Render → Railway `/automation-merge` (무료, BGM mixing 지원)

## 아키텍처 핵심
- SERVICE_MAP: src/app/api/chat/message/route.ts
- DashboardPage: src/app/[lang]/page.tsx 내부
- PMF API: NEXT_PUBLIC_APP_URL || NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'
- Fireworks AI: gpt-oss-120b 불안정 → llama-v3p3-70b-instruct + response_format json_object

# currentDate
Today's date is 2026-03-03.
