# CTX 프로젝트 메모리 (2026-04-02 업데이트)

## 2026-04-27 Dashboard 5-change multilens spec impl (/live iter 48)
- **결정**: `20260427-dashboard-ui-multilens-eval.md` 5-change spec 전체 구현: (1) `/api/retrieval-method-stats` endpoint + System Health 위젯, (2) utility rate reframe (Mixed 50% first, "vs 0% baseline"), (3) samples feed method dots, (4) alert banner retrieval_method annotation, (5) INJECTED→PROVIDED rename. Rollback: commit `a70a0d6`.
- **이유**: 23% utility rate가 첫인상에서 실패처럼 보이고, semantic 구조 증거가 4-step drill-down 뒤에 숨어있음. proof-of-value narrative를 banner→health→utility→graph 순서로 가시화.

## 2026-04-27 Dashboard semantic appeal implementation started (/live)
- **결정**: `20260427-dashboard-semantic-appeal-spec.md` 스펙 기반으로 CTX 대시보드 3가지 개선 구현. (1) `_explain_node()`에 `retrieval_method` 필드 추가 (KEYWORD/SEMANTIC/CASCADE 판별), (2) NL summary 업그레이드 — 시맨틱 구조 설명 포함, (3) 기여자 리스트 카드에 메소드 배지 + 시맨틱 브릿지 설명 UI. citation 인디케이터는 2차 구현 예정.
- **이유**: BM25가 0 점수인데 depth-1인 노드 = e5-small이 구조한 시맨틱 매칭. 이를 대시보드에서 시각적으로 보여줌으로써 "키워드 없이도 의미로 찾는다"는 CTX의 핵심 차별점을 증명.

## 2026-04-24 bge-daemon 구축 + 효용성 검증 완료
- **결정**: BGE cross-encoder를 `~/.local/share/claude-vault/bge-daemon.py` 에 Unix socket daemon으로 영속화. bm25-memory.py의 in-process 로드(7s cold)를 socket client로 교체 → 매 UserPromptSubmit마다 7s 로드 지불하던 구조 해결.
- **구성**: BAAI/bge-reranker-v2-m3, cuda fp16, VRAM ~4GB / 8GB. Socket protocol `{query, docs[]}` → `{scores[]}`. 2초 timeout, 실패 시 bi-encoder(vec-daemon) 자동 fallback. `CTX_CROSS_ENCODER=1` 기본 ON으로 복구.
- **효용성 검증 (172 commits corpus, 실측)**:
  - Broad 쿼리 ("bm25 threshold", "eval benchmark"): BGE가 의미상 더 적합한 커밋을 상위로 재정렬. 예: "bm25 threshold" → BGE는 구현 커밋(bm25-memory hook)을 #3으로 올림, 미사용 시 paper-edit 커밋에 밀려 #4로 demote.
  - Narrow 쿼리 (BM25가 이미 명확히 top-k 확정): 재정렬 없음. 품질 차이 無, latency만 +90ms.
  - Hard 쿼리 (BM25 zero-match, 가령 "windows notification popup"): rerank는 candidate 없이 발동 불가 → BGE 효용 無. 이는 L3 한계(candidate generation은 dense가 필요).
- **Latency**: daemon 추가 오버헤드 ~90ms/쿼리 (socket 왕복 + inference). 총 hook 경로 latency 평균 100-180ms로 유지 — UX budget 안.
- **다음 단계**: (1) systemd user service로 daemon 자동 기동화(재부팅 후 복구) (2) 장기 — BM25 candidate가 희박한 쿼리용으로 dense candidate generation을 vec-daemon 기반으로 추가 (지금은 rerank-only). — 2026-04-24

