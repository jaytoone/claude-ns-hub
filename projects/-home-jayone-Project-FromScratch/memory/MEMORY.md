# FromScratch Project Status (2026-04-27 update)

## ⏳ REMINDER (2026-04-28): Complete Syncthing toomu pairing
- [syncthing_pending.md](syncthing_pending.md) — WSL2 done, toomu install+pair TODO
- toomu: install Syncthing → add WSL2 device ID `XNRSWCK-36AXSUQ-...` → add folder `claude-inbox` → `C:\Users\toomu\claude-inbox`

---

# FromScratch Project Status (2026-04-24 — Darwin v9 35B DONE + Parcae Phase 4 SFT)

## 🔬 DARWIN v9 35B-A3B — COMPLETE (2026-04-24)
- **Goal**: KMMLU KR avg > 0.6744 via Darwin v9 LERP+CMA-ES on Qwen3.5-35B-A3B × Jackrong-Opus-Distilled
- **CMA-ES PPL**: ppl_A=4.1478 → ppl_best=4.1161 (+0.764%). 50-50 blend beats parent A in PPL (cooperative basin, unlike 27B)
- **KMMLU (no-template, limit=100)**: Merged=**0.5800**, Parent A=**0.5850**, Parent B=~0.5429
- **KEY FINDING**: Darwin v9 pure-merge LOSES to parent A by 0.5pp. Same scale-invariant pattern as 27B: PPL fitness ≠ KMMLU accuracy. Optimizing KR-PPL degrades KMMLU-aligned weights.
- **Eval pitfall**: Qwen3 chat-template BREAKS loglikelihood MCQ eval (thinking mode: 0.4907 with template vs 0.5850 without). Always eval without `--apply_chat_template` for Qwen3 KMMLU.
- **Best base for SFT**: Parent A (0.5850). Gap to SOTA: **8.94pp**.
- **Path forward**: Korean KMMLU SFT on parent A → `HAERAE-HUB/KMMLU` train split already cached at NIPA (`/home/work/.cache/huggingface/hub/datasets--HAERAE-HUB--KMMLU`). LoRA SFT r=16.
- **HF upload**: token `hf_oNATSkOGsevNREUMR` is read-only. User must create `Be2Jay/KorReason-35B-Darwin-v9` manually or provide write token.
- **Artifacts**: `/home/work/darwin_v9/merged_35b_v9_krppl/` (16 shards), genome `35b_krppl_genome.npy`
- **Doc**: `docs/research/20260424-darwin-v9-35b-a3b-results.md`

## 🔄 DARWIN × PARCAE v10 PHASE 4 — STEP 4b RUNNING (2026-04-24)
- **Step 3 done**: Korean warmup on core_block (1132.5M / 16.6% trainable). loss 12.38→0.0001, 4.1M tokens, 364s. Ckpt: `/home/work/parcae_v10/checkpoints/step3_warmup/final/step3_warmup_final.pt`
- **Step 4 done**: KMMLU SFT 2000 steps, loss 27.4→1.26, 10 subjects×~500 items=5K items, T=2 nsp=[2,2]
- **Step 5 done**: KMMLU T=1 bench avg=**0.3286** (14 subjects, 8pp above random 0.25, 34pp below SOTA 0.6744)
- **T-ablation finding**: T=1 has severe D-bias (60-92% D predictions). T=2 is optimal (avg 0.380, +5.5pp vs T=1, balanced predictions). T=4 = 0.355 (worse than T=2). **Always eval at T=2.**
- **Step 4b REGRESSED (discard)**: nsp=[0,2] mismatch vs step4's [2,2] → A-bias, T=2 dropped to 0.245. DO NOT use checkpoints in step4b_sft_ext/.
- **T=2 full bench (step4_sft_final.pt)**: avg **0.3771** (+4.85pp vs T=1). Best: Biology 0.44, Law/Chemistry/Marketing 0.42. Math: 0.30 (+10pp vs T=1).
- **SOTA target**: KR avg > **0.6744** (Rogue-v1). Current best: 0.3771 T=2. Gap: 29.7pp. Next: resume step4 with nsp=[2,2] for 10K+ steps.
- **GPU 7 constraint**: darwin_evolution_test (uvicorn port 7860) using GPU 7 — DO NOT TOUCH. GPUs 0-6 available.
- **NIPA SSH**: `ssh -i ~/.ssh/id_container -p 10533 work@proxy3.nipa2025.ktcloud.com`
- **Critical Parcae code patterns** (do not change without re-testing):
  - `create_config("parcae-small-140m", skip_initialization=True, init_orthogonal=False, **config_dict)` — saves 90+ min SVD init
  - `torch.load(ckpt_path, mmap=True, weights_only=False)` — saves 90+ min cold load for 13GB ckpt
  - `model(x, return_logits=True, num_steps_pair=nsp)` — `return_logits=True` is REQUIRED (default=False → logits=None)
  - `nsp = torch.tensor([T, 0])` for eval (T no-grad passes); `[0, T]` = T grad passes only; `[T_warm, T_grad]` = warmup + grad
  - **CRITICAL**: step4 trained with nsp=[2,2]. Any continuation MUST also use [2,2]. Using [0,2] causes nsp mismatch → A-bias regression

---

## 🎯 AETHER 5/5 RESUME TRAINING RESULT (2026-04-21 05:12 KST) — iter 3 gap-closing
- 12000 more steps (total 16000 = 6.3B tokens) + gate LR uncap (gate_lr=3e-4, no_gate_clip)
- Gate plateau broken: 0.03125 → **0.125 (=1/8)** for GDN/MLA/SW (4× increase)
- All-task wins vs vanilla: iter 2=2 → **iter 3=6** (3× improvement)
- Main 6 tasks: **arc_easy +3pp ✅, piqa +2pp ✅ NEW WIN**. hellaswag improved -6→-2pp, winogrande -4→-1pp. mmlu -5.4pp, arc_challenge -1pp still drag.
- Avg Δ: -6pp → -5pp (marginal improvement — Phase 1 freeze ceiling confirmed)
- 0 NaN across 16000 steps
- Loss min 1.77 at step 7850 resume (first sub-2.0 observation)
- Mamba2 gate still decaying to 0.004 (anomaly)
- Checkpoint: `aether_1t/checkpoints/graft_5of5_ddp_resume/final/consolidated_fp32/` (31GB)
- Report: `docs/research/20260421-aether-5of5-resume-benchmark.md`
- **Next (iter 4)**: Phase 2 LoRA+KD anchor (75% win-probability per gap-closing research) to unlock last 3-5pp on mmlu/hellaswag/winogrande

## 🏆 AETHER 5/5 BENCHMARK PASS (2026-04-20 22:48 KST) — GOAL MET
- **VERDICT: PASS** — 5/5 beats vanilla Qwen2.5-7B on ≥2 tasks (goal threshold)
- **arc_easy**: vanilla 0.79 → 5/5 **0.85** (+6pp) ✅ main win
- **arc_easy vs 3/5**: 3/5 0.77 → 5/5 0.85 (**+8pp over 3/5**) — adding Mamba2+GDN CONTRIBUTES on easy-reasoning
- **winogrande vs 3/5**: 3/5 0.70 → 5/5 0.73 (**+3pp**) — Mamba2+GDN also helps on commonsense
- **arc_challenge regression**: 3/5 was +3pp win (0.52), 5/5 = vanilla 0.49 (Mamba2+GDN costs 3pp on hard-reasoning)
- Full 6-task table: mmlu -6.4pp | hellaswag -6.0pp | arc_challenge 0 | arc_easy +6pp | piqa -2pp | winogrande -4pp | **avg Δ=-6.0pp** (still negative — undertrained)
- 5/5 wins across all 67 lm-eval tasks: 2 (goal ≥2)
- Benchmark results: `aether_1t/bench_5of5_rerun_20260420_221950/comparison.json`
- Report: `docs/research/20260420-aether-5of5-benchmark-result.md`

## 🏆 TRUE 5/5 CLEAN TRAINING (2026-04-20 ~20:20 KST) — FIRST EVER
- 16-GPU B200 × 2노드 **DDP** + Qwen2.5-7B + {5:mamba2, 10:gdn, 14:mla, 17:cross, 20:sw}
- step=175 기준 **0/22,400 NaN**, loss ce=2.17→2.08 descent, 5종 gate monotonic 성장
  - mamba2 5e-6→3.8e-4, gdn 6e-6→4.0e-4, mla 5e-6→3.1e-4, cross 6e-6→3.7e-4, sw 6e-6→3.5e-4
- Speed: ~1.25s/step, GPU 91-92% util, 54GB/180GB mem, ETA 4000 steps ~80min
- Output: `aether_1t/checkpoints/graft_5of5_ddp/`
- Log: `aether_1t/logs/ddp_5of5_node0_20260420_111612.log`
- Launch: `NODE_RANK={0,1} bash aether_1t/run_graft_5of5_ddp.sh` (nohup + disown 필수 — setsid 안됨)

### Root cause 규명 + 3-layer fix
1. **DeepSpeed → DDP** 전환 — DS는 1/8/16 GPU 모두 100% NaN, DDP는 clean
2. **freeze_qwen_layers 버그 수정** (graft_qwen.py:565) — Phase 1 helper가 `module.attn.parameters()`로 Mamba2 내부 (A_log/D/dt_bias/conv1d/in_proj/out_proj/norm)까지 unfreeze하여 Triton backward NaN 유발. 재-freeze 로직 추가 후 trainable 263.99M → 185.56M
3. **fla.chunk_gated_delta_rule → pure-PyTorch gated delta-rule** (graft_qwen.py:182 MiniGDNAttention.forward) — fp32 sequential loop ~30 lines, Triton kernel 완전 제거. fp32 autocast wrap은 NaN 해결 못했음

