# ASI Project - Core Context
_Slim pointer structure. Details → `docs/DOC_INDEX.md` → specific docs_
_Updated: 2026-03-20_

---

## Current Project State

- **Model**: AETHER-Micro 0.5B (Phase 0 Full Pre-training in progress)
- **Server**: NIPA 8×H200 143GB, nohup torchrun running
- **Training**: ~Step 1300/100K, Loss ~7.6 ← verify directly on NIPA server
- **Active features**: LTL ✅ Quality Head ✅ Self Eval ✅ MTP Loss ✅ Magic Square ✅
- **Disabled**: RLP (DDP incompatible)

## Open Issues

- **[BLOCKING/P0] scaler undefined variable** — NIPA server code may differ from repo
- **[P1] SelfEvalHead zero-gradient DDP overhead** — apply `enable_self_eval: false` + checkpoint strict=False
  - Target: `configs/train_config_full_05b.yaml`
- **[P2] WandB 401 error** — `scripts/fix_wandb_401.py` written, not applied (needs `nave94-vidraft/` format)
- **[NEW] Hook metacognition eval Phase 1** — `eval/` infra under construction
  - Plan: `docs/research/HOOK_METACOGNITION_EVAL_PLAN_20260306.md`
  - 4 metrics: ECE / Task Routing Accuracy / SCR / PRR → MCS composite score

## Key Files

- Training: `scripts/train_hf_multifile_full.py`
- Config: `configs/train_config_full_05b.yaml`
- Model: `configuration_aether_micro.py`
- Data: `/home/work/vidraft/data/raw/` (NIPA)

## Next Steps

1. [P0] Diff NIPA server scaler bug — BLOCKING
2. [P1] Apply `enable_self_eval: false` (after P0)
3. [P2] Fix WandB 401 (can run in parallel)

## MCP Tool Failure Patterns

- ❌ `agentdb_pattern-store` / `agentdb_pattern-search` — "Bridge not available" (do not use)
- ❌ `analyze_diff` / `analyze_diff-risk` — "require is not defined" (ESM/CommonJS error)
- ✅ Correct pattern tools: `hooks_intelligence_pattern-store` / `hooks_intelligence_pattern-search`
- ✅ `analyze_file-risk` — works as analyze_diff substitute

## Environment Traps

- **llama-server**: remove `-fa on` (causes SIGABRT)
- **WandB DDP**: needs `start_method="thread"` / project format `nave94-vidraft/name`
- **WSL2 crash**: keep pagefile at 48GB — reducing causes SystemCommit 100% → wslrelay overflow
- **mcp-obsidian**: `obsidian_get_recent_changes` requires Dataview plugin
- **mcp-obsidian**: `batch_get_file_contents` with 2 architecture files → 97K chars exceeded; read 1 file at a time for large docs

## Obsidian Vault Navigation (3-stage, updated 2026-03-20)

Stage 1: classify task type (0 calls) → Stage 2: `list_files_in_dir` or `complex_search` glob → Stage 3: `get_file_contents` (1 file, large docs) or `batch_get_file_contents` (max 2, small docs). `simple_search` is last resort only with `context_length=50`.
