#!/bin/bash
# SessionStart Hook for Model Language Forcing
# Forces non-Anthropic models (MiniMax, Gemini, Qwen, GLM) to respond in EN/KR only

MODEL="${ANTHROPIC_MODEL:-}"

LANG_PROMPT="IMPORTANT: Respond ONLY in English or Korean. Never Chinese or Japanese. 100% EN/KR."

case "$MODEL" in
  MiniMax*|Gemini*|Qwen*|GLM*)
    printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}' "$LANG_PROMPT"
    ;;
  *)
    printf '{}'
    ;;
esac
