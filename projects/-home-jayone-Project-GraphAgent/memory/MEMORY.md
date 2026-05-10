# GraphAgent Project Memory

## 프로젝트 완료 상태
- DAG-First multi-agent coding system MVP 완성
- 13개 테스트 모두 통과 (state×6, dag×5, graph×2)
- 실제 API 실행은 미테스트 (MiniMax M2.5 API 호출 필요)

## 핵심 아키텍처
- START → decomposer → [Send×N → worker] → aggregator → reviewer → (pass→END | revise→refiner→decomposer)
- LangGraph Send API로 병렬 worker spawn
- SqliteSaver 체크포인트 (sqlite3.connect 방식)

## 중요 설계 결정
- `completed: list[str]` — plain list (add reducer 없음), aggregator만 쓰고 refiner가 [] 리셋
- `review_notes: list[dict]` — plain list, reviewer가 매 iteration 덮어씀
- `files: Annotated[dict[str,str], merge_dicts]` — 병렬 worker 안전
- `merge_dicts(a, None) → {}` sentinel: refiner가 files 리셋할 때 None 반환
- graph.py에 module-level app 인스턴스 없음 — run() 내부에서 build_graph() 호출

## 주요 파일 경로
- state.py, graph.py, main.py (루트)
- nodes/: decomposer, worker, aggregator, reviewer, refiner
- utils/dag.py: topological_batches (Kahn's BFS + cycle detection)
- tests/: test_state.py, test_dag.py, test_graph.py

## 환경
- python3 사용 (python 아님)
- pip install --break-system-packages (PEP 668 환경)
- MiniMax M2.5, base_url=https://api.minimax.io/v1
