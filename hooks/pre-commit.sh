#!/bin/bash
# Pre-commit secret scanner — M936
# Blocks commits containing API keys, tokens, or personal credentials

RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

PATTERNS=(
  'ghp_[a-zA-Z0-9]{36}'          # GitHub PAT
  'hf_[a-zA-Z0-9]{20,}'          # HuggingFace token
  'sk-[a-zA-Z0-9]{20,}'           # OpenAI/generic sk- key
  'sb_[a-zA-Z0-9]{20,}'           # Supabase key
  'supabase.*service_role'         # Supabase service role
  'SUPABASE_SERVICE_KEY'
  'pypi-[a-zA-Z0-9\-_]{40,}'      # PyPI token
  'replicate.*r8_[a-zA-Z0-9]{40}' # Replicate token
  'r8_[a-zA-Z0-9]{40}'
  'paddle.*live_[a-zA-Z0-9]{40}'  # Paddle API key
  'ANTHROPIC_API_KEY.*sk-ant'      # Anthropic key
  'sk-ant-[a-zA-Z0-9\-_]{40,}'
  'AIza[0-9A-Za-z\-_]{35}'        # Google API key
  '[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com'  # Google OAuth client ID
  'ya29\.[0-9A-Za-z\-_]+'        # Google OAuth access token
  'notify_token.*=.*[a-zA-Z0-9]{20,}' # ntfy/bark token
  'bark.*key.*=.*[a-zA-Z0-9]{16,}'
)

FOUND=0
STAGED=$(git diff --cached --name-only --diff-filter=ACM)

for FILE in $STAGED; do
  # Skip binary files
  if git show ":$FILE" | file - | grep -q binary; then continue; fi
  for PATTERN in "${PATTERNS[@]}"; do
    MATCH=$(git show ":$FILE" | grep -iE "$PATTERN" | head -1)
    if [ -n "$MATCH" ]; then
      echo -e "${RED}SECRET DETECTED${NC} in ${YELLOW}$FILE${NC}"
      echo "  Pattern: $PATTERN"
      echo "  Match:   ${MATCH:0:80}..."
      FOUND=1
    fi
  done
done

if [ $FOUND -eq 1 ]; then
  echo ""
  echo -e "${RED}Commit BLOCKED.${NC} Remove secrets before committing."
  echo "Use 'git diff --cached' to review staged changes."
  exit 1
fi

exit 0
