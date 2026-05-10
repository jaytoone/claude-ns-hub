## MiddleAI / korag-serve 현재 상태 (2026-03-18)

### 프로젝트 위치
- /home/jayone/Project/MiddleAI/korag-serve/
- 한국어 온프레미스 LLM 서빙 벤치마크 포트폴리오

### RTX 3070 Ti 실측 결과 (2026-03-18)
- Ollama (Q4_K_M): 95.5 tok/s, 101ms TTFT, 3.2GB VRAM
- vLLM (float16): 35.8 tok/s, 1,611ms TTFT, 7.7GB VRAM
- 결론: 8GB GPU에서 Ollama가 2.7배 빠름

### RAGAS 개선 결과
- Baseline composite: 0.5304 → Improved: 0.5866 (+11%)
- Context Precision: 0.35 → 0.52 (+48%)
- Context Recall: 0.56 → 0.71 (+27%)
- 리랭커: cross-encoder/ms-marco-MiniLM-L-6-v2 (Top-9→Top-3)
- LLM: MiniMax-M2.5 (API KEY: /home/jayone/Project/PaintPoint/painpoint-dashboard/.env.local)

### 미완료 벤치마크
- H200 × 8 (회사 서버) - Qwen2.5-72B, vLLM TP=8
- Jetson Orin - Qwen2.5-3B, Ollama

### 다음 프로젝트 후보 (MiniMax M2.5 특화)
1. AI 보고서 자동 생성 에이전트 (위시켓 3,000~5,000만원)
2. 폐쇄망 기업 지식 챗봇 (Upwork $150~200/hr)
3. 계약서 심층 분석 API (M2.5 Reasoning)

### 환경
- WSL2 / Python 3.12 / CUDA 12.8 / Ollama 0.17.7 / vLLM 0.17.1
- vLLM 주의: enforce_eager=True, python3.12-dev 필요
- MiniMax base_url: https://api.minimax.io/v1
