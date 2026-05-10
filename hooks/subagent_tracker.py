#!/usr/bin/env python3
"""
Subagent Tracker — SubagentStart / SubagentStop Hook (async)
역할: 어떤 에이전트가 실행 중인지 /tmp/stream-log.txt에 기록
"""
import json, sys, os
from datetime import datetime

def main():
    data = json.load(sys.stdin)
    # 실제 payload 키 우선순위: agent_name > name > agent_type > subagentType > "unknown"
    agent_name = (data.get("agent_name")
                  or data.get("name")
                  or data.get("agent_type")
                  or data.get("subagentType")
                  or data.get("type")
                  or "unknown")
    event = os.environ.get("CLAUDE_HOOK_EVENT", "SubagentEvent")

    # 빈 문자열 방어
    if not agent_name or agent_name.strip() == "":
        agent_name = f"[{','.join(data.keys())}]"  # 실제 키 목록 기록

    log_line = f"[{datetime.now().strftime('%H:%M:%S')}] {event}: {agent_name}\n"

    try:
        with open("/tmp/stream-log.txt", "a") as f:
            f.write(log_line)
    except Exception:
        pass  # 로깅 실패는 무시

if __name__ == "__main__":
    main()
