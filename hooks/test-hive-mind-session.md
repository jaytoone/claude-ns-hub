# Hive Mind Phase 2.0 세션 테스트 가이드

## 🎯 테스트 목적
새 Claude Code 세션에서 Hive Mind Phase 2.0이 정상 작동하는지 확인

## 📋 테스트 체크리스트

### ✅ 사전 확인
- [ ] jq 설치 확인: `which jq`
- [ ] orchestrator 실행 가능: `ls -l ~/.claude/hooks/hive-mind-orchestrator.sh`
- [ ] 설정 확인: `cat ~/.claude/hooks/hive-mind-config.json | jq .enabled`

---

## 🧪 테스트 프롬프트

### Test 1: LOW 복잡도 (워커 1개)

**입력 프롬프트**:
```
파일 목록 보여줘
```

**기대 동작**:
1. System Prompt v7.1 주입
2. Hive Mind Mode: ACTIVATED 표시
3. 복잡도: LOW
4. 워커 수: 1 (자동 생성 완료)
5. Queen Agent 지시사항 출력

**확인 명령어**:
```bash
# 로그 확인
tail -20 ~/.claude-flow/logs/hive-mind.log | grep -E "Spawning|complexity|Workers"

# 워커 상태 확인
npx claude-flow@latest hive-mind status
```

---

### Test 2: MEDIUM 복잡도 (워커 2개)

**입력 프롬프트**:
```
이 함수의 성능을 개선하고 에러 핸들링을 추가하며 단위 테스트를 작성하고 코드 리뷰를 진행하고 문서를 업데이트하고 커밋 메시지를 작성하고 변경 사항을 검증하고 로그를 추가하고 타입 안정성을 보장하고 코드 스타일을 통일해주세요
```

**기대 동작**:
1. Hive Mind Mode: ACTIVATED
2. 복잡도: MEDIUM (35단어)
3. 워커 수: 2 (자동 생성 완료)

**확인 명령어**:
```bash
tail -5 ~/.claude-flow/logs/hive-mind.log | grep "Spawning"
```

---

### Test 3: HIGH 복잡도 - 키워드 방식 (워커 3개)

**입력 프롬프트**:
```
전체 프로젝트 아키텍처를 대규모 리팩토링하고 통합 테스트 실행해줘
```

**기대 동작**:
1. Hive Mind Mode: ACTIVATED
2. 복잡도: HIGH (키워드: "아키텍처", "리팩토링")
3. 워커 수: 3 (자동 생성 완료)

**확인 명령어**:
```bash
tail -5 ~/.claude-flow/logs/hive-mind.log | grep "Spawning"
```

---

### Test 4: HIGH 복잡도 - 단어 수 방식 (워커 3개)

**입력 프롬프트**:
```
이 코드의 모든 함수에 대해 상세한 문서를 작성하고 각 함수의 입력과 출력을 명확히 정의하며 에지 케이스를 고려한 단위 테스트를 작성하고 통합 테스트도 추가하며 성능 벤치마크를 수행하고 메모리 사용량을 프로파일링하며 보안 취약점을 검토하고 코드 리뷰를 진행하며 CI/CD 파이프라인을 구성하고 배포 전략을 수립하며 모니터링 시스템을 설정하고 알림 규칙을 정의하며 장애 복구 계획을 작성하고 사용자 문서를 업데이트하며 API 문서를 자동 생성하고 변경 로그를 작성하며 릴리스 노트를 준비하고 마이그레이션 가이드를 제공하며 이전 버전과의 호환성을 보장하고 최종 검증을 수행해주세요
```

**기대 동작**:
1. Hive Mind Mode: ACTIVATED
2. 복잡도: HIGH (120+ 단어)
3. 워커 수: 3 (자동 생성 완료)

---

## 📊 결과 검증

### 방법 1: 로그 파일 확인
```bash
# 최근 실행 기록
tail -50 ~/.claude-flow/logs/hive-mind.log
```

**기대 출력**:
```
[INFO] Detected complexity: LOW (word count: 3)
[INFO] Spawning 1 workers...
[INFO] Workers spawned successfully (1)
```

### 방법 2: 워커 상태 확인
```bash
npx claude-flow@latest hive-mind status
```

**기대 출력**:
```
Worker Agents
+----------------------+--------+--------+--------------+-----------+
| ID                   | Type   | Status | Current Task | Completed |
+----------------------+--------+--------+--------------+-----------+
| hive-worker-...      | worker | idle   | -            |         0 |
```

### 방법 3: 실시간 모니터링
```bash
# 터미널 1: 로그 실시간 감시
tail -f ~/.claude-flow/logs/hive-mind.log

# 터미널 2: Claude Code 세션에서 테스트 프롬프트 입력
```

---

## ✅ 성공 기준

- [ ] LOW 복잡도 → 워커 1개 생성
- [ ] MEDIUM 복잡도 → 워커 2개 생성
- [ ] HIGH 복잡도 (키워드) → 워커 3개 생성
- [ ] HIGH 복잡도 (단어수) → 워커 3개 생성
- [ ] 로그에 "Phase 2.0: Auto-initialization complete" 표시
- [ ] Queen Agent 지시사항이 응답에 포함됨

---

## 🐛 문제 해결

### 문제 1: Hive Mind가 활성화되지 않음

**확인**:
```bash
cat ~/.claude/hooks/hive-mind-config.json | jq '{enabled, minComplexity}'
```

**기대값**:
```json
{
  "enabled": true,
  "minComplexity": "LOW"
}
```

### 문제 2: 워커 수가 다름

**확인**:
```bash
cat ~/.claude/hooks/hive-mind-config.json | jq .workerCountByComplexity
```

**기대값**:
```json
{
  "LOW": 1,
  "MEDIUM": 2,
  "HIGH": 3
}
```

### 문제 3: jq 오류

**확인**:
```bash
which jq
```

**해결**:
```bash
sudo apt-get install jq  # Ubuntu/Debian
brew install jq          # macOS
```

---

## 📝 테스트 로그 템플릿

### Test 1 결과
- 복잡도: [ ]
- 워커 수: [ ]
- 시간: ___초
- 상태: ✅ / ❌

### Test 2 결과
- 복잡도: [ ]
- 워커 수: [ ]
- 시간: ___초
- 상태: ✅ / ❌

### Test 3 결과
- 복잡도: [ ]
- 워커 수: [ ]
- 시간: ___초
- 상태: ✅ / ❌

### Test 4 결과
- 복잡도: [ ]
- 워커 수: [ ]
- 시간: ___초
- 상태: ✅ / ❌

---

## 🎉 테스트 완료 후

모든 테스트 통과 시:
```bash
echo "✅ Hive Mind Phase 2.0 프로덕션 레디!"
```

## 📚 추가 문서
- Architecture: ~/.claude-flow/docs/HIVE_MIND_PHASE_2.0_RELEASE_NOTES.md
- Config: ~/.claude/hooks/hive-mind-config.json
- Orchestrator: ~/.claude/hooks/hive-mind-orchestrator.sh
