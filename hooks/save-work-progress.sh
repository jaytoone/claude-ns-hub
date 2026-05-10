#!/bin/bash
# Work Progress Auto-Save (Tier 1 Enhancement)
# Version: 1.0.0
# Called by PreCompact Hook

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id')
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path')
TRIGGER=$(echo "$INPUT" | jq -r '.trigger')

# 프로젝트별 격리: 현재 디렉토리 해시를 파일명에 포함
PROJECT_HASH=$(echo "$(pwd)" | md5sum | head -c8)
WORK_PROGRESS="$HOME/.claude/.work-progress-${PROJECT_HASH}.md"

# Start document
echo "# 📋 작업 진행 상황" > "$WORK_PROGRESS"
echo "" >> "$WORK_PROGRESS"
echo "**Session**: $SESSION_ID" >> "$WORK_PROGRESS"
echo "**Time**: $(date +"%Y-%m-%d %H:%M:%S")" >> "$WORK_PROGRESS"
echo "**Trigger**: $TRIGGER" >> "$WORK_PROGRESS"
echo "" >> "$WORK_PROGRESS"

# === Task 자동 추출 ===
if [ -f "$TRANSCRIPT" ]; then
    # TaskCreate 이벤트에서 Task ID + 설명 추출
    TASK_INFO=$(tail -500 "$TRANSCRIPT" 2>/dev/null | \
      jq -r 'select(.role=="user") | .content' 2>/dev/null | \
      grep -o 'Task #[0-9]\+ created successfully: .*' | \
      tail -5)

    if [ -n "$TASK_INFO" ]; then
        echo "## 🎯 생성된 Task (최근 5개)" >> "$WORK_PROGRESS"
        echo "" >> "$WORK_PROGRESS"
        echo "$TASK_INFO" | while IFS= read -r line; do
            task_id=$(echo "$line" | grep -o 'Task #[0-9]\+')
            task_desc=$(echo "$line" | sed 's/.*: //')
            echo "- **$task_id**: $task_desc" >> "$WORK_PROGRESS"
        done
        echo "" >> "$WORK_PROGRESS"
    fi
fi

# === Git 파일 변경 추적 ===
if git rev-parse --git-dir > /dev/null 2>&1; then
    CHANGED_FILES=$(git diff --name-only HEAD~1..HEAD 2>/dev/null | head -10)

    if [ -n "$CHANGED_FILES" ]; then
        echo "## 📝 최근 수정 파일 (마지막 커밋)" >> "$WORK_PROGRESS"
        echo "" >> "$WORK_PROGRESS"
        echo '```' >> "$WORK_PROGRESS"
        echo "$CHANGED_FILES" >> "$WORK_PROGRESS"
        echo '```' >> "$WORK_PROGRESS"
        echo "" >> "$WORK_PROGRESS"
    fi

fi

# === 마지막 사용자 메시지 (컨텍스트) ===
if [ -f "$TRANSCRIPT" ]; then
    LAST_USER_MSG=$(tail -100 "$TRANSCRIPT" 2>/dev/null | \
      jq -r 'select(.role=="user") | .content' 2>/dev/null | \
      tail -1 | \
      head -c 300)

    if [ -n "$LAST_USER_MSG" ]; then
        echo "## 💬 마지막 요청" >> "$WORK_PROGRESS"
        echo "" >> "$WORK_PROGRESS"
        echo "> $LAST_USER_MSG" >> "$WORK_PROGRESS"
        echo "" >> "$WORK_PROGRESS"
    fi
fi

# === 작업 디렉토리 ===
echo "## 📂 작업 디렉토리" >> "$WORK_PROGRESS"
echo "" >> "$WORK_PROGRESS"
echo '```' >> "$WORK_PROGRESS"
echo "$(pwd)" >> "$WORK_PROGRESS"
echo '```' >> "$WORK_PROGRESS"

# === 오래된 work-progress 정리 (30일 이상, 백그라운드) ===
(find "$HOME/.claude" -maxdepth 1 -name '.work-progress-*.md' -mtime +30 -delete 2>/dev/null) &

exit 0