### 진단 체인 (중요 — 향후 세션에서 기준점)
- `aether_1t/debug_1gpu_plain_7b.py`: 1-GPU plain PyTorch 7B 5/5 test — forward CLEAN(loss=2.30), backward step 0에 16 params NaN grad 발견 → distributed wrapper 문제 아님을 증명
- `aether_1t/debug_which_nan_grad.py`: 파라미터별 NaN grad 정밀 location 규명 — Mamba2 internal 9종 + GDN q/k/β/g proj
- **중요**: 이전 "1-GPU plain PyTorch clean" 가설은 **tiny 128-dim** 모델 기준 (`mamba_gdn_minimal_repro.py`). 7B scale에서는 backward에서 Triton이 NaN 냄. scale-dependent behavior 놓쳤던 것.

### DEAD-END 업데이트
- DeepSpeed + Mamba2+GDN coexistence (모든 scale): 영구 dead-end 확정
- fla.chunk_gated_delta_rule at 7B scale: backward NaN, fp32 autocast 무효 → 우회로는 pure-PyTorch 대체

### Next
1. step 4000 완료 대기 (~20:40 KST 예상)
2. consolidate fp32 → HF 포맷 save
3. Phase 1 3/5 benchmark 파이프라인 재사용해 5/5 vs 3/5 vs vanilla Qwen 비교
4. pure-PyTorch GDN 속도 최적화 (chunked parallel scan) — 현재 sequential O(T=2048) Python loop

---

# PRIOR STATUS (earlier 2026-04-20)

