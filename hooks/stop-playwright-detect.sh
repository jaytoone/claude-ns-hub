#!/bin/bash
# stop-playwright-detect.sh v5.1.1 (2026-05-04)
export PW_LANG=en  # Always use English output (CLAUDE.md: respond in English)
# Detect UI changes → prompt Playwright verification
# Flag: /tmp/pw-checked-{SESSION_HASH}-{HEAD_HASH}-{TARGETS_HASH}.flag
#
# v5.0.0 Changes:
#   - Split out pw_analysis.py (Python logic externalized)
#   - python3 calls reduced from ~9 to 2 (normal flow)
#   - Removed 3 heredoc Python blocks
#   - 820 lines → ~200 lines (75% reduction)

# ── Parse input (single python3 call) ─────────────────────────────
INPUT=$(cat)
eval "$(echo "$INPUT" | python3 -c "
import json, sys, shlex
d = json.load(sys.stdin)
print('CWD=' + shlex.quote(str(d.get('cwd',''))))
print('SESSION_ID=' + shlex.quote(str(d.get('session_id',''))))
print('STOP_HOOK_ACTIVE=' + shlex.quote(str(d.get('stop_hook_active',False))))
" 2>/dev/null)" || true
[ -z "$CWD" ] && CWD="$PWD"
[ -z "$STOP_HOOK_ACTIVE" ] && STOP_HOOK_ACTIVE="False"
[ "$STOP_HOOK_ACTIVE" = "True" ] && exit 0
[ -f "$CWD/.playwright-skip" ] && exit 0

# ── Project scope: only run in projects that have playwright.config.* ─
PW_CONFIG=$(find "$CWD" -maxdepth 3 -name 'playwright.config.*' -type f 2>/dev/null | head -1)
[ -z "$PW_CONFIG" ] && exit 0

# ── Auto-clean /tmp ui-* artifacts (7 days, background) ───────────
(find /tmp -maxdepth 1 \( \
  -name 'pw-block-*.flag' -o \
  -name 'pw-checked-*.flag' -o \
  -name 'pw-notified-*.flag' \
\) -mmin +10080 -delete 2>/dev/null) &

# ── JSON block output helper ──────────────────────────────────────
block_exit() {
  printf '%s' "$1" | python3 -c \
    "import json,sys; print(json.dumps({'decision':'block','reason':sys.stdin.read()}))" 2>/dev/null
  exit 0
}

# ── 1. Detect changed files (3-source) ────────────────────────────
SESSION_SNAPSHOT="/tmp/pw-session-snapshot-${SESSION_ID}.txt"
SESSION_START_HEAD="/tmp/pw-session-head-${SESSION_ID}.txt"

CURRENT_UNSTAGED=$(git -C "$CWD" -c core.quotepath=false diff HEAD --name-only 2>/dev/null)
PORCELAIN_RAW=$(git -C "$CWD" -c core.quotepath=false status --porcelain 2>/dev/null)
UNTRACKED=$(echo "$PORCELAIN_RAW" | grep '^??' | sed 's/^?? //')
DELETED_FILES=$(echo "$PORCELAIN_RAW" | grep '^ D\|^D ' | sed 's/^.. //')

CURRENT_ALL=$(printf '%s\n%s\n%s' \
  "$CURRENT_UNSTAGED" "$UNTRACKED" "$DELETED_FILES" \
  | grep -v '^[[:space:]]*$' | sort -u)

# New session: if snapshot is missing, save current state and skip
if [ ! -f "$SESSION_START_HEAD" ]; then
    git -C "$CWD" rev-parse HEAD > "$SESSION_START_HEAD" 2>/dev/null
    echo "$CURRENT_ALL" > "$SESSION_SNAPSHOT" 2>/dev/null
    [ -z "$CURRENT_ALL" ] && exit 0
    block_exit "New Claude session started - ignoring prior uncommitted changes.

If you have new work from this session, please mention it."
fi

# Existing session: extract only new changes since the snapshot
SESSION_BASE_FILES=$(cat "$SESSION_SNAPSHOT" 2>/dev/null)
SESSION_INIT_HEAD=$(cat "$SESSION_START_HEAD" 2>/dev/null)
CURRENT_HEAD=$(git -C "$CWD" rev-parse HEAD 2>/dev/null)

