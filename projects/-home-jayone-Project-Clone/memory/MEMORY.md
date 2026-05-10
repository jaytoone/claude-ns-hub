# OffClaw Project Memory
# (구 NodeClaw → 2026-03-27 폴더명 변경)
# (OffClaw → Clone 폴더명 변경 예정 — 2026-04-16 결정, Claude 메모리 먼저 이전 후 프로젝트 폴더 rename)

## 2026-04-16 결정
- [프로젝트 rename]: `OffClaw` → `Clone` — 2026-04-16, 사용자 지시
- [실행 순서]: ① Claude 메모리(`-home-jayone-Project-OffClaw/`) → `-home-jayone-Project-Clone/`로 이전 ② `/home/jayone/Project/OffClaw` → `/home/jayone/Project/Clone` 폴더 rename
- [Claude Team 가입]: 도메인 이메일 필수 (공개 도메인 불가) — 2026-04-16
- [Claude Team 요금]: Standard 연간 $20/seat/월, 최소 5석 → 5석 기준 연 $100/월(~₩145,000), 월간 $125/월(~₩181,000)
- [도메인 이메일 옵션]: 옵션1 다음 스마트워크(무료) 진행 결정 — `jaewon@vidraft.com` 생성용, Claude Team 가입이 1차 목적

## 2026-04-17 — Daum 스마트워크 MX 설정 (실제 값 확인)
- [도메인]: `mail.vidraft.net` (서브도메인 `mail` 사용)
- [이메일]: `jaewon@mail.vidraft.net`
- [관리 URL]: https://mail.daum.net/smartwork/manage (mail.daum.net 로그인 후 좌측 메뉴 "스마트워크")
- [정확한 MX 값]: `ASPMX.daum.net.` (우선순위 10), `ALT.ASPMX.daum.net.` (우선순위 20)
  - ❌ `mx1.daum.net` / `mx2.daum.net` 아님 (블로그 글 잘못된 정보)
  - ❌ TXT 도메인 인증 코드 불필요 — MX 조회만으로 소유권 확인
- [설정 기한]: 2026/05/01 (신청 후 15일) — 지나면 자동 취소
- [적용 소요]: 설정 후 48시간~1주일
- [확인]: 스마트워크 관리 페이지 [지금확인] 버튼

## 2026-04-26 — noVNC 컨테이너 WSL2 로컬로 이전 (Windows → WSL2)
- [브라우저 제어]: noVNC — WSL2 로컬 Docker (`localhost:7901/vnc.html`, MCP `http://localhost:8831/sse`)
- [외부 접근]: `http://100.66.30.40:7901/vnc.html?autoconnect=true` (Tailscale 직접 — 100.81.207.35 등에서 접근)
- [Docker]: WSL2에 Docker Engine 29.4.1 설치 완료, 이미지 `mcp-playwright:ready` 로드됨
- [컨테이너 실행]: `docker run -d --name mcp-playwright -p 7901:6901 -p 8831:8831 --entrypoint /usr/local/bin/startup.sh --restart unless-stopped mcp-playwright:ready`
- [MCP 등록]: `claude mcp add --scope user --transport sse playwright-mcp-remote http://localhost:8831/sse`
- [주의]: 포트 매핑은 8831:8831 필수 — MCP 서버가 Host 헤더로 localhost:8831 검증함 (다른 포트로 매핑 시 403)
- ❌ 구 설정 deprecated: `100.69.161.128:6901`, `http://localhost:8831/sse` (Windows Docker + portproxy)

## 2026-04-24 — 모두의 창업 지원서 v5 작성 인프라 구축 (구 설정, deprecated)
- [구 브라우저 제어]: noVNC Playwright 컨테이너 (`100.69.161.128:6901`, MCP `http://localhost:8831/sse`) ← 이제 WSL2 로컬로 대체됨
- [chrome-wrapper 경로]: `/ms-playwright/chromium-*/chrome-linux64/chrome` (not chrome-linux) — 수정 완료
- [진행 상태]: 사용자가 naver 로그인 완료 후 모두의 창업 지원서 페이지 진입, Claude가 v5 내용으로 폼 입력 진행 중

## 2026-04-20 — MX 검증 완료
- [검증]: Gmail(be2jay67) → `jaewon@mail.vidraft.net` 테스트 메일, Daum 스마트워크 받은편지함 수신 확인
- [상태]: MX 정상 작동, 도메인 이메일 사용 준비 완료
- [다음]: Claude Team 워크스페이스 생성 (`claude.ai` → Create workspace → 도메인 이메일로 가입)

## 세션 2026-03-27 — GitHub Actions + Claude Dispatch 설계

### 완료 작업
- `.github/workflows/daily_collect.yml` — GitHub Actions 수집 파이프라인 (UTC 23:00 = KST 08:00)
- `scripts/collect_only.py` — 경량 수집 스크립트 (OpenClaw/torch 없이)
- `requirements-collect.txt` — GitHub Actions용 경량 deps
- 아키텍처 확정: GitHub Actions 수집 → JSON commit → Claude Dispatch 분석 → iPhone Q&A

### 아키텍처 (확정)
```
GitHub Actions (PC 꺼져도) → collect_only.py → output/collected/YYYYMMDD.json → git push
Claude Dispatch (PC 켜져 있을 때) → JSON 읽고 분석 → iPhone Dispatch 알림/대화
```

### 미완료 (다음 세션 이어서)
- GitHub repo 생성 + push 필요
- GitHub Secrets 설정: TAVILY_API_KEY, YOUTUBE_API_KEY, NTFY_TOPIC
- Claude Cowork Dispatch 프롬프트 등록 (매일 8시 JSON 분석용)
- ntfy.sh iPhone 앱 구독 설정

### 세션 2026-03-22 인계 — env 중앙화 완료
- `~/.claude/env/shared.env` — 공유 API 키 원본 (Google Cloud, Gemini, YouTube, Tavily, MiniMax)
- 랜딩페이지: Google Forms URL / GA4 ID 미설정, GitHub Pages 미배포
- `docs/validation/launch-guide.md` — 30분 배포 체크리스트

### 핵심 문서
- `docs/research/20260325-chrome-cdp-no-extension-wsl2.md` — Chrome CDP WSL2 설정
- `docs/validation/launch-guide.md` — 랜딩페이지 배포 체크리스트
- `~/.claude/env/README.md` — 전체 키 인벤토리

# currentDate
Today's date is 2026-03-27.
