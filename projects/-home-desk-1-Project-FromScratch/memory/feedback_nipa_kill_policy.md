---
name: NIPA kill policy — never kill all Python processes
description: On NIPA Backend.AI, killing all Python processes kills the kernel launcher and destroys the container
type: feedback
originSessionId: aca1b20e-9f0b-41c3-ade3-6939d9401f99
---
**batch_size cap**: 35B MoE student model (Jackrong-35B-A3B base) fills ~138/139 GB VRAM per H200. Max safe batch_size=1 with grad_accum=32. batch_size=4 OOMs on MoE activation (`grouped_mm_experts_forward`). Do NOT retry batch>1 without gradient_checkpointing=True.

Never run broad kill commands on NIPA that target all Python processes (e.g., `ps aux | grep python | xargs kill`, `pkill python`, `kill -9 -1`).

**Why:** Backend.AI uses a Python process as the container kernel launcher. Killing it causes the container to be recycled immediately — all ephemeral `/home/work/` storage is lost and a new container is provisioned with a new port.

**How to apply:**
- To stop training: identify the specific torchrun PID first (`pgrep -f torchrun` or `ps aux | grep distill`), then `kill -15 <PID>` only that PID.
- Never use `-9` on the kernel anchor process — use `kill -15` (SIGTERM) for graceful stop.
- If you need to kill multiple GPU workers: kill the torchrun parent PID only — it propagates to workers.
- All persistent outputs must go to `/home/work/vidraft/` (NFS) not `/home/work/` (ephemeral).