## 2026-04-24 Task Scheduler 최종: Interactive + AtLogOn + 1min repeat (S4U는 실패)
- **결정**: `-LogonType Interactive` 유지 (S4U 시도는 실패). 트리거 2개: `AtLogOn` + 1-min `Repetition`. `-MultipleInstances IgnoreNew`.
- **S4U 실패 이유**: S4U는 Session 0 (service session)에서 실행 → 데스크톱 접근 권한 없음 → WinForms 팝업 렌더링 불가 (Windows Session 0 isolation). Listener는 살아있으나 `Show-Square` 스폰한 PowerShell이 화면에 표시 안 됨.
- **최종 해법**: Interactive로 팝업 UI 유지 + 1-min repeat trigger로 mid-session 사망 시 60초 내 자동 복구. 재부팅 후엔 사용자 logon 시 AtLogOn 발화. — 2026-04-24

## 2026-04-24 Dashboard 방법론 변경: 단일-노드 pane → 기여도 순위 리스트
- **결정**: node-details pane이 "클릭한 한 노드만 설명"하던 구조 → "프롬프트에 기여한 모든 노드를 기여도 순위로 나열하고 각 노드 클릭 시 그래프에 하이라이트 + 상세 메모리/정보 설명" 구조로 변경.
- **이유**: 사용자 관찰 — 현재 방법론은 노드 클릭 전까지 어느 노드가 프롬프트에 얼마나 기여했는지 비교 불가. 새 방법론은 리스트로 한눈에 우선순위를 보여주고 개별 노드 클릭 시 그래프-리스트 연동 + 상세 메모리 내용 확인 가능.
- **구성요소**: (1) 서버 `/api/prompt-contributors` 엔드포인트 — 프롬프트에 기여한 모든 노드 BM25/blended 점수 순으로 반환 (injection_preview, referenced_in_response, per-token contribution 포함) (2) 프론트 리스트 뷰 — 순위·점수 바·injection preview·referenced chip (3) 클릭 → 그래프 노드 focus+pulse (4) expandable 상세 섹션. — 2026-04-24

## 2026-04-24 BM25 노이즈 감소 2단계 (option 3 선택)
- **결정**: 사용자가 "BM25 결과에 무관한 노이즈 많음" 비판 수용 → Option 3 (단기 + 구조적 동시 실행). Iter 1 = min-score threshold + diversity/MMR filter (bm25-memory.py, ~15분). Iter 2 = semantic rerank via existing vec-daemon for G1/G2 (~45분).
- **이유**: 사용자 관찰 검증 — "token" 프롬프트에 4 hits 중 3개가 서로 다른 의미의 "token%" 페이퍼 편집 커밋 (surface-token match without semantic match). 20260417-ctx-semantic-search-upgrade-sota.md 로드맵의 T1 항목.
- **제약**: 현재 vault.db chat-memory만 hybrid (cosine+BM25), G1/G2는 pure BM25. vec-daemon 이미 가동 중이므로 재사용. — 2026-04-24

## 2026-04-24 Dashboard node-details pane 개선 scope 확정 (option C)
- **결정**: 사용자가 "why this node is related to the prompt" 증명을 위해 option C(full plan) 선택 — symmetric match highlighting + per-token BM25 contribution breakdown + one-line summary + rank-2 comparison + top-tokens-missed analysis (≈90분 작업).
- **준비 단계**: option C 구현 전에 직전 commit (91840cf: 4개 research docs) 롤백 검토 중. 롤백 시 새 변경사항을 합친 single commit으로 재작성 가능 — 2026-04-24

## 2026-04-24 claude-client-bootstrap 통합: 3-spec one-line 온보딩 완성
- **결정**: 서비스 이름 `ctx-setup-server` → `claude-client-bootstrap` (CTX 프로젝트와 무관함 명시). 단일 `irm http://100.66.30.40:9955/bootstrap | iex`가 Spec 1(popup) + Spec 2(clipboard) + Spec 3(browser tunnel) 모두 설정.
- **Spec 3 구현**: hardcoded port list 폐기 → 동적 same-URL mirror. 리스너 `/expose`, `/unexpose`, `/exposed` endpoint 추가. `netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=N connectaddress=100.66.30.40 connectport=N` 동적 실행. Task Scheduler `-RunLevel Highest`로 netsh portproxy 권한 확보.
- **CLI**: `~/.local/bin/wsl-expose <port>` + `wsl-unexpose <port>` (tailscale peer enum → /expose POST fanout).
- **Clipboard transport fix**: `clip-to-remote.sh`가 이전 `localhost:6789-6799` 브로드캐스트에서 tailnet peer direct POST로 전환.
- **검증**: jej98에서 `/expose 3003` → `netsh portproxy`에 `127.0.0.1:3003 → 100.66.30.40:3003` 생성 확인, `/unexpose`로 제거 확인.
- **제약**: Task `-RunLevel Highest` 등록은 로컬 admin 필요 (SSH 비-admin 세션에서는 실패) — toomu는 로컬 재실행 필요.

