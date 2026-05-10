## MarketGap 프로젝트 현재 상태 (2026-04-08)

### 프로젝트 진짜 목적 (2026-04-02 확인)
위시켓을 수주 채널이 아닌 **시장가치 측정 센서**로 사용.
- 인바운드 요청 빈도 = 시장가치 proxy
- 수주/계약 의도 없음
- 프로필 변수 실험 → 인바운드 반응 측정

### 트래킹 시스템
- [market-value-tracker.md](../../docs/wishket/market-value-tracker.md) — 주간 시그널 + 실험 기록

### v1.0 베이스라인 완료 (2024-05-24 ~ 2026-04-06)
- 주간 프로필 조회: 1~3회 (7주 평균 2.0회)
- 인바운드: 10개월간 1건 (03/30, #153733 Python/Airflow Pipeline)
- 지원서 열람: 4건 (코인/색상/153636/154099)
- **#154099 지원 후 0일 만에 열람** (04/06, 클라이언트 반응 빠름)

### v1.1 적용 완료 (2026-04-08)
- Airflow 보유기술 추가 (crypto_data_pipeline DAG 구축 기반)
- 포트폴리오 5번: "Airflow 기반 암호화폐 데이터 수집 파이프라인"
- 측정 기간: 3주 (~ 2026-04-29)
- 가설: Data Pipeline 인바운드 증가

### 인프라
- Airflow 2.10.4 venv (`~/my_airflow_venv`)
- DAG: crypto_data_pipeline (4-task SUCCESS)

### 기존 파이프라인 (참조용)
- DB: docs/wishket/projects.db
- P0 지원서(153636) 03/28 열람됨
- 제안서 전략: 5섹션 프레임워크, 약관 25조 준수

### Memory Index
- [feedback_wishket_intent.md](feedback_wishket_intent.md) — 위시켓은 수주 채널 아닌 시장가치 센서
- [project_20260406_session.md](project_20260406_session.md) — #154099 지원 + Airflow DAG + 프로필 LangGraph 3개 태스크 완료
- [project_20260408_v11_applied.md](project_20260408_v11_applied.md) — v1.0 베이스라인 종료 + v1.1 적용 완료 + 측정 기간 시작 (3주)
