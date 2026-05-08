---
category: 'Vertical'
name: AIKB
metric: "Physical keyboard hit rate on release APK"
current: "PoC 8/8 PASS (ADB-simulated)"
target: "98/100 on 3 real devices × 2 keyboards"
unit: "hit rate"
status: on-track
deadline: '2026-06-20'
note: BT HID keyboard → Android content controller. K1/K2/K3 = NUMPAD_1/2/3 confirmed.
milestones:
- done: true
  text: 'PoC complete — 8/8 acceptance criteria PASS (ADB-simulated)'
- done: true
  text: 'KeyInspector APK deployed (K1→Video, K2→URL, K3→Music, K0→Back)'
- done: true
  text: 'Demo video (poc_demo_v3.mp4) + web remote @ LT-1:8888'
- done: false
  text: 'MVP — Kotlin+Compose migration, full settings UI, SAF file picker, minSdk 26'
- done: false
  text: 'QA — 3 real devices × 2 keyboards, 98/100 hit rate'
- done: false
  text: Release APK
log:
- date: '2026-05-07'
  text: 'PoC Day 1 — HW validated on Huawei WAS-LX2J + GK104 BT1'
- date: '2026-05-07'
  text: 'live-inf 8 iterations → score 0.992, all dims 0.85+'
- date: '2026-05-08'
  text: 'Demo video + web remote (iPad accessible @ LT-1:8888)'
---

# AIKB — BT Keyboard Control App

## North Star
**물리 키보드 3개 키로 동영상/URL/음악이 1초 이내에 안정적으로 실행**  
3기기 × 2키보드에서 98/100 hit rate — 릴리즈 APK

## Current State
- PoC: **COMPLETE** (2026-05-07)
- K1=NUMPAD_1(145) → Video | K2=NUMPAD_2(146) → URL | K3=NUMPAD_3(147) → Music
- Remote test infra: WSL → SSH → LT-1 → ADB → Huawei
- Web viewer: http://100.125.152.31:8888/ (iPad/iPhone accessible)

## Next
MVP P0: Kotlin+Compose 마이그레이션, 설정 UI, SAF 파일 피커, minSdk 26 복원