## 2026-04-24 클라이언트 아키텍처 전환: SSH RemoteForward → Tailscale direct POST
- **결정**: 모든 Windows 클라이언트가 **공통 포트 6789** 사용. SSH tunnel 제거. (docs/research/20260424-common-port-fanout-tailscale-vs-ssh.md)
- **이유**: SSH RemoteForward는 같은 포트 multi-client bind 불가 (Address already in use). 각 Tailscale peer는 자기 IP namespace이므로 6789 공유 가능.
- **변경**: 
  - `client-setup-ps5.ps1`: listener 바인딩 `127.0.0.1:6789` → `0.0.0.0:6789` via `http://+:6789/`. URL ACL + Windows Firewall inbound rule 추가. SSH RemoteForward 블록 완전 제거.
  - WSL2 hooks (`windows-notify.sh`, `windows-stop.sh`, `close-popup.sh`, `windows-notify.sh`): `for port in 6789-6799 {localhost POST}` → `tailscale status --json | jq .Peer[] | while POST to tailscale-ip:6789`.
  - `ctx-setup-server.py`: `/next-port` + `client-ports.json` 레지스트리 제거. `/bootstrap`만 남김.
  - 순서 주의: ACL+Firewall을 Task Scheduler 시작 **전에** 등록해야 함 (listener.Start() 실패 방지).
- **1-line onboarding (공통)**: `irm http://100.66.30.40:9955/bootstrap | iex` — 모든 새 클라이언트 동일 command, 포트 네고 불필요.
- **E2E 검증**: DESKTOP-TI1C5VI (100.64.80.3) `/health` + `/notify` ok via 100.66.30.40:curl. 팬아웃 probe로 전체 tailnet 상태 즉시 확인 가능.
- **마이그레이션 필요**: 기존 3 클라이언트 (DESKTOP-8HIUJU8, DESKTOP-693UEOU=toomu, DESKTOP-BJOLBUL=jej98) 각각 bootstrap 1회 재실행으로 0.0.0.0 바인딩 전환.

## 2026-04-23 클라이언트 온보딩 North Star (/live option B 선택)
- **결정**: `/live -i` 대신 `/live` (bounded) 선택, north-star 3-spec 확정
- **Spec 1 — 팝업**: WSL hook → POST localhost:6789/notify → SSH RemoteForward → client 발룬 (✅ 이미 구현: client-setup-ps5.ps1 + claude-notify-listener.ps1 v2)
- **Spec 2 — 클립보드**: zellij copy_command → ~/.local/bin/clip-to-remote.sh → POST :6789/clipboard → client Set-Clipboard (✅ 이미 구현)
- **Spec 3 — 브라우저 터널 (gap)**: 현재 CTX 대시보드만 `tailscale serve`로 노출. 사용자가 원하는 것: 서버 dev 서버 (예: localhost:3003)를 **동일 URL로** 클라이언트에서 접근. 해결책: SSH LocalForward 공통 dev 포트 pre-declare (3000/3003/5173/8000/8080/8787 등) + dynamic 추가 헬퍼 `wsl-expose <port>` 스크립트.
- **이유**: `tailscale serve`는 URL 경로 매핑 (path-based), LocalForward는 포트 매핑 (same-URL invariant 보존). spec 3의 "동일 URL (localhost:3003)" 요구 사항에 LocalForward가 정확히 fit.
- **다음**: `wsl-client-bootstrap.{ps1,sh}` 업데이트로 LocalForward 블록 포함 + `wsl-expose` CLI 추가

