#!/bin/bash
# pre-tool-intent-check.sh v1.1
# PreToolUse: [의도 분석] 블록 없으면 도구 사용 deny
# v1.1: tool_result user 메시지 제외, 실제 human turn만 기준점으로 사용

STDIN_JSON=$(cat)
export TRANSCRIPT
TRANSCRIPT=$(echo "$STDIN_JSON" | python3 -c "
import sys, json
try: print(json.load(sys.stdin).get('transcript_path',''))
except: print('')
" 2>/dev/null)

[ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ] && exit 0

RESULT=$(python3 << 'PYEOF'
import sys, json, os

transcript = os.environ['TRANSCRIPT']
messages = []
with open(transcript) as f:
    for line in f:
        try:
            d = json.loads(line.strip())
            if d.get('type') in ('user', 'assistant'):
                messages.append(d)
        except:
            pass

def is_human_turn(msg):
    """tool_result user 메시지 제외, 실제 사용자 입력만 True"""
    if msg.get('type') != 'user':
        return False
    content = msg.get('message', {}).get('content', [])
    if isinstance(content, list):
        for item in content:
            if item.get('type') == 'tool_result':
                return False
    return True

# 마지막 실제 human turn 인덱스 찾기
last_human_idx = next(
    (i for i in range(len(messages)-1, -1, -1) if is_human_turn(messages[i])),
    None
)
if last_human_idx is None:
    print('skip'); sys.exit(0)

# 마지막 human turn 이후 모든 assistant 메시지에서 [의도 분석] 탐색
for m in messages[last_human_idx + 1:]:
    if m.get('type') != 'assistant':
        continue
    content = m.get('message', {}).get('content', [])
    items = content if isinstance(content, list) else [{'type': 'text', 'text': str(content)}]
    for item in items:
        if item.get('type') == 'text' and '[의도 분석]' in item.get('text', ''):
            print('found'); sys.exit(0)

print('not_found')
PYEOF
)

if [ "$RESULT" = "not_found" ]; then
    python3 -c "
import json
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': '[의도 분석] 누락. 먼저 출력 후 도구 사용:\n[의도 분석]\nX: ...\nY: ...\nZ: ...\n신뢰도: 0.X'
    }
}, ensure_ascii=False))
"
fi

exit 0
