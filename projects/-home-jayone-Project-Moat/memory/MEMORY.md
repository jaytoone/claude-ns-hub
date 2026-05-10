- [MOAT Project Purpose](project_moat_purpose.md) — AI 개인 브랜딩 + YouTube 콘텐츠 + 커리어 MOAT 구축 프로젝트
- [Conceptual 통합 (2026-04-15)](project_moat_purpose.md) — Conceptual(Arena+Chat) 전략/운영을 Moat 하위로 통합. 문서: docs/conceptual/. 코드: Sales/wtp-dashboard (별도 레포 유지)

## Conceptual 현황 (2026-04-15)
- 앱: paintpoint.co.kr/conceptual (v2.2.4 라이브)
- h2 카피: "한 관점으로만 결정하고 있진 않나요?" (ICP 재타깃, 4/14 배포)
- SUGGESTED 4개: ICP 내면 언어 기반 질문으로 교체 완료
- LinkedIn 홍보 포스트(P1): Draft1 "경쟁사" 게시 완료 (4/14). 38 impressions, 1 reaction, 1 comment.
- LinkedIn 팔로업 대상: 류태섭(커피챗 OK), 김근식(주말 가능) — **김송희 제외** (2026-04-15 결정)
- Arena 반전 이슈: **전략 확정 (2026-04-17)** → Option B: Arena = ICP 필터. Standard 선택자는 무시, Conceptual 선택자만 팔로업. Autopilot 전환.
- [#001 완성본](project_moat_purpose.md) — 001-full-v2.mp4 (62.9s/30MB) 완성. fade+zoompan+glow 적용.
- **#001 DELETED (2026-04-21)** — 두 버전(mZhDON-VAns, xdDb_yDjhdk) 모두 채널에서 삭제됨. 현재 채널 남은 영상: **#002 (JwclkyQwqjg) 단 한 편**. DARWIN 콘텐츠 → Memory Hook 시리즈로 피벗 확정
- [#001 썸네일 후보](project_moat_purpose.md) — test-output/thumbnails/ (8장: 1.5s~55s). BEST: thumb-1.5s.jpg (Meva face + hook text). 모바일 YT Studio 앱으로 업로드 필요.
- [자동화](project_moat_purpose.md) — gen-001-broll.mjs에 extractThumbnails() + BGM 자동 믹싱 추가. BGM: assets/background-music.mp3 (MiniMax "launch-power").
- [BGM 생성](project_moat_purpose.md) — MiniMax Music 2.6 API로 맞춤 BGM 생성 가능. 프롬프트: "Sleek futuristic electronic, confident, tech product launch energy". assets/bgm/ 에 3종 보관.
- [#001 SEO 업데이트](project_moat_purpose.md) — 설명란에 HuggingFace 모델 카드 링크 추가 + 고정 댓글 게시 완료 (2026-04-15)
- [BGM 리서치](project_moat_purpose.md) — Pixabay API 음악 미지원. 스케일: Stable Audio API ($0.04/곡). 현재: 큐레이션 로테이션 방식.

## #002 현황 (2026-04-18)
- YouTube: https://youtube.com/shorts/JwclkyQwqjg | "3 Hooks → Claude Code Never Forgets"
- 설명란 업데이트 (2026-04-18): 1M+ devs stat, 73% AI adoption, BM25+vector specs, GitHub link
- 썸네일 후보: test-output/002-thumbnails/thumb-1.jpg (MEMORY RESET 훅 프레임) — 모바일 YT Studio 앱으로 업로드 필요
- 고정 댓글: YouTube identity verification 필요 (수동 핸드폰 단계)
- entity skill Stage 3 templates: 한국어 → 영어 헤더로 전환 완료 (2026-04-17)
- 스크립트 formula 개선 결정 (2026-04-18): [Specific number]+[Personal accusation]+[Stakes] 훅 공식 + Proof-first 구조 (#003부터 적용)

## YouTube Shorts 제작→업로드→SEO 파이프라인 (2026-04-15 확립)
1. 영상 제작: gen-001-broll.mjs (섹션 클립 → 합본 → BGM 믹싱 → 썸네일 추출)
2. 업로드: Playwright YouTube Studio 자동화 (contenteditable + execCommand 패턴)
3. SEO: 제목/설명 영어 + HuggingFace 모델 카드 링크 + 해시태그
4. 트래픽: 고정 댓글에 HF 링크 + Subscribe CTA (설명란 클릭률 낮으므로 댓글이 더 효과적)
5. 음향: TTS 100% + BGM 15% + loudnorm -14 LUFS (YouTube 표준)
6. HF 링크: https://huggingface.co/mradermacher/Darwin-35B-A3B-Opus-i1-GGUF (2026-04-15 변경)
