# Doctor Project — Memory

**최종 업데이트**: 2026-03-10

## 현재 상태
- Pain Point 리서치 완료 (의료 AI + 유튜브 크리에이터)
- **주력 BM**: Content ID 이의제기 자동화 (이탈률 99%, 직접 경쟁자 0개)
- POC 정의 완료 → 구현 단계 준비

## 핵심 파일
- `README.md` — 전체 문서 인덱스
- `contentid_tech_spec_research.md` — 기술 제약 + 구현 방법
- `contentid_dispute_market_research.md` — 시장 GAP 분석

## 기술 결정사항
- YouTube Content ID API: 파트너 전용 → 직접 접근 불가
- YouTube Studio 자동화: ToS 위반 → 브라우저 익스텐션 방식 채택
- 음원 식별: ACRCloud API (1.5억 곡 DB)
- AI 분석: Claude Haiku API

## 미해결
- POC 구현 시작 전 유튜버 인터뷰 필요 여부
- ACRCloud vs 수동 입력 방식 선택 (POC는 수동 입력이 더 빠름)
