## GraphPrompt 프로젝트 현재 상태 (2026-03-19 업데이트)

### 폴더 변경 완료 (2026-03-19)
- MiddleAI → GraphPrompt 폴더 변경 완료
- 경로: /home/jayone/Project/GraphPrompt/
- CLAUDE.md, DOC_INDEX.md 내부 참조 업데이트 완료

### P0 포트폴리오 구현 완료 (2026-03-18)
- **korag-serve/**: 한국어 온프레미스 LLM 서빙 벤치마크 (압도적 포트폴리오)
  - Ollama: 95.5 tok/s, 101ms TTFT (RTX 3070 Ti, Qwen2.5-3B Q4_K_M)
  - vLLM: 35.8 tok/s, 1,611ms TTFT (float16, WSL2)
  - RAGAS 개선: Context Precision +48% (리랭킹 적용)
  - 결과 JSON: korag-serve/results/rtx3070ti/
- **p0-rag-demo/**: LangChain + Qdrant in-memory + MiniMax M2.5 RAG (RAGAS 0.53)
- **p0-agent-demo/**: CrewAI 3-에이전트 (Researcher+Analyst+Writer)
- **p0-vllm-serving/**: vLLM 서버 + 벤치마크 스크립트

### MiniMax M2.5 통합 패턴
- API KEY: /home/jayone/Project/PaintPoint/painpoint-dashboard/.env.local 참조
- base_url: https://api.minimax.io/v1 (OpenAI-compatible)
- `<think>` 태그 strip 필수: `re.sub(r"<think>[\s\S]*?</think>\s*", "", text).strip()`
- CrewAI: LLM_MODEL_STRING = "openai/MiniMax-M2.5" + base_url

### p0-legal-rag 벤치마크 현황 (2026-03-18 업데이트)
- eval/golden_set/annotations.json v1.1: alt_keywords 추가로 매칭 개선
- eval/cache/: LLM 탐지 결과 캐시 (재현성 보장)
- 현재 결과: F1=0.457, Recall=0.792 (목표 F1>=0.75 미달)
- C001 (리스크 계약서): F1=0.538, Recall=0.875 (8개 중 7개 탐지)
- C003 (NDA): Recall=1.000 (2개 모두 탐지)
- 남은 개선: Precision 향상(프롬프트 조정), Level Macro F1 개선, 골든셋 확장

### 다음 작업 우선순위
- p0-legal-rag Precision 개선 (프롬프트 조정으로 FP 감소)
- 위시켓 POC 제안 (200~400만원 계약서 분석 POC)
- H200 x 8 벤치마크 (회사 서버, Qwen2.5-72B)

### 기술 환경 (RTX 3070 Ti WSL2)
- WSL2 / Python 3.12 / CUDA 12.8
- vLLM 0.17.1 (enforce_eager=True, python3.12-dev 설치 필요)
- Ollama 0.17.7
- kubectl: ~/bin/kubectl (full path 필요)

### 프리랜서 플랫폼 현황
- **위시켓**: 지원 #4까지 완료. BOOST 미가입 (첫 계약 후 검토)
- **Upwork**: 온보딩 완료, Connects 구매 필요, 사진 교체 필요
- **Fiverr**: @jaewonjang129, 기그 1개, Portfolio 12개, Profile Strength 10/12

### Stop hook
- GraphPrompt (tsc --watch) -> 즉시 approve
