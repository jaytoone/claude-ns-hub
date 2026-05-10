---
name: HalluMaze 현재 상태 (2026-03-25)
description: 현재 진행 상태, 완료 항목, 다음 액션
type: project
---

## 현재 상태 (v1.11, 2026-03-25)

실험 완료: 10 models × 60 trials = 600 total. 잔여 한계 대부분 해결.

**Why:** NeurIPS 2026 D&B 제출 준비 완료 단계.
**How to apply:** 다음 세션에서는 arXiv 제출 완료 확인 또는 HF post 올리기부터 시작.

## 완료된 실험 (이번 세션)

- ICC(2,1): Claude=0.664(moderate), Llama=0.330(poor), GLM=0.156(poor)
- Temperature sweep GLM-4.7: t=0.3 peak MEI=0.683
- 9×9 scaling GLM-4.7 n=30: 5x5→7x7→9x9 MEI=0.637→0.588→0.487
- Kruskal + Wilson's 알고리즘 추가 (files/hallumaze.py)
- 논문 초안 v1.5 완성 (docs/research/20260323-hallumaze-paper-draft.md)
- LaTeX v1.5 완성 + arXiv 패키지 재빌드 (hallumaze_arxiv_submit.tar.gz)

## 다음 액션 (P0)

1. **arXiv 제출** — hallumaze_arxiv_submit.tar.gz 업로드
   - URL: https://arxiv.org/submit
   - Category: cs.CL
   - Playwright session 사용 시 SingletonLock/Socket 먼저 제거 필요
   - 제출 후 번호(2503.xxxxx) → README + HF Space에 반영

2. **HF Community Post** — docs/hf_post_v2.md 내용 + hallumaze_race_screenshot.png 첨부
   - 2026-03-26 10:30+ (quota reset 후)
   - URL: https://huggingface.co/posts/create

## 최신 git 상태

- Branch: main
- Latest commit: ed861e4 (v1.11)
- Remote: https://github.com/jaytoone/HalluMaze.git
- Untracked: PNG 스크린샷들 (커밋 불필요)
