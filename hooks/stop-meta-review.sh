#!/bin/bash
# Stop Hook: intent-vs-implementation metacognitive review
#
# Behavior:
#   - When code file changes are detected → Claude reads the git diff directly
#     and performs the review
#   - Flag based on git commit hash + diff hash prevents duplicate runs
#   - Flag creation = review-complete signal (windows-stop.sh holds its
#     notification in the meantime)
#
# Limitation: self-preference bias exists when an LLM evaluates its own output —
# only obvious misses/mismatches are detected (subtle quality issues should be
# caught via manual code-reviewer / intent-validator calls).
#
# Version: 1.2.0 (2026-02-20)

LOG_FILE="/tmp/meta-review-hook.log"
echo "=== Meta Review Hook $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"
echo "[INFO] PWD: $PWD" >> "$LOG_FILE"

# ────────────────────────────────────────────────────────────────
# 1. Detect code file changes
# ────────────────────────────────────────────────────────────────
CODE_CHANGES=$(git -C "$PWD" diff HEAD~1 HEAD --name-only 2>/dev/null \
  | grep -E '\.(py|ts|tsx|js|jsx|sh|yaml|yml)$' \
  | grep -v -E '(commit_tree|\.min\.|node_modules|__pycache__)' \
  | head -10)

STAGED_CHANGES=$(git -C "$PWD" diff --cached --name-only 2>/dev/null \
  | grep -E '\.(py|ts|tsx|js|jsx|sh|yaml|yml)$' \
  | head -5)

ALL_CODE_CHANGES=$(printf "%s\n%s" "$CODE_CHANGES" "$STAGED_CHANGES" \
  | sort -u | grep -v '^$')

if [ -z "$ALL_CODE_CHANGES" ]; then
  echo "[SKIP] No code file changes" >> "$LOG_FILE"
  echo '{"decision": "approve"}'
  exit 0
fi

CHANGE_COUNT=$(echo "$ALL_CODE_CHANGES" | wc -l | tr -d ' ')
echo "[INFO] Changed code files: ${CHANGE_COUNT}" >> "$LOG_FILE"

# ────────────────────────────────────────────────────────────────
# 2. Flag-based dedup
# ────────────────────────────────────────────────────────────────
GIT_HASH=$(git -C "$PWD" rev-parse --short HEAD 2>/dev/null || echo "no-git")

DIFF_CONTENT=$(git -C "$PWD" diff HEAD 2>/dev/null | head -500)
DIRTY_SUFFIX=""
if [ -n "$DIFF_CONTENT" ]; then
  DIFF_HASH=$(echo "$DIFF_CONTENT" | md5sum | cut -d' ' -f1 | head -c8)
  DIRTY_SUFFIX="-d${DIFF_HASH}"
fi

META_KEY="${GIT_HASH}${DIRTY_SUFFIX}"
META_FLAG="/tmp/meta-reviewed-${META_KEY}.flag"

if [ -f "$META_FLAG" ]; then
  echo "[APPROVED] Metacognitive review already completed ($META_KEY)" >> "$LOG_FILE"
  echo '{"decision": "approve"}'
  exit 0
fi

echo "[INFO] New change detected → Claude performs metacognitive review directly: $META_KEY" >> "$LOG_FILE"

# ────────────────────────────────────────────────────────────────
# 3. Most recent commit (truncated to one line to avoid parsing errors)
# ────────────────────────────────────────────────────────────────
RECENT_COMMIT=$(git -C "$PWD" log --oneline -1 2>/dev/null | cut -c1-60 || echo "(no commits)")

# ────────────────────────────────────────────────────────────────
# 4. Generate JSON (pass python3 variables via env)
# ────────────────────────────────────────────────────────────────
META_FLAG="$META_FLAG" \
META_KEY="$META_KEY" \
CHANGE_COUNT="$CHANGE_COUNT" \
RECENT_COMMIT="$RECENT_COMMIT" \
FILES_JOINED="$(echo "$ALL_CODE_CHANGES" | tr '\n' '|')" \
python3 - << 'PYEOF'
import json, os

meta_flag    = os.environ['META_FLAG']
meta_key     = os.environ['META_KEY']
change_count = os.environ['CHANGE_COUNT']
recent_commit= os.environ['RECENT_COMMIT']
files_raw    = os.environ['FILES_JOINED']

files_list = '\n'.join(f'  - {f}' for f in files_raw.split('|') if f.strip())

reason = f"""━━━ Metacognitive Review ({meta_key}) ━━━

[Most recent commit] {recent_commit}
[Changed code files: {change_count}]
{files_list}

━━━ Perform directly (in order) ━━━

**Step 1**: Inspect the changes

  git diff HEAD~1 HEAD -- {files_raw.replace('|', ' ').strip()} 2>/dev/null | head -200

If there are uncommitted changes:
  git diff HEAD -- {files_raw.replace('|', ' ').strip()} 2>/dev/null | head -200

**Step 2**: Recall the user's last request in this conversation and verify the 3 items below

  [ ] MISMATCH  — the requested feature was implemented differently
  [ ] INCOMPLETE — the requested feature is missing or left as TODO/stubbed
  [ ] DRIFT     — changes were added that were not requested (decide whether intentional)

**Step 3**: Output the result

  - On issue: report to the user in the form "[META ISSUE] MISMATCH: ..."
  - All OK: output a single line "META OK"

**Step 4**: Must run after completion (do not finish without this command)

  touch {meta_flag}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

result = {"decision": "block", "reason": reason, "continue": True}
print(json.dumps(result, ensure_ascii=False))
PYEOF

exit 0
