---
name: MarketGap 20260406 세션 성과
description: 위시켓 #154099 지원 제출, Airflow DAG 구축, 프로필 LangGraph 추가 — 3개 목표 완료
type: project
---

## 2026-04-06 세션 성과

### 완료 태스크 (1-3 병렬)

**1. 위시켓 #154099 지원 제출 ✅**
- 프로젝트: LangChain/LangGraph/Python/FastAPI 개발
- 630만/월, 90일, 분당 두산타워 상주, 미드 레벨
- 지원자 4명 (경쟁 낮음), 마감 04/27
- 클라이언트: 인증완료+평가우수 4.5, 누적 3.3억
- 지원서: `docs/wishket/proposal-154099.md`
- 경력 선택: VIDRAFT + 쉬모스랩
- 목적: 시장가치 측정 (열람/미팅 여부 관찰)

**2. Airflow P1 학습 + DAG 구축 ✅**
- venv: `~/my_airflow_venv` (Airflow 2.10.4)
- AIRFLOW_HOME: `~/my_airflow`
- DAG: `~/my_airflow/dags/crypto_data_pipeline.py`
- 파이프라인: fetch(CoinGecko) → transform → save → verify
- 테스트 결과: 4개 task 모두 SUCCESS, BTC $69129/ETH $2134/SOL $82 수집 성공
- 가이드: `docs/research/airflow-p1-guide.md`

**3. 프로필 LangGraph 추가 ✅**
- `docs/wishket/profile.md` 3곳 반영
  - AI/LLM 테이블: LangGraph (멀티에이전트 워크플로우) | 중상
  - 프로젝트 유형: LangGraph 기반 멀티에이전트 파이프라인 설계 및 토폴로지 실험
  - 포트폴리오: LangGraph StateGraph 5노드 코딩 에이전트

### 확인된 LangGraph/LangChain 실무 경험
- **GraphAgent**: StateGraph 5노드 (decomposer→worker병렬fan-out→aggregator→reviewer→refiner), conditional_edges, Send 병렬, SqliteSaver
- **AgentNode**: Hierarchical vs Single-Agent 토폴로지 비교 실험
- **OffClaw/NodeClaw**: LangGraph 10단계 뉴스 파이프라인 (4개 수집기 병렬)
- **korag-serve**: LangChain RAG Context Precision +48%
- **p0-rag-demo**: LangChain + Qdrant, RAGAS 0.53

### 다음 주 관찰 포인트 (시장가치 측정)
- 04/07~08: #154099 클라이언트 지원서 열람 여부
- 04/07~08: 위시켓 주간 프로필 조회수 알림
- 인터뷰 제안 시: 기술 어필 정확도 검증
- 프로필 v1.1 (Airflow) 실제 적용 여부 결정

### 주요 의사결정
- Airflow 설치: 시스템 Python 아닌 venv 격리 (의존성 충돌 방지)
- Airflow 버전: 2.10.4 (3.x는 API 변경 많음, 2.x 안정 버전 선택)
- 경력 선택: VIDRAFT(AI/ML 실무) + 쉬모스랩(ML 엔지니어) — LangGraph 연관성 높음
