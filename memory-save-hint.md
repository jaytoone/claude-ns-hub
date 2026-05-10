# Memory MCP - 세션 종료 저장 요청
_생성 시각: 2026-04-10 14:52:25_
_프로젝트: /home/jayone/Project/TTPS_
_브랜치: master_

## [자동 지시] SessionEnd/PreCompact 핵심 내용 저장

이 파일이 존재하는 경우, 세션 종료 전 다음을 실행하십시오:

1. 현재 세션에서 다룬 **중요 기술 결정**, **미해결 문제**, **재사용 가능한 패턴**을 식별합니다.
2. `mcp__memory__create_entities` 도구로 entities를 저장합니다.
3. `mcp__memory__create_relations` 도구로 entities 간 관계를 저장합니다.
4. 이 힌트 파일을 삭제합니다: `rm /home/jayone/.claude/memory-save-hint.md`

### 저장 기준 (선택적 저장 원칙)
- ✅ 저장: 중요 기술 결정, 미해결 문제 (P0/P1), 재사용 가능한 패턴, 환경 함정
- ❌ 저장 안 함: 일회성 작업 계획, 완료된 작업 상세, trajectory

### Entity 템플릿 예시
```json
{
  "entities": [
    {
      "name": "프로젝트명-결정사항-2026-04-10",
      "entityType": "TechnicalDecision",
      "observations": ["결정 내용 요약", "근거", "영향 범위"]
    },
    {
      "name": "프로젝트명-미해결-2026-04-10",
      "entityType": "OpenIssue",
      "observations": ["문제 설명", "우선순위", "현재 상태"]
    }
  ]
}
```

### 현재 세션 메타데이터
- 프로젝트: /home/jayone/Project/TTPS
- 브랜치: master
- 시각: 2026-04-10 14:52:25
- Memory 파일: /home/jayone/.claude/memory-graphs/TTPS/memory.jsonl
