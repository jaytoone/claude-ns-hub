---
name: live-state archive 2026-04-16
description: ameva-era live-state/goal-tree/progress.log archived to .omc/archive/20260416/ after ameva→entity rename. Fresh slate for new /live invocations.
type: project
---

ameva 시대 `live-state.json` / `goal-tree.json` / `live-progress.log` 3개 파일을 `.omc/archive/20260416/` 으로 이동(archive + reset).

**Why:** `ameva → entity` rename(2026-04-16, MEMORY.md 기록됨) 이후 `root_goal="ameva 개선"` 은 stale. 28 iter(0.86→0.994) 궤적은 git history(`f20b167` 이전) + archive 디렉터리에 보존. `/exhale`로 만든 3개 artifact(CGR/Mirage/Solver-Sampler)는 entity 컨텍스트이므로 깨끗한 상태에서 시작하는 편이 정합성 높다고 판단.

**How to apply:** 다음 `/live` 호출은 **반드시 goal 인자와 함께** 해야 함 (`/live <goal>`). 인자 없이 bare `/live` 호출 시 "No active goal" 에러 — 그게 의도된 동작. 과거 ameva 궤적 참조 필요 시 `.omc/archive/20260416/` 에서 복원.

**보존 파일:**
- `.omc/episodes.jsonl` (28 에피소드 — 교차 트라젝토리 학습에 계속 쓰임)
- `.omc/evolution-registry.jsonl` (CGR/Mirage/Solver-Sampler 포함)
- `.omc/infinite-state.json`, `.omc/world-model.json`, `.omc/skill-patches/` (live-inf 구조 유지)
