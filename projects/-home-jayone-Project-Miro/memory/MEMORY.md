# HalluMaze Project — Core Context
_Updated: 2026-03-26_

## Current State (v1.21) — 13-Model Leaderboard

### Full Leaderboard (MEI ↑)

| Rank | Model | MEI | SR | HRR |
|------|-------|-----|-----|-----|
| — | Random Walk ★ | 0.900 | 100% | 100% |
| 1 | **Claude-Sonnet-4.5** † | 0.783 | 36.7% | 89.2% |
| 2 | Claude-3.7-Sonnet | 0.774 | 56.7% | 87.5% |
| 3 | GLM-4.7 | 0.615 | 8.3% | 71.8% |
| 8 | Claude-Sonnet-4.6 † | 0.545 | 60.0% | 58.3% |
| 12 | Claude-Haiku-4.5 † | 0.376 | 5.0% | 38.3% |
| 13 | GPT-4o | 0.315 | 6.7% | 35.3% |

† Claude 4.x family, n=60 each

### MARL-SL Multi-Model Results

| Model | SR | Notes |
|-------|-----|-------|
| GLM-4.7 | 80% | reference |
| Claude-3.7-Sonnet | 67% | compatible |
| Qwen-2.5-72B | 33% | partial |
| Claude-3-Haiku | 8% | weak |
| MiniMax-M2.5 | 17% | direct API (OpenRouter blocked) |

## Key Findings

1. **SR ≠ MEI**: Sonnet-4.6 has highest SR (60%) but ranks #8 on MEI
2. **Newer ≠ better metacognition**: 4.6 < 4.5 < 3.7 on MEI
3. **Claude-Sonnet-4.5 is new leaderboard #1** (MEI=0.783)
4. All 13 models below random walk baseline (0.900)

## MiniMax API Notes

- OpenRouter blocked (privacy 404) → use direct `api.minimax.io/v1`
- MINIMAX_BASE_URL in shared.env = `https://api.minimax.io/anthropic` → strip `/anthropic`

## P0 Next Actions

1. **HF post v3**: `docs/hf_post_v3.md` 완성 → 포스팅
2. **arXiv 제출**: https://arxiv.org/submit → cs.CL
# currentDate
Today's date is 2026-03-26.
