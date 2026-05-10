#!/bin/bash
# Stop hook (command): read session_id at Stop and save per-project pointer file.
#
# Purpose: on Stop, read session_id and save it so downstream Stop agents can
#          locate per-session intent files.
#
# Version: 1.0.0 (2026-02-20) - initial session-isolation implementation
# Execution order: stop-playwright → [this script] → stop-agent → windows-stop

INPUT=$(cat)

# Extract session_id
SESSION_ID=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('session_id', '').strip()[:12])
except:
    print('')
" 2>/dev/null)

if [ -z "$SESSION_ID" ]; then
    exit 0
fi

# Save per-project session pointer file
GIT_ROOT=$(git -C "$(pwd)" rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
GIT_ROOT_HASH=$(echo "$GIT_ROOT" | md5sum | cut -d' ' -f1 | head -c8)

echo "$SESSION_ID" > "/tmp/claude-stop-session-${GIT_ROOT_HASH}.txt"

exit 0
