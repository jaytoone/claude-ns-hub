---
category: Vertical
current: ~0 new payers/week (37 total as of 2026-04-08)
deadline: '2026-05-12'
layer: 2
log:
- date: '2026-05-08'
  text: 'be6627b v1.23.396 20260416 - fix 립싱크 타임아웃 에러 메시지 개선 (일시적 혼잡 안내 + 13초 이하 짧은
    오디오 재시도 유도) - LipsyncVideoGenerator.tsx + lipsync-worker timeout/FAL/general 에러
    메시지에 팁 추가 v1.23.395 20260416 - fix 로딩스피너 마법사 바나나 복원 + shimmer bar 유지 (sparkle/bounce
    dots 제거 → 가로 shimmer bar 대체, pg_cron job 4/10 에러 수정: current_setting→직접키, extensions.http→net.http_post)
    v1.23.394 20260416 - fix 관리자 탭 중복 해소 + 로딩스피너 모던화 (adminTabs 13개→1개 통합, 12개 개별
    case 제거 → UnifiedAdminDashboard 일원화, BananaLoadingAnimation 리디자인: wizard hat+sparkle
    → 미니멀 glow pulse+shimmer bar) v1.23.388 20260409 1522 - fix WTP 설문 수집 3종 개선 (Rejection
    Interview 자동 표시 depleted 기본값 true, PSM 통화 필드 추가 lang→currency KRW/USD, psm-pricing
    API 통화별 유효성 검사 KRW>=100/USD>=0.5, psm-analysis 이상값 필터 + currency 쿼리 파람) v1.23.387
    20260409 1238 - fix creditsAgg PostgREST 집계 비활성화 → get_total_credits_consumed()
    RPC 교체 (228235 크레딧 정상 반환 확인) v1.23.386 20260409 1218 - perf 관리자 대시보드 로딩 속도 개선
    (phase=1 fast KPI <500ms + 2-phase 순차 로딩, creditsAgg DB 집계로 전환, 국가 쿼리 100k→5k
    제한, DB 인덱스 3개 추가) v1.23.385 20260409 1150 - fix 홈피드 이벤트 카드 정리 (promo-expiry-notice
    제거 → 당첨자발표 이미지 완전 숨김, announcement_video 재활성화 → 쇼츠 가이드 영상 복구) v1.23.384 20260409
    1137 - fix 마법사 바나나 로딩 + 당첨자 공지 카드 제거 (BananaLoadingAnimation 통합 SVG 좌표계 hat+body,
    promos.config promo-festa 항목 삭제) v1.23.383 20260409 1034 - feat BananaLoadingAnimation
    리디자인 (orbital rings → 귀여운 바나나 마스코트 SVG float+wiggle + 3-dot amber bounce, 21개
    컴포넌트 자동 적용) v1.23.382 20260409 1003 - feat 홈피드 영상 카드 9:16 portrait 전환 (aspect-video
    → aspect-[9/16], md:col-span-2 제거 — 이미지 카드와 동일 포맷) v1.23.381 20260408 2335 - feat
    영상 카드 hover 자동재생 (VideoPlayer hoverPlay prop — mouseenter 무음 loop 재생, mouseleave
    pause+reset, controls 숨김) v1.23.380 20260408 2328 - fix 홈피드 오버레이 중복 제거 (좋아요/댓글
    버튼 이중 렌더 → 통합 오버레이로 단일화, 비디오 Maximize2 z-10 중복 overlay 제거) v1.23.379 20260408
    2318 - feat 홈피드 영상 카드 2컬럼 그리드 + 미리보기 fix (grid 기본값, 영상 md:col-span-2로 존재감 확대,
    poster 없는 영상 preload=metadata→첫 프레임 썸네일 표시) v1.23.378 20260408 1807 - feat 홈피드
    카드 완전 오버레이 전환 (이미지/비디오 하단 블록 제거, 프롬프트+유저정보+좋아요/댓글+액션버튼 전부 미디어 위 오버레이로 통합, 기본 opacity-60
    → hover opacity-100, 오디오 타입만 별도 컨테이너 유지) v1.23.377 20260408 1759 - feat 홈피드 카드
    프롬프트 오버레이 (이미지/비디오 위 하단 오버레이 표시, gradient + backdrop-blur 배경, 기본 opacity-60 →
    hover opacity-100, 오디오 타입은 기존 별도 div 유지) v1.23.365 20260402 1612 - fix 환불 로직 통일
    (deduct_credits RPC 원자적 차감 + creditCharged 패턴 전체 적용) - 6개 Edge Function: users.update
    비원자적 차감 → deduct_credits RPC (FOR UPDATE lock, 프로모/구매 FIFO, 자동 credit_logs) -
    storyboard-submit: creditCharged + try-catch 환불 추가 (기존 환불 누락) - audio-voice-clone:
    creditCharged + generationId 없는 경우 직접 환불 경로 추가 - video-lipsync: creditCharged
    + genError 환불 시 credit_logs 기록 추가 - generate-nano-banana-pro/audio-tts/generate-video-multi:
    deduct_credits RPC 교체 v1.23.390 20260412 - chore test-results 업데이트 (DAU/MAU page_views
    검수 완료) v1.23.392 20260412 - feat 관리자 사용자 관리 월별 Excel 내보내기 (exportMonthlyUsersExcel.ts,
    UserManagement.tsx 월별 Excel 버튼, xlsx 패키지 추가, 월별 시트 분리 + 전체 요약 시트) v1.23.393 20260412
    - feat 월별 KPI 대시보드 Excel 고도화 (monthly-dashboard API: 9개 생성 카테고리 분류 + directors/simplevideo/videoedit/automation_projects
    테이블 통합, 기간활성사용자/활성률/활성상태 추가, 국가별 분포 top15 / exportMonthlyDashboardExcel: 월별 요약
    20컬럼 + 상세 시트 3섹션 사용자현황+콘텐츠생성현황+국가별분포) v1.23.397 20260420 - feat 사이드바 신규 유저 탭 추가
    (analyst 직접 접근: adminTabs divider + new-users 탭, NewUsersPanel dynamic import,
    case ''new-users'' 렌더링) v1.23.398 20260420 - fix 사이드바 신규 유저 탭 analyst 노출 (adminOnly
    → analystOnly, MobileSidebar analystUngroupedTabs 필터 조건 충족, 불필요 divider 제거) v1.23.399
    20260420 - feat 사이드바 Discord 커뮤니티 링크 추가 (MessageCircle 아이콘 + https://discord.gg/Z7wG5skk,
    FAQ 탭 다음 indigo 액센트, Discord 서버 생성: Hugwarts Banana 로고+10채널 INFO/SHOWCASE/COMMUNITY
    카테고리) v1.23.400 20260420 - docs Discord 거버넌스 코퍼스 추가 (DISCORD-GOVERNANCE-CORPUS-20260420.md,
    /entity -r Mode B 합성: 서버 구조/모더레이션/3-role 계층/주간 엔게이지먼트 루프/피드백 채널/4가지 링킹 방법 비교/Method
    C Linked Roles 추천/30-60-90 실행 계획) v1.23.401 20260420 - feat Discord Linked Roles
    백엔드 (Phase 1: DB migration discord_user_id/tokens + OAuth helper /lib/discord/oauth.ts
    + 3 API routes /api/discord/{link,callback,metadata} + metadata 스키마 등록 스크립트 discord-register-metadata.mjs,
    Client ID 1495673244802613359 App 생성+OAuth redirect+Bot token+Linked Roles URL
    설정 완료, 5개 metadata 필드 Discord 등록 has_paid/purchased_credits/credits_spent/account_age_days/country_code)
    v1.23.402 20260420 - feat 사이드바 Discord 탭 #2 위치 이동 + NEW 뱃지 (Home 아래 indigo/purple
    gradient + border + animate-pulse NEW 뱃지, 하단 기존 Discord 링크 제거, 채널 11개 bilingual
    EN/KR 개명 + 6개 pinned 가이드 메시지 포스트) v1.23.403 20260421 - feat 온보딩 Discord CTA +
    10 바나나 선물 (OnboardingFlowV2 complete step에 indigo/purple gradient Discord 카드 추가,
    Join Creator Community + 10 🍌 애니메이션 뱃지 + bilingual KR/EN 설명, /api/discord/callback
    첫 연동 시 promo_credits/credits +10 일회성 지급 + credit_logs 감사 로그, OnboardingFlowV2
    initialStep prop 추가, /ko/onboarding-preview 미리보기 라우트 추가) v1.23.404 20260421 -
    feat Discord 아이콘 적극 활용 (공식 Discord Clyde 브랜드 SVG 아이콘 컴포넌트 DiscordIcon.tsx 추가,
    사이드바 #2 Discord 탭 + 온보딩 CTA 카드 MessageCircle → DiscordIcon blurple #5865F2 교체,
    FAQ 페이지 헤더에 Discord 커뮤니티 CTA 카드 추가 - 답을 못 찾으셨나요? 카피 + ChevronRight + bilingual
    KR/EN, 브랜드 인지도 향상) v1.23.405 20260421 - feat 홈피드 Discord 초대 배너 (logged-in 유저 중
    Discord 미연동자만 노출, X 버튼으로 영구 dismiss localStorage v1, blurple gradient + Discord
    Clyde 아이콘 + +10 🍌 NEW 뱃지 + bilingual KR/EN 카피, culture-first 원칙: notice-not-coerce
    / doorway-not-turnstile / 1회성 — DiscordInviteBanner.tsx 신규, CommunityFeed.tsx
    상단 마운트, User 타입에 discord_linked_at 추가) v1.23.406 20260424 - fix 스토리보드 크레딧 환불 누락
    3종 수정 + Discord 배너 링크 수정 (storyboard-complete: imageUrls 빈 배열 시 completed 저장 차단,
    StoryboardGenerator: 전체 FAL submit 실패 시 즉시 refund-credit 호출 + externalImages 빈
    배열 guard, DiscordInviteBanner: window.location→/api/discord/link (Authorization
    헤더 없어 로그인 페이지로 튕기던 버그) → window.open discord.gg/Z7wG5skk 직접 오픈, login+AuthContext:
    return_to sessionStorage 왕복 추가 (post-login redirect 보존)) v1.23.407 20260424 -
    fix WTP/고객인터뷰 모달 닫기 버그 수정 (PSMSurveyModal + LowCreditAlertModal: 단일 outer div
    → backdrop onClick={onClose} + inner card onClick stopPropagation 패턴 적용, 배경 클릭
    시 모달 닫히지 않던 버그 수정, CustomerProblemSurveyModal은 기존 분리 overlay 구조로 이미 정상) v1.23.408
    20260424 - feat Discord 계정설정 연동 버튼 + 결제 후 메타데이터 자동 동기화 (AccountSettings.tsx Discord
    섹션 추가: discord_linked_at 기반 연동/미연동 분기, Link Discord → /api/discord/link-url JSON
    방식, Re-sync roles → POST /api/discord/metadata, /api/discord/link-url 신규 라우트,
    sevenzero webhook + paypal capture에 결제 성공 후 Discord metadata fire-and-forget push
    추가) v1.23.409 20260424 - fix dev server 무한 리빌드 (next.config.js watchOptions.ignored
    추가: .playwright-mcp/.omc/playwright/tests/_pw-verify 등 비소스 디렉토리 제외, poll:1000
    + 579개 로그파일 동시 변경이 매 1.2초마다 Fast Refresh 트리거하던 버그 수정) v1.23.410 20260427 - fix
    홈피드 조회수 threshold display (formatFeedCount 헬퍼 추가: view_count<10 → 숨김, 10~999 →
    정확한 숫자, 1000+ → K 포맷, 83.5% 제로뷰 아이템의 Eye 아이콘 제거로 ghost town 시각효과 제거) v1.23.413
    20260501 - fix SevenZero 결제 크레딧 미지급 근본 원인 수정 (process_payment_complete_with_logging
    RPC가 service_role 전용으로 제한된 이후 프론트엔드 authenticated 호출 → permission denied → 크레딧
    미지급, /api/payments/sevenzero/complete 신규 라우트 생성 supabaseAdmin 경유, SevenZeroPaymentModal
    RPC 직접 호출 → API route 호출로 변경) v1.23.414 20260501 - chore package-lock.json 정리
    (npm install --prefer-offline 후 lock 파일 1줄 변경) v1.23.415 20260503 - fix dev server
    host binding (next dev -H 127.0.0.1 로컬 전용 바인딩, Service Binding Rule 준수) v1.23.416
    20260504 - fix PushPermissionPrompt 알림켜기 후 팝업 미닫힘 버그 (setShow(false)를 subscribeToPush
    성공 여부와 무관하게 항상 호출) v1.23.417 20260504 - refactor Discord 초대 링크 env 변수화 (NEXT_PUBLIC_DISCORD_INVITE_URL)
    - FAQPage/DiscordInviteBanner/MobileSidebar 3파일 하드코딩 제거 → 링크 교체 시 Vercel 환경변수만
    변경하면 됨 v1.23.418 20260504 - feat 계정 탈퇴 구현 (PIPA 제36조) - AccountSettings.tsx 탈퇴
    섹션 + 확인 모달 (잔여 크레딧 경고, 취소/확인), /api/user/delete-account 신규 라우트 (auth 확인 → public.users
    익명화 → auth.users 삭제 → 감사 로그) v1.23.419 20260504 - fix 계정 탈퇴 버튼 위치 이동 (로그아웃 버튼
    우측으로, 별도 섹션 제거 → 한 행 flex 배치) v1.23.420 20260504 - feat AccountModal 계정 탈퇴 버튼
    추가 + 모달 닫힘 시 상태 초기화 (로그아웃 버튼 우측 탈퇴 버튼, 확인 모달, isOpen false 시 showDeleteConfirm
    리셋) v1.23.421 20260506 - fix 고객 문의 이메일 변경 (kimminsik1116 → be2jay67@gmail.com,
    FAQPage/FAQModal/ContactAdminModal/faqs.ts 5파일) v1.23.422 20260506 - feat UI/UX
    패턴 테스트 페이지 추가 (/ko/ui-test) - 7가지 패턴 인터랙티브 미리보기 (크레딧 카운터/2개 변형 출력/프롬프트 공개/스타일
    타일/히스토리/프롬프트 제안/크레딧 비용 미리보기) v1.23.423 20260506 - fix 이미지 연속 생성 불가 버그 (GenerationWarningModal
    confirmedRef 리셋 누락 → useEffect isOpen 변경 시 초기화) v1.23.424 20260506 - feat 채팅 버튼
    비활성화 (GlobalFloatingButtons ChatBottomBar 주석 처리 — 챗봇 미동작) v1.23.425 20260506 -
    feat 사이드바 크레딧 카운터 + 피드 카드 프롬프트 복사 + 미션 보상 시각화 (MobileSidebar 크레딧 pill, CommunityFeed
    프롬프트 복사 버튼, MissionDashboard 완료 미션 amber glow + 바운스 배지) v1.23.426 20260506 - feat
    히스토리 패널 미디어 미리보기 모달 (RecentPromptsPanel: 이미지/영상 클릭 시 다운로드 아닌 모달 확대 미리보기, fullscreen→max-w-2xl
    중앙 모달, backdrop-blur, 바깥 클릭 닫기) v1.23.427 20260506 - feat 인기 AI 쇼츠 큐레이션 (BannerSettingsPanel:
    YouTube API 자동 수집 버튼 + 수동 URL 추가, /api/admin/fetch-trending-shorts, /api/featured-shorts
    공개 API, CommunityFeed: 홈피드 인기 AI 쇼츠 캐러셀) v1.23.428 20260506 - feat 인기 AI 쇼츠 캐러셀
    순서 조정 + 20개로 확장 (Discord 배너→실시간 활동→인기 쇼츠 순, FeaturedShortsCarousel 위치 이동: 홈피드
    상단→모든작품 섹션 직전, YouTube API 3개 쿼리 20개 URL 수집) v1.23.429 20260506 - feat 인기 AI 쇼츠
    캐러셀 좌우 화살표 스크롤 버튼 추가 (CommunityFeed FeaturedShortsCarousel: useRef + 좌우 chevron
    버튼, 클릭 시 320px smooth scroll) v1.23.430 20260507 - fix SevenZero postMessage 수신
    실패 근본 수정 (origin 체크 완화: 77770000.co.kr 서브도메인 전체 허용, 전체 postMessage 디버그 로깅 추가,
    5분 타임아웃 fallback: 미수신 시 고객센터 안내 메시지) v1.23.431 20260507 - feat 결제 시도 로깅 추가 (payment_attempt_logs
    테이블 + /api/payments/sevenzero/log-attempt + SevenZeroPaymentModal: initiated/postmessage_received/processing/completed/failed/timeout
    6단계 추적, 향후 미결제 케이스 진단 가능) v1.23.432 20260507 - feat Paddle 결제 연동 (PaddlePaymentModal.tsx
    + /api/payments/paddle/webhook + CreditPurchaseModal에 글로벌카드결제 버튼 추가, @paddle/paddle-js
    SDK, 기존 process_payment_complete_with_logging RPC 재사용); 6b244fc v1.23.396 20260416
    - fix 립싱크 타임아웃 에러 메시지 개선 (일시적 혼잡 안내 + 13초 이하 짧은 오디오 재시도 유도) - LipsyncVideoGenerator.tsx
    + lipsync-worker timeout/FAL/general 에러 메시지에 팁 추가 v1.23.395 20260416 - fix 로딩스피너
    마법사 바나나 복원 + shimmer bar 유지 (sparkle/bounce dots 제거 → 가로 shimmer bar 대체, pg_cron
    job 4/10 에러 수정: current_setting→직접키, extensions.http→net.http_post) v1.23.394
    20260416 - fix 관리자 탭 중복 해소 + 로딩스피너 모던화 (adminTabs 13개→1개 통합, 12개 개별 case 제거 →
    UnifiedAdminDashboard 일원화, BananaLoadingAnimation 리디자인: wizard hat+sparkle → 미니멀
    glow pulse+shimmer bar) v1.23.388 20260409 1522 - fix WTP 설문 수집 3종 개선 (Rejection
    Interview 자동 표시 depleted 기본값 true, PSM 통화 필드 추가 lang→currency KRW/USD, psm-pricing
    API 통화별 유효성 검사 KRW>=100/USD>=0.5, psm-analysis 이상값 필터 + currency 쿼리 파람) v1.23.387
    20260409 1238 - fix creditsAgg PostgREST 집계 비활성화 → get_total_credits_consumed()
    RPC 교체 (228235 크레딧 정상 반환 확인) v1.23.386 20260409 1218 - perf 관리자 대시보드 로딩 속도 개선
    (phase=1 fast KPI <500ms + 2-phase 순차 로딩, creditsAgg DB 집계로 전환, 국가 쿼리 100k→5k
    제한, DB 인덱스 3개 추가) v1.23.385 20260409 1150 - fix 홈피드 이벤트 카드 정리 (promo-expiry-notice
    제거 → 당첨자발표 이미지 완전 숨김, announcement_video 재활성화 → 쇼츠 가이드 영상 복구) v1.23.384 20260409
    1137 - fix 마법사 바나나 로딩 + 당첨자 공지 카드 제거 (BananaLoadingAnimation 통합 SVG 좌표계 hat+body,
    promos.config promo-festa 항목 삭제) v1.23.383 20260409 1034 - feat BananaLoadingAnimation
    리디자인 (orbital rings → 귀여운 바나나 마스코트 SVG float+wiggle + 3-dot amber bounce, 21개
    컴포넌트 자동 적용) v1.23.382 20260409 1003 - feat 홈피드 영상 카드 9:16 portrait 전환 (aspect-video
    → aspect-[9/16], md:col-span-2 제거 — 이미지 카드와 동일 포맷) v1.23.381 20260408 2335 - feat
    영상 카드 hover 자동재생 (VideoPlayer hoverPlay prop — mouseenter 무음 loop 재생, mouseleave
    pause+reset, controls 숨김) v1.23.380 20260408 2328 - fix 홈피드 오버레이 중복 제거 (좋아요/댓글
    버튼 이중 렌더 → 통합 오버레이로 단일화, 비디오 Maximize2 z-10 중복 overlay 제거) v1.23.379 20260408
    2318 - feat 홈피드 영상 카드 2컬럼 그리드 + 미리보기 fix (grid 기본값, 영상 md:col-span-2로 존재감 확대,
    poster 없는 영상 preload=metadata→첫 프레임 썸네일 표시) v1.23.378 20260408 1807 - feat 홈피드
    카드 완전 오버레이 전환 (이미지/비디오 하단 블록 제거, 프롬프트+유저정보+좋아요/댓글+액션버튼 전부 미디어 위 오버레이로 통합, 기본 opacity-60
    → hover opacity-100, 오디오 타입만 별도 컨테이너 유지) v1.23.377 20260408 1759 - feat 홈피드 카드
    프롬프트 오버레이 (이미지/비디오 위 하단 오버레이 표시, gradient + backdrop-blur 배경, 기본 opacity-60 →
    hover opacity-100, 오디오 타입은 기존 별도 div 유지) v1.23.365 20260402 1612 - fix 환불 로직 통일
    (deduct_credits RPC 원자적 차감 + creditCharged 패턴 전체 적용) - 6개 Edge Function: users.update
    비원자적 차감 → deduct_credits RPC (FOR UPDATE lock, 프로모/구매 FIFO, 자동 credit_logs) -
    storyboard-submit: creditCharged + try-catch 환불 추가 (기존 환불 누락) - audio-voice-clone:
    creditCharged + generationId 없는 경우 직접 환불 경로 추가 - video-lipsync: creditCharged
    + genError 환불 시 credit_logs 기록 추가 - generate-nano-banana-pro/audio-tts/generate-video-multi:
    deduct_credits RPC 교체 v1.23.390 20260412 - chore test-results 업데이트 (DAU/MAU page_views
    검수 완료) v1.23.392 20260412 - feat 관리자 사용자 관리 월별 Excel 내보내기 (exportMonthlyUsersExcel.ts,
    UserManagement.tsx 월별 Excel 버튼, xlsx 패키지 추가, 월별 시트 분리 + 전체 요약 시트) v1.23.393 20260412
    - feat 월별 KPI 대시보드 Excel 고도화 (monthly-dashboard API: 9개 생성 카테고리 분류 + directors/simplevideo/videoedit/automation_projects
    테이블 통합, 기간활성사용자/활성률/활성상태 추가, 국가별 분포 top15 / exportMonthlyDashboardExcel: 월별 요약
    20컬럼 + 상세 시트 3섹션 사용자현황+콘텐츠생성현황+국가별분포) v1.23.397 20260420 - feat 사이드바 신규 유저 탭 추가
    (analyst 직접 접근: adminTabs divider + new-users 탭, NewUsersPanel dynamic import,
    case ''new-users'' 렌더링) v1.23.398 20260420 - fix 사이드바 신규 유저 탭 analyst 노출 (adminOnly
    → analystOnly, MobileSidebar analystUngroupedTabs 필터 조건 충족, 불필요 divider 제거) v1.23.399
    20260420 - feat 사이드바 Discord 커뮤니티 링크 추가 (MessageCircle 아이콘 + https://discord.gg/Z7wG5skk,
    FAQ 탭 다음 indigo 액센트, Discord 서버 생성: Hugwarts Banana 로고+10채널 INFO/SHOWCASE/COMMUNITY
    카테고리) v1.23.400 20260420 - docs Discord 거버넌스 코퍼스 추가 (DISCORD-GOVERNANCE-CORPUS-20260420.md,
    /entity -r Mode B 합성: 서버 구조/모더레이션/3-role 계층/주간 엔게이지먼트 루프/피드백 채널/4가지 링킹 방법 비교/Method
    C Linked Roles 추천/30-60-90 실행 계획) v1.23.401 20260420 - feat Discord Linked Roles
    백엔드 (Phase 1: DB migration discord_user_id/tokens + OAuth helper /lib/discord/oauth.ts
    + 3 API routes /api/discord/{link,callback,metadata} + metadata 스키마 등록 스크립트 discord-register-metadata.mjs,
    Client ID 1495673244802613359 App 생성+OAuth redirect+Bot token+Linked Roles URL
    설정 완료, 5개 metadata 필드 Discord 등록 has_paid/purchased_credits/credits_spent/account_age_days/country_code)
    v1.23.402 20260420 - feat 사이드바 Discord 탭 #2 위치 이동 + NEW 뱃지 (Home 아래 indigo/purple
    gradient + border + animate-pulse NEW 뱃지, 하단 기존 Discord 링크 제거, 채널 11개 bilingual
    EN/KR 개명 + 6개 pinned 가이드 메시지 포스트) v1.23.403 20260421 - feat 온보딩 Discord CTA +
    10 바나나 선물 (OnboardingFlowV2 complete step에 indigo/purple gradient Discord 카드 추가,
    Join Creator Community + 10 🍌 애니메이션 뱃지 + bilingual KR/EN 설명, /api/discord/callback
    첫 연동 시 promo_credits/credits +10 일회성 지급 + credit_logs 감사 로그, OnboardingFlowV2
    initialStep prop 추가, /ko/onboarding-preview 미리보기 라우트 추가) v1.23.404 20260421 -
    feat Discord 아이콘 적극 활용 (공식 Discord Clyde 브랜드 SVG 아이콘 컴포넌트 DiscordIcon.tsx 추가,
    사이드바 #2 Discord 탭 + 온보딩 CTA 카드 MessageCircle → DiscordIcon blurple #5865F2 교체,
    FAQ 페이지 헤더에 Discord 커뮤니티 CTA 카드 추가 - 답을 못 찾으셨나요? 카피 + ChevronRight + bilingual
    KR/EN, 브랜드 인지도 향상) v1.23.405 20260421 - feat 홈피드 Discord 초대 배너 (logged-in 유저 중
    Discord 미연동자만 노출, X 버튼으로 영구 dismiss localStorage v1, blurple gradient + Discord
    Clyde 아이콘 + +10 🍌 NEW 뱃지 + bilingual KR/EN 카피, culture-first 원칙: notice-not-coerce
    / doorway-not-turnstile / 1회성 — DiscordInviteBanner.tsx 신규, CommunityFeed.tsx
    상단 마운트, User 타입에 discord_linked_at 추가) v1.23.406 20260424 - fix 스토리보드 크레딧 환불 누락
    3종 수정 + Discord 배너 링크 수정 (storyboard-complete: imageUrls 빈 배열 시 completed 저장 차단,
    StoryboardGenerator: 전체 FAL submit 실패 시 즉시 refund-credit 호출 + externalImages 빈
    배열 guard, DiscordInviteBanner: window.location→/api/discord/link (Authorization
    헤더 없어 로그인 페이지로 튕기던 버그) → window.open discord.gg/Z7wG5skk 직접 오픈, login+AuthContext:
    return_to sessionStorage 왕복 추가 (post-login redirect 보존)) v1.23.407 20260424 -
    fix WTP/고객인터뷰 모달 닫기 버그 수정 (PSMSurveyModal + LowCreditAlertModal: 단일 outer div
    → backdrop onClick={onClose} + inner card onClick stopPropagation 패턴 적용, 배경 클릭
    시 모달 닫히지 않던 버그 수정, CustomerProblemSurveyModal은 기존 분리 overlay 구조로 이미 정상) v1.23.408
    20260424 - feat Discord 계정설정 연동 버튼 + 결제 후 메타데이터 자동 동기화 (AccountSettings.tsx Discord
    섹션 추가: discord_linked_at 기반 연동/미연동 분기, Link Discord → /api/discord/link-url JSON
    방식, Re-sync roles → POST /api/discord/metadata, /api/discord/link-url 신규 라우트,
    sevenzero webhook + paypal capture에 결제 성공 후 Discord metadata fire-and-forget push
    추가) v1.23.409 20260424 - fix dev server 무한 리빌드 (next.config.js watchOptions.ignored
    추가: .playwright-mcp/.omc/playwright/tests/_pw-verify 등 비소스 디렉토리 제외, poll:1000
    + 579개 로그파일 동시 변경이 매 1.2초마다 Fast Refresh 트리거하던 버그 수정) v1.23.410 20260427 - fix
    홈피드 조회수 threshold display (formatFeedCount 헬퍼 추가: view_count<10 → 숨김, 10~999 →
    정확한 숫자, 1000+ → K 포맷, 83.5% 제로뷰 아이템의 Eye 아이콘 제거로 ghost town 시각효과 제거) v1.23.413
    20260501 - fix SevenZero 결제 크레딧 미지급 근본 원인 수정 (process_payment_complete_with_logging
    RPC가 service_role 전용으로 제한된 이후 프론트엔드 authenticated 호출 → permission denied → 크레딧
    미지급, /api/payments/sevenzero/complete 신규 라우트 생성 supabaseAdmin 경유, SevenZeroPaymentModal
    RPC 직접 호출 → API route 호출로 변경) v1.23.414 20260501 - chore package-lock.json 정리
    (npm install --prefer-offline 후 lock 파일 1줄 변경) v1.23.415 20260503 - fix dev server
    host binding (next dev -H 127.0.0.1 로컬 전용 바인딩, Service Binding Rule 준수) v1.23.416
    20260504 - fix PushPermissionPrompt 알림켜기 후 팝업 미닫힘 버그 (setShow(false)를 subscribeToPush
    성공 여부와 무관하게 항상 호출) v1.23.417 20260504 - refactor Discord 초대 링크 env 변수화 (NEXT_PUBLIC_DISCORD_INVITE_URL)
    - FAQPage/DiscordInviteBanner/MobileSidebar 3파일 하드코딩 제거 → 링크 교체 시 Vercel 환경변수만
    변경하면 됨 v1.23.418 20260504 - feat 계정 탈퇴 구현 (PIPA 제36조) - AccountSettings.tsx 탈퇴
    섹션 + 확인 모달 (잔여 크레딧 경고, 취소/확인), /api/user/delete-account 신규 라우트 (auth 확인 → public.users
    익명화 → auth.users 삭제 → 감사 로그) v1.23.419 20260504 - fix 계정 탈퇴 버튼 위치 이동 (로그아웃 버튼
    우측으로, 별도 섹션 제거 → 한 행 flex 배치) v1.23.420 20260504 - feat AccountModal 계정 탈퇴 버튼
    추가 + 모달 닫힘 시 상태 초기화 (로그아웃 버튼 우측 탈퇴 버튼, 확인 모달, isOpen false 시 showDeleteConfirm
    리셋) v1.23.421 20260506 - fix 고객 문의 이메일 변경 (kimminsik1116 → be2jay67@gmail.com,
    FAQPage/FAQModal/ContactAdminModal/faqs.ts 5파일) v1.23.422 20260506 - feat UI/UX
    패턴 테스트 페이지 추가 (/ko/ui-test) - 7가지 패턴 인터랙티브 미리보기 (크레딧 카운터/2개 변형 출력/프롬프트 공개/스타일
    타일/히스토리/프롬프트 제안/크레딧 비용 미리보기) v1.23.423 20260506 - fix 이미지 연속 생성 불가 버그 (GenerationWarningModal
    confirmedRef 리셋 누락 → useEffect isOpen 변경 시 초기화) v1.23.424 20260506 - feat 채팅 버튼
    비활성화 (GlobalFloatingButtons ChatBottomBar 주석 처리 — 챗봇 미동작) v1.23.425 20260506 -
    feat 사이드바 크레딧 카운터 + 피드 카드 프롬프트 복사 + 미션 보상 시각화 (MobileSidebar 크레딧 pill, CommunityFeed
    프롬프트 복사 버튼, MissionDashboard 완료 미션 amber glow + 바운스 배지) v1.23.426 20260506 - feat
    히스토리 패널 미디어 미리보기 모달 (RecentPromptsPanel: 이미지/영상 클릭 시 다운로드 아닌 모달 확대 미리보기, fullscreen→max-w-2xl
    중앙 모달, backdrop-blur, 바깥 클릭 닫기) v1.23.427 20260506 - feat 인기 AI 쇼츠 큐레이션 (BannerSettingsPanel:
    YouTube API 자동 수집 버튼 + 수동 URL 추가, /api/admin/fetch-trending-shorts, /api/featured-shorts
    공개 API, CommunityFeed: 홈피드 인기 AI 쇼츠 캐러셀) v1.23.428 20260506 - feat 인기 AI 쇼츠 캐러셀
    순서 조정 + 20개로 확장 (Discord 배너→실시간 활동→인기 쇼츠 순, FeaturedShortsCarousel 위치 이동: 홈피드
    상단→모든작품 섹션 직전, YouTube API 3개 쿼리 20개 URL 수집) v1.23.429 20260506 - feat 인기 AI 쇼츠
    캐러셀 좌우 화살표 스크롤 버튼 추가 (CommunityFeed FeaturedShortsCarousel: useRef + 좌우 chevron
    버튼, 클릭 시 320px smooth scroll) v1.23.430 20260507 - fix SevenZero postMessage 수신
    실패 근본 수정 (origin 체크 완화: 77770000.co.kr 서브도메인 전체 허용, 전체 postMessage 디버그 로깅 추가,
    5분 타임아웃 fallback: 미수신 시 고객센터 안내 메시지) v1.23.431 20260507 - feat 결제 시도 로깅 추가 (payment_attempt_logs
    테이블 + /api/payments/sevenzero/log-attempt + SevenZeroPaymentModal: initiated/postmessage_received/processing/completed/failed/timeout
    6단계 추적, 향후 미결제 케이스 진단 가능) (+1 more)'
