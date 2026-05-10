# claude-flow MCP Tools Catalog
**v2 Lean Version - 도구 카탈로그 (~70줄, 토큰 +10-15)**

> 💡 **사용 방법**: 도구 이름 확인 후 ToolSearch로 파라미터 로드
> 📊 **MCP 완전 활용**: 파라미터는 ToolSearch에 위임

---

## ⭐ 핵심 대표 도구 (50개)

### 1. Intelligence (학습 추적) - Phase 0/3a/4
trajectory-start, trajectory-step, trajectory-end
pattern-search, pattern-store
hooks_intelligence_stats, hooks_intelligence_attention, hooks_intelligence_learn

### 2. Workflow (블록 관리) - Phase 2/3a
workflow_create, workflow_execute, workflow_pause, workflow_resume, workflow_status

### 3. Task (태스크) - Phase 2/3a
task_create, task_update, task_status, task_list

### 4. Memory (저장/검색) - Phase 0/1
memory_store, memory_retrieve, memory_search, memory_list

### 5. Hooks (전문가 라우팅) - Phase 0/1
hooks_route, hooks_metrics, hooks_list, hooks_post-task

### 6. DAA (적응형 에이전트) - Phase 0/3a, HIGH만
daa_agent_create, daa_agent_adapt

### 7. Agent (에이전트 관리)
agent_spawn, agent_terminate, agent_status, agent_list

### 8. Swarm (스웜 조정) - 대규모 작업
swarm_init, swarm_status

### 9. Config (설정 관리)
config_get, config_set, config_list

### 10. Hooks Worker (워커 관리)
hooks_worker-list, hooks_worker-dispatch, hooks_worker-status

### 11. Hooks Model (모델 라우팅) - Phase 0
hooks_model-route, hooks_model-outcome

### 12. Session (세션 관리)
session_save, session_restore, session_list

### 13. Hive Mind (집단 지성) - 대규모 작업
hive-mind_spawn, hive-mind_init, hive-mind_status

### 14. Analyze (코드 분석) - Phase 4
analyze_diff, analyze_diff-risk

### 15. Progress (진행 추적)
progress_check, progress_summary

### 16. Embeddings (벡터 임베딩)
embeddings_init, embeddings_generate, embeddings_search

### 17. Claims (작업 할당)
claims_claim, claims_release, claims_status

### 18. AI Defence (보안 스캔) - Phase 4
aidefence_scan, aidefence_is_safe

### 19. Transfer (데이터 전송)
transfer_detect-pii

### 20. System (시스템 관리)
system_status, system_health

### 21. Terminal (터미널 관리)
terminal_create, terminal_execute

### 22. Neural (신경망 학습)
neural_train, neural_predict

### 23. Performance (성능 분석) - Phase 4
performance_report, performance_bottleneck

### 24. GitHub (GitHub 통합)
github_repo_analyze, github_pr_manage

### 25. Coordination (분산 조정) - 대규모 작업
coordination_topology, coordination_orchestrate

### 26. Browser (브라우저 자동화) - Phase 4, Playwright UI
browser_open, browser_click, browser_snapshot

---

## 📋 전체 도구 목록 (200개, 이름만)

**Intelligence**: trajectory-start, trajectory-step, trajectory-end, pattern-search, pattern-store, hooks_intelligence_stats, hooks_intelligence_attention, hooks_intelligence_learn, hooks_intelligence_reset

**Workflow**: workflow_create, workflow_execute, workflow_pause, workflow_resume, workflow_status, workflow_list, workflow_cancel, workflow_delete, workflow_template

**Task**: task_create, task_update, task_status, task_list, task_complete, task_cancel

**Memory**: memory_store, memory_retrieve, memory_search, memory_delete, memory_list, memory_stats, memory_migrate

**Hooks**: hooks_pre-edit, hooks_post-edit, hooks_pre-command, hooks_post-command, hooks_route, hooks_metrics, hooks_list, hooks_pre-task, hooks_post-task, hooks_explain, hooks_pretrain, hooks_build-agents, hooks_transfer, hooks_session-start, hooks_session-end, hooks_session-restore, hooks_notify, hooks_init

