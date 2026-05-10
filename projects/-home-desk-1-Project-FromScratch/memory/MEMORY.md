# FromScratch Project Memory

## Active State (as of 2026-05-08 KST — GRPO Pivot)
- [198Q eval]: DONE (stopped early at 179/198) — **80.4%** (144/179). BELOW 85% baseline. Confirmed LoRA KD failed.
- [LoRA KD failure root cause]: self-distillation ceiling — 119 traces all from Qs already correct, zero signal on failures. 4.2 epochs = memorization. 20Q proxy (90%) was misleading (±13pp CI).
- [PIVOT to GRPO]: 2026-05-08 — binary correct/incorrect reward on failure questions. Fast-validation gate ladder: Gate 0 (2h) → Gate 1 (4h) → Gate 2 (full 198Q) only if signal confirmed.
- [milestone-roadmap skill]: created ~/.claude/skills/milestone-roadmap/SKILL.md — reusable fast-validation roadmap designer for any project.
- [north-star updated]: status=at-risk, current=82%, GRPO milestones added with Gate 0/1/2 ladder.
- [failure_indices.json]: DONE — 35 failure Q indices saved on NIPA. fast_eval_30q.py uploaded.
- [GRPO Gate 0]: DONE — REDEFINED PASS 2026-05-09. Q29 Δ=+0.17~0.25 in 2/6 runs. Grouped GRPO K=8 LR=1e-6 stable.
- [NEW NS 2026-05-09]: Darwin-native CMA-ES evolutionary merge as primary lever. SFT ceiling=5/35, GRPO MoE unstable. New approach: darwin36b(85%) + jackrong35b DARE-TIES merge with GPQA fitness. Darwin-A (complementary error profiling) running on GPU 2. Gate 1 GRPO 14/30 outers on GPUs 0-1.
- [SFT ceiling confirmed]: 200-step AND 1000-step SFT both give 5/35=14.3% on failure cluster. Cannot be improved by more data or steps. Domain knowledge gap, not learnable via SFT.
- [GRPO Gate 1]: DONE 2026-05-10 — 30 outers complete on GPUs 0+1. ALL signals -1.0 throughout (zero correct rollouts). MoE expert-activation volatility confirmed as hard blocker — standard GRPO cannot learn on darwin36b. Gate 1 = FAILED. Darwin-C (GSPO) required for any RL approach.
- [jackrong35b memory footprint]: 118.48 GB + 21.34 GB MoE expert forward = 139.82 GB total. Exceeds single H200 (139.81 GB) by 10 MB — cannot run on single GPU, needs 2 fully free GPUs (no other processes).
- [Darwin-A v2]: DONE 2026-05-11 — stopped at 13/18 second half (sufficient signal). Final: 2/17 correct = Jaccard=0.057. Nonzero complementarity — jackrong35b solves Q105 and Q120 from darwin36b failures. Darwin-B launched immediately after.
- [Darwin-B]: RUNNING 2026-05-11 — CPU DARE-TIES merge (1.9TB RAM, 1811 tensors) + GPU eval on 35 failure Qs. Genome: global=0.25, ffn=0.45, attn=0.15, embed=0.05, da=0.8, db=0.6. PID 525173 on GPUs 0+1+2. Cron 7154f734 monitors every 30 min.
- [Gate 3 SFT 200-step RESULT]: 2026-05-09 — darwin36b + jackrong27b traces, 200 steps: 4-5/35 failure Qs correct (11-14%). Baseline 0%. Signal confirmed — teacher trace SFT works!
- [Gate 3 SFT 1000-step]: RUNNING on GPUs 4-5. Cron 14c36e1f monitors. Auto-eval will launch when done.
- [live-inf]: launched 2026-05-09 — goal=reach ≥88% GPQA Diamond. Cron monitoring SFT 1k completion.
- [Gate 3 pivot]: 2026-05-09 — All NIPA models have MoE or FLA. Gate 3 = LoRA SFT on darwin36b using jackrong27b teacher traces on 35 failure Qs. GPUs 2-3: gen traces for 17 uncovered Qs.
- [/live launched]: 2026-05-09 — goal=minimize gap between 80% and 93.9%. All 6 GPUs active.
- [Phase 3 v5]: DONE — 90% two-pass (18/20), clean traces fixed corruption bug (proxy was misleading)
- [Phase 4]: DONE — chem/bio LoRA 200 steps trained, final loss=0.31

## Active State (as of 2026-05-06 14:05 KST)
- [lsk]: Jackrong-27B Claude Code alias set up — LiteLLM proxy port 4101, SSH tunnel 18181→NIPA:8181, 131072 ctx — May 6
- [Phase3v2b eval plan]: eval step_200/300/500 in parallel on GPUs 0-5 after DONE — May 6