COMMITTED_SINCE_START=""
if [ -n "$SESSION_INIT_HEAD" ] && [ "$SESSION_INIT_HEAD" != "$CURRENT_HEAD" ]; then
    COMMITTED_SINCE_START=$(git -C "$CWD" -c core.quotepath=false diff --name-only "${SESSION_INIT_HEAD}..HEAD" 2>/dev/null)
fi

if [ -n "$SESSION_BASE_FILES" ]; then
    CHANGED=""
    for f in $CURRENT_ALL; do
        if ! echo "$SESSION_BASE_FILES" | grep -q "^${f}$"; then
            CHANGED="${CHANGED}
${f}"
        fi
    done
    CHANGED=$(echo "$CHANGED" | grep -v '^[[:space:]]*$' | sort -u)
else
    CHANGED="$CURRENT_ALL"
fi

if [ -n "$COMMITTED_SINCE_START" ]; then
    CHANGED=$(printf '%s\n%s' "$CHANGED" "$COMMITTED_SINCE_START" | grep -v '^[[:space:]]*$' | sort -u)
fi

if [ -z "$CHANGED" ]; then
    block_exit "No new work in this Claude session.

If you have newly changed files, please mention them."
fi

# ── 2. Skip patterns (extension + build artifacts) ────────────────
SKIP_EXT='\.md$|\.txt$|\.rst$|\.pdf$|\.csv$|\.log$'
SKIP_EXT+="|\.py$|\.pyc$|\.pyo$|\.pyd$|__pycache__/"
SKIP_EXT+="|\.ipynb$|\.pkl$|\.pt$|\.safetensors$|\.bin$|\.npy$"
SKIP_EXT+="|\.lock$|\.gitignore$|Dockerfile$"
SKIP_EXT+="|\.sh$|\.bash$|\.zsh$|\.fish$"
SKIP_EXT+="|\.yml$|\.yaml$"
SKIP_EXT+="|\.db$|\.index$|\.sqlite$|\.sqlite3$"
SKIP_EXT+="|\.spec\.ts$|\.test\.ts$|\.spec\.tsx$|\.test\.tsx$"
SKIP_EXT+="|\.test\.js$|\.test\.jsx$|\.spec\.js$|\.spec\.jsx$"
SKIP_EXT+="|tsconfig\.tsbuildinfo$|\.tsbuildinfo$|next-env\.d\.ts$"
SKIP_EXT+="|commit_tree\.txt$|MEMORY\.md$"
SKIP_EXT+="|hnsw\.|sona-patterns"
SKIP_EXT+="|\.png$|\.jpg$|\.jpeg$|\.gif$|\.svg$|\.ico$|\.webp$"
SKIP_EXT+="|\.woff$|\.woff2$|\.ttf$|\.eot$"
SKIP_DIR='^dist/|^\.next/|^build/|^out/|^\.git/|^node_modules/'
SKIP_DIR+="|^playwright-report/|^\.playwright/|^\.claude/"
SKIP_DIR+="|^\.swarm/|^\.env|^\.github/"
SKIP_DIR+="|^coverage/|^\.turbo/|^\.vercel/"
SKIP="${SKIP_EXT}|${SKIP_DIR}"

TARGETS=$(echo "$CHANGED" | grep -vE "$SKIP")

# ── 3. Duplicate-verification guard ───────────────────────────────
SESSION_HASH=$(echo -n "$SESSION_ID" | md5sum | cut -c1-8)
DIFF_HASH=$(printf '%s' "$TARGETS" | sort | md5sum | cut -c1-8)
[ "$DIFF_HASH" = "d41d8cd9" ] && DIFF_HASH=$(git -C "$CWD" diff HEAD~1 HEAD 2>/dev/null | md5sum | cut -c1-8)
HEAD_HASH=$(git -C "$CWD" rev-parse --short HEAD 2>/dev/null)
FLAG="/tmp/pw-checked-${SESSION_HASH}-${HEAD_HASH}-${DIFF_HASH}.flag"
BLOCK="/tmp/pw-block-${SESSION_HASH}.flag"

