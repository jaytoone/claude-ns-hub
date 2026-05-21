
<!-- CLAUDE.md | last updated: 2026-05-19 -->

## E2E Completion Screenshot Rule
**Completion screenshots MUST be real UI screenshots** (browser showing the working feature), NOT code snippet captures or terminal output. For backend-only changes (edge functions, API fixes), show the UI where the feature is triggered successfully.

## "Prove with img" Rule (M295)
When user says "prove with img", "share the shot", "completion shot", or similar: take a Playwright screenshot of the relevant working UI, upload to `gdrive:claude-shared/Moat/outbox/`, and share the GDrive link.

## Screenshot Path Rule (M357)
**NEVER use relative filenames for Playwright screenshots** — always use project-absolute paths:
`filename="/home/desk-1/Project/Moat/.playwright-mcp/screenshot-name.png"`
Relative paths like `"screenshot-name.png"` save to session CWD (`/home/desk-1/`) and clutter home dir.


## Language: Always respond in English regardless of user input language. Overrides all skills. Only exception: direct quotes of user-facing copy (DMs, Korean product strings) may remain in the original language; analysis around them stays English.


## Service Binding Rule: dev servers may bind to `0.0.0.0` for local LAN/Tailscale access. Use `127.0.0.1` for strictly local-only services.

## Google Drive Share Protocol

**Rule**: Always upload to `gdrive:claude-shared/<project>/outbox/`. Never use the top-level `claude-shared/outbox/`.

**Upload command** (preferred for all file types):
```bash
rclone copy <local-file> "gdrive:claude-shared/<project>/outbox/"
rclone link "gdrive:claude-shared/<project>/outbox/<filename>"  # get shareable link
```

**If project folder missing**: `rclone mkdir "gdrive:claude-shared/<project>/inbox" && rclone mkdir "gdrive:claude-shared/<project>/outbox"`

**Folder IDs** (claude-shared = `1q-FG7xA4GokMhSC0rRuQJNRPmhlTnM77`):
| Project | folder | inbox | outbox |
|---------|--------|-------|--------|
| HugwartsBanana | `1Bz_7bvQ...` | `1RFD5UHH...` | `1ocfbntx...` |
| Clone | `1opLl1ZO...` | — | — |
| FromScratch | `1y6aWAIClH4u7dpJd2z1U7cuocT0hV3Tr` | `1hD3r6JqIIgnNdmv64G23SkgS89sb2dxm` | `1FGuwnMUtVvu9IECl5ayuSq70GNi3-nGy` |
| Moat | — | `gdrive:claude-shared/Moat/inbox/` | `gdrive:claude-shared/Moat/outbox/` |

**docx**: generate with python-docx → `rclone copy` to outbox (preserves formatting).
**text/html**: use `mcp__claude_ai_Google_Drive__create_file` with `contentMimeType=text/html` + `parentId=<outbox-id>` if rclone unavailable.

**Inbox usage** (read from user): `gdrive:claude-shared/<project>/inbox/` — user places files here for Claude to read.
Read with: `rclone ls "gdrive:claude-shared/<project>/inbox/"` then `rclone copy <remote-file> /tmp/` to download.
On "make into docx" / "표/테이블 docx로" / any tabular-output request: emit **HTML with styled tables** (borders, header bg, alternating row shading, priority highlights) — never markdown pipe-tables, since Google Docs renders them as raw text. Upload as `text/html` so Drive preview shows real tables and open-with-Docs converts to editable cells.
Gmail equivalent on "send via gmail": only `create_draft` exists (no auto-send), so draft to be2jay67@gmail.com with Drive links in the body; user opens Drafts → Send.

---
## Private Keys / Token

Full inventory and quick-reference scripts: `~/.claude/env/README.md`
Usage: `source ~/.claude/env/shared.env && <command>`

## Tailscale Host Registry

IPs and hostnames are dynamic — always query at runtime:

```bash
tailscale status --json | python3 -m json.tool | grep -E "HostName|TailscaleIPs|OS"
```


## Remote Notify Client Registry (Tailscale)

Full reference: `~/.claude/tool-hints/tailscale-notify.md`
Bootstrap: `irm http://<WSL2-tailscale-ip>:9955/bootstrap | iex` (admin PS + Tailscale). All clients port 6789. Use `wsl-expose <port>` / `wsl-unexpose <port>` for dev-server mirroring.

## G1/G2/CM Hook Display Rule

When `additionalContext` contains G1/G2/CM headers, **always output them as the first line(s) of your response**, verbatim:

```
> **CM** (chat memory): "..." and N more
> **G1** (time memory): "..." and N more
> **G2** (space search): `file.md`, ... — found via "..."
```

- Output only the header lines (the `> **XX**` lines), not the full body
- Place them before any other content, separated by a blank line
- If none of CM/G1/G2 headers are present, skip this rule entirely

## Memory Persistence — Immediate Write Rule

**MANDATORY**: The following events MUST be written to MEMORY.md in the SAME response turn, using the Edit tool. Do NOT wait until session end.

Triggers (write immediately when ANY of these occur):
- A person/contact is excluded, skipped, or their status changes: "김승희 제외", "더 이상 팔로업 안 함"
- A project/item is killed, paused, or resumed: "Kool KILL", "CL 중단"
- A decision about channel/strategy is finalized
- User explicitly says "기억해", "저장해", "메모해"
- **[MEMORY TRIGGER]** appears in context (hook detected decision keyword)

