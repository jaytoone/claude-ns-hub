# claude-ns-hub

[![PyPI Downloads](https://img.shields.io/pypi/dm/claude-ns-hub?label=downloads%2Fmonth&color=orange)](https://pypi.org/project/claude-ns-hub/)
[![PyPI Version](https://img.shields.io/pypi/v/claude-ns-hub?color=blue)](https://pypi.org/project/claude-ns-hub/)
[![GitHub Stars](https://img.shields.io/github/stars/jaytoone/claude-ns-hub?style=flat&color=yellow)](https://github.com/jaytoone/claude-ns-hub)
[![Python](https://img.shields.io/pypi/pyversions/claude-ns-hub)](https://pypi.org/project/claude-ns-hub/)

**당신은 매일 아이디어를 잃어버린다.**

메모장도, 노트앱도, 컴퓨터 앞에 앉아야만 하는 환경도 — 당신 뇌의 속도를 따라가지 못한다.

> _"신이 아이디어를 잃어버리는 이유"_ — 그 답이 여기 있다.

![NS-Hub — Second Brain for Claude Code users](https://raw.githubusercontent.com/jaytoone/claude-ns-hub/master/assets/ns-hub-banner-v9.png)

---

## NS Hub is your Second Brain × AI execution layer

아이디어가 떠오른 순간 → **Stone으로 변환** → Claude가 자율 실행 → 폰에서 결과 확인.

컴퓨터 앞에 앉지 않아도 된다. 메모할 필요도 없다. 컨텍스트를 잃을 이유도 없다.

| Without NS Hub | With NS Hub |
|---|---|
| 아이디어 떠오름 → 나중에 하려다 망각 | 즉시 Stone 생성 → Claude가 큐에서 자율 실행 |
| Claude가 뭘 하는지 모름 (blind run) | 폰에서 실시간 세션 모니터링 |
| 컴퓨터 열어야 컨텍스트 확인 가능 | 어디서든 ↻ 버튼 하나로 이전 세션 재개 |
| 할 일 적어두다 컨텍스트 유실 | Stone 영속성 — 아이디어가 사라지지 않음 |

---

## Why this exists

Claude Code가 자율 실행 중일 때 당신은 **blind** — 어떤 세션이 살아있는지, 멈춰있는지, 뭘 했는지 알 수 없다.

더 깊은 문제는 **아이디어 유실**이다. 폰으로 떠오른 생각, 이동 중의 인사이트, 자다가 깨서 메모한 아이디어 — 대부분 컨텍스트 없이 흩어진다.

NS Hub는 두 문제를 동시에 해결한다:

- **Second Brain**: 아이디어를 즉시 Stone으로 캡처 → 컨텍스트와 함께 영속 보존
- **Agent 실행 허브**: Stone → Claude 자율 실행 → 결과 알림 — 폰으로 전체 루프 완결

---

## Core loop

```
아이디어 떠오름
    ↓
Stone 생성 (폰에서 5초)
    ↓
Claude Code가 큐에서 자동 픽업
    ↓
실행 중 — 폰에서 live 세션 모니터링
    ↓
완료 알림 → 결과 확인
    ↓
다음 Stone 자동 디스패치
```

컴퓨터 없이도 이 루프 전체가 돌아간다.

---

## Install (60 seconds)

```bash
pip install claude-ns-hub
hub                          # starts at http://localhost:9001
```

설정 파일 없음. 환경변수 없음. 별도 데몬 없음. 출력된 URL을 폰 브라우저에 열면 끝.

### Prerequisites

- Python 3.10+
- [Claude Code CLI](https://claude.ai/code) (`claude --version`)
- `tmux` (`brew install tmux` / `apt install tmux`)
- Tailscale (optional, for remote mobile access)

---

## Quick start

```bash
# 1. Start the hub
hub

# 2. Inject the NS Hub protocol into Claude Code (run once)
hub install-global
# Writes stone lifecycle protocol to ~/.claude/CLAUDE.md

# 3. Add your first project
# North Star tab → "+ node" → set repo_path

# 4. Drop a Stone and let Claude run it
# Click project card → "+ milestone" → type your task → "live"
```

---

## What you get

| Feature | What it does |
|---------|-------------|
| **Stone capture** | Drop any idea as a Stone — Claude picks it up on next idle |
| **Live exec sessions** | Real-time session visibility: busy/idle state, session ID, last tool used |
| **Mobile terminal** | Type from your phone directly into the running Claude session |
| **Session resume** | ↻ resumes exact prior context — no re-explaining, no lost work |
| **Context persistence** | Stone history, evidence URLs, conversation summaries — all local SQLite, fully portable |
| **North Star swimlane** | All projects + milestones on one screen, any device |
| **Entity corpus browser** | Browse all local skills/agents/corpora; inline search |
| **Zero-config install** | `pip install claude-ns-hub && hub` — that's the entire setup |

---

## Telemetry & privacy

On startup, one anonymized `hub_start` event is sent (fields: `ts`, `event`, `install_id=sha256(hostname)[:16]`, `version`, `os`). **No PII, no code, no Stone text** is ever transmitted.

Opt out anytime:

```bash
curl -X POST http://localhost:9001/api/hub/consent \
  -H 'Content-Type: application/json' \
  -d '{"data_collection": false}'
```

---

## Troubleshooting

### tmux not found
```bash
sudo apt install tmux   # Ubuntu/WSL
brew install tmux        # macOS
tmux -V                  # verify
```

### Claude Code not authenticated
```bash
claude --version
npm install -g @anthropic-ai/claude-code   # if missing
claude login
```

### Hub can't find my project
```bash
hub init <PROJECT_ID> --dir /path/to/your/project
```
Or: North Star → "+ node" → set `repo_path` manually.

### Hooks not firing
```bash
hub install-global
cat ~/.claude/settings.json | grep hub
```

---

## Data schema & portability

All data lives in local SQLite (`~/.hub/hub.db`). No vendor lock-in.

```sql
-- milestones (Stones)
CREATE TABLE milestones (
  id TEXT PRIMARY KEY,          -- e.g. "M1301"
  project TEXT,
  text TEXT,                    -- your original idea / task
  status TEXT,                  -- queued | in_progress | pending_confirmation | done
  done INTEGER DEFAULT 0,
  exec_start TEXT,
  exec_end TEXT,
  model_used TEXT,
  evidence_url TEXT,
  append_message TEXT,          -- Claude's completion summary
  created_at TEXT DEFAULT (datetime('now'))
);
```

Export/import: `sqlite3 ~/.hub/hub.db .dump > backup.sql`

---

## Screenshots

**Mobile dark theme** — capture ideas, monitor execution, read results. No laptop needed:

![Mobile dark — detail card](https://i.imgur.com/tjM3kwD.png)

![Mobile dark — swimlane overview](https://i.imgur.com/riH661r.png)

**North Star swimlane** — all projects, all lanes, live exec indicators:

![North Star swimlane](https://i.imgur.com/nM5naaI.png)

**Project detail card** — goal, progress, live session row, Stone list:

![Project detail card](https://i.imgur.com/KjCAx1B.png)

**Skill / Agent badge picker** — assign any agent to a Stone directly from the row:

![Skill badge picker](https://i.imgur.com/v8VRaAz.png)

---

## Metrics endpoint

```bash
curl http://localhost:9001/api/metrics?proj_id=MOAT
# → stones_completed, stones_queued, total_tokens per day
```

---

**pip install claude-ns-hub** — stop losing your ideas.

---

## License

Currently **MIT**. If commercial redistribution becomes an issue, we may adopt [Elastic License v2 (ELv2)](https://www.elastic.co/licensing/elastic-license) — source-available, free for personal/internal use, restricted for managed-service resale only. Community PRs and personal deployments will always remain free.
