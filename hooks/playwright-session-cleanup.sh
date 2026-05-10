#!/bin/bash
SESSIONS_DIR="$HOME/.playwright-sessions"
[ -d "$SESSIONS_DIR" ] || exit 0

# 살아있는 Chrome 프로세스 강제 종료
if pgrep -f "playwright-sessions/" >/dev/null 2>&1; then
  pkill -9 -f "playwright-sessions/" 2>/dev/null
  sleep 0.5
fi

# SingletonLock / SingletonSocket 제거
find "$SESSIONS_DIR" -name "SingletonLock" -o -name "SingletonSocket" 2>/dev/null | xargs rm -f 2>/dev/null

echo "[playwright-cleanup] Done"