## CTX 포지셔닝 (2026-04-02 재정립)
**CTX = 코딩 에이전트의 context bootstrapper** (검색 엔진이 아님)
- Claude Code가 첫 턴 60%+ 시간을 agentic grep에 소비 → CTX가 <1ms 부트스트랩
- 유일한 cross-session memory (다른 도구 전부 세션 리셋)
- 경쟁이 아닌 보완: Cursor(임베딩), Aider(PageRank), Windsurf(SWE-Grep) 대비

## 현재 G1/G2 수치 (2026-04-26 iter 38 최종)

| Goal | 지표 | 수치 | 비고 |
|------|------|------|------|
| G1 | CTX 59-query Recall@7 | **0.983** | iter 34 hybrid BM25+dense RRF — 174-commit corpus |
| G1 | BM25-only baseline | 0.966 | hybrid 대비 +1.7pp |
| G1 | CTX 0-7d Recall@7 | **0.711** | 2026-04-11 측정 (hybrid 이전) |
| G1 | Flask Recall@7 | **0.667** | 과적합 없음 — 이종 도메인 검증 |
| G2-CODE | External R@5 mean | **0.602** | Flask 0.66, FastAPI 0.40, Requests 0.75 |
| G2-CODE | COIR R@5 | **1.000** | NL→Code 완벽 |
| G2-DOCS | Doc R@5 | **0.940** | 문서 검색 우수 (hybrid 이전 측정치) |
| G2-CODE | Node count (auto-reindex) | **3693** | iter 38 자동 reindex 후 (이전 2441) |

## 핵심 기술 결정
- BM25 > TF-IDF (소규모 코퍼스에서 IDF 역효과)
- .md 문서 인덱싱 추가 (iter 2에서 수정 — README/CLAUDE.md 검색 가능)
- High-level query detection + doc-priority boost
- PascalCase SYMBOL_PATTERN (8+ chars)
- Hybrid scoring (50% LLM judge + 50% keyword) for G1 eval

## 구조적 한계 (dead-ends)
- FastAPI external R@5=0.40 (50% 쿼리가 구조적으로 모호 — 개선 불가)
- Medium dataset concept strict R@5=0.495 (0/200 파일이 고유 concept — 이론적 상한)
- Dense embedding은 Code→Code에서 역효과 (Flask R@5 -0.106)
- MiniMax M2.5 judge가 {0, 5, 10}만 출력 → hybrid scoring으로 해결

## 범용화 연구 결론 (2026-04-09)
**오픈셋 0.250 = BM25 open-domain ceiling(≈0.22), keyword overfit이 주원인 아님**
- 개선 우선순위: (1) FACT-2 decision verbs 추가(add/use/remove/kill/introduce/check) (2) G2a 동적 경로 발견 (3) ablation 후 hybrid 판단
- Hybrid BM25+Dense: +15-30% 예상이나 <1ms 보장 파기 → two-stage 옵션 고려
- CTX 유일성 확인: Copilot/Cursor/Aider/Zed 모두 cross-session git memory 없음
- 연구 문서: `docs/research/20260409-bm25-memory-generalization-research.md`

## G1 개선 이력 (2026-04-11)
- iter 1: n=15→30 + BM25+deep grep: 0.169→0.431 (+155%)
- iter 2: _is_decision() 편향 제거 + Pass0 게이트 제거: 0.431→0.525 (+22%), Flask 0→0.667
- iter 3: compound/numeric 키워드 추출: 0.525→0.661 (+26%), 0-7d 0.422→0.622
- iter 4: synonym map + temporal timeline + G2a importers: 0.661→0.746 (+13%)
- 실제 상한선: ~0.75-0.80 (7/15 잔여 miss = live-inf iter 구조적 노이즈 필터)

