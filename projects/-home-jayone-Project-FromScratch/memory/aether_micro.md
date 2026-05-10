# AETHER-Micro 상세 기록

## 코드베이스
- **NIPA**: `/home/work/vidraft/new_training/`
- **모델**: Total 2.30B, Active 0.41B (MoE 20 experts, big.LITTLE)

## Ablation 최종 (2B tokens)
| Variant | last_loss | min_loss | ppl |
|---------|-----------|----------|-----|
| v5_full | **0.2460** | 0.0549 | **1.28** |
| v3_moe_magic_wuxing | 0.6533 | 0.2453 | 1.92 |
| v6_ta_moe | 0.8041 | 0.0447 | 2.23 |

## Phase 2 Pre-training v3 완료 (03-04)
- step 15894, loss=2.0472, 49.99B tokens
- 체크포인트: `pretrain_v3_final.pt`

## 벤치마크 (~50B tokens)
| 모델 | ARC-Easy | HellaSwag | WinoGrande | BoolQ |
|------|----------|-----------|------------|-------|
| AETHER v3 | 45.24% | 34.44% | 52.01% | 51.87% |
| Pythia-410M | 42.76% | 35.36% | 50.59% | 56.91% |

## 데이터: ~333B tokens, ~1,197GB
- Dolmino-DCLM 50B (205.2GB)
- Stack v1 Python/JS/TS (246.9GB)

## v2 Ablation (03-10)
- v5_baseline 완료, v2_deltanet_fg 실행
- FLA GatedDeltaNet 주 병목

## Kimi-K2.5 vLLM (03-13)
- 소스 빌드 PTX 8.7, port 8000, TP=8
- 가이드: `docs/infrastructure/NIPA_Kimi-K2.5_API_SETUP_GUIDE.md`

## GLM-4.7-Flash (03-08)
- Q8_0, port 8081, GPU 7, --parallel 1 필수
