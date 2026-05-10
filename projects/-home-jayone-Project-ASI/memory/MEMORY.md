# ASI Project - 핵심 컨텍스트
_슬림 포인터 구조: 핵심 상태만 여기. 상세는 → `docs/DOC_INDEX.md` → 특정 docs_
_업데이트: 2026-03-06_

---

## 프로젝트 현재 상태

- **모델**: AETHER-Micro 0.5B (Phase 0 Full Pre-training 진행 중)
- **서버**: NIPA 8×H200 143GB, nohup torchrun 실행 중
- **훈련**: ~Step 1300/100K, Loss ~7.6 ← NIPA 서버 직접 확인 필요
- **활성 기능**: LTL ✅ Quality Head ✅ Self Eval ✅ MTP Loss ✅ Magic Square ✅
- **비활성**: RLP (DDP 비호환)

## 미해결 문제

- **[BLOCKING/P0] scaler 미정의 변수** — NIPA 서버 코드가 레포와 다른 버전 의심
- **[P1] SelfEvalHead zero-gradient DDP overhead** — `enable_self_eval: false` + checkpoint strict=False 적용 필요
  - `configs/train_config_full_05b.yaml` 수정 대상
- **[P2] WandB 401 에러** — `scripts/fix_wandb_401.py` 작성됨, 미적용 (nave94-vidraft/ 형식 필요)
- **[완료] WSL 크래시** — 페이지파일 48GB 복원 필요 → `docs/infrastructure/WSL2_DISCONNECT_ROOT_CAUSE_20260304.md`

## 핵심 파일

- 훈련: `scripts/train_hf_multifile_full.py`
- 설정: `configs/train_config_full_05b.yaml`
- 모델: `configuration_aether_micro.py`
- 데이터: `/home/work/vidraft/data/raw/` (NIPA) → `docs/data/NIPA_FINAL_DATA_STATUS_20260212.md`

## 다음 작업

1. [P0] NIPA 서버 scaler 버그 diff 확인 — BLOCKING
2. [P1] `enable_self_eval: false` 적용 (P0 완료 후)
3. [P2] WandB 401 수정 (병렬 가능)
4. **[NEW] 훅 메타인지 평가 Phase 1** — `eval/` 디렉토리 인프라 구축 중
   - 계획: `docs/research/HOOK_METACOGNITION_EVAL_PLAN_20260306.md`
   - 4대 지표: ECE / Task Routing Accuracy / SCR / PRR → MCS 복합 점수

## 작업 원칙

- **문서/리서치 전**: `Read("docs/DOC_INDEX.md")` → 지형 파악 + 중복 확인 → search_code 정제
- **코드 수정 전**: `search_code("키워드")` → 기존 구현 파악
- **문서 생성 시**: DOC_INDEX.md 상단 테이블 등록 필수 (post-hook 강제)

## MCP 도구 실패 패턴 (즉시 참조용 — 재발견 비용 높음)

- ❌ `agentdb_pattern-store` / `agentdb_pattern-search` — "Bridge not available" (사용 금지)
- ❌ `analyze_diff` / `analyze_diff-risk` / `analyze_diff-classify` — "require is not defined" (ESM 환경 CommonJS 오류)
- ✅ **올바른 pattern 도구**: `hooks_intelligence_pattern-store` / `hooks_intelligence_pattern-search` (HNSW 384dim + BM25)
  - ToolSearch 키워드: `"intelligence pattern store"` / `"intelligence pattern search"`
- ✅ `analyze_file-risk` — analyze_diff 대체 가능 (동작 확인)
- 파이프라인 v3.3 thin orchestrator: `~/.claude/hooks/agent_nodes.md`
  - 노드 스킬: node1-ask / node2-debate / node3-paper / node4-result / node5-verify

## 환경 함정 (한 번 이상 실패한 것들)

- **llama-server**: `-fa on` 제거 필수 (SIGABRT 발생)
- **WandB DDP**: `start_method="thread"` 없으면 spawn 충돌 / project 형식 `nave94-vidraft/이름` 필요
- **WSL2 크래시**: 페이지파일 48GB 유지 필수 — 축소 시 SystemCommit 100% → wslrelay 오버플로우
  - 상세: `docs/infrastructure/WSL2_DISCONNECT_ROOT_CAUSE_20260304.md`
- **code-index**: FAISS(IndexIVFFlat) + sentence-transformers(384dim) 글로벌 멀티 프로젝트 인덱스
  - ASI 인덱스: 22,389 청크, 1,177 파일 (2026-03-05 전체 재인덱싱) ✅
  - ⚠️ 세션 시작 시 활성 프로젝트가 `claude-context-local`로 초기화됨
  - `search_code()` 전 반드시 `switch_project("/home/jayone/Project/ASI")` 필요
  - Step 1.5: 프로젝트 전환 / Step 2: 품질 검수(chunks≥1000, project_path 일치, 언어태그) → 미통과 시 강제 재인덱싱
  - ⚠️ `.local/lib/python3.12/` 노이즈 5314 chunks — `merkle_dag.py` 패치 완료(`.local`, `site-packages` 추가), 다음 세션 재시작 시 반영
  - 검색 팁: 시맨틱 모델이라 식별자 직접 검색 안 됨 → 자연어 or `search_mode="hybrid"` 사용

## 참조 문서 (설정 상세)

| 영역 | 문서 |
|------|------|
| NIPA 서버 접속 | `docs/infrastructure/NIPA_SERVER_SETUP_AND_ACCESS.md` |
| code-index MCP 패치 내역 | `docs/research/CODEBASE_INDEXING_CONTEXT_MANAGEMENT_RESEARCH_20260227.md` |
| WorldModel/GDELT | `/home/jayone/Project/WorldModel/` — H1 채택, BigQuery MCP |

## NIPA LLM API

- `qsk` alias → CCR v2.0.0 (port 3456) → SSH 터널 (8088) → llama-server
- 모델: MiniMax M2.5 230B.A10B MoE Q3_K_XL / `-fa on` 제거 (SIGABRT 방지)
- 상세: `docs/infrastructure/NIPA_SERVER_SETUP_AND_ACCESS.md`

## celi / zellij 세션

- `~/scripts/zellij-csk.sh` / `Alt+a` = fzf 복귀 / csk-01~08 (8개 세션, git 없음)