# 3-A. Cross-session verification (exact HEAD_HASH + DIFF_HASH match — prevents reusing stale verifications from other sessions)
CROSS_SESSION_FLAG=$(find /tmp -maxdepth 1 -name "pw-checked-*-${HEAD_HASH}-${DIFF_HASH}.flag" 2>/dev/null | head -1)
if [ -n "$CROSS_SESSION_FLAG" ]; then
  rm -f "$BLOCK"
  UNCOMMITTED=$(git -C "$CWD" diff HEAD --name-only 2>/dev/null | grep -vE "$SKIP" | head -5)
  STAGED=$(git -C "$CWD" diff --cached --name-only 2>/dev/null | grep -vE "$SKIP" | head -5)
  if [ -n "$UNCOMMITTED" ] || [ -n "$STAGED" ]; then
    block_exit "Cross-session verification passed (reusing existing verification result).

Changed files:
${UNCOMMITTED}${STAGED}

Commit steps:
1. Inspect changes with: git diff HEAD --stat
2. Append one new version line to commit_tree.txt
3. git add <changed files> commit_tree.txt
4. git commit -F commit_tree.txt"
  else
    block_exit "Cross-session verification passed. No uncommitted changes — mention any additional work."
  fi
fi

# 3-B. Same-session verification complete (exact SESSION_HASH + HEAD_HASH + DIFF_HASH match — forces re-verification after new commits)
SAME_SESSION_FLAG=$(find /tmp -maxdepth 1 -name "pw-checked-${SESSION_HASH}-${HEAD_HASH}-${DIFF_HASH}.flag" 2>/dev/null | head -1)
if [ -n "$SAME_SESSION_FLAG" ] || [ -f "$FLAG" ]; then
  rm -f "$BLOCK"
  touch "/tmp/pw-notified-${SESSION_HASH}.flag"
  UNCOMMITTED=$(git -C "$CWD" diff HEAD --name-only 2>/dev/null | grep -vE "$SKIP" | head -5)
  STAGED=$(git -C "$CWD" diff --cached --name-only 2>/dev/null | grep -vE "$SKIP" | head -5)
  if [ -n "$UNCOMMITTED" ] || [ -n "$STAGED" ]; then
    block_exit "Playwright verification complete. Please commit the uncommitted changes.

Changed files:
${UNCOMMITTED}${STAGED}

Commit steps:
1. Inspect changes with: git diff HEAD --stat
2. Append one new version line to commit_tree.txt
3. git add <changed files> commit_tree.txt
4. git commit -F commit_tree.txt"
  else
    block_exit "Playwright verification complete. No uncommitted changes — mention any additional work."
  fi
fi