- date: '2026-05-08'
  text: '09bda42 v1.23.433 20260508 - fix Paddle 가격 정책 KRW 일치 + 테스트 패키지 지원 (PaddlePaymentModal
    PADDLE_PRICE_MAP에 100원 테스트 패키지 추가, 나머지 5개 패키지 KRW 실가격으로 업데이트 예정); be6627b v1.23.396
    20260416 - fix 립싱크 타임아웃 에러 메시지 개선 (일시적 혼잡 안내 + 13초 이하 짧은 오디오 재시도 유도) - LipsyncVideoGenerator.tsx
    + lipsync-worker timeout/FAL/general 에러 메시지에 팁 추가 v1.23.395 20260416 - fix 로딩스피너
    마법사 바나나 복원 + shimmer bar 유지 (sparkle/bounce dots 제거 → 가로 shimmer bar 대체, pg_cron
    job 4/10 에러 수정: current_setting→직접키, extensions.http→net.http_post) v1.23.394
    20260416 - fix 관리자 탭 중복 해소 + 로딩스피너 모던화 (adminTabs 13개→1개 통합, 12개 개별 case 제거 →
    UnifiedAdminDashboard 일원화, BananaLoadingAnimation 리디자인: wizard hat+sparkle → 미니멀
    glow pulse+shimmer bar) v1.23.388 20260409 1522 - fix WTP 설문 수집 3종 개선 (Rejection
    Interview 자동 표시 depleted 기본값 true, PSM 통화 필드 추가 lang→currency KRW/USD, psm-pricing
    API 통화별 유효성 검사 KRW>=100/USD>=0.5, psm-analysis 이상값 필터 + currency 쿼리 파람) v1.23.387
    20260409 1238 - fix creditsAgg PostgREST 집계 비활성화 → get_total_credits_consumed()
    RPC 교체 (228235 크레딧 정상 반환 확인) v1.23.386 20260409 1218 - perf 관리자 대시보드 로딩 속도 개선
    (phase=1 fast KPI <500ms + 2-phase 순차 로딩, creditsAgg DB 집계로 전환, 국가 쿼리 100k→5k
    제한, DB 인덱스 3개 추가) v1.23.385 20260409 1150 - fix 홈피드 이벤트 카드 정리 (promo-expiry-notice
    제거 → 당첨자발표 이미지 완전 숨김, announcement_video 재활성화 → 쇼츠 가이드 영상 복구) v1.23.384 20260409
    1137 - fix 마법사 바나나 로딩 + 당첨자 공지 카드 제거 (BananaLoadingAnimation 통합 SVG 좌표계 hat+body,
    promos.config promo-festa 항목 삭제) v1.23.383 20260409 1034 - feat BananaLoadingAnimation
    리디자인 (orbital rings → 귀여운 바나나 마스코트 SVG float+wiggle + 3-dot amber bounce, 21개
    컴포넌트 자동 적용) v1.23.382 20260409 1003 - feat 홈피드 영상 카드 9:16 portrait 전환 (aspect-video
    → aspect-[9/16], md:col-span-2 제거 — 이미지 카드와 동일 포맷) v1.23.381 20260408 2335 - feat
    영상 카드 hover 자동재생 (VideoPlayer hoverPlay prop — mouseenter 무음 loop 재생, mouseleave
    pause+reset, controls 숨김) v1.23.380 20260408 2328 - fix 홈피드 오버레이 중복 제거 (좋아요/댓글
    버튼 이중 렌더 → 통합 오버레이로 단일화, 비디오 Maximize2 z-10 중복 overlay 제거) v1.23.379 20260408
    2318 - feat 홈피드 영상 카드 2컬럼 그리드 + 미리보기 fix (grid 기본값, 영상 md:col-span-2로 존재감 확대,
    poster 없는 영상 preload=metadata→첫 프레임 썸네일 표시) v1.23.378 20260408 1807 - feat 홈피드
    카드 완전 오버레이 전환 (이미지/비디오 하단 블록 제거, 프롬프트+유저정보+좋아요/댓글+액션버튼 전부 미디어 위 오버레이로 통합, 기본 opacity-60
    → hover opacity-100, 오디오 타입만 별도 컨테이너 유지) v1.23.377 20260408 1759 - feat 홈피드 카드
    프롬프트 오버레이 (이미지/비디오 위 하단 오버레이 표시, gradient + backdrop-blur 배경, 기본 opacity-60 →
    hover opacity-100, 오디오 타입은 기존 별도 div 유지) v1.23.365 20260402 1612 - fix 환불 로직 통일
    (deduct_credits RPC 원자적 차감 + creditCharged 패턴 전체 적용) - 6개 Edge Function: users.update
    비원자적 차감 → deduct_credits RPC (FOR UPDATE lock, 프로모/구매 FIFO, 자동 credit_logs) -
    storyboard-submit: creditCharged + try-catch 환불 추가 (기존 환불 누락) - audio-voice-clone:
    creditCharged + generationId 없는 경우 직접 환불 경로 추가 - video-lipsync: creditCharged
    + genError 환불 시 credit_logs 기록 추가 - generate-nano-banana-pro/audio-tts/generate-video-multi:
    deduct_credits RPC 교체 v1.23.390 20260412 - chore test-results 업데이트 (DAU/MAU page_views
    검수 완료) v1.23.392 20260412 - feat 관리자 사용자 관리 월별 Excel 내보내기 (exportMonthlyUsersExcel.ts,
    UserManagement.tsx 월별 Excel 버튼, xlsx 패키지 추가, 월별 시트 분리 + 전체 요약 시트) v1.23.393 20260412
    - feat 월별 KPI 대시보드 Excel 고도화 (monthly-dashboard API: 9개 생성 카테고리 분류 + directors/simplevideo/videoedit/automation_projects
    테이블 통합, 기간활성사용자/활성률/활성상태 추가, 국가별 분포 top15 / exportMonthlyDashboardExcel: 월별 요약
    20컬럼 + 상세 시트 3섹션 사용자현황+콘텐츠생성현황+국가별분포) v1.23.397 20260420 - feat 사이드바 신규 유저 탭 추가
    (analyst 직접 접근: adminTabs divider + new-users 탭, NewUsersPanel dynamic import,
    case ''new-users'' 렌더링) v1.23.398 20260420 - fix 사이드바 신규 유저 탭 analyst 노출 (adminOnly
    → analystOnly, MobileSidebar analystUngroupedTabs 필터 조건 충족, 불필요 divider 제거) v1.23.399
    20260420 - feat 사이드바 Discord 커뮤니티 링크 추가 (MessageCircle 아이콘 + https://discord.gg/Z7wG5skk,
    FAQ 탭 다음 indigo 액센트, Discord 서버 생성: Hugwarts Banana 로고+10채널 INFO/SHOWCASE/COMMUNITY
    카테고리) v1.23.400 20260420 - docs Discord 거버넌스 코퍼스 추가 (DISCORD-GOVERNANCE-CORPUS-20260420.md,
    /entity -r Mode B 합성: 서버 구조/모더레이션/3-role 계층/주간 엔게이지먼트 루프/피드백 채널/4가지 링킹 방법 비교/Method
    C Linked Roles 추천/30-60-90 실행 계획) v1.23.401 20260420 - feat Discord Linked Roles
    백엔드 (Phase 1: DB migration discord_user_id/tokens + OAuth helper /lib/discord/oauth.ts
    + 3 API routes /api/discord/{link,callback,metadata} + metadata 스키마 등록 스크립트 discord-register-metadata.mjs,
    Client ID 1495673244802613359 App 생성+OAuth redirect+Bot token+Linked Roles URL
    설정 완료, 5개 metadata 필드 Discord 등록 has_paid/purchased_credits/credits_spent/account_age_days/country_code)
    v1.23.402 20260420 - feat 사이드바 Discord 탭 #2 위치 이동 + NEW 뱃지 (Home 아래 indigo/purple
    gradient + border + animate-pulse NEW 뱃지, 하단 기존 Discord 링크 제거, 채널 11개 bilingual
    EN/KR 개명 + 6개 pinned 가이드 메시지 포스트) v1.23.403 20260421 - feat 온보딩 Discord CTA +
    10 바나나 선물 (OnboardingFlowV2 complete step에 indigo/purple gradient Discord 카드 추가,
    Join Creator Community + 10 🍌 애니메이션 뱃지 + bilingual KR/EN 설명, /api/discord/callback
    첫 연동 시 promo_credits/credits +10 일회성 지급 + credit_logs 감사 로그, OnboardingFlowV2
    initialStep prop 추가, /ko/onboarding-preview 미리보기 라우트 추가) v1.23.404 20260421 -
    feat Discord 아이콘 적극 활용 (공식 Discord Clyde 브랜드 SVG 아이콘 컴포넌트 DiscordIcon.tsx 추가,
    사이드바 #2 Discord 탭 + 온보딩 CTA 카드 MessageCircle → DiscordIcon blurple #5865F2 교체,
    FAQ 페이지 헤더에 Discord 커뮤니티 CTA 카드 추가 - 답을 못 찾으셨나요? 카피 + ChevronRight + bilingual
    KR/EN, 브랜드 인지도 향상) v1.23.405 20260421 - feat 홈피드 Discord 초대 배너 (logged-in 유저 중
    Discord 미연동자만 노출, X 버튼으로 영구 dismiss localStorage v1, blurple gradient + Discord
    Clyde 아이콘 + +10 🍌 NEW 뱃지 + bilingual KR/EN 카피, culture-first 원칙: notice-not-coerce
    / doorway-not-turnstile / 1회성 — DiscordInviteBanner.tsx 신규, CommunityFeed.tsx
    상단 마운트, User 타입에 discord_linked_at 추가) v1.23.406 20260424 - fix 스토리보드 크레딧 환불 누락
    3종 수정 + Discord 배너 링크 수정 (storyboard-complete: imageUrls 빈 배열 시 completed 저장 차단,
    StoryboardGenerator: 전체 FAL submit 실패 시 즉시 refund-credit 호출 + externalImages 빈
    배열 guard, DiscordInviteBanner: window.location→/api/discord/link (Authorization
    헤더 없어 로그인 페이지로 튕기던 버그) → window.open discord.gg/Z7wG5skk 직접 오픈, login+AuthContext:
    return_to sessionStorage 왕복 추가 (post-login redirect 보존)) v1.23.407 20260424 -
    fix WTP/고객인터뷰 모달 닫기 버그 수정 (PSMSurveyModal + LowCreditAlertModal: 단일 outer div
    → backdrop onClick={onClose} + inner card onClick stopPropagation 패턴 적용, 배경 클릭
    시 모달 닫히지 않던 버그 수정, CustomerProblemSurveyModal은 기존 분리 overlay 구조로 이미 정상) v1.23.408
    20260424 - feat Discord 계정설정 연동 버튼 + 결제 후 메타데이터 자동 동기화 (AccountSettings.tsx Discord
    섹션 추가: discord_linked_at 기반 연동/미연동 분기, Link Discord → /api/discord/link-url JSON
    방식, Re-sync roles → POST /api/discord/metadata, /api/discord/link-url 신규 라우트,
    sevenzero webhook + paypal capture에 결제 성공 후 Discord metadata fire-and-forget push
    추가) v1.23.409 20260424 - fix dev server 무한 리빌드 (next.config.js watchOptions.ignored
    추가: .playwright-mcp/.omc/playwright/tests/_pw-verify 등 비소스 디렉토리 제외, poll:1000
    + 579개 로그파일 동시 변경이 매 1.2초마다 Fast Refresh 트리거하던 버그 수정) v1.23.410 20260427 - fix
    홈피드 조회수 threshold display (formatFeedCount 헬퍼 추가: view_count<10 → 숨김, 10~999 →
    정확한 숫자, 1000+ → K 포맷, 83.5% 제로뷰 아이템의 Eye 아이콘 제거로 ghost town 시각효과 제거) v1.23.413
    20260501 - fix SevenZero 결제 크레딧 미지급 근본 원인 수정 (process_payment_complete_with_logging
    RPC가 service_role 전용으로 제한된 이후 프론트엔드 authenticated 호출 → permission denied → 크레딧
    미지급, /api/payments/sevenzero/complete 신규 라우트 생성 supabaseAdmin 경유, SevenZeroPaymentModal
    RPC 직접 호출 → API route 호출로 변경) v1.23.414 20260501 - chore package-lock.json 정리
    (npm install --prefer-offline 후 lock 파일 1줄 변경) v1.23.415 20260503 - fix dev server
    host binding (next dev -H 127.0.0.1 로컬 전용 바인딩, Service Binding Rule 준수) v1.23.416
    20260504 - fix PushPermissionPrompt 알림켜기 후 팝업 미닫힘 버그 (setShow(false)를 subscribeToPush
    성공 여부와 무관하게 항상 호출) v1.23.417 20260504 - refactor Discord 초대 링크 env 변수화 (NEXT_PUBLIC_DISCORD_INVITE_URL)
    - FAQPage/DiscordInviteBanner/MobileSidebar 3파일 하드코딩 제거 → 링크 교체 시 Vercel 환경변수만
    변경하면 됨 v1.23.418 20260504 - feat 계정 탈퇴 구현 (PIPA 제36조) - AccountSettings.tsx 탈퇴
    섹션 + 확인 모달 (잔여 크레딧 경고, 취소/확인), /api/user/delete-account 신규 라우트 (auth 확인 → public.users
    익명화 → auth.users 삭제 → 감사 로그) v1.23.419 20260504 - fix 계정 탈퇴 버튼 위치 이동 (로그아웃 버튼
    우측으로, 별도 섹션 제거 → 한 행 flex 배치) v1.23.420 20260504 - feat AccountModal 계정 탈퇴 버튼
    추가 + 모달 닫힘 시 상태 초기화 (로그아웃 버튼 우측 탈퇴 버튼, 확인 모달, isOpen false 시 showDeleteConfirm
    리셋) v1.23.421 20260506 - fix 고객 문의 이메일 변경 (kimminsik1116 → be2jay67@gmail.com,
    FAQPage/FAQModal/ContactAdminModal/faqs.ts 5파일) v1.23.422 20260506 - feat UI/UX
    패턴 테스트 페이지 추가 (/ko/ui-test) - 7가지 패턴 인터랙티브 미리보기 (크레딧 카운터/2개 변형 출력/프롬프트 공개/스타일
    타일/히스토리/프롬프트 제안/크레딧 비용 미리보기) v1.23.423 20260506 - fix 이미지 연속 생성 불가 버그 (GenerationWarningModal
    confirmedRef 리셋 누락 → useEffect isOpen 변경 시 초기화) v1.23.424 20260506 - feat 채팅 버튼
    비활성화 (GlobalFloatingButtons ChatBottomBar 주석 처리 — 챗봇 미동작) v1.23.425 20260506 -
    feat 사이드바 크레딧 카운터 + 피드 카드 프롬프트 복사 + 미션 보상 시각화 (MobileSidebar 크레딧 pill, CommunityFeed
    프롬프트 복사 버튼, MissionDashboard 완료 미션 amber glow + 바운스 배지) v1.23.426 20260506 - feat
    히스토리 패널 미디어 미리보기 모달 (RecentPromptsPanel: 이미지/영상 클릭 시 다운로드 아닌 모달 확대 미리보기, fullscreen→max-w-2xl
    중앙 모달, backdrop-blur, 바깥 클릭 닫기) v1.23.427 20260506 - feat 인기 AI 쇼츠 큐레이션 (BannerSettingsPanel:
    YouTube API 자동 수집 버튼 + 수동 URL 추가, /api/admin/fetch-trending-shorts, /api/featured-shorts
    공개 API, CommunityFeed: 홈피드 인기 AI 쇼츠 캐러셀) v1.23.428 20260506 - feat 인기 AI 쇼츠 캐러셀
    순서 조정 + 20개로 확장 (Discord 배너→실시간 활동→인기 쇼츠 순, FeaturedShortsCarousel 위치 이동: 홈피드
    상단→모든작품 섹션 직전, YouTube API 3개 쿼리 20개 URL 수집) v1.23.429 20260506 - feat 인기 AI 쇼츠
    캐러셀 좌우 화살표 스크롤 버튼 추가 (CommunityFeed FeaturedShortsCarousel: useRef + 좌우 chevron
    버튼, 클릭 시 320px smooth scroll) v1.23.430 20260507 - fix SevenZero postMessage 수신
    실패 근본 수정 (origin 체크 완화: 77770000.co.kr 서브도메인 전체 허용, 전체 postMessage 디버그 로깅 추가,
    5분 타임아웃 fallback: 미수신 시 고객센터 안내 메시지) v1.23.431 20260507 - feat 결제 시도 로깅 추가 (payment_attempt_logs
    테이블 + /api/payments/sevenzero/log-attempt + SevenZeroPaymentModal: initiated/postmessage_received/processing/completed/failed/timeout
    6단계 추적, 향후 미결제 케이스 진단 가능) v1.23.432 20260507 - feat Paddle 결제 연동 (PaddlePaymentModal.tsx
    + /api/payments/paddle/webhook + CreditPurchaseModal에 글로벌카드결제 버튼 추가, @paddle/paddle-js
    SDK, 기존 process_payment_complete_with_logging RPC 재사용) (+1 more)'
