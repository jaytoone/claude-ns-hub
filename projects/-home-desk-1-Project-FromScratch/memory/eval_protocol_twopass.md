---
name: GPQA Two-Pass Eval Protocol (Reproduced)
description: Two-pass eval that reproduces darwin36b 84.3% — use this for all model comparisons
type: reference
originSessionId: aca1b20e-9f0b-41c3-ade3-6939d9401f99
---
# GPQA Diamond Two-Pass Eval Protocol

**Reproduced**: 17/20 = 85% on darwin36b (vs published 84.3%) — confirmed correct.

## Protocol
- **Script**: `/home/work/vidraft/distill/gpqa_twopass.py`
- **Pass 1**: greedy, `do_sample=False`, `max_new_tokens=5120` — all questions
- **Pass 2**: only Pass1 failures → `do_sample=True`, `temperature=0.7`, `n_votes=8`, `max_new_tokens=4608`
- **Split**: 20Q across 6 GPUs (4+3+3+4+3+3), 10s stagger between launches
- **Output dir**: `/home/work/vidraft/distill_traces/eval_twopass_{model_name}/`

## Launch Command
```bash
configs="0,0,4 1,4,3 2,7,3 3,10,4 4,14,3 5,17,3"
for cfg in $configs; do
  gpu=$(echo $cfg | cut -d, -f1); off=$(echo $cfg | cut -d, -f2); lim=$(echo $cfg | cut -d, -f3)
  CUDA_VISIBLE_DEVICES=$gpu nohup python3 /home/work/vidraft/distill/gpqa_twopass.py \
    --model <MODEL_PATH> --offset $off --limit $lim --n_votes 8 \
    --output /home/work/vidraft/distill_traces/eval_twopass_<NAME>/gpu${gpu}.json \
    > /home/work/vidraft/distill_traces/logs/twopass_<NAME>_gpu${gpu}.log 2>&1 &
  sleep 10
done
```

## Key Findings
- `max_new_tokens=4608` is the sweet spot for Pass 2 (not 3000, not 5120)
- `max_new_tokens=5120` for Pass 1 greedy (full thinking chain)
- `do_sample=False` for Pass 1 ONLY — all votes in Pass 2 must use sampling
- 20Q sample size gives ±2-3 question variance vs published 198Q number

## Baseline
- darwin36b two-pass on 20Q: **17/20 = 85%** (published 84.3% on 198Q)
