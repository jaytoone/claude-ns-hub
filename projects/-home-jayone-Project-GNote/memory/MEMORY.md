# GNote 프로젝트 메모리

## 현재 상태 (2026.03.04)
- **극단 퀄리티 업그레이드 완료**: ConceptScene/CommitVideo/CodeScene/ProgressBar 전면 개선
- **영상 구조**: TitleScene(5s) → ConceptScene×N(3.5s) → CodeScene + ConceptBanner 오버레이
- 17종 컨셉: rocket/bug/gear/pencil/loading/fireworks/confetti/heart/checkmark/data/star + shield/team/api/search/email/database
- `--skip-tts` 사용 시 기존 audio.mp3 자동 재사용 (cli.ts 수정)

## 영상 씬 구조
- TitleScene (5s): SHA badge, 커밋 메시지, stats, file badges + Lottie 아이콘(우45%)
- ConceptScene (3.5s×N, 최대 2개): 3중 오빗링 + 부유파티클 + 글자단위 스프링 + 페이지네이션 도트
- CodeScene (나머지): 코드 diff + 터미널 커서 + ConceptBanner 오버레이 + KeyPoints + 자막
- WipeTransition: 모든 씬 경계(타이틀↔컨셉, 컨셉↔컨셉, 컨셉↔코드)

## ConceptScene 업그레이드 내용
- OrbitRings: 3중(내6/중10역/외16), 부유파티클 12개, 글자단위 CharRevealLabel
- ConceptIndexBadge: 다중 컨셉 시 페이지네이션 도트 표시
- 아이콘 부유: sin 파형 7px 흔들림
- ConceptBanner: 타이머 진행바 + shimmer 효과 + 아이콘 맥박

## Lottie 에셋 (`public/lottie/`)
- icon-{feat/fix/refactor/docs/default/loading}.json — 커밋 타입 아이콘
- concept-{heart/checkmark/data/shield/user/code/search/email/database}.json
- fireworks.json, confetti.json

## @remotion/lottie API 주의
- `useLottie` 없음 → `delayRender/continueRender + fetch(staticFile(...))` 패턴 사용
- AnimatedBackground는 반투명(hsla 0.55)으로 해야 Lottie가 보임

## 기술 스택
- Remotion v4.0.427 + @remotion/lottie + @remotion/bundler
- Google Gemini 2.5 Flash — 내레이션 / Fish Audio speech-1.5 — TTS
- CLI: `--sha=`, `--doc=`, `--rerender`, `--regen-tts`, `--skip-tts`
- `--skip-tts`: TTS 스킵 + temp/audio.mp3 재사용
- `enableCaching: false` in render.ts bundle() — 코드 변경 즉시 반영 (webpack 캐시 무효화)
- `concurrency: 2` in renderMedia() — WSL2 OOM 방지 (기본값 사용 시 78%에서 kill)

## OrbitRings 가시성 (확정값)
- 내 6개 r200: size=7, opacity=0.60 / 중 10개 r318: size=5.5, opacity=0.35 / 외 16개 r436: size=4, opacity=0.18
- FloatingParticles: opacity 0.18±0.08 (이전 0.04±0.02에서 상향)

## .env
- /home/jayone/Project/GNote/.env (GEMINI_API_KEY, FISH_AUDIO_API_KEY)

# currentDate
Today's date is 2026-03-04.
