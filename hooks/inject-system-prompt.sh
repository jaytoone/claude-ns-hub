#!/bin/bash
# Enhanced system prompt injection with task restoration and Git-smart document loading
# Version: 5.5.0 (node1-ask 트리거 → CLAUDE.md로 이전, hook에서 제거)


COMPACT_MARKER="$HOME/.claude/.compact-marker"
RECOVERY_PATH="$HOME/.claude/hooks/post-compact-recovery.md"
# 프로젝트별 격리: PROJECT_ROOT 해시로 work-progress 파일 분리
PROJECT_HASH=$(echo "${PROJECT_ROOT:-$PWD}" | md5sum | head -c8)
WORK_PROGRESS="$HOME/.claude/.work-progress-${PROJECT_HASH}.md"
TOKEN_LOG="$HOME/.claude/.git-smart-token-usage.log"
MEMORY_HINT="$HOME/.claude/.memory-update-hint.md"

# Handle compact recovery if marker exists
if [ -f "$COMPACT_MARKER" ]; then
    if [ -f "$RECOVERY_PATH" ]; then
        cat "$RECOVERY_PATH"
        echo ""
    fi
    rm -f "$COMPACT_MARKER"
fi

# MEMORY.md 업데이트 힌트 - compact 여부와 무관하게 감지 (v4.2)
# SessionEnd 또는 PreCompact 후 생성됨
if [ -f "$MEMORY_HINT" ]; then
    echo "<!-- MEMORY.md Update Required -->"
    echo "⚡ **[자동 감지]** MEMORY.md 업데이트가 필요합니다."
    head -2 "$MEMORY_HINT" 2>/dev/null | sed 's/^/> /'  # 멀티라인 > 프리픽스 보장
    echo ""
    echo "> 현재 프로젝트 상태를 확인하고 즉시 업데이트 후 \`rm ~/.claude/.memory-update-hint.md\`를 실행하세요."
    echo ""
    # 힌트 파일은 Claude가 업데이트 완료 후 직접 삭제 (여기서 자동 삭제 안 함)
fi

# Restore work progress (NEW in v2.0.0)
if [ -f "$WORK_PROGRESS" ]; then
    echo ""
    echo "<!-- Work Progress Restoration -->"
    echo "## 📋 이전 작업 진행 상황"
    echo ""
    cat "$WORK_PROGRESS"
fi

# Git-smart document loading (v4.1: Cooldown - 1 hour limit)
PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
DOCS_DIR="$PROJECT_ROOT/docs"
GIT_SMART_FLAG="$HOME/.claude/.git-smart-cooldown"
GIT_SMART_COOLDOWN=3600  # 1 hour in seconds

# Check cooldown: skip git-smart if ran within last hour
SKIP_GIT_SMART=false
if [ -f "$GIT_SMART_FLAG" ]; then
    LAST_RUN=$(cat "$GIT_SMART_FLAG" 2>/dev/null)
    LAST_RUN=${LAST_RUN:-0}  # 빈 파일 방어: 산술 오류 방지
    NOW=$(date +%s)
    ELAPSED=$((NOW - LAST_RUN))
    if [ $ELAPSED -lt $GIT_SMART_COOLDOWN ]; then
        SKIP_GIT_SMART=true
    fi
fi

