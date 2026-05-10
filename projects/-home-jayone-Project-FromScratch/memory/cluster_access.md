---
name: Ginigen B200 Cluster Access
description: SSH access pattern to reach both nodes of the Ginigen B200 2-node cluster (10.50.6.73 / 10.50.6.74). Essential for launching 2-node training without separate external SSH sessions.
type: reference
originSessionId: 8af068da-9ee2-4576-a747-93eb27010493
---
Ginigen project `0426030036_A` runs on a 2-node B200 cluster. Both nodes are reachable by hopping:

**External entry (single SSH from local → node 0)**:
- Host: `genigen-b200` (ssh config alias) → `59.150.35.1:54501`
- User: `gmail_gini`
- Key: `~/.ssh/DCTN-0413110535-1_key` (key was rotated 2026-04-20; user provisions fresh via Windows Downloads + rename)
- Lands at: `DCTN-0417120013-1` (bond0 `10.50.6.73`)

**Inter-node hop (node 0 → node 1 via IB fabric)**:
- From inside `DCTN-0417120013-1` container, SSH to `10.50.6.74` works **without separate key/auth**.
- Passwordless via shared tenant keys on the IB network (bond0).
- Peer hostname: `DCTN-0417120013-2`, bond0 `10.50.6.74`.

**Topology** (from `/etc/hosts` on either node):
```
10.50.6.73 DCTN-0417120013-1    # node 0 (local landing)
10.50.6.74 DCTN-0417120013-2    # node 1
```

**2-node training launch pattern**:
- Workspace: `/NHNHOME/WORKSPACE/0426030036_A` (shared NHNHOME Lustre mount, visible from BOTH nodes).
- Launcher sets `MASTER_ADDR=10.50.6.74` — i.e., **node 1 (DCTN-...-2) is rank 0** (master), and **current node (DCTN-...-1, 10.50.6.73) is rank 1**.
- Command from external session (`genigen-b200`):
  ```bash
  # Launch rank 0 on peer first, then rank 1 locally
  ssh 10.50.6.74 "cd /NHNHOME/WORKSPACE/0426030036_A && bash aether_1t/run_graft_3of5_phase1.sh 0" &
  cd /NHNHOME/WORKSPACE/0426030036_A && bash aether_1t/run_graft_3of5_phase1.sh 1
  ```

**Why this matters**: I only have external SSH to `genigen-b200` (which lands on node 0). To launch 2-node training, I don't need a separate external key for node 1 — just hop internally via IB. Saves user from running commands on node 1 manually.

**Dead-ends to remember** (from MEMORY.md):
- `NCCL_SOCKET_IFNAME=bond0` alone causes "loopback connection refused" — need `bond0` + explicit HCA (`NCCL_IB_HCA=mlx5_5:1,mlx5_6:1`)
- `IBext_v10` NCCL plugin ignores `NCCL_IB_DISABLE=1` — must use `NCCL_NET_PLUGIN=none` to force socket fallback
- Multi-node DS + `mamba_ssm` Triton compile skew causes 20+ min NCCL hang — pre-warm Triton kernels per-rank before `deepspeed.initialize()`

**Key rotation**: NHN GPUaaS B200 containers periodically expire. User refreshes keys via the Ginigen portal → downloads to Windows `C:\Users\Jayone\Downloads\DCTN-0417120013-{1,2}_key` → I copy to `~/.ssh/DCTN-0413110535-1_key` (name referenced by ssh config) with `chmod 600`.
