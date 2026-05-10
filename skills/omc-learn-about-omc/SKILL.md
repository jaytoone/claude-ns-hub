---
name: learn-about-omc
description: "Analyze your OMC usage patterns and generate personalized recommendations for getting more out of oh-my-claudecode. Use when you want to discover underused features or optimize your workflow."
---

# Learn About OMC

## Use When
- You want to understand your own OMC usage patterns and habits
- You want personalized recommendations for skills you haven't tried
- User says "learn about omc", "what am I using?", "how do I use OMC better?"

## Do Not Use When
- You want to configure OMC features (use `omc-setup` or specific configure skills)
- You want to understand what OMC IS conceptually (use `omc-help`)
- `.omc/sessions/` does not exist — there's no usage data to analyze yet

---

Analyze your OMC usage patterns and provide personalized recommendations for getting more out of oh-my-claudecode.

## Usage

```
/oh-my-claudecode:learn-about-omc
```

## Behavior

1. **Scan usage data** from:
   - `.omc/sessions/` for session history (if exists)
   - `.omc/state/` for mode usage patterns
   - `.omc/episodes.jsonl` for past episode outcomes (success/failure/partial)
   - `.omc/live-progress.log` for per-iteration score trajectory (if present)
   - `.omc/notepad.md` for working memory and open items
   - `.omc/world-model.json` for tried strategies and dead-ends (infinite loop runs)
   - `.omc/skill-patches/` for experience-based skill patches (if exists)
   - Agent flow traces (via `omc-trace`) for tool and agent usage patterns
2. **Analyze patterns**:
   - Most-used modes and skills
   - Agent types spawned most frequently
   - Common workflows and task types
   - Episode outcomes: success rate, most common failure phases
   - Score trajectory: improving vs plateau trends (from live-progress.log)
   - Dead-end strategies to avoid (from world-model.json)
3. **Generate recommendations**:
   - Underused features that match your current workflow patterns
   - More efficient skill combinations (e.g., replace omc-ralph with live-inf for quality tasks)
   - Configuration optimizations (live-config.json, skill-patches)
   - Tips based on your usage profile and failure patterns

## Sparse Data Handling

If `.omc/sessions/` is missing or has fewer than 3 entries:
- Fall back to `.omc/episodes.jsonl` as primary signal
- Use `.omc/world-model.json` tried_strategies as proxy for usage history
- Report: "Limited session data — recommendations based on episode history"
- Still proceed: don't skip analysis entirely

## Output

A personalized report with:
1. **Usage snapshot**: which skills/modes appear most in data sources
2. **Pattern insights**: 2-3 key workflow habits (good or improvable)
3. **Concrete next steps**: specific skills or configs to try next session
4. **Gaps flagged**: known dead-ends or anti-patterns from world model
