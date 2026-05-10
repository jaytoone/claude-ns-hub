# OffClaw Project Memory
# (구 NodeClaw → 2026-03-27 폴더명 변경)
# (OffClaw → Clone 폴더명 변경 예정 — 2026-04-16 결정, Claude 메모리 먼저 이전 후 프로젝트 폴더 rename)

## 2026-04-16 결정
- [프로젝트 rename]: `OffClaw` → `Clone` — 2026-04-16, 사용자 지시
- [실행 순서]: ① Claude 메모리(`-home-jayone-Project-OffClaw/`) → `-home-jayone-Project-Clone/`로 이전 ② `/home/jayone/Project/OffClaw` → `/home/jayone/Project/Clone` 폴더 rename

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
