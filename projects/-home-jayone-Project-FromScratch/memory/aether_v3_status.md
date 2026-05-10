---
name: aether_v3_transplant_status
description: AETHER-166B v3 transplant progress - fused expert key mismatch blocking full weight copy
type: project
---

## AETHER-166B v3 Transplant Status (2026-04-03)

### Completed
- Teacher MRI: expert_transplant_plan.json generated (router-only mode)
- Model shell built: 166B params, 621GB RSS → 1186GB at save time
- Transplant plan: 38,598 direct copies expected

### BLOCKING: Fused Expert Key Mismatch
- v3 weight_map.py expects: `model.language_model.layers.X.mlp.experts.{i}.gate_proj.weight` (individual)
- Actual safetensors format: `model.language_model.layers.X.mlp.experts.gate_up_proj` (fused [512, 2048, 4096])
- Result: 38,697 weights SKIPPED, only 1 copied (lm_head only)

**Why:** v3 guide code was written for individual expert weight format, but Qwen3.5-397B uses fused expert tensors.

**How to apply:** Must modify gpu_utils.py `load_donor_sharded()` to:
1. Detect fused format (`experts.gate_up_proj` vs `experts.{i}.gate_proj.weight`)
2. When fused: load `gate_up_proj [512, 2048, 4096]`, split into gate[512, 1024, 4096] + up[512, 1024, 4096]
3. Index individual experts: `gate_up_proj[expert_idx, :1024, :]` → gate_proj, `gate_up_proj[expert_idx, 1024:, :]` → up_proj
4. Similarly for `down_proj [512, 4096, 1024]` → `down_proj[expert_idx]`

### Fixes Already Applied
1. teacher_mri.py: hf_hub_download → local path support + dtype fix
2. gpu_utils.py: hf_hub_download → local path support
3. weight_map.py: `model.layers` → `model.language_model.layers` prefix + embed/norm prefix

### Fix Still Needed
- gpu_utils.py or transplant.py: fused expert tensor unpacking (gate_up_proj → individual experts)

### Darwin Serving
- vLLM on GPU 6+7, port 7947
- External: https://proxy2.nipa2025.ktcloud.com:10280
- Model: FINAL-Bench/Darwin-35B-A3B-Opus

### NIPA File Locations
- v3 code: /home/work/vidraft/aether-v3/
- 397B model: /home/work/vidraft/models/qwen3.5-397b/
- Output (incomplete): /home/work/vidraft/aether-166b/
