# Ontolo Project - Key Learnings

## 프로젝트 정보
- 경로: /home/jayone/Project/Ontolo
- 개발 서버: `npm run dev -- -p 3003 > /tmp/ontolo-dev3.log 2>&1 &`
- Supabase Admin Client: `@/lib/supabase/admin` → `createAdminClient()` (SERVICE_ROLE_KEY, RLS 우회)

## 핵심 패턴: FK 에러 해결 (created_by / user_id)
**증상**: `insert or update violates foreign key constraint "..._created_by_fkey"`
**해결**: insert 시 `created_by`, `user_id` 필드 제거 (NOT NULL이 아닌 경우)
**적용 파일**: conversations/route.ts, channels/virtual/route.ts, agents/create/route.ts

## 핵심 패턴: RLS 에러 해결
**증상**: `42501 - new row violates row-level security policy`
**원인**: `createClient()` (ANON_KEY) 사용 → RLS 차단
**해결**: `createAdminClient()` (SERVICE_ROLE_KEY) 교체

## 핵심 패턴: React 스크롤 문제
**증상**: `scrollIntoView`가 앱 전체 스크롤 유발
**해결**: 컨테이너 ref 직접 사용 → `container.scrollTop = container.scrollHeight`

## 핵심 패턴: Job 취소 기능
**API**: `DELETE /api/jobs/{jobId}` → status='cancelled' 업데이트
**analyze 루프**: 각 영상 처리 전 SELECT status → 'cancelled'면 return 조기 종료
**UI 폴링**: job.status === 'cancelled' → clearInterval + setAnalyzingJobId(null)
**취소 버튼**: 진행 중 UI에 onClick → DELETE → setAnalyzingJobId(null)

## 핵심 패턴: Gemini API Vertex AI 전용 (Studio fallback 비활성화)
**구조**: `lib/utils/gemini-client.ts` 공통 유틸리티
- `createGeminiModel()` - 비스트리밍용 (개념 추출, 분류 등)
- `createGeminiStreamClients()` - 스트리밍용 (Agent Chat)
- `GOOGLE_CLOUD_PROJECT_ID` 없으면 throw Error (Studio fallback 제거됨)
- 기본 모델: `GEMINI_MODEL=gemini-2.5-flash`

## 핵심 패턴: generate-document 백그라운드 Job
**API 동작**: POST → 즉시 `{success:true, jobId}` 반환, 실제 처리는 백그라운드
**UI 폴링**: `GET /api/jobs/{jobId}` 3초마다 → completed 시 `job.results.documentId` 취득
**문서 조회**: `GET /api/video-document?documentId={id}` → `document_json` 반환
**jobs/[id]**: `results` 필드 추가 + `DELETE` 엔드포인트 (취소용)

## 핵심 패턴: Agent 생성 (복수 문서 병합)
**API**: `POST /api/agents/create` - `ontologyDocIds: string[]` 복수 지원
**병합**: `concepts`, `relationships`, `rules` flatMap 후 단일 persona 변환
**DB**: `created_by` 필드 제거 (FK 에러 방지)
**문서 카드 UI**: `video-document` API에 `channelTitle` 추가 (ontolo_channels join)

## 핵심 패턴: Stop Hook (v3.1) - Playwright 자동 검수
**파일**: `~/.claude/hooks/stop-playwright-validation.sh`
**플래그 키**: `{GIT_HASH}-d{DIFF_HASH}` (diff 내용 md5 기반)
- 새 커밋 → 새 hash → 재검수
- uncommitted 변경 → `git diff HEAD | md5sum` → 내용 바뀌면 재검수
- 같은 파일 반복 수정도 감지 (파일 수 기반 아님)
- 플래그 삭제 안 함 → 같은 상태면 영구 approve
- 서버 없으면 package.json dev 스크립트로 자동 시작

## 수정된 주요 파일
- `app/api/agents/create/route.ts` - 복수 문서 병합, created_by 제거
- `app/api/agents/[agentId]/stream/route.ts` - Vertex AI 전용, gemini-2.5-pro
- `app/api/agents/[agentId]/route.ts` - DELETE 핸들러 추가 (Agent 삭제)
- `app/api/analyze/route.ts` - 루프 내 cancelled 상태 체크
- `app/api/jobs/[id]/route.ts` - DELETE(취소) + results 필드
- `app/api/video-document/route.ts` - channelTitle join 추가
- `app/api/search-query-chat/route.ts` - Vertex AI 전용 SSE
- `lib/utils/gemini-client.ts` - Vertex AI 전용 유틸 (Studio fallback 제거)
- `components/ontolo/AgentPanel.tsx` - 복수 문서 선택 UI, Agent 삭제 버튼, MD MIME fallback
- `components/ontolo/AgentChatPanel.tsx` - MD 파일 업로드 MIME fallback (확장자 기반)
- `app/page.tsx` - Job 취소 버튼, 폴링 cancelled 처리
