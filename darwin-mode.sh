#!/bin/bash
# Switch Claude Code to use Darwin-28B-Coder via local bridge
# Bridge: localhost:8860 → NIPA:8850 → lmdeploy:8790 (darwin28b_code_v2)

# Start SSH tunnel if not running
if ! curl -sf http://localhost:8860/health >/dev/null 2>&1; then
  echo "Starting SSH tunnel to NIPA..."
  ssh -i ~/.ssh/id_container -p 10522 -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
    -fN -L 8860:localhost:8850 work@proxy3.nipa2025.ktcloud.com
  sleep 3
fi

if curl -sf http://localhost:8860/health >/dev/null 2>&1; then
  echo "Bridge ready at http://localhost:8860"
  echo ""
  echo "To use Darwin in Claude Code, start it with:"
  echo "  ANTHROPIC_BASE_URL=http://localhost:8860 ANTHROPIC_API_KEY=darwin-2026 claude"
  echo ""
  echo "Or export for current shell:"
  export ANTHROPIC_BASE_URL=http://localhost:8860
  export ANTHROPIC_API_KEY=darwin-2026
  echo "  ANTHROPIC_BASE_URL=$ANTHROPIC_BASE_URL"
  echo "  ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
else
  echo "ERROR: Bridge not reachable"
fi
