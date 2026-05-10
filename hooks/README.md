# Claude Code Prompt Enhancement Hook

## Overview

This UserPromptSubmit hook automatically enhances your prompts with relevant context based on the services mentioned in your request.

**Location**: `~/.claude/hooks/improve-prompt.py`

## How It Works

When you submit a prompt to Claude Code, this hook:
1. Analyzes your prompt for service-related keywords
2. Automatically loads relevant context about that service
3. Adds the context to Claude's processing (invisible to you)
4. Claude processes your request with full project context

## Supported Services

### 1. DWM (Deep Work Music)
**Triggers**: DWM, deep work, 음악, music, generate, composer, 오디오, audio

**Context Loaded**:
- API routes and endpoints
- Python scripts
- Database tables
- Tech stack (Gemini, MiniMax, FFmpeg, R2)
- Recent changes

### 2. YouTube Hub / GenViral
**Triggers**: youtube, viral, gemini, replicate, subtitle, 자막, 비디오

**Context Loaded**:
- API routes and components
- Database structure
- Tech stack (Gemini, Replicate, Whisper, FFmpeg)
- Feature list

### 3. Oddsculator
**Triggers**: oddsculator, backtest, 백테스트, strategy, 전략, crypto, trading

**Context Loaded**:
- API routes
- Python backtest scripts
- Database structure
- Auto-discovery features

### 4. Briefer
**Triggers**: briefer, briefing, 뉴스, news, tavily, groq, 시황, 분석

**Context Loaded**:
- API routes
- Analysis scripts
- Database structure
- Multi-layer analysis pipeline

### 5. Infrastructure
**Triggers**: deploy, 배포, railway, vercel, supabase, r2, cloudflare, production, 프로덕션

**Context Loaded**:
- Production stack overview
- Deployment rules
- Recent infrastructure changes

### 6. Database
**Triggers**: database, db, supabase, postgres, table, query, sql

**Context Loaded**:
- Database access patterns
- Key tables
- Connection methods
- Security warnings

## Bypass Options

Start your prompt with these prefixes to skip enhancement:

- `*` - Skip enhancement (pass-through)
- `/` - Slash commands (automatic bypass)
- `#` - Memorization commands (automatic bypass)

## Examples

### Example 1: DWM Development
```
You: DWM에 새 음악 스타일 추가해줘

Hook automatically loads:
- DWM API routes
- Python scripts
- Database schema
- Recent changes

Claude receives your prompt + context
```

### Example 2: YouTube Feature
```
You: YouTube 비디오 자막 기능 개선

Hook automatically loads:
- YouTube Hub routes
- Subtitle processing tech
- Database structure

Claude receives your prompt + context
```

### Example 3: General Question
```
You: 프로젝트 구조 설명해줘

Hook loads:
- General project info
- All 4 services overview
- Dev server URL

Claude receives your prompt + context
```

## Configuration

**Settings File**: `~/.claude/settings.json`

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python C:\\Users\\Jayone/.claude/hooks/improve-prompt.py"
          }
        ]
      }
    ]
  }
}
```

## Testing

Test the hook manually:
```bash
echo '{"prompt": "DWM 개선", "session_id": "test"}' | python ~/.claude/hooks/improve-prompt.py
```

## Troubleshooting

### Hook not working?
1. Check if Python is in PATH: `python --version`
2. Verify settings.json has the hook configured
3. Check hook script permissions
4. Restart Claude Code

### Encoding errors?
The script uses UTF-8 encoding via `sys.stdout.buffer.write()` to handle Korean characters properly on Windows.

### Want to disable temporarily?
Add `*` prefix to your prompt:
```
*DWM 개선해줘  # Hook skipped
```

## Customization

Edit `~/.claude/hooks/improve-prompt.py` to:
- Add new service patterns
- Modify context templates
- Add custom detection logic

After editing, restart Claude Code for changes to take effect.

## File Structure

```
~/.claude/
├── hooks/
│   ├── improve-prompt.py   # Main hook script
│   └── README.md            # This file
└── settings.json            # Hook configuration
```

## Notes

- **No external LLM calls**: Uses Claude Code's internal Claude
- **No extra cost**: Just adds context to your prompts
- **Automatic**: Works on every prompt submission
- **Smart detection**: Multiple patterns per service
- **Windows compatible**: Proper UTF-8 encoding handling

## Version

- **Created**: 2025-12-09
- **Python**: 3.11.9
- **Claude Code**: 2.0+

---

**Enjoy enhanced prompts! 🚀**
