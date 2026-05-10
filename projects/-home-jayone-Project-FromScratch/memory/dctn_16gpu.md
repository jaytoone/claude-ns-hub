---
name: DCTN 16 GPU Cluster Config
description: DCTN NIPA 16 GPU (B200 x16) 클러스터 접속 및 훈련 설정
type: reference
---

## 클러스터 정보

| | Node-1 (Master) | Node-2 |
|---|---|---|
| 호스트명 | DCTN-0413110535-1 | DCTN-0413110535-2 |
| 내부 IP | 10.50.6.73 | 10.50.6.74 |
| 외부 접속 | 59.150.35.1:54501 | node-1 경유 내부망 |
| GPU | B200 × 8 (179GB each) | B200 × 8 (179GB each) |
| 유저 | gmail_gini | gmail_gini |

## SSH 접속

```bash
# Node-1 (외부)
ssh -i /home/jayone/.ssh/DCTN-0413110535-1_key \
  -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
  -p 54501 gmail_gini@59.150.35.1

# Node-2 (Node-1 경유)
ssh gmail_gini@10.50.6.74  # node-1 내부에서
```

## 16 GPU torchrun 설정

```bash
# NCCL 환경변수 (필수)
export NCCL_NVLS_ENABLE=0       # B200 NVLink Switch 버그 — 필수
export NCCL_IB_DISABLE=0
export NCCL_NET_GDR_LEVEL=5
export NCCL_SOCKET_IFNAME=bond0
export NCCL_IB_HCA="^=mlx5"

# torchrun (node-1 rank=0)
torchrun --nnodes=2 --nproc_per_node=8 \
  --rdzv_backend=c10d \
  --rdzv_endpoint=10.50.6.73:29501 \
  --node_rank=0 train.py

# torchrun (node-2 rank=1)
torchrun --nnodes=2 --nproc_per_node=8 \
  --rdzv_backend=c10d \
  --rdzv_endpoint=10.50.6.73:29501 \
  --node_rank=1 train.py
```

## FSDP 설정

```python
fsdp="full_shard auto_wrap"
fsdp_config={
    "fsdp_transformer_layer_cls_to_wrap": ["Qwen3_5DecoderLayer"],
    "fsdp_activation_checkpointing": True,
}
```

## 주요 제약사항

- **GRAD_ACC=1 필수**: ACC=2 → GPU util 63% dead-end (B200 FSDP 버그)
- **model_type=qwen3_5_text**: checkpoint-94 config.json 패치 필요 (backup: config.json.bak)
- **NCCL_NVLS_ENABLE=0**: 없으면 NCCL hang

## 워크스페이스

- 경로: `/home/gmail_gini/sft_workspace`
- 스크립트: `rogue_sft/`
- 로그: `logs/`
- 데이터: `orpo_data/`

## 현재 진행 중 (2026-04-14)

- 데이터 생성: 8 GPU × 1250 pairs (KMMLU seed 42-49) → ~20:00 완료 예상
- 완료 후 post_gen_train.sh (PID 175581) 자동으로 16 GPU 훈련 시작
- 출력: Rogue-27B-KR-v2-orpo-r2
