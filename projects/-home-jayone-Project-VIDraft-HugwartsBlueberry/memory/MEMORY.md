# HugwartsBlueberry Project Memory

## 현재 상태 (2026-03-04)
- **최신 커밋**: v1.7.9 (26aab43) — AI 선거 탭 제거
- **Vercel 배포 완료**: https://hugwarts-blueberry.vercel.app
- **서버 실행 중**: http://localhost:3000 (CWD: HugwartsBlueberry)

## 최근 변경 내역 (v1.7.x)
- v1.7.9: SlimSidebar + MobileSidebar + page.tsx에서 선거 탭 완전 제거
- v1.7.8: SlimSidebar 인라인 확장 (no overlay) + pf-hamburger 제거
- v1.7.7: 홈피드 4컬럼 그리드 breakpoints 수정
- v1.7.6: ProtoFeedCommunity 홈피드 교체 (USE_PROTO_FEED=true)

## 프로젝트 구조
- Next.js 15 App Router (`src/app/[lang]/`)
- Supabase Auth + DB (프로젝트: icujxxvskipacrboaxha → rteypbamkblsxhgbqwbf)
- i18n: ko/en 지원
- Stop hook: playwright-session-4 고정 사용

## 미해결 이슈
- 폰트 404: `cdn.jsdelivr.net/.../NanumSquareNeo-Variable.woff` (외부 CDN, 비기능적)
- git status에 D(deleted) 파일 다수 존재 (public/, scripts/ 등)
  → Windows에서 복사 완료, rsync로 src/ 복원됨

## 핵심 환경 정보
- DB Host: `aws-1-ap-northeast-2.pooler.supabase.com:5432`
- Vercel URL: `https://hugwarts-blueberry.vercel.app`
- playwright-session-4 고정 (stop hook 요구사항)