- date: '2026-05-08'
  text: a79caf6 v1.23.434 20260508 - fix Paddle 결제 버튼 프로덕션 숨김 (NEXT_PUBLIC_PADDLE_ENABLED=true
    일 때만 노출, 기본값 hidden — 테스트 완료 후 Vercel env 추가로 활성화); 09bda42 v1.23.433 20260508
    - fix Paddle 가격 정책 KRW 일치 + 테스트 패키지 지원 (PaddlePaymentModal PADDLE_PRICE_MAP에 100원
    테스트 패키지 추가, 나머지 5개 패키지 KRW 실가격으로 업데이트 예정) (+1 more)
- date: '2026-05-08'
  text: c5ed032 v1.23.435 20260508 - feat Paddle subscription.activated 핸들러 추가 (30일
    무료 체험 구독 활성화 시 즉시 크레딧 지급, PADDLE_SUB_ 접두사 orderId, ginigen.ai 도메인 승인 후 활성화 예정);
    a79caf6 v1.23.434 20260508 - fix Paddle 결제 버튼 프로덕션 숨김 (NEXT_PUBLIC_PADDLE_ENABLED=true
    일 때만 노출, 기본값 hidden — 테스트 완료 후 Vercel env 추가로 활성화) (+1 more)
- date: '2026-05-08'
  text: 'd173746 v1.23.436 20260508 - feat 법적 필수 페이지 추가 (이용약관/개인정보처리방침/환불정책) + 푸터
    링크 활성화 (Paddle 도메인 승인 요건: Terms/Privacy/Refund 3개 페이지 실제 URL 제공); c5ed032 v1.23.435
    20260508 - feat Paddle subscription.activated 핸들러 추가 (30일 무료 체험 구독 활성화 시 즉시 크레딧
    지급, PADDLE_SUB_ 접두사 orderId, ginigen.ai 도메인 승인 후 활성화 예정) (+1 more)'