# Only load if in a git repository and docs directory exists, and cooldown passed
if [ "$SKIP_GIT_SMART" = false ] && [ -d "$DOCS_DIR" ] && git rev-parse --git-dir > /dev/null 2>&1; then
    date +%s > "$GIT_SMART_FLAG"

    # === AUTO-TUNING: Project Size Detection (단일 find 패스, 배치 exec) ===
    _MD_STATS=$(find "$DOCS_DIR" -name "*.md" -exec wc -l {} + 2>/dev/null)
    TOTAL_FILES=$(echo "$_MD_STATS" | awk '$2 != "total" && NF>=2{count++} END{print count+0}')
    AVG_SIZE=$(echo "$_MD_STATS" | awk '$2 != "total" && NF>=2{sum+=$1; count++} END{if(count>0) print int(sum/count); else print 500}')

    # Default values based on project size
    if [ "$TOTAL_FILES" -gt 100 ]; then
        # Large project (100+ files)
        AUTO_COMMIT_RANGE=3
        AUTO_MAX_FILES=2
        AUTO_LINES_PER_FILE=100
    elif [ "$TOTAL_FILES" -gt 50 ]; then
        # Medium project (50-100 files)
        AUTO_COMMIT_RANGE=5
        AUTO_MAX_FILES=3
        AUTO_LINES_PER_FILE=150
    else
        # Small project (<50 files)
        AUTO_COMMIT_RANGE=10
        AUTO_MAX_FILES=5
        AUTO_LINES_PER_FILE=200
    fi

    # Adjust for long documents
    if [ "$AVG_SIZE" -gt 1000 ]; then
        AUTO_LINES_PER_FILE=$((AUTO_LINES_PER_FILE * 80 / 100))
    fi

    # Environment variables override (user can still customize)
    COMMIT_RANGE="${GIT_SMART_COMMIT_RANGE:-$AUTO_COMMIT_RANGE}"
    MAX_FILES="${GIT_SMART_MAX_FILES:-$AUTO_MAX_FILES}"
    LINES_PER_FILE="${GIT_SMART_LINES_PER_FILE:-$AUTO_LINES_PER_FILE}"
    FILE_PATTERN="${GIT_SMART_FILE_PATTERN:-docs/.*\.md$}"

    # === TOKEN MONITORING ===
    TOKEN_BUDGET=2000  # Target budget
    TOTAL_LINES=0
    TOTAL_TOKENS=0

    # Get recently modified files
    RECENT_FILES=$(git diff --name-only HEAD~${COMMIT_RANGE}..HEAD 2>/dev/null | \
                   grep "$FILE_PATTERN" | \
                   head -${MAX_FILES})

    # Calculate actual token usage
    if [ -n "$RECENT_FILES" ]; then
        while IFS= read -r file; do
            if [ -f "$file" ]; then
                file_lines=$(wc -l < "$file" 2>/dev/null || echo 0)
                actual_lines=$((file_lines < LINES_PER_FILE ? file_lines : LINES_PER_FILE))
                TOTAL_LINES=$((TOTAL_LINES + actual_lines))
                TOTAL_TOKENS=$((TOTAL_TOKENS + actual_lines * 4))  # ~4 tokens/line
            fi
        done <<< "$RECENT_FILES"

        # Auto-adjust if over budget (비율 계산으로 단일 패스 처리)
        ACTUAL_TOKENS=$TOTAL_TOKENS  # 조정 전 실제값 보존
        if [ $TOTAL_TOKENS -gt $TOKEN_BUDGET ]; then
            LINES_PER_FILE=$((LINES_PER_FILE * TOKEN_BUDGET / TOTAL_TOKENS))
            TOTAL_TOKENS=$TOKEN_BUDGET
        fi

        # Log token usage (ACTUAL_TOKENS = 조정 전 실제 추정값)
        echo "$(date +"%Y-%m-%d %H:%M:%S"),${TOTAL_FILES},${AVG_SIZE},${COMMIT_RANGE},${MAX_FILES},${LINES_PER_FILE},${ACTUAL_TOKENS},${TOKEN_BUDGET}" >> "$TOKEN_LOG"

        # Display documents
        echo ""
        echo "<!-- Git-Smart Document Loading -->"
        echo "## 📄 최근 작업 문서 (Git-Smart v4.0)"
        echo ""
        echo "**Auto-Tuning**: Project: ${TOTAL_FILES} files, Avg: ${AVG_SIZE} lines | Range: ${COMMIT_RANGE} commits, Max: ${MAX_FILES} files, Lines: ${LINES_PER_FILE}/file"
        echo ""
        echo "**Token Usage**: ${TOTAL_TOKENS}/${TOKEN_BUDGET} tokens ($(((TOTAL_TOKENS * 100) / TOKEN_BUDGET))%)"
        echo ""

        echo "$RECENT_FILES" | while IFS= read -r file; do
            if [ -f "$file" ]; then
                echo "### 📝 $file"
                echo ""
                head -${LINES_PER_FILE} "$file"
                echo ""
                echo "---"
                echo ""
            fi
        done
    fi
fi