## 새 hook 기능 (iter 4)
- _SYNONYM_MAP: COIR/BM25/SOTA/G1/G2/eval → commit 검색 가능 동의어
- [DECISION TIMELINE]: "진행/역사/timeline" 쿼리 감지 → 날짜 prefix + 시간순 출력
- G2a importers: G2가 찾은 Python 파일 → 역방향 import 의존성 1-hop 확장

## eval안정화 (2026-04-14 iter 1 완료)
- g1_fair_eval.py 캐시 구현 완료 — corpus_hash=55ca40380ff70ea3
- 3회 연속 Recall@7 = 0.678 고정 (분산 0pp, 목표 <2pp 달성)
- verb synonym rollback → 재결정: Flask cross-domain 1.000 확인 후 유지
- cache file은 .gitignore로 미커밋 — fresh install 시 LLM 1회 재생성 필요

## 다음 세션 후보
- G1 7/15 rank-out 분석: DECISION_CAP 증가 or pass2 dedup 개선
- G2a 동향 데이터 수집 + ablation
- memory-keyword-trigger.py → settings.json 등록 (현재 미작동)

## 2026-04-17 live-inf 세션 최종 요약 (11 iterations shipped)

### 발견: CM + G1 semantic layer가 6일간 silent 장애 상태
- vec-daemon 2026-04-11부터 사망 → socket stale
- SessionStart hook이 `test -S $sock`으로만 체크 → stale socket 감지 못 함 → daemon 재시작 안 됨
- CM은 hybrid BM25+vector (vault.db+vec0+multilingual-e5-small, 20260410 bench P@5 0.76→0.88) 인프라 이미 존재, 단지 daemon 죽어서 BM25-only fallback
- G1도 같은 daemon 공유 → semantic rerank 비활성

### iter 1-2: 복구 + 관측성
- daemon 재시작, settings.json의 SessionStart hook을 실제 socket 연결 probe로 업그레이드 (python3 -c "...s.connect(...)")
- CM hook: `chat memory/bm25 ⚠ vec-daemon down` 경고 태그 추가
- G1 hook: `[RECENT DECISIONS (BM25 ⚠ vec-daemon down — semantic rerank disabled)]` 경고 헤더

### iter 3-6: G2 goldset + T1-A/C ship
- 8-query → 12-query G2 gold-truth bench: `benchmarks/eval/g2_goldset.json` + scorer
- 이전 세션 "T1-A dead-end" 결론은 3연속 tokenizer 버그로 인한 오판 (폐기)
- v3 tokenizer (CamelCase + snake_case split, `bm25` 단일 토큰 유지)로 T1-A ship
- 12-query bench: OLD Hit@5=0.50 MRR=0.37 → ROUTER Hit@5=0.58 MRR=0.49 (T1-C 포함)
- T1-C: >=5 keywords → length-ASC, else BM25 — q5 (Korean ko_en 확장) 퇴행 방지

### iter 7-10: latency + staleness
- latency 측정: OLD=1.41ms, BM25=3.16ms (cold 57ms rank_bm25 import), ROUTER=1.50ms. "10× latency" 원래 주장은 cold-start noise였음
- codebase-memory-mcp DB 254시간(10.6일) stale 발견 → 수동 reindex → G2 MRR +15%
- auto-index.py는 hint만 출력하고 실제 실행 안 함 → Claude가 hint 무시하면 silent staleness
- auto-index.py tiered warning: 24h silent / 3-7d ⚠ / 7d+ ⚠⚠ CRITICAL

### iter 11: T1-B NEGATIVE
- git log co-occurrence synonym mining (SOTA 로드맵의 마지막 T1 항목)
- 226 commits에서 top pairs가 live-inf 템플릿 boilerplate (iter↔live, goal↔success)
- 진짜 semantic synonym은 불출 → 미배포. Topic-stratified/MI scoring 필요

### 현재 hook 상태 (모든 surface)
- CM: **hybrid 작동 중** (vec-daemon 복구됨)
- G1: **BM25+semantic rerank 작동 중** (vec-daemon 복구됨)
- G2 symbol search: **BM25 v3 tokenizer + T1-C router ship됨**, Hit@5 0.50→0.58 (+16%)
- 모든 silent failure가 이제 visible warning