- date: '2026-05-08'
  text: 'b3652a7 v1.23.437 20260508 - fix lipsync-worker 70% 고착 버그 (reinvokeWorker
    fire-and-forget → 200ms await 추가); d173746 v1.23.436 20260508 - feat 법적 필수 페이지
    추가 (이용약관/개인정보처리방침/환불정책) + 푸터 링크 활성화 (Paddle 도메인 승인 요건: Terms/Privacy/Refund 3개
    페이지 실제 URL 제공) (+1 more)'
- date: '2026-05-08'
  text: b254e7e v1.23.438 20260508 - fix video-lipsync worker 미시작 버그 (fire-and-forget
    → 200ms await 추가); b3652a7 v1.23.437 20260508 - fix lipsync-worker 70% 고착 버그 (reinvokeWorker
    fire-and-forget → 200ms await 추가) (+1 more)
- date: '2026-05-09'
  text: b254e7e v1.23.438 20260508 - fix video-lipsync worker 미시작 버그 (fire-and-forget
    → 200ms await 추가); b3652a7 v1.23.437 20260508 - fix lipsync-worker 70% 고착 버그 (reinvokeWorker
    fire-and-forget → 200ms await 추가) (+1 more)
- date: '2026-05-10'
  text: b254e7e v1.23.438 20260508 - fix video-lipsync worker 미시작 버그 (fire-and-forget
    → 200ms await 추가); b3652a7 v1.23.437 20260508 - fix lipsync-worker 70% 고착 버그 (reinvokeWorker
    fire-and-forget → 200ms await 추가) (+1 more)