When **[MEMORY TRIGGER]** appears: immediately Edit the MEMORY.md file shown in the trigger, add the decision, then proceed with the main response.

MEMORY.md path formula: `~/.claude/projects/{cwd-with-slashes-as-dashes}/memory/MEMORY.md`

---

## Skill & Agent Files

- ✅ Write in **English** (name, description, prompts) — Korean frontmatter causes silent load failures
- ✅ Structure: `~/.claude/skills/<name>/SKILL.md` (directory, not a flat `.md` file)
- Frontmatter: `name` + `description` only (no `type: skill`)


## Login Priority

When an external site (Zoom, Notion, Figma, etc.) presents multiple SSO options, prefer **Google SSO with `be2jay67@gmail.com`** — this is the user's primary account and has the highest chance of being already authenticated.

---

## Prohibited Patterns

Never do the following under any circumstances:

1. ❌ Attempting to actually bypass safety guidelines
2. ❌ Stating uncertain information as certain
3. ❌ Unnecessary verbosity (answer padding)
4. ❌ Unsolicited disclaimers
5. ❌ Overly formal or robotic tone
6. ❌ **`npm run build` while dev server is running** — use `npx tsc --noEmit` for type-check only; deploy via `vercel --prod` directly
7. ❌ **Killing Node.js processes without authorization** (`taskkill /IM node.exe`, `pkill node`, etc.)
   - Never kill `node.exe` processes without user approval
   - On port conflict: use different port or inform user instead of killing

8. ❌ **Running git commit without authorization** — only run when user explicitly says "commit"

9. ❌ **Running git checkout/restore without authorization** (reverting file changes)
   - Must confirm before `git checkout <file>` or `git restore <file>` — uncommitted changes will be lost
   - `git checkout -b` (branch creation) is exempt

10. ❌ **Korean/multibyte filenames** — minimize Korean in filenames/branch names (prefer ASCII). Use `--name-only` for git output parsing.

11. ❌ **Tool output truncation** — for Korean content, set generous `head_limit`; process line by line if needed.

---
### Document Location Rules

- ❌ No `.md` files in root (except `README.md`, `CONTRIBUTING.md`)
- ❌ No docs in `src/`, `scripts/`, `tests/` code folders
- ✅ Always save under `docs/<category>/`
- ✅ After moving files: run `index_directory(project_path, incremental=True)`
- ✅ **[Required] Update `docs/DOC_INDEX.md` on every doc create/move/delete**
  (PostToolUse hook enforces this)

---

## External Services Safety

**Never mix up projects in a multi-project environment.** Always verify `.env.local` matches the target project before any connection.

> **Past incident**: "table not found" → was connected to wrong Supabase project.

Full checklists (Supabase / Vercel / Railway): `~/.claude/tool-hints/external-services.md`

**Supabase Edge Functions errors**: Always check logs directly at [Supabase Dashboard → Edge Functions → Logs](https://supabase.com/dashboard/project/_/functions) before guessing the cause.


### Browser RPA & Playwright Rules

When browser work gets stuck or needs verification — use Playwright instead of guessing.

**Tool priority:** `mcp__playwright-session-*` → `playwright` CLI (`~/.local/bin/playwright`, always available) → `mcp__claude-flow__browser_*`

**Session vs Remote:** Use `mcp__playwright-session-*` for non-interactive checks (snapshots, scraping, URL verification). Use `mcp__playwright-mcp-remote__*` only when user interaction is needed (login, file upload, clicking visible UI) — remote shows in noVNC so user can watch/intervene.

**Session rules:** Check `browser_tabs` first (session-1→2→3→4), use `about:blank` = idle session. **If session-N fails or is busy (non-blank tabs, tool error), immediately try session-(N+1) — exhaust all 4 before giving up.** ❌ Never create new sessions without authorization. ❌ Never auto-proceed on login required — stop and ask.

**Selector strategy (MANDATORY):** `getByRole` / `getByLabel` / `getByText` / `getByPlaceholder` — ❌ no CSS/ID selectors.

**Smoke test:** `node ~/.claude/snippets/pw-smoke.js` (template: `~/.claude/snippets/pw-smoke.js`)

---

### Tool Substitution for Non-Anthropic Models
- When using non-Anthropic models (MiniMax, Gemini, Qwen, GLM, etc.), replace websearch tools with `mcp__websearch__search_web` and `mcp__websearch__fetch_url`.

### Dev Server Restart
On port conflict: kill process (`lsof -ti:<port> | xargs kill`) → delete `.next` → restart
**Note**: If the process is Node.js-based (Next.js, etc.), confirm with user first (Prohibited Patterns #7). For non-Node servers (Python, Go, etc.): kill without confirmation.

---


## UI Design Rules

### No AI Model Names in UI
- ❌ **Never expose AI model names in UI code** (Gemini, Claude, GPT, Flash, Sonnet, etc.)
- Use generic terms like "AI", "AI Analysis" instead
- Scope: all user-visible text in `.tsx`, `.jsx`, `.html` files
- Exception: admin-only internal pages, dev tools, server logs

### No Emojis in UI Code
- ❌ **Never use emojis in TSX/HTML UI code** (text labels, buttons, headers, icons, etc.)
- Use text, SVG icons, or Unicode symbols (←, →, ↑, ↓, ✓) instead
- Scope: strings inside JSX/HTML elements in `.tsx`, `.jsx`, `.html` files
- Exception: only when explicitly requested by user