# Memory MCP - 세션 시작 컨텍스트 복원 요청
_생성 시각: 2026-04-10 14:52:10_
_프로젝트: /home/jayone/Project/TTPS_

## [자동 지시] SessionStart 컨텍스트 복원

이 파일이 존재하는 경우, 세션 시작 시 다음을 실행하십시오:

1. `mcp__memory__read_graph` 도구를 호출하여 전체 Knowledge Graph를 읽습니다.
2. 반환된 entities / relations 중 현재 프로젝트와 관련된 항목을 요약합니다.
3. 요약 내용을 컨텍스트에 주입합니다 (사용자에게 간략히 보고).
4. 이 힌트 파일을 삭제합니다: `rm /home/jayone/.claude/memory-context-hint.md`

### 복원 명령 (Claude가 실행할 내용)
```
mcp__memory__read_graph({})
```

### 결과 처리 지침
- entities: 프로젝트명, 기술 결정, 미해결 문제 위주로 요약
- relations: 인과관계 / 의존관계 중심으로 파악
- 현재 프로젝트 경로(/home/jayone/Project/TTPS)와 관련된 항목 우선 제시

### Memory 파일 경로 (프로젝트 격리)
- 프로젝트: TTPS
- Memory 파일: /home/jayone/.claude/memory-graphs/TTPS/memory.jsonl

### Conceptual Paradigm State (auto-loaded, apply silently)
```json
{
  "epistemic_basis": "intuition-first",
  "locus_of_control": "internal",
  "causal_model": "linear",
  "recurring_tensions": [
    {"tension": "AI agent as tool vs AI agent as proxy — credential gap substitution", "count": 1},
    {"tension": "discovery_vs_conversion bottleneck", "count": 1}
  ],
  "concept_gaps": [
    "meta_gap: AI agent capability assumed from reasoning not direct experience",
    "ToS compliance for AI-assisted vs AI-proxy work on Alignerr",
    "Hubstaff activity monitoring creates detection risk for non-human work patterns"
  ],
  "paradigm_edges": [
    "2026-04-09: baseline session — linear model (AI tool → gap solved) challenged by systems lens (ToS loop, Hubstaff monitoring, screening bottleneck)"
  ],
  "last_updated": "2026-04-09T00:00:00Z",
  "session_count": 1
}
```