- date: '2026-05-11'
  text: b254e7e v1.23.438 20260508 - fix video-lipsync worker 미시작 버그 (fire-and-forget
    → 200ms await 추가); b3652a7 v1.23.437 20260508 - fix lipsync-worker 70% 고착 버그 (reinvokeWorker
    fire-and-forget → 200ms await 추가) (+1 more)
- date: '2026-05-11'
  text: c125d40 v1.23.440 20260511 - SevenZero 결제 버튼 임시 점검 숨김 (NEXT_PUBLIC_SEVENZERO_ENABLED=true
    일 때만 노출); 3f2baee v1.23.439 20260511 - fix SevenZero 결제 후 크레딧 미지급 버그 (세션 만료 +
    실패 미로깅) (+1 more)
- date: '2026-05-11'
  text: 1f75c36 v1.23.441 20260511 - SevenZero 결제 버튼 점검 안내 오버레이 (클릭 불가 + '점검 중' 텍스트);
    c125d40 v1.23.440 20260511 - SevenZero 결제 버튼 임시 점검 숨김 (NEXT_PUBLIC_SEVENZERO_ENABLED=true
    일 때만 노출) (+1 more)
- date: '2026-05-11'
  text: f278b88 v1.23.442 20260511 - 로컬 dev 환경에서 테스트 패키지(₩100) 표시 (모든 유저); 1f75c36
    v1.23.441 20260511 - SevenZero 결제 버튼 점검 안내 오버레이 (클릭 불가 + '점검 중' 텍스트) (+1 more)
