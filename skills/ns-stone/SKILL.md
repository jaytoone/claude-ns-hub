---
name: ns-stone
description: "North Star setup and milestone roadmap. Two modes: INIT (new project or blank north-star) and PIVOT (existing project hit a wall, need next milestones with fast-validation gates). Auto-detects mode from north-star.md existence. Triggers: /ns-stone, '다음 마일스톤', 'northstar 만들어', 'roadmap 업데이트', 'what's next', 'north star init'"
---

# ns-stone — North Star Setup + Milestone Roadmap

Two modes, one skill:
- **INIT**: project has no north-star.md or it's blank → create from scratch
- **PIVOT**: project has north-star.md → update milestones with fast-validation gate ladder

---

## Mode Detection

Parse invocation args first:
```
args = invocation arguments (e.g. "MOAT", "--init", "--pivot ProjectName")

# Extract ProjectName if provided (any non-flag token)
PROJECT_ARG = first non-flag token in args (not --init/--pivot/--refresh)
             e.g. "/ns-stone MOAT" → PROJECT_ARG="MOAT"
             e.g. "/ns-stone --pivot" → PROJECT_ARG=None

# Determine project
if PROJECT_ARG:
    PROJECT = PROJECT_ARG
    CWD = "$HOME/Project/$PROJECT"  # infer path; use PROJECT for hub lookup
else:
    PROJECT = $(basename $(pwd))
    CWD = $(pwd)
```

```bash
NS_FILE="$HOME/.claude/hub/projects/${PROJECT}/north-star.md"

if [ "--init" in args ]: MODE=INIT   # explicit override
elif [ "--pivot" in args ]: MODE=PIVOT  # explicit override
elif [ -f "$NS_FILE" ] && grep -q "target:" "$NS_FILE": MODE=PIVOT
else: MODE=INIT
```

---

## INIT Mode — Create north-star.md from scratch

### Step 1: Detect project path

```bash
CWD=$(pwd)
PROJECT=$(basename "$CWD")
mkdir -p "$HOME/.claude/hub/projects/$PROJECT"
```

### Step 2: Gather context (run all simultaneously)

```bash
# A. CLAUDE.md
cat CLAUDE.md 2>/dev/null | head -60

# B. Git history
git log --oneline -20 --no-merges 2>/dev/null

# C. Recent docs
find docs/ -name "*.md" -newer docs/DOC_INDEX.md 2>/dev/null |
  xargs ls -t 2>/dev/null | head -5 | xargs head -20 2>/dev/null

# D. README
cat README.md 2>/dev/null | head -30

# E. CTX graph hot nodes
curl -s "http://$(ss -tlnp | grep ':8787' | grep -oP '\d+\.\d+\.\d+\.\d+'):8787/api/graph" 2>/dev/null |
  python3 -c "
import json,sys,os
d=json.load(sys.stdin)
proj=os.path.basename(os.getcwd()).lower()
nodes=[n for n in d.get('nodes',[]) if proj in n.get('label','').lower()]
for n in sorted(nodes, key=lambda x: x.get('utility_heat_raw',0), reverse=True)[:5]:
    print(f'[{n[\"type\"]}] heat={n.get(\"utility_heat_raw\",0):.2f} {n[\"label\"][:60]}')
" 2>/dev/null
```

### Step 3: Goal Clarity Check

Score available context:
- +2 if CLAUDE.md has a clear goal statement
- +2 if git log has ≥5 meaningful commits
- +1 if README.md has a project description
- +1 if recent docs found
- +1 if CTX hot nodes found

**If score < 3 → ask exactly ONE question:**
> "이 프로젝트 목표가 뭐야? 한 줄로." (e.g. "GPQA 90%", "구독자 1000명", "첫 유료 유저 10명")

From that answer, infer: metric, target, milestones, status=behind. Use `—` for unknowns. **Never ask Q2 or Q3.**

If score ≥ 3 → skip question entirely, infer directly.

### Step 4: Write north-star.md

