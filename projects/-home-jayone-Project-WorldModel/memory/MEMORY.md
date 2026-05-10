# WorldModel Project Memory

## 현재 상태 (2026-03-05)
- GDELT BigQuery ETL → RAG Memory → A/B 평가 파이프라인 1사이클 완료
- 실험 결론 구체화 완료 (4축 채점, 시계열, 방법론 한계)

## 핵심 수치
- Information Gain: 평균 +77% (5→78/100점)
- 최강: Q3 파키스탄 +95% | 최약: Q4 ICT +50%
- Novelty 축 최고 88%, Specificity 80%

## GCP 설정
- 프로젝트: gen-lang-client-0579037685
- 서비스 계정 키: /home/jayone/Project/OneViral/keys/vertex-ai-service-account.json
- GDELT 올바른 경로: gdelt-bq.gdeltv2.events (bigquery-public-data 아님 → 403)

## 스크립트
- 01_gdelt_etl.py --days 7 --min-articles 5 → data/world_snapshot.json
- 02_build_world_memory.py → data/memory_payload.json
- 03b_evaluate_local.py → data/eval_results/ (로컬, API 불필요)
- 03_evaluate_world_model.py → 실 LLM A/B (ANTHROPIC_API_KEY 필요) ← 미실행

## 미해결 / 다음 작업
1. [최우선] 03_evaluate_world_model.py 실행 — 실 LLM 응답 격차 측정
2. 01_gdelt_etl.py cron 자동화
3. WorldModel 전용 rag-memory 인스턴스 격리