- date: '2026-05-11'
  text: 40942a0 v1.23.443 20260511 - SevenZero 결제 에러 시 PG 실제 메시지 표시 (CC66 → '생년월일
    불일치' 등); f278b88 v1.23.442 20260511 - 로컬 dev 환경에서 테스트 패키지(₩100) 표시 (모든 유저) (+1
    more)
- date: '2026-05-11'
  text: 9c5d9da v1.23.444 20260511 - SevenZero 결제 버튼 점검 안내 제거 (정상화); 40942a0 v1.23.443
    20260511 - SevenZero 결제 에러 시 PG 실제 메시지 표시 (CC66 → '생년월일 불일치' 등) (+1 more)
- date: '2026-05-11'
  text: 1b50787 v1.23.445 20260511 - fix 계정 탈퇴 세션 만료 버그 (getSession → refreshSession);
    9c5d9da v1.23.444 20260511 - SevenZero 결제 버튼 점검 안내 제거 (정상화) (+1 more)
- date: '2026-05-11'
  text: e1afeda v1.23.446 20260511 - fix 탈퇴 확인 모달 즉시 닫힘 버그; 1b50787 v1.23.445 20260511
    - fix 계정 탈퇴 세션 만료 버그 (getSession → refreshSession) (+1 more)
- date: '2026-05-11'
  text: ce2fe2b v1.23.447 20260511 - fix AccountSettings 탈퇴 세션 만료 버그 (getSession →
    refreshSession); e1afeda v1.23.446 20260511 - fix 탈퇴 확인 모달 즉시 닫힘 버그 (+1 more)