```yaml
---
name: {ProjectName}
metric: "{single north star metric}"
current: "{current value or —}"
target: "{target value}"
unit: "{unit}"
status: {behind|on-track|achieved|paused}
deadline: "{YYYY-MM-DD or empty}"
note: "{1-line project description}"
milestones:
- done: {true|false}
  text: "{milestone 1 — most foundational}"
- done: {true|false}
  text: "{milestone 2}"
log:
- date: "{YYYY-MM-DD}"
  text: "{most recent event from git/docs}"
---

# {ProjectName} — North Star

## Why this metric
{1-2 sentences}

## Strategy
{bullet points}

## Links
- Repo: {CWD}
```

### Step 5: Reload hub + confirm with user

```bash
hub-stop && hub
```

Then show the user a summary of what was written and ask:
> "맞아? 수정할 부분 있어?" (Did I get it right? Anything to adjust?)

This is mandatory — never silently write north-star.md without showing the user. Open http://100.119.82.4:9000 to verify the node appears.

---

## PIVOT Mode — Update milestones with fast-validation gates

### Step 1: Load current state

```bash
PROJECT=$(basename "$(pwd)")
NS_FILE="$HOME/.claude/hub/projects/${PROJECT}/north-star.md"
MEMORY_FILE="$HOME/.claude/projects/$(pwd | tr '/' '-')/memory/MEMORY.md"
```

Read in order:
1. `north-star.md` — current milestones, current%, target
2. `MEMORY.md` — what was tried, what failed
3. Last 3 research docs in `docs/research/`
4. `git log --oneline -10`

### Step 2: Diagnosis (output before milestones)

Answer 4 questions:
1. **Blocker**: what is blocking the north star right now? (one sentence)
2. **Kill-shot test**: smallest experiment to invalidate the current approach?
3. **Green-light test**: smallest experiment to validate the next approach?
4. **Untested assumptions**: what hasn't been verified yet?

### Step 3: Design milestones with gate ladder

**Fast-Validation Principle** — never run 3+ hour eval without a cheap gate first:
- **Gate 0** (≤2h, tiny scale): does signal exist at all?
- **Gate 1** (≤4h, small scale): is direction confirmed?
- **Gate 2** (full scale): only if Gate 0+1 pass

Each milestone must have: goal, validation method, time estimate, pass/fail threshold.

### Step 4: Update north-star.md

- Mark completed milestones `done: true` with actual result in text
- For wrong/failed milestones: `done: true` + "REVISED: actual result" in text — never delete
- Update `current:` to best CONFIRMED score (never proxy/estimate)
- Update `status:` → on-track / at-risk / pivoting
- Update `note:` to reflect current understanding (not original plan)
- Add new milestones Gate 0 first, then 1, 2
- Add log entry with today's date

### Step 5: Post to dashboard (optional)

After north-star.md is updated, the hub at http://100.119.82.4:9000 will reflect changes automatically on next reload. For a manual dash.vidraft.net update, use `/dash-post` — but note that dash-post posts git commit logs, not milestone summaries. For milestone-specific posting, copy the Output Format table above into a dash manual entry.

---

## Output Format (PIVOT)

```
## [ProjectName] — North Star Update

### Diagnosis
Blocker: [one sentence]
Kill-shot: [smallest invalidation test]
Green-light: [smallest validation test]

### New Milestones
| # | Gate | Goal | Validation | Time | Pass if |
|---|------|------|------------|------|---------|
| M1 | 0   | ...  | ...        | ~2h  | >X%     |
| M2 | 1   | ...  | ...        | ~4h  | >Y%     |
| M3 | 2   | ...  | ...        | ~3h  | >Z%     |

north-star.md updated ✓
```

---

## Anti-patterns

- ❌ Don't guess metrics — use only CLAUDE.md, git, docs, or user answers
- ❌ Don't mark milestones done without evidence
- ❌ Don't set current% above best CONFIRMED full-eval score
- ❌ Don't add a 3+ hour milestone without a Gate 0 before it
- ❌ Don't delete old milestones — mark done with actual result
- ❌ Don't ask more than 1 question in INIT mode when context is thin
- ❌ Don't silently write north-star.md — always show summary and ask "맞아? 수정할 부분 있어?"
- ✅ `find docs/ -name "*.md" -newer docs/DOC_INDEX.md` exits cleanly even if docs/ doesn't exist

---

## Usage

```
/ns-stone              ← auto-detect mode
/ns-stone --init       ← force INIT (create fresh)
/ns-stone --pivot      ← force PIVOT (update milestones)
/ns-stone ProjectName  ← specify project by name
```
