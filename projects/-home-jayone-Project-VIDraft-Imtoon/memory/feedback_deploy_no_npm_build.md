---
name: No npm run build before vercel deploy
description: dev 서버 실행 중 npm run build 하지 말 것, vercel --prod 직접 실행
type: feedback
---

개발 서버 실행 중일 때 `npm run build`로 로컬 빌드하지 말 것.

**Why:** 불필요하고 (Vercel이 서버에서 빌드함), dev 서버 실행 중엔 충돌 위험 있음.

**How to apply:** 배포 시 `vercel --prod` 직접 실행. 타입 체크가 필요하면 `npx tsc --noEmit` 사용.