- date: '2026-05-11'
  text: b95b479 v1.23.448 20260511 - fix 탈퇴 확인 클릭 무효화 버그 (stale closure); ce2fe2b
    v1.23.447 20260511 - fix AccountSettings 탈퇴 세션 만료 버그 (getSession → refreshSession)
    (+1 more)
metric: Weekly new payers
milestones:
- claude_ack: 2026-05-11T12:25
  done: false
  id: M11
  layer: 0
  parent_id: null
  status: queued
  text: 홈피드 게시물 클릭 -> 확대시 여백이 많이 보이지 않도록해야함 -> 예를 들어 영상 재생시 검은 여백이 많이 보이게됨.
  user_added_at: 2026-05-11T12:05
- claude_ack: 2026-05-11T18:20
  done: false
  id: M14
  layer: 0
  parent_id: null
  status: queued
  text: hugwarts app 기능을 고려한 ui 대폭 개선 -> trending ui 고려 -> 후보를 디스코드에서 투표하도록 유도
  user_added_at: 2026-05-11T16:36
- claude_ack: 2026-05-11T13:11
  done: false
  id: M12
  layer: 0
  parent_id: null
  status: queued
  text: 서버 불안정성 -> 대응안이 무엇인가 ? 우리는 실시간 디테일 로그가 필요하다. → ux
  user_added_at: 2026-05-11T13:09