# 3-C. BLOCK re-entry guard
[ -f "$BLOCK" ] && [ -z "$TARGETS" ] && rm -f "$BLOCK"
if [ -f "$BLOCK" ]; then
  CTX_JSON="/tmp/pw-context-${SESSION_HASH}.json"
  if [ -f "$CTX_JSON" ]; then
    REMINDER=$(python3 - <<PYEOF 2>/dev/null
import json, sys, subprocess, socket
ctx = json.load(open("${CTX_JSON}"))
fw           = ctx.get("fw", "?")
url          = ctx.get("url", "?")
mag          = ctx.get("magnitude", "?")
total        = len(ctx.get("targets", []))
cats         = ctx.get("cats", {})
dev_cmd      = ctx.get("dev_cmd", "npm run dev")
can_start    = ctx.get("can_start_local", True)
deployed_url = ctx.get("deployed_url", "")
has_uncommitted = ctx.get("has_uncommitted", True)  # True=not deployed, False=deployed
cat_order = ["page","component","api","hook","style","config","store","edge_function","migration","util","type"]
cat_str = " ".join(f"[{k.upper()}]" for k in cat_order if cats.get(k)) or "[UTIL]"

# Recheck server state on re-entry
def server_alive(url_check):
    try:
        r = subprocess.run(["curl","-sf","--max-time","2",url_check], capture_output=True, timeout=4)
        return r.returncode == 0
    except Exception:
        return False

srv_running = server_alive(url if url.startswith("http://localhost") else "")
local_url_reentry = url if url.startswith("http://localhost") else f"http://localhost:3000"
dep_url = deployed_url if deployed_url.startswith("http") else (f"https://{deployed_url}" if deployed_url else "")

# Decide which URL to verify: uncommitted → local, committed + deployed URL → deployed server
use_deployed = (not has_uncommitted) and bool(deployed_url)

if srv_running:
    srv_state = "(running)"
    check_url = local_url_reentry
elif use_deployed:
    srv_state = "(deployed server)"
    check_url = dep_url
else:
    srv_state = f"(stopped - run {dev_cmd})"
    check_url = local_url_reentry

# can_start_local=False + server down + not deployed → cannot verify
cannot_verify = (not srv_running) and (not use_deployed) and (not can_start)

file_unit = "files"
srv_lbl, cat_lbl = "Server", "Categories"
if srv_running:
    how = f"Verify {check_url} with Playwright, then run the flag command above"
elif use_deployed:
    how = f"Verify {check_url} (deployed server) with Playwright, then run the flag command above"
elif cannot_verify:
    how = f"[Cannot verify] No local server + no deployed URL. Deploy first or manually: touch ${{FLAG}}"
else:
    how = f"Run `{dev_cmd}` in background, verify {check_url} with Playwright, then run the flag command above"

print(f"[PLAYWRIGHT PENDING] {mag}: {total} {file_unit} | {fw}")
print(f"{srv_lbl}: {url} {srv_state}")
print(f"{cat_lbl}: {cat_str}")
print(f"Flag: touch ${FLAG}")
print(f"How to verify: {how}")
PYEOF
)
    [ -n "$REMINDER" ] && block_exit "$REMINDER" || block_exit "Verification pending. Flag: touch ${FLAG}"
  else
    block_exit "Verification pending. Flag: touch ${FLAG}"
  fi
fi

[ -z "$TARGETS" ] && exit 0

# ── 4. Analyze + output (single pw_analysis.py call) ──────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
_TMP="/tmp/pw-diff-${SESSION_HASH}.tmp"
git -C "$CWD" diff HEAD --unified=0 2>/dev/null > "${_TMP}.head"
git -C "$CWD" diff HEAD~1 HEAD --unified=0 2>/dev/null > "${_TMP}.commit"

_TARGETS_FILE="/tmp/pw-targets-${SESSION_HASH}.tmp"
_DELETED_FILE="/tmp/pw-deleted-${SESSION_HASH}.tmp"
printf '%s' "$TARGETS"      > "$_TARGETS_FILE"
printf '%s' "$DELETED_FILES" > "$_DELETED_FILE"

touch "$BLOCK"

export PW_CWD="$CWD"
export PW_TARGETS_FILE="$_TARGETS_FILE"
export PW_DELETED_FILE="$_DELETED_FILE"
export PW_DIFF_HEAD_FILE="${_TMP}.head"
export PW_DIFF_COMMIT_FILE="${_TMP}.commit"
export PW_SESSION_HASH="$SESSION_HASH"
export PW_FLAG="touch ${FLAG}"
export PW_PACKAGE_JSON="$CWD/package.json"

# Extract deployed URL: monorepo-aware — scans CWD and up to 2 sub-levels for .env.local
PW_DEPLOYED_URL=""
for _ENVKEY in NEXT_PUBLIC_BASE_URL VERCEL_URL NEXTAUTH_URL; do
  for _ENVFILE in "$CWD/.env.local" $(find "$CWD" -maxdepth 2 -name ".env.local" 2>/dev/null | sort); do
    _VAL=$(grep -E "^${_ENVKEY}=" "$_ENVFILE" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
    if [ -n "$_VAL" ] && echo "$_VAL" | grep -qE '^https?://|^[a-z0-9-]+\.vercel\.app'; then
      PW_DEPLOYED_URL="$_VAL"
      break 2
    fi
  done
done
export PW_DEPLOYED_URL

python3 "$SCRIPT_DIR/pw_analysis.py"
