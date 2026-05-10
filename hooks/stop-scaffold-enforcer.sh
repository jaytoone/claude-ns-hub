#!/bin/bash
# stop-scaffold-enforcer.sh
# Stop hook: verifies that Claude's response contains the required scaffold blocks.
# If missing → decision: block → forces Claude to redo the response.

STDIN_JSON=$(cat)

# Infinite-loop guard: stop_hook_active=true means a Stop hook is already running.
STOP_ACTIVE=$(echo "$STDIN_JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(str(d.get('stop_hook_active', False)).lower())
except: print('false')
" 2>/dev/null)

if [ "$STOP_ACTIVE" = "true" ]; then
    exit 0
fi

# Extract the Claude response text
RESPONSE=$(echo "$STDIN_JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('response_text', ''))
except: print('')
" 2>/dev/null)

# Skip verification if the response is too short (greetings, simple confirmations, etc.) — under 50 chars.
RESP_LEN=$(echo "$RESPONSE" | wc -m)
if [ "$RESP_LEN" -lt 50 ]; then
    exit 0
fi

# Verify [Intent Analysis] block is present
if ! echo "$RESPONSE" | grep -q "\[Intent Analysis\]"; then
    python3 -c "
import json
print(json.dumps({
    'decision': 'block',
    'reason': '[scaffold enforcer] [Intent Analysis] block is missing.\n\nBefore restarting the response, you must:\n1. Output the [Intent Analysis] block with X/Y/Z/confidence\n2. Output the complexity header\n3. Then write the actual answer'
}))
"
    exit 0
fi

# Verify the complexity header is present
if ! echo "$RESPONSE" | grep -qE "Complexity:?\s*(LOW|MEDIUM|HIGH)"; then
    python3 -c "
import json
print(json.dumps({
    'decision': 'block',
    'reason': '[scaffold enforcer] Complexity header is missing.\n\nAfter the [Intent Analysis] block, output the complexity header:\nComplexity: LOW|MEDIUM|HIGH'
}))
"
    exit 0
fi

exit 0