### 교훈 (다음 세션용)
1. harness tokenizer bug가 원칙적 실패로 보일 수 있음 — candidate tokens 먼저 inspect
2. 외부 daemon 의존성은 실제 연결 probe로 health check (file existence 불충분)
3. Index staleness가 retrieval algorithm보다 영향 큼 — freshness가 accuracy보다 중요
4. 관측 가능한 degradation이 silent degradation보다 안전 (visible warning pattern)
5. auto-index.py의 "hint" 모델은 불안정 — 실제 실행하는 구조로 리팩터 필요

### 남은 과제 (2026-04-17 기준, 일부 완료됨)
- ~~auto-index.py를 hint → 실제 execute로 리팩터~~ → **iter 38에서 완료** (`check_and_trigger_reindex()`)
- Cross-project goldset (Flask/FastAPI external)
- T1-B 제대로 구현 (MI scoring + topic stratification)
- CM hybrid 현재 성능 재측정 (20260410 bench 갱신)

## 2026-04-24 popup/CM 인프라 버그픽스 (3건)
- **CM global scope**: `settings.json` chat-memory hook에 `CHAT_MEMORY_SCOPE=global` 추가 → 모든 프로젝트 vault.db 검색 (이전: project-scoped only)
- **close-popup.sh 완전 수정**: (1) 포트 6789 단일 → 6789-6799 broadcast, (2) `[ -d "$LOCK_DIR" ] || exit 0` early-exit 제거 — REMOTE_NOTIFY_ONLY=1 환경에서 LOCK_DIR 없으면 remote broadcast 전혀 안 됐음 (stop 팝업이 다음 프롬프트에서 닫히지 않던 실제 원인)
- **windows-stop.sh**: curl timeout 1s → 5s (notify와 동일하게)
- **client-setup-ps5.ps1**: 내장 listener를 toomu Show-Square 버전으로 교체 + step 3을 Start-Process → Start-ScheduledTask로 변경 (SSH 세션 종료 후 생존)

## 2026-04-24 jej98 (DESKTOP-BJOLBUL) 클라이언트 온보딩 완료 ✅ ALL 3 SPECS
- **Spec 1 팝업 ✅**: 포트 충돌 해결 (toomu=6789 legacy, jej98=6790 신규). curl timeout 1s→5s 수정. Task Scheduler(ClaudeNotifyListener) 로 process 소유 — SSH 세션 종료 후에도 생존.
- **Spec 1 square popup**: toomu의 `claude-notify-listener.ps1` (Show-Square WinForms)를 jej98에 배포. 100.69.161.128=WSL2 host Windows, toomu/jej98 모두 remote client. square popup은 listener에 내장됨 (balloon이 아님).
- **Spec 2 클립보드 ✅**: root cause = `$res.Close()` 예외 시 clip.exe 미실행. fix: 응답 write를 inner try/catch로 감쌈. curl timeout 1s→3s. clip.exe BaseStream UTF-16 LE 방식.
- **Spec 2 zellij**: `copy_command` 현재 주석처리 (user가 일반 터미널처럼 사용 원함). 재활성화: `~/.config/zellij/config.kdl` line 378 주석 해제.
- **Spec 3 브라우저 터널**: SSH config LocalForward 10개 포트 pre-declared. `wsl-expose` CLI 추가.
- **인프라 키**: listener는 반드시 `Start-ScheduledTask -TaskName ClaudeNotifyListener`로 시작 (SSH Start-Process는 세션 종료 시 죽음). URL ACL `netsh http add urlacl url=http://127.0.0.1:6789/ user=jej98` 등록됨.

## 2026-04-26 live-inf iters 39-45 완료 — G2-DOCS 정량 벤치마크 + 한국어 fix

### 최종 G2-DOCS 결과 (20-query goldset, corpus drift excluded)
| Method | H@3 | H@5 | MRR |
|--------|-----|-----|-----|
| BM25 | 0.800 | 0.800 | 0.717 |
| Hybrid | 0.750 | **1.000** | 0.688 |