- claude_ack: 2026-05-09T23:09
  done: false
  id: M10
  layer: 0
  parent_id: null
  status: queued
  text: Playwright MCP + Stop Hook research notes
- claude_ack: 2026-05-09T23:09
  done: false
  id: M4
  layer: 0
  status: queued
  text: 120 → 370 payers (10x from current) — investor-ready PMF signal
- claude_ack: 2026-05-11T18:20
  done: false
  id: M13
  layer: null
  parent_id: null
  status: queued
  text: 'business diagnosis needed


    이 산업의 핵심  병목이 무엇이냐


    ai shorts viral - 수익화 도구


    인기 상위 쇼츠 연결 - viewtools


    top-down





    기본 saas app flow 대비 누락 사항을 확인'
  user_added_at: 2026-05-11T16:35
- claude_ack: null
  done: true
  id: M0
  layer: 0
  text: 'Phase 0: Diagnostic — COGS audit + 5x payer interviews + competitor check'
- claude_ack: 2026-05-12T10:54
  done: false
  id: M0.1
  layer: 1
  parent_id: M0
  pending_confirm_at: 2026-05-12T10:54
  queued_at: 2026-05-11T16:42
  status: pending_confirmation
  text: Pull credit_logs for 37 payers → median COGS/user/month (pass if <7,000 KRW)
- claude_ack: 2026-05-09T23:09
  done: false
  id: M0.2
  layer: 1
  parent_id: M0
  status: queued
  text: Interview 5x Directors/Shortform payers — extract purchase trigger language
- claude_ack: 2026-05-12T14:42
  done: false
  id: M0.3
  layer: 1
  parent_id: M0
  pending_confirm_at: 2026-05-12T14:42
  status: pending_confirmation
  text: Competitive check — does Vrew/TypeCast own "YouTube policy compliance" angle?
- claude_ack: null
  done: true
  id: M1
  layer: 0
  text: 'Phase 1: Fix — Activation + pricing + positioning'
- claude_ack: null
  done: true
  id: M1.1
  layer: 1
  parent_id: M1
  text: Automation Studio first-session → pre-built template (output in <5 min, not
    blank canvas)
- claude_ack: 2026-05-09T23:09
  done: false
  id: M1.2
  layer: 1
  parent_id: M1
  status: queued
  text: Instrument first_output_completed event per feature
- claude_ack: 2026-05-09T23:09
  done: false
  id: M1.3
  layer: 1
  parent_id: M1
  status: queued
  text: Launch subscription tiers (9,900/29,900/79,900 KRW + Shorts cap) — credits
    become overage
- claude_ack: 2026-05-09T23:09
  done: false
  id: M1.4
  layer: 1
  parent_id: M1
  status: queued
  text: Landing page rewrite — policy compliance angle (or "10-min Shorts" if interviews
    reject compliance)
- claude_ack: null
  done: true
  id: M2
  layer: 0
  text: 'Phase 2: Acqdfuire — inbound channel validated (3+ new payers/week x 2 weeks)'
- claude_ack: null
  done: true
  id: M2.1
  layer: 1
  parent_id: M2
  text: Collect 3-5 before/after Shorts videos from paying Directors/Shortform users
- claude_ack: 2026-05-09T23:09
  done: false
  id: M2.3
  layer: 1
  parent_id: M2
  status: queued
  text: Korean creator community seeding — 3-5 communities (Naver cafe, creator Discords)
- claude_ack: null
  done: true
  id: M3
  layer: 0
  text: 37 → 120 payers (3x)
- claude_ack: null
  done: true
  id: M_DONE1
  layer: 0
  text: Core video generation pipeline (lipsync + Directors + Shortform + Cardtoon)
    working
- claude_ack: null
  done: true
  id: M_DONE2
  layer: 0
  text: First paying user reached
- claude_ack: null
  done: true
  id: M_DONE3
  layer: 0
  text: 37 total payers (as of 2026-04-08) — Directors 71.4%, Shortform 66.7% Aha
    conversion
- claude_ack: null
  done: true
  id: M_DONE4
  layer: 0
  text: Paddle global payment integration added (v1.23.432-436, 2026-05-07/08)
- claude_ack: null
  done: true
  id: M2.4
  layer: 1
  parent_id: M2
  text: New milestone
- claude_ack: 2026-05-09T23:09
  done: false
  id: M1.6
  layer: 1
  parent_id: M1
  status: queued
  text: New milestone
- claude_ack: 2026-05-12T17:41
  done: false
  id: M15
  layer: 0
  parent_id: null
  status: queued
  text: test the paddle system .
  user_added_at: 2026-05-12T17:41
name: HugwartsBanana
note: 'Korean Shorts monetization compliance pipeline. OMTM: payers/week. Core bottleneck:
  Activation (wrong Aha path — Automation Studio 403 users/1.5% vs Directors 10 users/71.4%).
  ICP: Korean Shorts creator with income urgency (personal card buyer, no procurement).
  COGS floor: 3x rule → 29,900 KRW tier requires <30 lipsync Shorts/month cap. Next
  action: M0 diagnostic sprint this week.'
parent: FromScratch
position_x: 0
repo_path: ''
status: behind
target: 5 new payers/week by Week 10
unit: payers/week
x: 585
y: 130
---

# HugwartsBanana — North Star

## Project
Next.js 15 AI multimedia content creation platform (VIDraft). Korean Shorts monetization compliance pipeline — lipsync + Directors + TTS pipeline produces face+voice compliant AI Shorts (YouTube July 2025 policy requirement).

## North Star
**Weekly new payers** — the pre-PMF stage OMTM. MAU is a vanity metric at 37-payer scale; payers/week directly tracks conversion velocity and validates the monetization hypothesis.

## Sector / ICP
- Sector: Korean short-form video production for monetized creators (not "AI tools")
- ICP: Solo Korean Shorts creator, 1K–500K subscribers, personal card buyer, income tied to posting frequency
- JTBD: "Publishable 60-90s video from script in under 10 min, monetization-compliant"
- Competitor: CapCut + Clova TTS + stock footage manual stack (synchronization pain)

## Bottleneck Diagnosis (2026-05-08)
- Stage: Activation (not acquisition)
- Automation Studio paradox: 403 users / 1.5% conversion = tinkerers with no economic urgency
- Directors: ~10 users / 71.4% conversion = output-first buyers with intent
- Aha Moment: "finished, shareable content in one session" — must fire in session 1
- COGS floor: 3x rule → 29,900 KRW tier requires <30 lipsync Shorts/month cap

## Pricing Model (target)
- Credits → overage top-up only (not primary model)
- Subscription: 9,900 KRW (10 Shorts) / 29,900 KRW (30 Shorts) / 79,900 KRW (100 Shorts)
- Value metric: Shorts/month quota (composite score 20 vs credits composite 10)

## Strategy
M0 diagnostic (interviews + COGS audit) → M1 fix (Activation + pricing) → M2 acquire (community seeding) → M3/M4 scale to 370 payers.