# Imtoon Project Memory

## 현재 상태 (2026-04-06)
- **최신 커밋**: v1.7.18 — xAI Grok Imagine 전환 완료
- **Vercel 배포 완료**: https://imtoon.vercel.app
- **서버 실행 중**: http://localhost:3000 (CWD: Imtoon)
- **폴더 경로**: `/home/jayone/Project/VIDraft/Imtoon`

## 최근 변경 내역 (v1.7.x)
- v1.7.21: 카드툰 영상변환 Kling→Grok reference-to-video 전환 (30크레딧 고정, 폴링 제거)
- v1.7.20: NotificationToast createPortal 수정 (removeChild crash 해결)
- v1.7.18: generate-nano-banana/pro → xAI grok-imagine-image 전환
- v1.7.17: CreditTokenIcon alias, 🫐→SVG 교체, 로그인 버그 fix
- v1.7.16: BlueberryIcon→크레딧토큰, FAQ/i18n 리브랜딩
- v1.7.9: SlimSidebar + MobileSidebar + page.tsx에서 선거 탭 완전 제거

## 프로젝트 구조
- Next.js 15 App Router (`src/app/[lang]/`)
- **Supabase 프로젝트**: `icujxxvskipacrboaxha` (production, .env.local)
  - `.env.vercel.local`의 `rteypbamkblsxhgbqwbf`는 별도 프로젝트 — 혼동 주의
- Edge Function 배포: `supabase functions deploy <name> --project-ref icujxxvskipacrboaxha`
- i18n: ko/en 지원
- Stop hook: playwright-session-4 고정 사용

## 미해결 이슈
- 폰트 404: `cdn.jsdelivr.net/.../NanumSquareNeo-Variable.woff` (외부 CDN, 비기능적)
- git status에 D(deleted) 파일 다수 존재 (public/, scripts/ 등)
  → Windows에서 복사 완료, rsync로 src/ 복원됨

## 핵심 환경 정보
- DB Host: `aws-1-ap-northeast-2.pooler.supabase.com:5432`
- Vercel URL: `https://imtoon.vercel.app`
- playwright-session-4 고정 (stop hook 요구사항)