- 4 query types: heading_exact / heading_paraphrase / keyword / **korean_crosslingual** (모두 Hybrid H@5=1.000)
- `benchmarks/eval/g2_docs_goldset.json` (20q) + `benchmarks/eval/g2_docs_eval.py`

### iter별 주요 결정 (39-45)
- **iter 40-41** (Citation probe): `log_retrieved_nodes()` in bm25-memory.py → `.omc/retrieval_log.jsonl`. `citation_probe.py` cross-ref with vault.db. **7.6% citation rate → recall is binding, FP reduction low priority**. `.gitignore` 업데이트.
- **iter 42** (G2-DOCS goldset): 15-query goldset (English). Hybrid H@5=1.000 첫 측정.
- **iter 43** (Benchmark synthesis): 모든 surface paper-ready 정리. Paper §5.1 coverage map.
- **iter 44** (Korean fix): `_KO_EN_DOCS` + `_expand_ko_en_docs()` → Korean H@3 0.200→0.800 (+60pp). bm25_search_docs() + hybrid_search_docs() 모두 적용.
- **iter 45** (Corpus drift fix): `--exclude-docs` / `--corpus-cutoff` 추가 to g2_docs_eval.py. Definitive H@5=1.000 all 20 queries.

### 핵심 발견
- **Corpus drift**: synthesis/goldset-eval meta-docs 추가 시 source docs 보다 높은 rank 차지 → eval 시 exclude 필요
- **Dense embedding 패턴 (전 surface 공통)**: BM25 precision ≥ Hybrid precision at H@3; Hybrid recall >> BM25 recall at H@5. Dense embedding은 paraphrase/semantic query에서 recall 개선, keyword/exact는 BM25 충분.
- **Citation probe**: 수동 분석 필요 (5+ sessions 축적 후 `citation_probe.py --summary-only` 실행)

### 남은 과제 (2026-04-26 이후)
- Citation probe 데이터 축적 (자동 — 아무것도 안 해도 됨)
- G2-DOCS goldset 확장 (30q) — Korean 5개 추가 완료, paraphrase 5개 더 추가 가능
- CM hybrid 성능 재측정 (마지막 측정: 2026-04-10, P@5=0.88)

## 2026-04-26 live-inf iters 34-38 완료 — CTX 전면 hybrid retrieval 업그레이드

### 전체 결과 요약
| Surface | Before | After | 지표 |
|---|---|---|---|
| CM (chat memory) | hybrid (BM25+vec cosine α=0.5) | 변동없음 | 기존 P@5 0.88 유지 |
| G1 (decisions) | BM25+BGE rerank | **BM25+dense RRF+BGE** | Recall@7 0.966→**0.983** (+1.7pp) |
| G2-DOCS (docs) | BM25+BGE rerank | **BM25+dense RRF+BGE** | 질적 개선 (vocab mismatch 복구) |
| G2-CODE (codebase) | BM25 keyword, 수동 reindex | BM25 + **자동 staleness 감지+reindex** | node count 2441→3693 (+51%) |

### iter별 주요 결정
- **iter 34** (G1 hybrid): `embed_corpus_items()` + `dense_rank_decisions()` + `rrf_merge()` + `hybrid_rank_decisions()`. RRF k=60. 172→174 commits corpus. 0.983 Recall@7.
- **iter 35-36** (MAB/벤치마크 연구 + G2-DOCS hybrid): `hybrid_search_docs()` — 86 docs pre-embed cache (`.omc/docs_corpus_emb.json`). vec-daemon down → BM25 fallback 자동.
- **iter 37** (G2-CODE gap + FP 분석): G2-CODE hybrid 불필요 (keyword-exact가 코드 검색에 정확). BGE reranker가 homograph FP를 demote 안 함 (avg rank 3.3 vs 3.5 — insignificant). Citation probe가 FP 실제 영향 측정의 올바른 다음 단계.
- **iter 38** (G2-CODE staleness auto-fix): `check_and_trigger_reindex()` — DB >24h stale 감지 시 `codebase-memory-mcp cli index_repository --mode fast` 백그라운드 spawn. lock file 중복 방지. tool discovery: MCP stdio `tools/list` 프로토콜. ✅ **남은 과제 "auto-index hint→execute" 완료**.