## 🚀 PATH C DAY 3.4 MILESTONE (2026-04-20 12:26 UTC) — Qwen2.5-7B mcore CONVERTED
- Path 1 (NVIDIA Megatron-Bridge) ATTEMPTED but hit 2 API skews:
  (a) nvidia-resiliency-ext `get_write_results_queue` → `_get_write_results_queue` (patched)
  (b) `FileSystemWriter` kwarg `use_cached_data_structure` unexpected (blocker, couldn't bypass)
- PIVOTED to Path 2 (Alibaba Pai-Megatron-Patch) per research doc fallback plan
- Pai requires git submodule `Megatron-LM-250328`; initial `--depth 1` clone left it empty → `git submodule update --init --recursive` fixed
- Conversion command: `bash scripts/qwen2_5/run_8xH20.sh 7B <hf_src> <mcore_dst> false true bf16`
- **Wall time: 14.6 seconds** (!) on 8 GPU, PP=4 TP=1
- Output: `/NHNHOME/WORKSPACE/0426030036_A/models/Qwen2.5-7B-mcore-pai/` = 15 GB distcp-sharded mcore + tokenizer files
- Structure: `release/{__0_0..__7_1}.distcp + common.pt + metadata.json`
- DEAD-END (Bridge): don't retry Megatron-Bridge 0.5.0 + megatron-core 0.17 without matching version pins
- Next: Day 4 — wire our `nemo_qwen_hybrid.build_block_spec()` into Pai's training pipeline with `hybrid_override_pattern` for 5/5 graft

## 🚀 PATH C DAY 3.2 MILESTONE (2026-04-20 11:05 UTC) — 5/5 block spec VALIDATED on cluster
- Installed megatron-core 0.12.2 via `pip install --user --break-system-packages`
- `nemo_qwen_hybrid.py::build_block_spec()` runs successfully with real megatron-core:
  - ✅ Native `MambaLayer` (megatron.core.ssm) — unlocks Mamba2 (previously DS-blocked)
  - ✅ Our custom `GDNAttention` plugin registers — unlocks GDN (previously DS-blocked)
  - ✅ Our custom `PrefixCrossAttention` plugin registers
  - ✅ `SelfAttention` handles Qwen GQA + SlidingWindow
  - ⚠️ `MultiLatentAttention` absent in megatron-core 0.12.2 → MLA falls back to SelfAttention (needs full nvidia-nemo-toolkit 25.04 for native MLA)
- **First time 5/5 types all have working module specs** — unblocks Path C progression
- Remaining Day 3-4: (a) MLA resolution, (b) Qwen2.5-7B → Megatron-Core checkpoint conversion, (c) Gate 1 fp32 tolerance check
- Day 5-14: 5/5 Phase 1 training + benchmark vs 3/5 PASS

## 🚨 PHASE 2 GATE-COLLAPSE (2026-04-20 10:50 UTC) — STRUCTURAL, stopped at step 500
- Resumed from Phase 1 endpoint (gates 0.08-0.14). After 500 Phase 2 joint-tune steps with Qwen LR=1e-6 AETHER LR=3e-5, gates collapsed: MLA 0.140→1.27e-05 (11,000× smaller), Cross 0.081→1.05e-04 (770× smaller), SW 0.142→2.82e-04 (500× smaller).
- **Root cause is gradient direction, not magnitude**: when Qwen unfrozen, easiest path for CE minimization is gate→0 + Qwen's pretrained attention. Even extremely-low Qwen LR doesn't help because the AETHER gate gradient itself points toward collapse.
- Real fixes (require code change, not just hyperparameter tuning):
  (A) Freeze AETHER gate specifically in Phase 2 (~5 lines)
  (B) KD anchor loss (KL vs vanilla Qwen output)
  (C) LoRA-only on Qwen (freeze Qwen weights)
- **Decision**: Phase 1 endpoint is the final deliverable (PASS verdict stands). Phase 2 retry is research-level work.
- Also fixed: DS config had `offload_optimizer: cpu` which requires DeepSpeedCPUAdam (dead-end per CUDA mismatch); removed. 7.8B fits on B200 without offload.
- DEAD-END confirmed: `Phase 2 with Qwen LR=1e-6 + AETHER LR=3e-5 without KD anchor` → gate collapse, don't retry.
- Doc: `docs/research/20260420-aether-phase2-gate-collapse.md`

## 🏆 PHASE 1 3/5 BENCHMARK PASS (2026-04-20 10:27 UTC) — FINAL DELIVERABLE
- **16 B200 × 2 nodes, 12m34s wall, rc=0 clean** — Qwen2.5-7B + MLA@14 + Cross@17 + SW@20
- Gates at step 4000: **MLA 0.140, Cross 0.081, SW 0.142** (all 16-28× above contribution threshold)
- Benchmark vs vanilla Qwen (limit=100, 0-shot, 6 tasks):
  - **arc_challenge 0.52 vs vanilla 0.49 → +3pp POSITIVE** (first positive on reasoning task)
  - arc_easy −2pp, hellaswag −3pp, piqa −2pp, winogrande −7pp, mmlu −4.3pp
  - **Average Δ: −2.57pp** (matches predicted −2.5pp)
- **2/5 arm confirmed STUCK**: all gates at 0.0 → validates dead-zone fix was critical (prior −2.5pp 2/5 was "Qwen + identity passthroughs", not trained)
- VERDICT: PASS on both gates (MLA contributes ≥3 tasks: True; not disruptive ≥4 tasks: True)
- Checkpoints: `graft_3of5_phase1/final/consolidated_fp32/` (15GB, 4 HF shards)
- Next: Phase 2 joint-tune (close MMLU gap), then Path C NeMo for 5/5

## 🧹 CLUSTER DISK FREED (2026-04-20) — 14T → 1.3T used
- Removed deprecated from-scratch artifacts: full64_aether (4.5T) + full64_baseline (4.9T) + full64_phase3_kd (3.2T) = 12.7TB freed
- All superseded by Qwen graft approach (Path 3 pivot 2026-04-19)
- Current: 18.7TB free at /NHNHOME/WORKSPACE/0426030036_A

## 🔑 CLUSTER ACCESS PATTERN (2026-04-20 — memoized)
- External: `ssh genigen-b200` → lands on node DCTN-0417120013-1 (bond0=10.50.6.73)
- Inter-node: ssh 10.50.6.74 → DCTN-0417120013-2 works passwordless via IB fabric (no separate key)
- 2-node launch: script's MASTER_ADDR=10.50.6.74 = peer node (rank 0), current SSH host = rank 1
- Key rotation: refresh key via Ginigen portal → Windows Downloads → copy to ~/.ssh/DCTN-0413110535-1_key (ssh config alias)
- Full detail: `~/.claude/projects/-home-jayone-Project-FromScratch/memory/cluster_access.md`

---

# PRIOR STATUS (2026-04-18 — PHASE 3 KD TEACHER GEN IN PROGRESS)

## 💾 GINIGEN /NHNHOME QUOTA (confirmed 2026-04-18 via user portal)
- **Project `0426030036_지니젠에이아이_A` quota: 20 TB Lustre/NHNHOME shared storage**
- Workspace quota: 20 TB (same pool). User screenshot as of 10:26 KST: 10,644.1 GB used (53.2%)
- `df -h /NHNHOME` is MISLEADING (shows 3.2 TB local nvme mount); ignore for quota decisions
- `quota`/`lfs` commands unavailable — session portal is the only ground truth
- Observed failure point: writes begin returning `Disk quota exceeded` around ~17 TB usage
- Auto-prune trigger: when `du -sh /NHNHOME/WORKSPACE/0426030036_A/` > 17 TB, delete oldest Phase 3 KD intermediate checkpoint

## 🏆 PATH 3 MILESTONE: SDPA-only graft PRESERVES Qwen quality (2026-04-19 12:35 UTC) — CURRENT SUCCESS
- **Phase 1 v2 SDPA-only benchmark vs vanilla Qwen2.5-7B (limit=100, 0-shot)**:
  - MMLU abs_alg 0.51 (−0.03), HellaSwag norm 0.67 (−0.01), ARC-C norm 0.45 (−0.04), ARC-E norm 0.74 (−0.05), **PIQA norm 0.86 (+0.01!)**, Winogrande 0.74 (−0.03)
  - **Average degradation: −2.5 pp across all 6 tasks, all within 2σ stderr**
- **Root-cause-confirmed for Mamba2/GDN failures**: implementation fragility (Triton kernel + DS bf16 AMP incompat), NOT architectural disruption
- **Graft architecture itself is SOUND** — 2 SDPA layers (CrossAttn @17, SW-4K @20) + 313M trainable params preserves Qwen knowledge within noise
- **This is publishable as-is** (2/5 architectural validation, "SDPA-pure subset verified"). Precedent: Samba §4 acknowledges framework limits.

## 🎯 5/5 VERIFICATION PATHS (2026-04-19, expert-research v2) — A→C CHOSEN
- **Docs**: `docs/research/20260419-aether-5arc-verification-paths.md`, `20260419-aether-path-c-nemo-validation.md`, `20260419-aether-nemo-migration-blueprint.md`
- **Path A**: Add MLA (pure PyTorch, no Triton) → **3/5**, 2-3 days, 85% P. Precedent: TransMLA, MHA2MLA.
- **Path C**: NeMo/Megatron (NVIDIA 8B Mamba2-Hybrid released, arxiv:2504.03624) → **5/5**, 10-14 days, 80-85% P.
- **Decision**: A→C (12-16 days, guarantees 3/5 + 80% chance 5/5). Pure C has 15-20% tail risk of 0/5 after 14 days.

## 🚨 CRITICAL FINDINGS (2026-04-19 iter 10-11)
- **iter 10**: MLA and SlidingWindow were MISSING RoPE entirely. Attention was position-agnostic → would collapse at seq>64. Fixed with Qwen-compatible RoPE (theta=1e6).
- **iter 11a (bug)**: AETHERGraftLayer missing `attention_type` attribute → transformers v5.5 Qwen2Model crashes on first forward (`decoder_layer.attention_type` lookup). Fixed by inheriting from replaced Qwen layer. **Any prior run that "worked" likely bypassed this via DS internals and could fail unexpectedly**.
- **iter 11b (semantic)**: "Identity init" (gate=0) is a MISNOMER. At gate=0, new attn contributes zero BUT we've REPLACED Qwen's original attention. Net = "FFN-only layer at graft positions". Test confirmed rel_diff=0.98 between grafted (gate=0) and vanilla Qwen at forward time. Prior "−2.5pp SDPA-only" result means the new attention nearly recovered Qwen's silenced attention — an impressive training result, not an "identity preservation" trivia. For 5/5: 5 attention-silenced layers at init → bigger gap to climb.

## 🔥 LIVE-INF ITER 1-2 COMPLETE (2026-04-19 22:15 KST)
- **iter 1** commit `ce5e636`: MiniMLALayer class added (29M params, DeepSeek-V2 style, pure PyTorch). DEFAULT_GRAFT_POSITIONS now `{14:mla, 17:cross, 20:sliding_window}`.
- **CRITICAL BUG FOUND**: gate=0 AND o_proj.weight=0 both zero-init → BOTH zero gradient → layer was a gradient sink. Prior SDPA-only Phase 1 may have had attn stuck at identity the entire run. The −2.5pp benchmark could just be "Qwen + 2 identity passthroughs" not validated novel attention.
- **FIX**: Keep gate=0 (identity at init), let o_proj use default random init → gate gradient nonzero (measured 1e-3 range) → layer CAN escape identity during training.
- **iter 2** commit `pending`: NeMo migration blueprint (Day 3-14), gate_progression_stats() diagnostic wired into train log, run_graft_3of5_phase1.sh ready for cluster.
- **Next cluster actions** (for resume on B200): (1) run `bash run_graft_3of5_phase1.sh 0` on node 0 + `1` on node 1, (2) verify gate values > 1e-3 at step 500 (not stuck), (3) benchmark vs 2/5 + vanilla Qwen to prove MLA contributes.

## 🛑 MULTI-NODE + MAMBA_SSM DEAD-END (2026-04-19 10:48)
- **Confirmed**: BOTH ZeRO-3 AND ZeRO-2 hang at NCCL init post-[FREEZE] with 2-node × 8 GPU DeepSpeed + mamba_ssm/fla kernels
- **Pattern**: procs alive, GPUs 15.8 GB (Qwen loaded), 0% util, 7-20 min no log progress, hangs forever
- **Root cause (hypothesized)**: mamba_ssm/fla first-run Triton kernel compilation happens per-rank at DS init; one rank's compile takes longer → other ranks stuck at NCCL all-reduce waiting → deadlock
- **Tried and failed**:
  - ZeRO-3 + default config → hang
  - ZeRO-2 + default config → hang (same pattern)
- **Next session must try ONE of**:
  1. **Single-node 8 GPU** (no multi-node NCCL) — `torchrun --nnodes=1 --nproc_per_node=8`
  2. **Pre-compile Triton kernels** by running a warmup forward on rank 0 BEFORE deepspeed.initialize (precache)
  3. **Switch from DeepSpeed to accelerate** for simpler dist handling
  4. **Use plain PyTorch DDP** (no ZeRO, just replicated 7.8B on each GPU — 15 GB/GPU, fits)
- **Do NOT retry**: multi-node DeepSpeed + mamba_ssm + fla (confirmed dead-end 2× now)

## 📋 SESSION HANDOFF — Path 3 v2 Phase 1 hang (2026-04-19 10:30)
- **Phase 1 v2 launch HUNG** at NCCL init / post-[FREEZE] in DeepSpeed initialize, 21 min no progress, GPU 15.8 GB loaded, 0% util
- **Killed** both nodes, cluster clean
- **Root-cause hypotheses** (next session diagnoses):
  1. ZeRO-3 `set_z3_leaf_modules` missing for new AETHER classes — DS tries to partition Triton-kernel weights and deadlocks
  2. mamba_ssm/fla first-run Triton kernel compile at rank init on some ranks only → cross-rank mismatch
  3. `nan_to_num` or `grad_scrub` pattern incompatible with DS ZeRO-3 optimizer state update
- **Working artifacts (ready to resume)**:
  - `aether_1t/graft_qwen.py` — real kernels + zero-gate identity-init (smoke-verified LOCAL, 5 steps no NaN)
  - `aether_1t/train_graft_kd.py` — training wrapper
  - `models/Qwen2.5-7B/` 15 GB, mamba-ssm 2.3.1, fla 0.4.2 installed, 12 B FineWeb-Edu tokens ready
- **Resume plan (next session)**:
  1. Try ZeRO-**2** instead of ZeRO-3 (smaller model ~7.8B fits 16 B200 VRAM comfortably, avoids partition complexity)
  2. Add `deepspeed.zero.Init(config_dict_or_path=...)` context + `set_z3_leaf_modules([AETHERGraftLayer])`
  3. OR: fall back to vanilla `accelerate` FSDP (simpler than DS ZeRO-3 for small models)
- **Validated infrastructure** (NOT broken — hang is on integration layer only):
  - Graft architecture (real kernels + identity init): ✅ smoke PASS
  - Qwen base forward: ✅ loss 14 on random ids, 0.17 on real text
  - FineWeb-Edu data: ✅ 12 B tokens tokenized
  - Benchmark pipeline: ✅ vanilla Qwen scored correctly (MMLU 0.54, HellaSwag 0.68 norm)

## ✅ OPTION A KERNEL REWRITE DONE + SMOKE PASS (2026-04-19 10:05)
- Real `mamba_ssm.Mamba2` + `fla.ops.chunk_gated_delta_rule` + SDPA-window-mask deployed
- **Zero-gate identity init** (Samba/Hymba trick): each graft layer = `x + gate * norm(out)` with gate init to 0 → layer is IDENTITY at step 0, contributes only as gate grows during training
- **nan_to_num defensive scrubbing**: mamba_ssm/fla kernels can produce NaN on random-init bf16; scrub in forward (kernel out) + backward (grads)
- **Smoke test 5 steps PASSED**: loss 14.3-14.5 (matches vanilla Qwen baseline on random ids — confirms identity-start works)
- fla 0.4.2 installed (was missing from earlier install)
- Next: relaunch Phase 1 with fixed graft + conservative LR (1e-5 for gate stability)

## 🔧 PATH 3 OPTION A COMMIT (2026-04-19) — Real kernels + corrected recipe
- **Decision**: Rewrite `MiniMamba2Layer/MiniGDNAttention/MiniSlidingWindowAttention` with real kernels from `mamba_ssm` + `flash-linear-attention` packages already installed
- **Why**: Phase 1 showed placeholder implementations themselves degrade Qwen by 20-36 pp BEFORE any overfitting
- **Corrected Phase 2 recipe** (research-grounded): Qwen LR=1e-6 (20× lower), reverse KL from MiniLLM, KD weight=0.5, 3k steps not 15k, 40% FineWeb/40% SlimPajama/20% replay buffer
- **ETA**: ~1 day total (kernel swap 3h + Phase 1 12h + Phase 2 6h + bench 1h)
- **Files to edit**: `aether_1t/graft_qwen.py` (swap MiniXXX with real kernels), `aether_1t/train_graft_kd.py` (add KD + replay buffer)

## 🚨 PATH 3 PHASE 2 FAILURE — CATASTROPHIC FORGETTING (2026-04-19)
- **Phase 2 benchmark results are DISASTROUS**:
  - MMLU: 0.23 (Qwen ref ~35% at 0-shot → lost ~12pp)
  - HellaSwag norm: 0.22 (vs 78% → **−56pp, near random**)
  - ARC-Easy: 0.25 (vs 77% → **−52pp, exactly random**)
  - ARC-C: 0.31 (vs 48%), PIQA: 0.54 (vs 79%), Winogrande: 0.54 (vs 72%)
- **Root cause**: Phase 2 trained to ce=0.05 on FineWeb-Edu → overfit narrow distribution → pretrained Qwen weights drifted catastrophically. No KD anchor prevented drift.
- **Contributing factors**: (1) Qwen LR=2e-5 × 15k steps too aggressive, (2) CE-only loss = no regularization toward teacher, (3) 100% FineWeb-Edu data too narrow.
- **Recovery plan**: Consolidate + benchmark Phase 1 endpoint (ce=0.998, only 316M AETHER params changed, Qwen frozen) to see if rollback point still has Qwen knowledge. If yes → Phase 2 needs KD regularization retrain.

## 🏆 PHASE 2 CONVERGED (2026-04-19 07:47 UTC) — Grafted Qwen2.5-7B complete
- **Final CE: 0.0497** (from 1.05 start = 95.3% reduction)
- **Trajectory**: step 500=1.05 → 4000=0.30 → 7400=0.15 → 11100=0.09 → 15000=0.05
- 6 checkpoints saved (3k/6k/9k/12k/15k/final, 18 GB each = 108 GB)
- Total training time Phase 1 + Phase 2: ~5 hours wall
- **Consolidation launched** → `graft_phase2/consolidated_fp32.bin/` (HF sharded format)
- **Next**: benchmark 6 tasks (MMLU/HellaSwag/ARC-C/ARC-E/PIQA/Winogrande) vs vanilla Qwen2.5-7B reference numbers. Go/No-Go for 128K extension.

## 🚀 PHASE 1 RUNNING (2026-04-19 11:00) — Path 3 LIVE
- **Phase 1 freeze-warm LIVE on 16 B200 (2 nodes)** — Qwen2.5-7B + 6 AETHER graft, only 316M trainable
- **step 2520/8000 (31.5%) in 10 min**, ce=~2.1 stable, 4.5 s/step (2× faster than from-scratch AETHER)
- ETA: ~7 hours (total ~10h for Phase 1, was estimated 2 days — revised)
- Data: 12 B tokens ready (2.15 existing + 9.9 new FineWeb-Edu 10BT tokenized)
- `train_graft_kd.py` deployed, `run_graft_phase1.sh` launched on both nodes
- Output: `aether_1t/checkpoints/graft_phase1/step-{N}/`

## 📋 PATH 3 SESSION HANDOFF (2026-04-19 iter 4) — context-limit stop
- **State**: graft skeleton smoke-verified end-to-end; ready for real Phase 1 launch.
- **Ready artifacts on cluster**:
  - `aether_1t/graft_qwen.py` (smoke PASSED: 315.83 M trainable, loss 14.60→13.29)
  - `models/Qwen2.5-7B/` (15 GB, 4 safetensors shards)
  - mamba-ssm 2.3.1 + causal-conv1d 1.6.1 + triton 3.6.0 installed
  - Existing data: `aether_1t/data/` 17 shards ~2.15 B tokens (Qwen2.5 tokenized FineWeb-Edu)
- **Next session tasks** (in order):
  1. Write `aether_1t/train_graft.py` (copy train.py, swap AETHER1TForCausalLM→build_grafted_qwen, integrate get_param_groups_for_phase2 with DeepSpeed ZeRO-3)
  2. Launch Phase 1 freeze-warm on existing 2.15 B data (~2.3 epochs → 5 B tokens target) on 16 B200
  3. In parallel: download more FineWeb-Edu partitions + SlimPajama-long-doc, tokenize to .bin, reach 50 B total
  4. Launch Phase 2 joint-tune at seq=32K (YaRN-extended)
  5. MANDATORY baseline arm: same data, graft_positions={}, vanilla Qwen continue-train
  6. RULER-128K + LongBench benchmark, compare vs baseline
- **Budget tracking**: 16 B200 × 4 weeks ≈ $45-80 k GPU-time (per research-grounded plan)
- **Success target**: RULER-128K Δ ≥ +5p vs baseline, MMLU within −0.5%
- **Resume prompt**: `/live -i continue Path 3 publishable — build train_graft.py + launch Phase 1`

## ✅ GRAFT SMOKE PASSED (2026-04-19 iter 3) — Path 3 Unblocked
- **Smoke test verified end-to-end on real Qwen2.5-7B**: build_grafted_qwen() loads + freeze_qwen_layers() + 5-step training, loss 14.60→13.29, 0 NaN/Inf.
- **Trainable params**: 315.83 M (4.1% of 7.78B total) — matches planned 6-layer AETHER insertion exactly.
- **Installed on cluster**: Qwen2.5-7B (15 GB, 4 shards), mamba-ssm 2.3.1 (TMPDIR=/NHNHOME fix for /tmp mmap issue), causal-conv1d 1.6.1, triton 3.6.0.
- **One fix applied during smoke**: AETHERGraftLayer.forward was returning (h,) tuple → broke next Qwen layer's input_layernorm dtype check. Changed to bare tensor return. Transformers v5.5 Qwen2 expects tensor, not tuple.
- **Next iters**: data prep (50B token mix) → Phase 1 launch (freeze + 5B tokens) → Phase 2 joint (45B tokens) → RULER benchmark.

## 🎯 NEW GOAL — Path 3 Publishable (2026-04-19, user /live -i)
- **Pivoted from** "train AETHER-1T from scratch" → **"Qwen2.5-7B + AETHER 5-attn graft, workshop paper at NeurIPS ENLSP or EMNLP Findings"**
- **Research-grounded (arxiv: 2406.07522/2507.00035/2411.15242/2411.13676)**: Samba (Mistral+Mamba2 graft, +4.1% LongBench at 3.2B tokens) is direct template. Nemotron-H pattern: keep full attention at layers {0, mid, last}; hybrid in middle block.
- **Graft config**: Qwen2.5-7B 28 layers + 6 AETHER inserts at positions {5(Mamba2), 10(GDN), 17(Cross), 20(SW-4K), 23(Mamba2)}, keeping full GQA at {0, 13, 27} per Nemotron-H. Total ~7.4B params.
- **Training recipe**: Phase 1 freeze Qwen + train only new 6 layers (5B tokens, lr=1e-4). Phase 2 joint with differential LR (new=5e-5, Qwen=2e-5) for 45B more tokens. Seq 8K→32K via YaRN.
- **MANDATORY baseline**: vanilla Qwen2.5-7B continue-trained on SAME 50B data, same steps → isolates architectural Δ from fine-tune benefit. Total compute = 2× run.
- **Target**: RULER-128K +5~12p over baseline, MMLU within −0.5%.
- **Novelty**: No published paper grafts GatedDeltaNet (GDN) onto pretrained dense transformer → first-of-kind contribution claim.
- **Budget**: 16 B200 × ~4 weeks (2 arms interleaved) ≈ $45-80 k GPU-time.
- **Plan doc**: `docs/research/20260419-aether-path3-publishable-plan.md`
- **Iter 1 next action**: write `aether_1t/graft_qwen.py` (load Qwen2.5-7B + insert 6 AETHER layers + freeze helper + smoke-test 1K steps).

## 📘 KD EFFICIENCY REALITY CHECK (2026-04-18, user insight)
- **User asked**: why couldn't KD distill enough intelligence from a strong teacher?
- **Answer — KD is a 2-5× sample efficiency multiplier, NOT a 35,000× compute substitute**
  - Pretraining: N tokens to reach quality Q
  - KD: N/3 to N/5 tokens to reach quality Q
  - Our run: N/40,000 → quality gap remains ~1/8,000th
- **Token budget comparison**:
  - Our KD: 1,200 steps × mb=2 × seq=4096 = ~10 M teacher-labeled tokens
  - Published recipes (Gemma-2, MiniLLM): 10-100k steps typical for measurable benchmark lift
  - We did 1/10th to 1/100th of the KD budget needed
- **Conceptual**: teacher knowledge must FLOW THROUGH shown contexts. Student never sees the 10 T tokens of world knowledge that shaped teacher — only the 10 M tokens of teacher-on-our-FineWeb-contexts. KD transfers what's COVERED by training distribution, not everything teacher knows.
- **Our base was under-trained going INTO KD**: KD works best on a strong base being aligned to teacher (Gemma-2 recipe assumes already-good student). We KD'd a near-random weight model — like sending kindergarten student to PhD seminar.
- **Rule of thumb (tokens needed)**: coherent=1B, above-random bench=10B, competitive=100B, Mixtral-match=5T, Claude-match=15T. KD shifts each row DOWN 3×, does NOT skip rows.
- **14.7% CE improvement (5.04→4.66)** is in-line with literature (~10-20% per KD round) but doesn't translate to benchmark lift because benchmarks need emergent capabilities (scale-dependent), not polish.

## 🏆 FIRST BENCHMARK RESULTS (2026-04-18 11:47 UTC) — END-TO-END PIPELINE CONVERGED
- **lm-eval ran cleanly** on AETHER FULL32 Phase 3 KD: mmlu_abstract_algebra + hellaswag + arc_challenge (limit=50, 0-shot)
- **Numbers** (acc_norm when available):
  - HellaSwag: **0.38** (+0.13 vs random 0.25) — commonsense signal
  - MMLU abstract_algebra: **0.32** (+0.07 vs random) — weak math
  - ARC-Challenge: 0.22 (−0.03, within stderr 0.054) — indistinguishable from random
- **Honest context**: trained for only 2,200 steps total (1000 Phase 2 + 1200 Phase 3 KD) = ~134 M tokens. Mixtral 8×7B saw 35,000× more data. Results are an INFRASTRUCTURE VALIDATION, not a quality claim.
- **User's original goal fulfilled**: "train AETHER successfully and finally, compare with other compatible models with benchmarks" — training succeeded, benchmark comparison done (albeit on an under-trained model).
- **Scientific contribution stands**: 5-attention Latin square architecture Δ=0.762 CE (matched ablation, decisively beats plain-MHA) from Phase 2 validation remains the publishable finding.
- **What was fixed to unlock this**: NCCL 2-node hang, ZeRO-3 MoE partition hang, Kimi seed silent hang, KD sequential-stream data alignment, KL batchmean inflation, cross-device aux_loss accumulation, accelerate buffer dtype, lm-eval device kwarg. 8 distinct infrastructure bugs resolved end-to-end.

## 🎯 BENCHMARK INFRASTRUCTURE LIVE (2026-04-18 11:33 UTC)
- **lm-eval wrapper working end-to-end**: `aether_1t/lm_eval_wrapper.py` (AetherLM registered as model='aether')
- **SANITY PASSED**: "capital of France = Paris" (log_p=-9.56) > "Tokyo" (log_p=-11.63). Δ=2.06 nats. World knowledge retained.
- **Corrections from implementation**:
  - Actual model scale: **70B total / 22B active** (full32=32E, NOT 64E — --num_experts override only applied to --mid branch, not --full32). Memory note inflation to "140B" was wrong.
  - Buffer dtype fix: rotary cos/sin stayed fp32 after accelerate dtype conversion → explicit `buf.data.to(bf16)` loop added
  - Cross-device aux_loss accumulation (model.py:597): `aux_loss.to(total_aux_loss.device)` one-line fix for device_map=auto
- **Inference speed**: ~0.9 s/request (single-req forward pass on 8-GPU dispatch)
- **Launch**: `bash run_bench.sh` runs `mmlu,hellaswag,arc_challenge` with `limit=200` (sub-sample for speed)
- **Next**: full MMLU/HellaSwag/ARC run, compare vs Mixtral 8×7B + Qwen3.5-35B-A3B reference numbers

## ✅ CHECKPOINT CONSOLIDATED (2026-04-18 11:03 UTC)
- Phase 3 KD final ZeRO-3 checkpoint → sharded HuggingFace-style fp32 state_dict
- Path: `aether_1t/checkpoints/full64_phase3_kd/consolidated_fp32.bin/`
- 55 shards × ~5 GB each = **269.7 GB total** (67.4 B trainable elements, fp32)
- Contains `pytorch_model-{00001..00055}-of-00055.bin` + `pytorch_model.bin.index.json`
- Current disk: 13 TB / 20 TB (65%), 7 TB free
- **Next**: write custom loader + lm-eval LM wrapper for AETHER1TForCausalLM since model isn't HF-registered. Use accelerate `load_checkpoint_and_dispatch` for multi-GPU bf16 loading.

## 🏆 PHASE 3 KD CONVERGED_SUCCESS (2026-04-18 10:36 UTC)
- **Status**: Phase 3 KD training COMPLETE. rc=0. 1200 steps in 3h 40min.
- **Final loss**: ce=4.66 (endpoint), best ce=4.30 during run
- **KD loss**: 9.42 (step 20) → 7.70 (best) → 8.35 (final) — teacher alignment +16% over run
- **Improvement over Phase 2**: Δ=−0.38 CE endpoint-to-endpoint, Δ=−0.74 best-to-endpoint (14.7%)
- **Aux loss**: 0.79 → 0.22 (MoE routing converged to balanced specialization)
- **Checkpoints**: 4 saves × 754 GB = 3 TB at `aether_1t/checkpoints/full64_phase3_kd/{step-000400, step-000800, step-001200, final}`
- **Disk**: 13 TB / 20 TB (65%)
- **Pipeline validated end-to-end**: Phase 2 CE (1000) → architectural validation Δ=0.762 → Phase 3 KD (1200) w/ rank-aware sparse-topK (k=256) from Qwen2.5-72B teacher
- **Next**: benchmark `full64_phase3_kd/final` vs Mixtral 8×7B + Qwen3.5-35B-A3B on MMLU/HellaSwag/ARC/GSM8K. Need: consolidate ZeRO-3 → single-rank bf16 via `zero_to_fp32.py`, then custom lm-eval LM wrapper.

## 🚀 PHASE 3 KD LIVE (2026-04-18 06:55)
- **Status**: Phase 3 KD training RUNNING on 16 GPUs × 2 nodes with rank-aware sparse-topK (k=256) logits from Qwen2.5-72B teacher.
- **Pipeline end-to-end validated**: full64_aether/final → +1200 KD steps → ce+0.3*kd+0.01*aux
- **Step 20 reading**: ce=5.30, kd=9.42, aux=0.55, lr=8.92e-05 (warmup to 1e-4). Total weighted≈6.54, healthy.
- **KD bug caught at iter 1**: original `batchmean` reduction inflated KL by seq_len=4096× (kd=36742 would have exploded grads). Fix: `kl_elem.sum(-1).mean()` → Hinton-style per-token KL. Redeployed, relaunched, clean.
- **Logit artifact**: 226 GB at `aether_1t/logits_sparse_k256/rank_{0..15}/step_{0..1199}.pt`, schema `{values: bf16[2,4096,256], indices: int32[2,4096,256]}`.
- **ETA**: ~3.3h for 1200 steps at ~10s/step. Save every 400 steps.
- **Next**: benchmark Phase2 vs Phase3-KD on MMLU/HellaSwag/ARC/GSM8K vs Mixtral 8×7B + Qwen3.5-35B-A3B.

## 🔧 KD FIX IMPLEMENTED (2026-04-18, /live complete)
- **Status**: all 3 code artifacts shipped + unit tests passing + deployed to cluster (as staging `train_kd_v2.py` — live `train.py` locked by running Phase 3 CE).
- **gen_kd_logits.py** rewritten: `iter_rank_batches(rank, world_size)` MIRRORS `AETHERDataset.__iter__` including `min(end, len(arr) - seq_len)` truncation. Sparse output `{values: bf16 [MB,L,K], indices: int32 [MB,L,K]}` at k=256. Per-rank dir `logits/rank_{R}/`.
- **train.py::load_teacher_logits** now rank-aware: reads `{logit_dir}/rank_{rank}/step_{N}.pt`, falls back to legacy flat path. New helper `kd_loss_sparse_topk()` computes KL over top-K support via gather + log_softmax (ref arXiv:2503.16870 §4.2). Training loop dispatches sparse vs dense by file format.
- **Unit tests** (`aether_1t/tests/test_kd_rank_alignment.py`): rank alignment across 4 ranks × 3 shards = byte-identical to AETHERDataset ✓; resume skip preserves alignment ✓; sparse-KD numerical smoke (same-dist KL≈0, diff>0, temperature scaling) ✓.
- **Disk cleanup**: deleted 2.8 TB old sequential-stream logits (`logits/` + `logits_n1/` — unusable for new format). Freed disk for ~230 GB sparse regen.
- **Launch script**: `run_kd_logit_gen.sh <node>` iterates 8 ranks sequentially on each node (N0→ranks 0..7, N1→ranks 8..15). Teacher via `device_map=auto` across 8 GPUs per rank. Total 16 ranks × 1200 steps × 12 MB = ~230 GB.
- **Next**: swap `train_kd_v2.py` → `train.py` after Phase 3 CE completes (~12h remaining) → kick KD regen (~8h) → Phase 3 KD training from FULL64 checkpoint.

## 🔧 KD FIX PLAN (2026-04-18 initial)
- Per `docs/research/20260418-kd-architecture-fix.md` — superseded by implementation above.

## 🚨 NETWORK TOPOLOGY FIX (2026-04-18) — CRITICAL
- **CORRECT mapping** (supersedes all prior memory):
  - `DCTN-0417120013-2` @ `10.50.6.74` (ext: 59.150.35.1:54601, key DCTN-0417120013-2_key) — **use as node_rank=0 (master)**
  - `DCTN-0417120013-1` @ `10.50.6.73` (SSH via: ssh 10.50.6.73 from -2) — **use as node_rank=1**
- **Prior memory had the IPs SWAPPED.** Launching node_rank=1 via `ssh 10.50.6.74` loops back to same machine → 16 ranks on 8 GPUs → NCCL "Duplicate GPU detected" crash.
- Launch pattern: `ssh 59.150.35.1:54601` (Node-0) + inner `ssh 10.50.6.73` (Node-2). MASTER_ADDR=10.50.6.74.

## 🚨 CRITICAL ARCHITECTURAL ISSUE — KD DATA ALIGNMENT (2026-04-18)
- **Problem**: `gen_kd_logits.py` iterates data SEQUENTIALLY from shard start (single stream, no rank sharding). `train.py::AETHERDataset` shards data across 16 ranks (`per_rank = total_seqs // world_size`, each rank takes its own slice). At training step N, rank R sees data from rank R's partition — NOT the sequential stream position N×mb.
- **Impact**: Logit file `step_0000000.pt` contains teacher outputs for seqs[0:2] of shard 0. But at training step 0, rank 0 sees seqs[0:2], rank 1 sees seqs[per_rank:per_rank+2], etc. All ranks load the SAME logit file → rank 0 is correct, ranks 1–15 are aligned with WRONG teacher signal.
- **Solutions ranked**:
  - (A) **Smallest fix** — train Phase 3 with `world_size=1` (single-node 8-GPU). Removes sharding, matches logit gen stream. Cost: halves throughput.
  - (B) **Correct fix** — re-gen logits partitioned by (rank, step) → 16× storage ≈ 48 TB (not feasible on 3.2 TB /NHNHOME).
  - (C) **Online KD** — teacher lives on GPUs during training alongside student (needs VRAM). 72B @ bf16 = ~144 GB → fits 1 B200 but steals budget.
  - (D) **Shared-data training** — override AETHERDataset to NOT shard; all 16 ranks see same stream. DP becomes gradient-averaging over 16-copy batch (pointless) OR reduce to single rank.
- **DECISION**: defer until logit gen completes. Likely pick (A) — Phase 3 at 8-GPU single-node; 19k steps will take ~100h instead of 50h but correct KD signal.
- **Evidence log**: `aether_1t/gen_kd_logits.py:50-75` vs `aether_1t/train.py:360-392`.

## Phase 3 KD Teacher Logit Gen — 2-NODE PARALLEL (2026-04-18 00:16 KST)
- N0: `logits/` steps 0..599, at step 300/600 (~36 min in, 3.6s/step, 2.49 GB/file, 762 GB written)
- N1: `logits_n1/` steps 600..1199, launched 00:40 KST after fixing `transformers` missing on N1. At step 700/1200 (~8 min in)
- Teacher: Qwen2.5-72B-Instruct (vocab=152064 exact match to AETHER). Loaded via `device_map=auto` (~55 GB/GPU × 8 GPUs per node).
- Split done via separate output_dirs (not auto-resume collision): N1 uses `logits_n1/` to prevent `max(existing)+1` overwriting CLI `--resume_step 600`. Post-gen merge step needed.
- Data: `aether_1t/data/*.bin` (Qwen2.5 tokenized, max_id=151643 verified).
- ETA: ~2h more for both nodes to reach 600/1200 files each.

# FromScratch Project Status (2026-04-17 evening — FULL STACK UNLOCKED)

## DECISION (2026-04-17): Kimi seed 3-mitigations IMPLEMENTED locally; awaiting SSH restore to deploy
- **True root cause of 39/75**: NOT name-mismatch but extract(40L)↔train(20L) **layer-count mismatch**. Extract used default AETHER1TConfig (40L → 8 MLA × 9 + 3 = 75 keys), training used 20L (4 MLA × 9 + 3 = 39 match). Other 36 seed keys reference layers 21/25/32/39 that don't exist in the 20L model.
- **Local patches (Project/FromScratch/aether_1t/)**:
  - `train.py::load_seed_weights` — M1 bidirectional diff log + `--strict_seed_match` (raises on unmatched/shape-mismatch); M2 NaN/Inf validation with cross-rank broadcast
  - `train.py::run_dry_run_forward` — M3 one synthetic forward inside SIGALRM 120s watchdog; default ON via `--dry_run_forward`
  - `extract_kimi_seed.py` — `--preset` arg (`full`/`full32`/`mid`/`mid_64e`); use `--preset mid_64e` for current 64E×20L run to get 39/39 exact
- **Deploy sequence (needs SSH)**: scp both files → re-extract `--preset mid_64e` → launch with `--strict_seed_match` → expect `Seed weights loaded: 39 / 39 tensors` + `[DRY-RUN] OK` + first step=10 within ~2 min
- **SSH UNBLOCKED (2026-04-17 07:00)**: new container port is **54601** (not 54501), key = `~/.ssh/DCTN-0417120013-2_key`. Hostname confirms `DCTN-0417120013-2`.
- **Deployment done**: patched `train.py` + `extract_kimi_seed.py` on ginigen `/NHNHOME/WORKSPACE/0426030036_A/aether_1t/`. Seed filtered 75→39 (`models/kimi_seed_20l.safetensors`, 5.17 GB, layers {0,9,13,17}). Launch script staged: `run_64e_kimi_phase2_m3.sh` (uses `--strict_seed_match --dry_run_forward --dry_run_timeout 180`).
- **KIMI M3 RUN SUCCESSFUL (2026-04-17 07:26 UTC)**: baseline killed, Kimi 64E×20L Phase 2 launched with filtered 39-tensor seed. Log shows `Seed weights loaded: 39 / 39 tensors (matched=39, unmatched_seed=0, shape_mismatch=0)` ✓, `[DRY-RUN] OK — loss=14.1875, no hang, no NaN/Inf` ✓ in 2s, then `step=10 loss=13.13 → step=30 loss=10.83` clean descent. All 3 mitigations validated end-to-end. No NCCL hang.
- **Fix required before relaunch**: `--num_experts` CLI flag was missing from local train.py (remote version had it, local didn't). Added in parse_args and `cfg.router.num_experts = args.num_experts` override in `--mid` branch. Re-scp'd. Always scp with CLI flag parity check first.
- **Checkpoint save hang at step=200 (08:00 UTC) — FIXED**: `engine.save_checkpoint()` was guarded by `and rank == 0`, but ZeRO-3 save_checkpoint is a collective (internal all_gather to consolidate sharded params). Fix: removed `rank==0` guard on save_checkpoint, kept it only on the log.info line. Same fix applied to final checkpoint block.
- **🏆 PHASE 2 CONVERGED_SUCCESS (2026-04-17 10:45 UTC)**: AETHER 64E×20L Phase 2 full 1000 steps complete on 16-GPU B200×2-node. Final loss=5.07 (from 13.03 init, −61%), aux loss 0.79 (MoE routing stabilized). 6 checkpoints saved: 200/400/600/800/1000/final (each ~668 GB). Wallclock 2h 38min @ 9.5s/step. All Kimi 3-mitigations (M1 strict 39/39, M2 NaN/Inf, M3 SIGALRM dry-run) validated end-to-end with zero anomalies. Checkpoint save bug fixed and proven across 5 saves. `final/` at /NHNHOME/WORKSPACE/0426030036_A/aether_1t/checkpoints/64e_kimi_m3/final.
- **Next**: verify final checkpoint load-correctness → Phase 3 prep (Qwen 3.5-397B teacher logit generation for 19k-step KD).
- **DECISION (2026-04-17, user "ok then, full scales test first")**: before committing to Phase 3 KD (50h on current 64E×20L), run scale-up validation FIRST — `--full32` preset (40L × 32E, ~70B) Phase 2, 1000 steps. Reason: 20L config only activates 4/8 MLA layers (half the Latin square); 40L is the architecture's real form. If FULL32 trains cleanly in 16-GPU memory, THEN decide Phase 3 commitment on the scaled model.
- **DECISION (2026-04-17 ~20:30 KST, user /live -i for architecture validation)**: next experiment = matched Transformer+MoE BASELINE at MID 20L × 32E top-2 scale. Built `aether_1t/baseline_model.py` with StandardMHA (RoPE) + SparseMoE (top-4, 64E matching AETHER) — user caught that 32E top-2 baseline vs 64E top-4 AETHER had 4-variable confound (total params, num experts, top-k, attention). Corrected: baseline now = 20L × 64E × top-4 + plain MHA, ONLY attention differs. Launch script `run_baseline_mid.sh` uses `--mid --num_experts 64 --baseline`. Added `--baseline` flag to train.py.
- **DECISION (2026-04-17, user "/live kill. and move to the next goals")**: kill FULL32 at step=560/1000 — not needed for validation goal (FULL32 only tests AETHER at larger size, doesn't isolate attention-architecture variable). Launch matched baseline immediately to free the 1.5h that FULL32 completion would otherwise cost. Sunk cost of 560 steps accepted. Priority: validation > scale-up diagnostic.
- **DECISION (2026-04-17, user "kill + full64")**: 20L baseline already showed decisive architectural signal (Δ=0.3-0.5 at steps 200/300/400) — 20L validation complete. Pivot to FULL64 (40L × 64E, ~140B) paired test: AETHER FULL64 + baseline FULL64 at 1000 steps each. Reason: Latin-square architecture's FULL form is 40L (8 periods × 5 attention types); 20L tested only half. Kill 20L baseline at step ~400, launch AETHER FULL64 with Kimi seed (has all 8 MLA layers), then baseline FULL64 (random init, plain MHA). Total +6h for full architectural validation at the paper's actual scale.
- **ROOT GOAL (2026-04-17, user /live -i)**: "train the aether successfully and finally, compare with other compatible models with benchmarks." End-to-end scope: (1) complete FULL64 AETHER + baseline paired validation → (2) Phase 3 KD with Qwen 397B teacher (~60h) → (3) benchmark on MMLU, HellaSwag, ARC, GSM8K, HumanEval vs Mixtral 8×7B + Qwen 3.5-35B-A3B. Live-inf autonomous, convergence-only termination.
- **🏆 ARCHITECTURAL VALIDATION CONVERGED (2026-04-18 04:40 UTC) — CORRECTED**: AETHER 5-attention Latin square BEATS plain MHA decisively at matched `--full32 --num_experts 64` config (which ACTUALLY trained at 40L × **32 experts**, ~70B total / 22B active, because `--num_experts` override only applies in the `--mid` branch; `--full32` always uses its hardcoded 32E default). The dir name `full64_aether` is a misleading label from the launch script, NOT the actual expert count. **Final Δ = 0.762 CE loss at step=1000** (AETHER 5.044 vs baseline 5.806). Matched ablation is still valid — BOTH arms used identical `--full32 --num_experts 64` flags, so both are 32E. The comparison is apples-to-apples. Depth amplification confirmed: 20L Δ=0.3-0.5 → 40L Δ=0.4-0.8. Both arms have full Phase 2 checkpoints at `/NHNHOME/WORKSPACE/0426030036_A/aether_1t/checkpoints/{full64_aether,full64_baseline}/final/`. Caveats: N=1 seed, 134M tokens < 1B publication threshold, Kimi seed asymmetry (small residual bias).
- **Phase 3 KD INFRA SURVEY (2026-04-18 iter 7)**: On-disk teacher is **Qwen 3.5-122B** (39 shards, ~234 GB), NOT 397B as older memory note claimed. Decision: use Qwen 122B as teacher — skip 24h 397B download, still has trillions-of-tokens knowledge advantage over AETHER at 134M tokens. gen_kd_logits.py deployed to cluster (was missing). Checkpoints on shared storage (16+ TB of AETHER artifacts despite df showing 3.2 TB — nvme2n1p1 is local staging, real data on Lustre). Next: smoke-test Qwen 122B load on 16-GPU → small-scale logit gen → full 19k-step KD run.
- **Phase 3 TEACHER PIVOT (2026-04-18)**: Downloaded Qwen 3.5-397B (752 GB, 21 min) — then smoke-test revealed `vocab=248,320` (NOT the 151,936 the plan-spec assumed). Qwen 3.5 uses a restructured tokenizer, NOT prefix-compatible with Qwen 2.5. Data is Qwen 2.5-tokenized (empirically verified: max token ID = 151,643 in `.bin` shards). Deleted 397B (freed 752 GB). Deleted 122B (freed 234 GB, also wrong — Qwen 3.5 family). Final teacher choice: **Qwen2.5-72B-Instruct** (exact Qwen 2.5 tokenizer, ~145 GB, ~1h download, ~4h parallel logit gen on 2 nodes). Patched gen_kd_logits.py vocab constants (Qwen 2.5 = 151,643 ⊂ AETHER 152,064, 421 dormant positions padded −100). Download in progress. User authorized 16-GPU use: plan runs logit gen on both nodes in parallel (N0 first half, N1 second half of data) to halve wall-time. Decision gate at step=1000: Δ ≥ 0.3 = win, 0.1-0.3 = extend to 3000 steps, <0.1 = no advantage. Will launch when FULL32 completes (~14:15 UTC).
  3. **Pre-training dry-run forward**: run 1 synthetic forward pass BEFORE entering training loop; if hangs >60s or produces NaN loss → exit with error (not 30-min silent hang)
- **Until mitigations in place**: train WITHOUT Kimi seed (proven stable: ce 12→6.77 @ step 200)
- **Docs**: `docs/research/20260417-kimi-seed-silent-hang-diagnosis.md`, `20260417-kimi-seed-partial-transplant.md`

## AETHER MID 16-GPU + CPUAdam CPU offload — SUCCESS (2026-04-17 04:08 UTC)
- **First-ever 16-GPU + CPU offload training working** on new containers (DCTN-0417120013)
- Env: PyTorch 2.7 / CUDA 12.8 / NCCL 2.25.1 / DS 0.18.6 — matching across both nodes
- CPUAdam JIT compiles natively (no venv hack, no CUDA mismatch)
- MID 20L×32E (45B) at 4.4s/step, GPU 110 GB/GPU (40% B200), CPU 490 GB/node (22%)
- Goal: complete Phase 2 (1000 steps, lr=1e-4, seq=4096) then scale experts
- New container config: Node-0 SSH 54601 (DCTN-0417120013-2 key)
- Lustre survives: /NHNHOME/WORKSPACE/0426030036_A/ (code + data + ckpts all preserved)

## Scaling experiments (2026-04-17 afternoon) — found capacity ceiling
- Full 800B (640E × 40L): GPU OOM (optimizer states 800 GB/GPU without CPU offload)
- 710B (384E × 40L) with CPU offload: CPU OOM at fp32 master partition (peak > 2.2TB/node)
- 484B (256E × 40L): CPU OOM at peak ~1517 GB + spike
- 386B (200E × 40L): CPU 56% but GPU OOM on backward (40L activations too heavy)
- 259B (128E × 40L): same 40L activation problem (GPU hit 178 GB)
- **Working: MID 45B (32E × 20L)** — 20L activations fit, Phase 2 viable
- **Conclusion**: 40L + large E pair is bottlenecked by GPU activation memory, not CPU.
- **Next scaling**: 64E × 20L (~90B), 128E × 20L (~180B) — maintain 20L depth

## Previous MID 16-GPU success (2026-04-17 11:07, old containers)
- **첫 16-GPU 2-node 학습 성공** — 수주간 블로킹되어 있던 NCCL hang 해결
- **Config**: MID 20L×32E×h7168, ~45B params, 8B active
- **Performance**: 56s init, 3.87s/step, ce 12.08→9.69 @ step 35 (clean curve, matches 8-GPU)
- **GPU**: 87 GB/GPU × 16 (47% of B200 183GB)

### Root cause (fixed):
- NCCL 버전 불일치: Node-0(cu128) = NCCL 2.27.5 vs Node-1(NGC nv25.12) = NCCL 2.28.9
- NVIDIA IBext_v10 proprietary plugin이 cross-version handshake 불가 → 무한 hang
- **Fix**: Node-1에 venv로 matching cu128 stack 설치 (~/venv_cu128, torch 2.10.0+cu128, DS 0.18.6)
- CPUAdam JIT 실패 → GPU AdamW fallback patch (train.py)

### Working config:
- 코드 경로: `/NHNHOME/WORKSPACE/0426030036_A/aether_1t/` (Lustre 공유)
- 런치: `/NHNHOME/WORKSPACE/0426030036_A/run_mid_16gpu.sh [0|1]`
- Node-0 = 59.150.35.1 (master, bond0=10.50.6.73), Node-1 = 10.50.6.74 (worker, venv 활성)
- NCCL: IB enabled, IBext_v10, `NCCL_NVLS_ENABLE=0`, `NCCL_IB_GID_INDEX=3`

### 다음 단계: AETHER-1T (800B) 도달 경로
Progressive expert scaling (user 방침):
| Step | Config | Params | 16-GPU 예상 mem | 상태 |
|------|--------|--------|-----------------|------|
| 1 | MID 32E × 20L | 45B | 87 GB ✅ | 완료 |
| 2 | MID 64E × 20L | 75B | ~110 GB | next |
| 3 | MID 128E × 20L | 120B | ~160 GB | 경계선 |
| 4 | FULL 32E × 40L | 70B | ~105 GB | 심화 |
| 5 | FULL 640E × 40L (AETHER-1T) | 800B | ~800 GB | **EP 필요** |

### 자원 상태:
- vLLM gemma-4-26B 서빙은 16-GPU 학습 위해 종료됨 (재시작 필요 시 `/NHNHOME/WORKSPACE/...`)
- 데이터: 17 shards FineWeb-Edu 10BT (Lustre shared)
- Kimi seed: 75 tensors, 5.6GB
- Qwen 397B Teacher: 752GB downloaded
- **Kimi K2.5 seed 추출 완료** (2026-04-15): 75 tensors, 5.6GB → `kimi_seed.safetensors`
  - HF에서 9/64 shard만 선택 다운로드 (70GB) → seed 추출 → shard 삭제
- **토크나이저**: Qwen2.5 (vocab 151643, < AETHER 152064 ✅). Kimi 토크나이저는 tiktoken 의존성 문제
- **데이터**: ORPO 31K texts → 7.6M tokens, 1860 seqs @ seq_len=4096
- **DeepSpeed 0.18.9 수정**: optimizer를 config string이 아닌 직접 객체로 전달 (호환성)
- **디스크 제약**: 362GB 여유 → 800B init checkpoint (1.6TB) 불가 → ZeRO-3 메모리 직접 초기화
- **Qwen 397B Teacher**: 디스크 부족으로 미다운로드 → CE-only 학습 진행 중
- **ZeRO-3 deadlock 확정 (2026-04-15)**: MoE top-k routing이 근본 원인
  - DS 0.14.5, 0.18.9 모두 동일 → DS 버전 무관
  - nn.Parameter→RMSNorm 변환, zero.Init() 유무 모두 무관
  - NCCL 자체 정상 (all_reduce PASS, TinyModel PASS)
  - ZeRO-2 forward OK (8GPU) → ZeRO-3만 hang
  - **근본 원인**: MoE top-k routing → rank별 다른 expert 호출 → ZeRO-3 all-gather 순서 불일치
  - **해결 완료**: MoE dispatch를 deterministic loop로 재작성 (모든 expert 항상 호출)
  - **8-GPU ZeRO-3 학습 성공**: MID 35B (20L, 32E, h=7168) — ce=13.78→12.13 loss 감소 확인
  - GPU: 62-77 GB/GPU, CPU: 1.0 TB/2.2 TB, 13초/step
  - **8-GPU 한계**: 32E(35B) OK, 64E(64B) OOM, 80E(78B) OOM — fp32 optimizer가 제약
  - DS 0.14.5, MLA RMSNorm 모듈화 완료
  - **Kimi seed**: 31/75 tensors 적용 (MLA layers)
  - **KD 미적용 → 해결 중**: /NHNHOME 3.2TB 발견! Qwen 397B 다운로드 시작 (2026-04-15 20:41)
  - **Phase 2 CE-only 830 step 완료**: ce 13.0→2.8 (8-GPU ZeRO-3). 데이터 3.6회 반복 (1860 seq)
  - step 830에서 silent crash (OOM 추정, 에러 없음). save_interval=9999 설정으로 checkpoint 저장 안 됨
  - **/NHNHOME**: 20TB 쿼터, 3.2TB NVMe — 모델/체크포인트/logit 저장용
  - **FineWeb-Edu 10BT**: 17 shards, 2.15B tokens 토크나이즈 완료 (/NHNHOME)
  - **Qwen 397B Teacher**: 752GB 다운로드 완료 (/NHNHOME)
  - **16-GPU 800B full**: 모델 로딩 성공 (143GB/GPU) but ZeRO-3 partition init에서 50분+ hang
    - 2노드 NCCL 통신 자체는 정상 (all_reduce PASS)
    - 원인: 640E × 40L = 76,800 모듈의 ZeRO-3 hook 등록이 극도로 느림 (또는 deadlock)
    - dead-end: full 800B + DS ZeRO-3 + 16-GPU → partition init hang
    - dead-end: pilot 581B(640E) + DS ZeRO-3 + 16-GPU → 동일 hang
    - **확정**: DS ZeRO-3 + 640 expert = 어떤 GPU 수에서든 hang (32E까지만 작동)
    - dead-end: ExpertChunk(64개씩 묶기)도 효과 없음 — zero.Init()가 재귀 탐색
    - dead-end: zero.Init() 없이 → 581B × 8 rank = 9.3TB > 2.2TB RAM → OOM
    - **결론**: DS ZeRO-3는 대형 MoE(640E)에서 근본적 비호환. FSDP2 전환 필요
    - **FSDP2 시도**: 모델 로딩 성공(164GB/GPU, 100% util) but NCCL timeout on first step
    - FSDP2도 동일 문제: MoE 동적 routing → rank간 all-gather 순서 불일치 → deadlock
    - **확정 결론**: DS ZeRO-3도 FSDP2도 640E MoE와 비호환. Expert Parallelism(EP) 필요
    - **Next**: EP 기반 MoE 재설계 (all-to-all token dispatch) 또는 Megatron-LM

## Darwin V5 실전 실행 (2026-04-15, 지니젠 B200×8)
- **버그 2개 수정**: (1) proxy 누수 (Phase1→Phase2 best_score 오염), (2) cleanup이 best merge 삭제
- **점수 차이 근본 원인**: NIPA `num_fewshot=25` vs B200 `num_fewshot=0` (25-shot→0.64 vs 0-shot→0.52)
  - lm-eval 버전(0.4.0 vs 0.4.11), transformers 버전(4.55 vs 5.5) 무관 확인
  - B200에서 25-shot 재평가 시 NIPA 점수 재현 예상
- **동일 환경(B200, 25-shot) 최종 비교**:
  - Base: 0.5964 / V4: 0.6160 / **V5 best: 0.6237** / Instruct: 0.6459
  - **V5(0.6237) > V4(0.6160)** +0.0077 — MRI+Surrogate 효과 확인
  - **V5 = Instruct의 96.6%** — 학습 없이 Instruct 근접 달성
- **V5 best genome**: [0.432, 0.679, 0.568, 0.527, 0.831, 0.951] — V4 best와 유사 수렴
- **V6 DE 업그레이드** (2026-04-15): Differential Evolution + Restart 구현
  - DE/rand/1 교배, stagnation 감지(5 steps), population restart
  - V6 DE best: 0.6212 (25-shot) — V4(0.6160) > 하지만 V5(0.6246) < 
  - **결론**: 진화 엔진보다 초기 seed 품질이 더 중요
  - Phase 2 정체는 50문제 평가 해상도 한계 (±4%p 노이즈 > 진화 개선폭)
- **코드 위치**: 지니젠 `/home/gmail_gini/sft_workspace/darwin_v5/`

## 지니젠 B200×8 — gemma-4-26B-A4B-it vLLM 서빙 (2026-04-16)
- **모델**: google/gemma-4-26B-A4b-it (safetensors, 49GB) → `/NHNHOME/WORKSPACE/gemma-4-26b-a4b-it/`
- **vLLM**: 0.19.0, `--enforce-eager` (triton shared memory 문제 회피), TP=8, bf16
- **GPU 메모리**: 167 GB/GPU × 8 (full utilization)
- **PORT**: 8000 (OpenAI-compatible API)
- **SSH 터널**: `ssh -L 18000:localhost:8000 gmail_gini@59.150.35.1 -p 54501 -N` (port 18000 사용)
- **gsk alias**: `/home/jayone/.local/bin/gsk — `ANTHROPIC_BASE_URL=http://localhost:18000/v1`, SSH tunnel 자동 생성
- **사용**: `gsk "프롬프트"` — Claude Code에서 gemma-4-26B 직접 사용 가능

## 지니젠 클러스터 (DCTN-0413110535, B200×16)
- Node-1: 59.150.35.1:54501 (key: DCTN-0413110535-1_key), Node-2: 10.50.6.74 (내부)
- ZeRO-3 + DeepSpeedCPUAdam bf16 → 1.7 TB/node (fits 2.0 TB)

## NIPA H200 × 8 — 미사용 (사용 불가 결정)
- SSH: proxy3.nipa2025.ktcloud.com:10569 (key: id_container_nipa, user: work)
- Darwin live-inf CONVERGED (iter 21, best_score=0.952, plateau_count=7/7)
- 최종 결론: base-dominant ✓, instruct-competitive ✓, instruct-dominant ✗
- 아티팩트: docs/research/20260414-darwin-paradigm-empirical-proof.md
- 모든 GPU idle — 다음 작업 미정

# FromScratch Project Status (2026-04-03)

## AETHER-166B v3 Transplant — IN PROGRESS
- See: `memory/aether_v3_status.md` for details
- BLOCKING: fused expert key mismatch (gate_up_proj vs individual experts)
- Teacher MRI done, model shell built, weight copy failed (38697 skip)
- Next: fix gpu_utils.py for fused expert unpacking

## Darwin-35B-A3B-Opus Serving
- vLLM TP=2 on GPU 6+7, port 7947
- External: https://proxy2.nipa2025.ktcloud.com:10280
- proxy2:10280 → internal port 7947 (confirmed)

## NIPA GPU Layout
- GPU 0-5: AETHER work (currently idle)
- GPU 6-7: Darwin serving (133GB each)

## Key Paths (NIPA)
- v3 code: `/home/work/vidraft/aether-v3/`
- 397B model: `/home/work/vidraft/models/qwen3.5-397b/`
- Output: `/home/work/vidraft/aether-166b/`

## Previous Work
- Pre-AGI: `memory/aether_micro.md`
- AETHER-Micro: ablation complete, 50B pretrain done

## 2026-04-23 Darwin Decisions
- [Darwin-v9-lite]: SHIPPED as production merge artifact = v7 MRI-seed + KR-PPL 20-doc + LERP + LA-CMAES 4-step. DOCX `docs/reports/20260423_Darwin_v9Lite_Ship_LoopLLM_Direction_KR.docx` (45.4KB, 9 sections) — 2026-04-23 / reason: 2-session 24-iter CONVERGED_SUCCESS, KR avg 0.6683
- [Darwin-v10 direction]: **Darwin × Parcae hybrid** 권장 (NOT Ouro) — arxiv 2604.12946, github.com/sandyresearch/parcae 오픈소스. 3-stage Prelude(4L) + Recurrent(56L looped T×) + Coda(4L) 분해, 2-3B 토큰 stabilization, μ_rec=3 목표 — 2026-04-23 / reason: 사용자 Chrome RL AI타임스 idxno=209435 Parcae 기사가 실제 참조 소스 (Ouro 아님). 코드공개+수학적 spectral-norm stability+3-stage 재사용성 우위
- [Darwin ceiling at same-family 27B]: 27B Qwen3.5×Opus-Distilled에서 **모든 pure Darwin merge는 parent B alone (0.6724)에 −0.35~0.57pp 패배**. Rogue-v1만 +0.20pp 우위 via post-merge Korean SFT. Darwin merge is NEGATIVE-value here. v7-vs-v4 우위 주장은 잘못된 baseline 비교 — 2026-04-23 / reason: iter 13 메타분석
- [Darwin dead-ends registered]: DARE(−64%)/TIES(−2.6%)/SIGN(−10.6%)/Layer-Swap(−44%) 모두 3B divergent pair에서 LERP에 패배. Extended 15-step CMA-ES는 4-step 대비 overfit. Calibration-benchmark inverse correlation @ small PPL deltas 확인 — 2026-04-23 / reason: 24 iterations 누적, 향후 재시도 금지