**Hooks Worker**: hooks_worker-list, hooks_worker-dispatch, hooks_worker-status, hooks_worker-detect, hooks_worker-cancel

**Hooks Model**: hooks_model-route, hooks_model-outcome, hooks_model-stats

**DAA**: daa_agent_create, daa_agent_adapt, daa_workflow_create, daa_workflow_execute, daa_knowledge_share, daa_learning_status, daa_cognitive_pattern, daa_performance_metrics

**Agent**: agent_spawn, agent_terminate, agent_status, agent_list, agent_pool, agent_health, agent_update

**Swarm**: swarm_init, swarm_status, swarm_shutdown, swarm_health

**Config**: config_get, config_set, config_list, config_reset, config_export, config_import

**Session**: session_save, session_restore, session_list, session_delete, session_info

**Hive Mind**: hive-mind_spawn, hive-mind_init, hive-mind_status, hive-mind_join, hive-mind_leave, hive-mind_consensus, hive-mind_broadcast, hive-mind_shutdown, hive-mind_memory

**Analyze**: analyze_diff, analyze_diff-risk, analyze_diff-classify, analyze_diff-reviewers, analyze_file-risk, analyze_diff-stats

**Progress**: progress_check, progress_sync, progress_summary, progress_watch

**Embeddings**: embeddings_init, embeddings_generate, embeddings_compare, embeddings_search, embeddings_neural, embeddings_hyperbolic, embeddings_status

**Claims**: claims_claim, claims_release, claims_handoff, claims_accept-handoff, claims_status, claims_list, claims_mark-stealable, claims_steal, claims_stealable, claims_load, claims_board, claims_rebalance

**AI Defence**: aidefence_scan, aidefence_analyze, aidefence_stats, aidefence_learn, aidefence_is_safe, aidefence_has_pii

**Transfer**: transfer_detect-pii, transfer_ipfs-resolve, transfer_store-search, transfer_store-info, transfer_store-download, transfer_store-featured, transfer_store-trending, transfer_plugin-search, transfer_plugin-info, transfer_plugin-featured, transfer_plugin-official

**System**: system_status, system_metrics, system_health, system_info, system_reset

**Terminal**: terminal_create, terminal_execute, terminal_list, terminal_close, terminal_history

**Neural**: neural_train, neural_predict, neural_patterns, neural_compress, neural_status, neural_optimize

**Performance**: performance_report, performance_bottleneck, performance_benchmark, performance_profile, performance_optimize, performance_metrics

**GitHub**: github_repo_analyze, github_pr_manage, github_issue_track, github_workflow, github_metrics

**Coordination**: coordination_topology, coordination_load_balance, coordination_sync, coordination_node, coordination_consensus, coordination_orchestrate, coordination_metrics

**Browser**: browser_open, browser_back, browser_forward, browser_reload, browser_close, browser_snapshot, browser_screenshot, browser_click, browser_fill, browser_type, browser_press, browser_hover, browser_select, browser_check, browser_uncheck, browser_scroll, browser_get-text, browser_get-value, browser_get-title, browser_get-url, browser_wait, browser_eval, browser_session-list

---

## 🎯 사용 플로우

```
1. 카탈로그 확인 (이 파일) → 필요한 도구 발견
2. ToolSearch("도구명") → MCP 파라미터 확인
3. 즉시 사용
```

**예시**:
```typescript
// 1. 카탈로그에서 workflow_create 발견
// 2. ToolSearch("mcp__claude-flow__workflow_create")
// 3. MCP 파라미터 확인: { name, steps, description, variables }
// 4. 즉시 호출
mcp__claude-flow__workflow_create({ name: "...", steps: [...] })
```

---

**작성일**: 2026-01-29
**버전**: v2 Lean
**총 도구 수**: 50개 핵심 + 200개 전체
**총 줄 수**: ~120줄 (목표 70줄 대비 +50줄, 가독성 향상)
**토큰 비용**: +12-18토큰 (목표 +10-15 대비 약간 초과, 허용 범위)