### 현재 hook 상태 (2026-04-26 기준)
- CM: hybrid BM25+vec (vec-daemon 필수, fallback=BM25-only)
- G1: **hybrid BM25+dense RRF+BGE rerank** (Recall@7=0.983 on 174-commit corpus)
- G2-DOCS: **hybrid BM25+dense RRF+BGE rerank** (86 docs, cache key=filenames fingerprint)
- G2-CODE: BM25-only + **자동 staleness 감지** (>24h → background reindex 자동 발화)

### 남은 우선 과제 (2026-04-26)
1. **Citation probe** (HIGH ROI, 1주): retrieved node가 Claude 응답에 실제 인용됐는지 추적 — FP 실제 영향 측정
2. **Domain-specific filter** (MEDIUM ROI, 1일): 알려진 무관 패턴 커밋 필터 (homograph FP 구조적 해결)
3. **G2-DOCS 정량 벤치마크**: 질적 A/B 외 quantitative eval 미구축 상태

## 2026-04-27 CTX plugin distribution 완료 — v0.2.0 ship ✅

### 완료된 작업
- **package_data fix**: hook files → `src/hooks/` subpackage (`ctx_retriever.hooks`). `importlib.resources.files("ctx_retriever.hooks")` in install.py → auto-copy to `~/.claude/hooks/` on `ctx-install`
- **pyproject.toml**: version 0.1.0→0.2.0, `ctx_retriever.hooks` package + `"ctx_retriever.hooks": ["*.py"]` package-data, `"claude-code-plugin"` keyword 추가
- **marketplace.json fix**: `$schema` 필드 추가 (없으면 `/plugin marketplace add` 실패), `plugin/.claude-plugin/plugin.json` 신규 생성 (source="./plugin" → Claude Code가 하위 `.claude-plugin/plugin.json` 탐색)
- **hooks.json 재설계**: `${CLAUDE_PLUGIN_ROOT}/hooks/*.py` → `$HOME/.claude/hooks/*.py`. Setup hook이 inline으로 `pip install ctx-retriever && ctx-install` 실행 (setup.sh 의존 제거). CLAUDE_PLUGIN_ROOT update bug (#18517/#52218) 우회.
- **PyPI v0.2.0**: GitHub Release `v0.2.0` 트리거 → Actions OIDC Trusted Publisher 자동 publish (토큰 불필요)
- **검증 완료**: `/plugin install ctx@jaytoone` → `/reload-plugins` → 5 CTX hooks all registered in `~/.claude/settings.json`

### 핵심 아키텍처 결정
- 외부 레포 plugin install 시 Claude Code는 `.claude-plugin/` 디렉토리만 복사 (hooks/, scripts/ 미포함) → 모든 hook 실행 경로를 `$HOME/.claude/hooks/`로 고정해야 함
- Dual-path 배포: `/plugin install ctx@jaytoone` (native, hooks.json 자동 등록) + `pipx install ctx-retriever && ctx-install` (PyPI fallback)
- Pending: `platform.claude.com/plugins/submit` 공식 Anthropic registry 제출 (미완료)

## 2026-04-21 배포 전략 결정 (`/plugin` path)
- [배포 방식]: Claude Code `/plugin marketplace add jaytoone/ctx && /plugin install ctx` 두 줄 설치로 결정 — pip+ctx-install은 fallback. claude-mem (38k stars) 패턴 미러링. ~3h 작업. — 2026-04-21 / 4라운드 리서치 replay `20260421-ctx-distribution-research-replay.md` 참조
- [claude-mem 검증]: 시스템에 이미 설치됨(`~/.claude/claude-mem/` v10.0.7/plugin v9.0.6). 실제 작동 여부 + SessionStart 컨텍스트 주입 + worker-service 상태 검증 시도 중 (배포 전 실제 UX 경험 목적) — 2026-04-21