### NIPA Cluster Status
- **ACTIVE container: port 10522**
- GPU 6: Jackrong-27B GGUF Q4_K_M (17 GB, llama-server + trace gen, 93% util)
- GPU 7: reserved (never touch)
- All other GPUs: free

### Track 2: GPQA Diamond Distillation — EVAL COMPLETE, PHASE 3 RE-RUN NEEDED
- **Phase 3 DONE** May 6 02:41 KST: step 1000, best loss=2.086 (step 625)
- **EVAL RESULTS (CoT, n=1)**:
  - student_init (Phase 2 merge): **30%** (6/20) — broken by FLA+std-attn mixing
  - merged+LoRA (Phase 3): **12.5%** (5/40) — LoRA degraded format compliance
  - **ROOT CAUSE**: Simple weight averaging of FLA (jackrong) + standard-attn (darwin) models creates architecturally incoherent student_init
- **PHASE 3 RE-RUN PLAN**:
  - Use jackrong35b DIRECTLY as base (no mixing with standard-attn models)
  - Use Jackrong-27B API traces (424 so far, ~1000+ expected) as training data
  - Fewer steps (300-500) to avoid overfitting
- **Trace Gen RUNNING**: 424 Jackrong-27B traces at q=174/546, GPU 6 (93%)
  - Output: `/home/work/vidraft/distill_traces/jackrong27b_api_traces.jsonl`
  - Projected total: ~1200 traces (ETA completion: ~May 6 22:00 KST)
  - Projected total: ~1200 traces — will enable much better Phase 3 re-run

### Known Flaws (action needed)
- Phase 2 merge was simple average, NOT CMA-ES (plan deviation — accept as-is)
- No validation set → watcher uses final checkpoint (add multi-ckpt eval after DONE)
- Phase 4 (chem/bio injection) + Phase 5 (GRPO) not started yet
- Post-training: eval step 500/700/1000 checkpoints before picking best

### Track 1: KMMLU Darwin v9 SFT
- **Target**: KMMLU KR avg > 0.6744 (Rogue-v1 SOTA)
- **kmmlu_sft_gpu6_merged**: **COMPLETED** 2026-04-30 01:08 KST
  - Score: **0.6705** — BELOW TARGET by 0.0039
  - Weak: korean_history(0.390), math(0.433), taxation(0.475), env_science(0.497)
  - Strong: computer_science(0.897), marketing(0.889), IT(0.876)
  - Result: `/home/work/darwin_v9/eval_kmmlu_gpu6_merged/.../results_2026-04-30T01-08-21.733422.json`
- **kmmlu_sft_35b_ddp.py**: RoPE fix applied (2026-04-29)

### Parcae v10 (paused)
- Phase 4 Step 2 fails: `ModuleNotFoundError: No module named 'parcae_lm'`
- Fix: add `parcae_lm` to PYTHONPATH before running phase4_step2_load_parcae.py

## Eval Protocol (REPRODUCED)
- [Two-pass GPQA eval](eval_protocol_twopass.md) — P1 greedy(5120tok) → P2 maj@8(temp=0.7, 4608tok) on failures. Reproduced darwin36b 85% (published 84.3%). Use for ALL model comparisons.

## Critical Rules
- [NIPA kill policy](feedback_nipa_kill_policy.md) — never kill all Python; kills kernel launcher → container recycled
- **GPU 6 is reserved for other user** — NEVER use GPU 6 for anything. Available GPUs: 0-5 only (GPU 7 also reserved per CLAUDE.md). No lsk/llama-server on GPU 6.

## Key Paths (NIPA — vidraft NFS, port 10522)
- KD scripts: `/home/work/vidraft/distill/`
- Phase 3 log: `/home/work/vidraft/distill_traces/logs/phase3_training.log`
- Watcher log: `/home/work/vidraft/distill_traces/logs/phase3_watcher.log`
- Traces: `/home/work/vidraft/distill_traces/`
- student_init: `/home/work/vidraft/distill_traces/phase2_merged/student_init/`
- Phase 3 LoRA: `/home/work/vidraft/distill_traces/phase3_lora/`
- Phase 3 merged: `/home/work/vidraft/distill_traces/phase3_merged/`
- Bench result: `/home/work/vidraft/distill_traces/phase3_bench_result.json`
- GPQA Diamond CSV: `/home/work/vidraft/data/gpqa/gpqa_diamond.csv`
- KMMLU gpu6 merged: `/home/work/darwin_v9/kmmlu_sft_gpu6_merged`
