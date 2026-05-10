#!/usr/bin/env node
/**
 * Pre-Compact Hook Handler
 * Purpose: Save session context before auto-compaction
 * Runs BEFORE Claude compacts conversation history
 */

const fs = require('fs');
const path = require('path');

const MARKER_FILE = path.join(
  process.env.HOME,
  '.claude',
  '.compact-marker'
);

// Read stdin (PreCompact hook input JSON)
let input = '';
process.stdin.setEncoding('utf8');

process.stdin.on('data', (chunk) => {
  input += chunk;
});

process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);

    // Extract transcript path and session ID
    const transcriptPath = data.transcript_path;
    const sessionId = data.session_id;
    const trigger = data.trigger; // 'auto' or 'manual'

    // Create marker file to signal compact event
    fs.writeFileSync(MARKER_FILE, `${new Date().toISOString()}\nTrigger: ${trigger}`);

    // Call save-work-progress.sh (Tier 1: Auto-save Work Progress)
    try {
      const { execFileSync } = require('child_process');
      const progressScript = path.join(process.env.HOME, '.claude', 'hooks', 'save-work-progress.sh');

      if (fs.existsSync(progressScript)) {
        execFileSync('bash', [progressScript], {
          input: JSON.stringify(data),
          encoding: 'utf8',
          timeout: 2000  // 2 second timeout
        });
        console.log(`[PreCompact] Work progress saved`);
      }
    } catch (err) {
      console.error('[PreCompact] Work progress save failed:', err.message);
    }

    // Save MEMORY.md update hint (Tier 2: Signal Claude to update MEMORY.md on recovery)
    try {
      const hintFile = path.join(process.env.HOME, '.claude', '.memory-update-hint.md');
      const hintContent = [
        `# MEMORY.md 업데이트 힌트`,
        `**Compact 발생**: ${new Date().toISOString()}`,
        `**Session**: ${sessionId}`,
        `**Trigger**: ${trigger}`,
        ``,
        `이 파일이 존재하면 MEMORY.md 업데이트가 필요합니다.`,
        `복구 후 MEMORY.md를 현재 프로젝트 상태로 업데이트하고 이 파일을 삭제하세요.`,
      ].join('\n');
      fs.writeFileSync(hintFile, hintContent);
      console.log(`[PreCompact] MEMORY.md update hint saved`);
    } catch (err) {
      // Non-critical
    }

    // Log to stdout (optional, visible to Claude)
    console.log(`[PreCompact] Context saved (trigger: ${trigger}, session: ${sessionId})`);

    // Exit successfully
    process.exit(0);
  } catch (error) {
    console.error('[PreCompact] Error:', error.message);
    // Still exit with 0 to not block compact process
    process.exit(0);
  }
});

// Handle timeout
setTimeout(() => {
  console.error('[PreCompact] Timeout');
  process.exit(0);
}, 5000);
