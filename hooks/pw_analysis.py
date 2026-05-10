#!/usr/bin/env python3
"""
pw_analysis.py v2.0.0 (2026-04-10)
Playwright stop hook — framework detection + analysis + output
Called by stop-playwright-detect.sh via env vars.
Outputs: {"decision": "block", "reason": "..."} to stdout

v2.0.0 Changes:
  - Lean block output (~6 lines) — static instructions removed from block
  - Full context written to /tmp/pw-context-{SESSION_HASH}.json
  - stop hook re-entry guard reads JSON to show reminder message

v1.1.0 Changes:
  - edge_function category: supabase/functions/**/*.ts → DB-level API verification
  - migration category: supabase/migrations/*.sql → SQL trigger/function verification
"""
import os, re, sys, json, subprocess

# ── Language Detection ───────────────────────────────────────────
def detect_lang(cwd, targets):
    """Return 'ko' if project has Korean content, 'en' otherwise.
    Checks: PW_LANG env > CLAUDE.md/package.json Korean text > target file content.
    """
    env_lang = os.environ.get('PW_LANG', '').lower()
    if env_lang in ('ko', 'en'):
        return env_lang

    ko_range = re.compile(r'[\uAC00-\uD7A3]')

    # Check package.json description field
    pkg_json = os.path.join(cwd, 'package.json')
    if os.path.exists(pkg_json):
        try:
            desc = json.load(open(pkg_json)).get('description', '')
            if ko_range.search(desc):
                return 'ko'
        except Exception:
            pass

    # Check up to 3 target files for Korean content
    for f in targets[:3]:
        path = f if os.path.isabs(f) else os.path.join(cwd, f)
        try:
            sample = open(path, encoding='utf-8', errors='ignore').read(2000)
            if ko_range.search(sample):
                return 'ko'
        except Exception:
            pass

    return 'en'


# ── Target Filtering ────────────────────────────────────────────
_SKIP = re.compile(
    r'(?:^|[\\/])node_modules[\\/]'
    r'|package-lock\.json$'
    r'|yarn\.lock$'
    r'|pnpm-lock\.yaml$'
    r'|\.lock$'
    r'|\.min\.js$'
    r'|\.map$'
)

def filter_targets(targets):
    """Remove noise files (node_modules, lock files, build artifacts, non-ASCII filenames)."""
    return [t for t in targets if not _SKIP.search(t) and t.isascii()]


# ── Best package.json for Monorepo ───────────────────────────────
def find_best_pkg_json(cwd, targets):
    """In a monorepo, pick the package.json closest to the changed files
    that has a known framework dependency. Falls back to cwd/package.json.
    """
    PRIORITY = ['next', 'vite', '@vitejs/plugin-react', 'react-scripts', 'nuxt', '@sveltejs/kit']

    # Collect unique candidate directories from changed file paths
    candidate_dirs = set()
    for t in targets:
        path = t if os.path.isabs(t) else os.path.join(cwd, t)
        d = os.path.dirname(path)
        # Walk up to cwd, collecting each intermediate directory
        while len(d) >= len(cwd):
            candidate_dirs.add(d)
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent

    best_pkg = os.path.join(cwd, 'package.json')
    best_priority = 99  # lower = better

    for d in sorted(candidate_dirs, key=lambda x: -len(x)):  # deepest first
        pkg = os.path.join(d, 'package.json')
        if not os.path.exists(pkg):
            continue
        try:
            p = json.load(open(pkg))
            deps = {**p.get('dependencies', {}), **p.get('devDependencies', {})}
            for i, key in enumerate(PRIORITY):
                if key in deps and i < best_priority:
                    best_priority = i
                    best_pkg = pkg
                    break
        except Exception:
            pass

    return best_pkg


# ── Framework Detection ──────────────────────────────────────────
def detect_framework(pkg_path):
    if not os.path.exists(pkg_path):
        return 'unknown', '3000', 'npm run dev'
    try:
        pkg = json.load(open(pkg_path))
        deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        dev_script = pkg.get('scripts', {}).get('dev', '')
        if 'next' in deps:
            fw = 'nextjs'
        elif 'vite' in deps or '@vitejs/plugin-react' in deps:
            fw = 'vite'
        elif 'react-scripts' in deps:
            fw = 'cra'
        elif 'nuxt' in deps:
            fw = 'nuxt'
        elif '@sveltejs/kit' in deps:
            fw = 'sveltekit'
        else:
            fw = 'unknown'
        m = re.search(r'(?:--port|-p)\s*(\d+)', dev_script)
        port = m.group(1) if m else ('5173' if fw == 'vite' else '3000')
        pkg_dir = os.path.dirname(pkg_path)
        bin_base = os.path.join(pkg_dir, 'node_modules', '.bin')
        if fw == 'nextjs':
            b = os.path.join(bin_base, 'next')
            dev_cmd = f"{b} dev -p {port}" if os.access(b, os.X_OK) else f"npx next dev -p {port}"
        elif fw == 'vite':
            b = os.path.join(bin_base, 'vite')
            dev_cmd = f"{b} --port {port}" if os.access(b, os.X_OK) else f"npx vite --port {port}"
        elif fw == 'cra':
            dev_cmd = f"PORT={port} npx react-scripts start"
        else:
            dev_cmd = 'npm run dev'
        return fw, port, dev_cmd
    except Exception:
        return 'unknown', '3000', 'npm run dev'

# ── Server Detection ─────────────────────────────────────────────
def detect_server(cwd, port):
    try:
        r = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=3)
        norm_cwd = os.path.realpath(cwd)
        for line in r.stdout.splitlines():
            pm = re.search(r':(\d+)\s', line)
            pidm = re.search(r'pid=(\d+)', line)
            if pm and pidm:
                p = int(pm.group(1))
                if (3000 <= p <= 3100) or p == 4173 or (5173 <= p <= 5200) or p == 8080:
                    pid = pidm.group(1)
                    srv_link = f'/proc/{pid}/cwd'
                    srv_cwd = os.path.realpath(srv_link) if os.path.exists(srv_link) else ''
                    if not srv_cwd or srv_cwd.startswith(norm_cwd):
                        rc = subprocess.run(
                            ['curl', '-sf', '--max-time', '3', f'http://localhost:{p}'],
                            capture_output=True, timeout=5)
                        if rc.returncode == 0:
                            return True, p
    except Exception:
        pass
    return False, int(port)

# ── File Classification ──────────────────────────────────────────
def classify_files(targets):
    cats = {k: [] for k in ('api', 'component', 'page', 'hook', 'style', 'config', 'store',
                             'util', 'type', 'edge_function', 'migration')}
    rules = [
        # Edge Function 최우선 매칭 (supabase/functions/ 경로)
        ('edge_function', [r'(?:^|/)supabase/functions/[^/]+/.*\.[tj]s$',
                           r'(?:^|/)supabase/functions/[^/]+/index\.[tj]s$']),
        # DB 마이그레이션
        ('migration',     [r'(?:^|/)supabase/migrations/.*\.sql$',
                           r'(?:^|/)migrations/.*\.sql$']),
        ('api',    [r'(?:^|/)api/', r'(?:^|/)server/', r'(?:^|/)actions/', r'\.server\.[tj]sx?$', r'route\.[tj]sx?$']),
        ('page',   [r'(?:^|/)pages?/', r'(?:^|/)app/.*page\.[tj]sx?$', r'(?:^|/)app/.*layout\.[tj]sx?$',
                    r'(?:^|/)app/.*loading\.[tj]sx?$', r'(?:^|/)app/.*error\.[tj]sx?$',
                    r'(?:^|/)app/.*not-found\.[tj]sx?$', r'(?:^|/)views?/']),
        ('hook',   [r'(?:^|/)use[A-Z]', r'(?:^|/)hooks?/']),
        ('style',  [r'\.css$', r'\.scss$', r'\.sass$', r'\.less$', r'\.module\.css$', r'\.module\.scss$', r'globals?\.']),
        ('config', [r'next\.config', r'tailwind\.config', r'vite\.config', r'postcss\.config',
                    r'tsconfig\.json$', r'\.eslintrc', r'middleware\.[tj]sx?$']),
        ('store',  [r'(?:^|/)store/', r'(?:^|/)stores?/', r'(?:^|/)context/', r'(?:^|/)redux/',
                    r'(?:^|/)slices?/', r'(?:^|/)atoms?/', r'Provider\.[tj]sx?$']),
        ('type',   [r'\.d\.ts$', r'(?:^|/)types?/', r'(?:^|/)interfaces?/']),
    ]
    for f in targets:
        for cat, pats in rules:
            if any(re.search(p, f) for p in pats):
                cats[cat].append(f)
                break
        else:
            cats['component' if re.search(r'\.[tj]sx$', f) else 'util'].append(f)
    return cats


# ── Edge Function Name Extraction ─────────────────────────────────
def extract_edge_fn_names(files):
    """supabase/functions/<name>/index.ts → name 추출"""
    names = []
    for f in files:
        m = re.search(r'supabase/functions/([^/]+)/', f)
        if m:
            names.append(m.group(1))
    return list(dict.fromkeys(names))  # 순서 유지 중복 제거


# ── Credit/Refund 관련 함수 감지 ──────────────────────────────────
CREDIT_KEYWORDS = re.compile(
    r'refund|credit|banana|deduct|charge|cost|payment|환불|크레딧|바나나',
    re.IGNORECASE
)

def is_credit_related(files):
    return any(CREDIT_KEYWORDS.search(f) for f in files)

# ── Function Extraction ──────────────────────────────────────────
FN_PAT = re.compile(
    r'^(\s*)(?:export\s+(?:default\s+)?)?(?:const|let|var)\s+([a-zA-Z_]\w+)\s*'
    r'=\s*(?:useCallback|useMemo|React\.memo|memo|forwardRef|async\s*\(|\([^)]*\)\s*=>|\(\s*\)\s*=>|function)'
    r'|^(\s*)(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s+([a-zA-Z_]\w+)\s*\('
    r'|^(\s*)(?:export\s+default\s+)?class\s+([a-zA-Z_]\w+)'
    r'|^(\s*)(?:async\s+)?([a-zA-Z_]\w+)\s*\([^)]*\)\s*\{'
)
SKIP_NAMES = {'if', 'for', 'while', 'switch', 'catch', 'constructor'}

def extract_fns(diff_text, allowed):
    allowed_set = set(allowed)
    results, changed_files, cur = set(), {}, None
    for line in diff_text.splitlines():
        m = re.match(r'^\+\+\+ b/(.+)', line)
        if m:
            cur = m.group(1)
            if cur in allowed_set:
                changed_files[cur] = []
            continue
        if cur not in changed_files:
            continue
        m = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', line)
        if m:
            s, c = int(m.group(1)), int(m.group(2)) if m.group(2) else 1
            changed_files[cur].append((s, s + c))
    for fpath, ranges in changed_files.items():
        try:
            fl = open(fpath).readlines()
            for s, _ in ranges:
                if s < 1 or s > len(fl):
                    continue
                ci = len(fl[s-1]) - len(fl[s-1].lstrip())
                for i in range(min(s-1, len(fl)-1), max(0, s-100), -1):
                    m2 = FN_PAT.match(fl[i])
                    if m2:
                        if len(fl[i]) - len(fl[i].lstrip()) < ci or i == s - 1:
                            name = m2.group(2) or m2.group(4) or m2.group(6) or m2.group(8)
                            if name and name not in SKIP_NAMES:
                                results.add(name)
                                break
        except Exception:
            pass
    return results

# ── API Endpoint Extraction ───────────────────────────────────────
def extract_api_endpoints(api_files, cwd, srv_port):
    """Next.js app router route.ts → endpoint path + HTTP methods + streaming flag."""
    endpoints = []  # list of (ep, methods, is_streaming)
    for f in api_files:
        m = re.search(r'app(/api/[^/]+(?:/[^/]+)*)/route\.[tj]sx?$', f)
        if not m:
            # fallback: try to extract something useful
            endpoints.append((f'/{f}', [], False))
            continue
        ep = m.group(1)
        full = f if os.path.isabs(f) else os.path.join(cwd, f)
        try:
            content = open(full).read()
            methods = [m2 for m2 in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')
                       if re.search(rf'export\s+(?:async\s+)?function\s+{m2}', content)]
            is_streaming = bool(re.search(r'ReadableStream|text/event-stream|EventSource', content))
        except Exception:
            methods, is_streaming = [], False
        endpoints.append((ep, methods, is_streaming))
    return endpoints


def build_api_curl(ep, methods, is_streaming, srv_port):
    lines = []
    for method in (methods[:2] if methods else ['POST']):
        if is_streaming:
            lines.append(
                f"   # {method} {ep}  (SSE streaming)\n"
                f"   curl -N -X {method} http://localhost:{srv_port}{ep} \\\n"
                f"     -H 'Content-Type: application/json' \\\n"
                f"     -d '{{\"question\": \"테스트\"}}' 2>&1 | head -10\n"
                f"   # 기대: 'data: {{' 청크가 1개 이상 출력됨"
            )
        elif method == 'GET':
            lines.append(
                f"   # GET {ep}\n"
                f"   curl -s http://localhost:{srv_port}{ep} -w '\\n%{{http_code}}'\n"
                f"   # 기대: 200 + JSON 응답"
            )
        else:
            lines.append(
                f"   # {method} {ep}\n"
                f"   curl -s -X {method} http://localhost:{srv_port}{ep} \\\n"
                f"     -H 'Content-Type: application/json' \\\n"
                f"     -d '{{}}' -w '\\n%{{http_code}}'\n"
                f"   # 기대: 200/201 (400/422는 페이로드 확인 필요)"
            )
    return '\n'.join(lines) if lines else \
        f"   curl -s http://localhost:{srv_port}{ep} -w '\\n%{{http_code}}'"


# ── Build Instructions ────────────────────────────────────────────
def build_instructions(cats, deleted_ui, cwd='', srv_port=3000):
    instr = []

    # ── Edge Function: DB 레벨 검수 ──────────────────────────────
    if cats['edge_function']:
        fn_names = extract_edge_fn_names(cats['edge_function'])
        fn_list = ', '.join(fn_names[:5])
        credit_related = is_credit_related(cats['edge_function'])

        if credit_related:
            instr.append(
                f"[EDGE_FUNCTION/CREDIT] {', '.join(cats['edge_function'][:5])}\n"
                f"   -> 크레딧/환불 관련 Edge Function 변경 — UI 브라우저 검수 불가, DB 레벨 검수 필수\n"
                f"   -> Step 1: TypeScript 확인: npx tsc --noEmit 2>&1 | head -20\n"
                f"   -> Step 2: DB 연결 확인: grep SUPABASE_DB_URL .env.local | head -1\n"
                f"   -> Step 3: 환불 트리거 존재 확인:\n"
                f"      DB_URL=$(grep SUPABASE_DB_URL .env.local | cut -d= -f2-)\n"
                f"      PGPASSWORD=$(echo $DB_URL | grep -o 'password=[^&]*' | cut -d= -f2) psql \"$DB_URL\" -c \\\n"
                f"        \"SELECT trigger_name, event_object_table FROM information_schema.triggers \\\n"
                f"         WHERE trigger_name LIKE '%refund%' OR trigger_name LIKE '%auto%';\"\n"
                f"   -> Step 4: 최근 실패 레코드 + 환불 로그 확인 (실제 환불 동작 여부):\n"
                f"      psql \"$DB_URL\" -c \"SELECT id, status, credits_used, updated_at FROM audio_video_generations \\\n"
                f"        WHERE status='failed' ORDER BY updated_at DESC LIMIT 5;\"\n"
                f"      psql \"$DB_URL\" -c \"SELECT user_id, amount, type, description, created_at FROM credit_logs \\\n"
                f"        WHERE type='refund' ORDER BY created_at DESC LIMIT 10;\"\n"
                f"   -> Step 5: 이중 환불 없는지 확인:\n"
                f"      psql \"$DB_URL\" -c \"SELECT related_id, COUNT(*) as refund_count FROM credit_logs \\\n"
                f"        WHERE type='refund' AND related_id IS NOT NULL \\\n"
                f"        GROUP BY related_id HAVING COUNT(*) > 1 LIMIT 5;\"\n"
                f"   -> [PASS 기준] 이중 환불 0건 + 실패 레코드에 대응하는 환불 로그 존재"
            )
        else:
            instr.append(
                f"[EDGE_FUNCTION] {', '.join(cats['edge_function'][:5])}\n"
                f"   -> Edge Function 변경 — 브라우저 UI 불가, API 레벨 검수 필요\n"
                f"   -> Step 1: TypeScript 확인: npx tsc --noEmit 2>&1 | head -20\n"
                f"   -> Step 2: 함수 로직 검토 — 입력/출력/에러 처리 변경 확인\n"
                f"   -> Step 3 (배포 후): curl -X POST <SUPABASE_URL>/functions/v1/{fn_names[0] if fn_names else 'fn'} \\\n"
                f"      -H 'Authorization: Bearer <ANON_KEY>' -H 'Content-Type: application/json' \\\n"
                f"      -d '{{\"test\": true}}' — 정상 응답 확인\n"
                f"   -> [PASS 기준] TypeScript 에러 0 + 로직 검토 완료"
            )

    # ── DB 마이그레이션: SQL 검증 ─────────────────────────────────
    if cats['migration']:
        migration_files = cats['migration'][:5]
        # 함수/트리거 이름 추출 시도
        fn_names_sql = []
        for f in migration_files:
            m = re.search(r'FUNCTION\s+(?:public\.)?(\w+)', open(f).read() if os.path.exists(f) else '', re.IGNORECASE)
            if m:
                fn_names_sql.append(m.group(1))
        fn_hint = f" (함수: {', '.join(fn_names_sql[:3])})" if fn_names_sql else ""
        instr.append(
            f"[MIGRATION] {', '.join(migration_files)}{fn_hint}\n"
            f"   -> DB 마이그레이션 변경 — SQL 함수/트리거 실제 존재 여부 검증 필요\n"
            f"   -> Step 1: DB 연결: DB_URL=$(grep SUPABASE_DB_URL .env.local | cut -d= -f2-)\n"
            f"   -> Step 2: 함수 존재 확인:\n"
            f"      psql \"$DB_URL\" -c \"SELECT proname, prosrc IS NOT NULL as has_body \\\n"
            "        FROM pg_proc WHERE proname LIKE '%refund%' OR proname LIKE '%credit%';\"\n"
            f"   -> Step 3: 트리거 확인:\n"
            f"      psql \"$DB_URL\" -c \"SELECT trigger_name, event_object_table, action_timing \\\n"
            f"        FROM information_schema.triggers ORDER BY trigger_name;\"\n"
            f"   -> [PASS 기준] 함수/트리거 DB에 실제 존재 확인"
        )

    if cats['api']:
        eps = extract_api_endpoints(cats['api'], cwd, srv_port)
        curl_blocks = [build_api_curl(ep, methods, streaming, srv_port)
                       for ep, methods, streaming in eps[:3]]
        curl_section = '\n\n'.join(curl_blocks)
        instr.append(
            f"[API] {', '.join(cats['api'][:5])}\n"
            f"   -> E2E 검수 필수 — 타입체크만으로 불충분, 실제 엔드포인트 호출:\n"
            f"{curl_section}\n"
            f"   -> FAIL 기준: 5xx 응답 / streaming API에서 첫 청크 미수신 / 빈 응답"
        )
    if cats['page']:
        routes = []
        for f in cats['page'][:3]:
            m = re.search(r'app/(.+)/page\.[tj]sx?$', f)
            if m:
                routes.append('/' + m.group(1))
                continue
            m = re.search(r'pages/(.+)\.[tj]sx?$', f)
            if m:
                r = m.group(1)
                routes.append('/' if r in ('index', '_app', '_document') else '/' + r.replace('/index', ''))
        hint = f" -> 검수 페이지: {', '.join(routes)}" if routes else ""
        instr.append(f"[PAGE] {', '.join(cats['page'][:5])}{hint}\n"
                     "   -> 해당 페이지 직접 네비게이션\n"
                     "   -> [셀렉터 원칙] getByRole('button',{name:'...'}) / getByLabel / getByText 사용 — CSS selector 금지\n"
                     "   -> browser_snapshot()으로 렌더링 확인\n"
                     "   -> 레이아웃 깨짐/빈 화면/hydration 에러 확인")
    if cats['component']:
        instr.append(f"[COMPONENT] {', '.join(cats['component'][:5])}\n"
                     "   -> 해당 컴포넌트가 사용되는 페이지 방문\n"
                     "   -> [셀렉터 원칙] getByRole/getByLabel/getByText 우선 — CSS/ID 셀렉터 금지\n"
                     "   -> browser_click / browser_fill_form 으로 인터랙션 테스트\n"
                     "   -> props 변경 시 조건부 렌더링 분기 확인")
    if cats['hook']:
        instr.append(f"[HOOK] {', '.join(cats['hook'][:5])}\n"
                     "   -> 훅을 사용하는 컴포넌트에서 상태 변화 시나리오 실행\n"
                     "   -> 로딩/에러/성공 상태 전환 확인\n"
                     "   -> 콘솔에 hook 관련 에러 없는지 확인")
    if cats['style']:
        instr.append(f"[STYLE] {', '.join(cats['style'][:5])}\n"
                     "   -> 스타일 변경 영향받는 페이지 방문\n"
                     "   -> browser_snapshot()으로 visual regression 확인\n"
                     "   -> 반응형: browser_resize(width=375, height=812) 모바일 확인")
    if cats['config']:
        instr.append(f"[CONFIG] {', '.join(cats['config'][:5])}\n"
                     "   -> 설정 변경이 빌드에 영향 → 서버 재시작 필요 여부 확인\n"
                     "   -> 메인 페이지 정상 로딩 확인 (빌드 에러 없는지)")
    if cats['store']:
        instr.append(f"[STATE] {', '.join(cats['store'][:5])}\n"
                     "   -> 상태 관리 변경 → 해당 상태를 사용하는 UI 전체 확인\n"
                     "   -> 상태 변경 트리거(버튼 클릭 등) → UI 업데이트 확인\n"
                     "   -> 페이지 새로고침 후 상태 초기화 정상 확인")
    if deleted_ui:
        instr.append(f"[DELETE WARNING] {', '.join(deleted_ui[:5])}\n"
                     "   -> 삭제된 파일을 import하는 다른 파일이 있으면 빌드 에러 발생\n"
                     "   -> browser_console_messages(onlyErrors=True) 에서 Module not found 확인\n"
                     "   -> 삭제된 컴포넌트가 렌더링되던 페이지 방문하여 깨짐 확인")
    if not instr and (cats['util'] or cats['type']):
        instr.append(f"[UTIL/TYPE] {', '.join((cats['util'] + cats['type'])[:5])}\n"
                     "   -> 유틸/타입 변경 → 사용처 UI에 간접 영향 가능\n"
                     "   -> 메인 페이지 정상 로딩 + 콘솔 에러 없는지 확인")
    return '\n\n'.join(instr)

# ── Main ──────────────────────────────────────────────────────────
def main():
    cwd = os.environ.get('PW_CWD', os.getcwd())
    session_hash = os.environ.get('PW_SESSION_HASH', 'x')
    flag_cmd = os.environ.get('PW_FLAG', '')
    pkg_path = os.environ.get('PW_PACKAGE_JSON', os.path.join(cwd, 'package.json'))

    def read_file_lines(env_key):
        path = os.environ.get(env_key, '')
        if path and os.path.exists(path):
            return [l.strip() for l in open(path) if l.strip()]
        return []

    targets = filter_targets(read_file_lines('PW_TARGETS_FILE'))
    deleted = filter_targets(read_file_lines('PW_DELETED_FILE'))

    # Nothing to verify after noise filtering
    if not targets and not deleted:
        print(json.dumps({"decision": "allow"}))
        return

    dh = os.environ.get('PW_DIFF_HEAD_FILE', '')
    dc = os.environ.get('PW_DIFF_COMMIT_FILE', '')
    diff_head   = open(dh).read() if dh and os.path.exists(dh) else ''
    diff_commit = open(dc).read() if dc and os.path.exists(dc) else ''

    # Monorepo: find best package.json from actual changed files
    if not os.path.exists(pkg_path) or pkg_path == os.path.join(cwd, 'package.json'):
        pkg_path = find_best_pkg_json(cwd, targets)
    fw, port, dev_cmd = detect_framework(pkg_path)
    server_running, srv_port = detect_server(cwd, port)
    deployed_url = os.environ.get('PW_DEPLOYED_URL', '').strip()
    can_start_local = bool(pkg_path and os.path.exists(pkg_path) and dev_cmd)

    # 미커밋 여부: 변경 대상 파일이 아직 커밋 안 됐으면 = 배포 안 됨 = 로컬 검수
    def has_uncommitted_targets(t_list):
        try:
            r = subprocess.run(
                ['git', '-C', cwd, 'diff', 'HEAD', '--name-only'],
                capture_output=True, text=True, timeout=5
            )
            changed = set(r.stdout.splitlines())
            r2 = subprocess.run(
                ['git', '-C', cwd, 'diff', '--cached', '--name-only'],
                capture_output=True, text=True, timeout=5
            )
            changed |= set(r2.stdout.splitlines())
            return any(t in changed for t in t_list)
        except Exception:
            return True  # conservative: 판단 불가 → 로컬 검수

    has_uncommitted = has_uncommitted_targets(targets)

    if server_running:
        url = f"http://localhost:{srv_port}"
    elif has_uncommitted or not deployed_url:
        # 미커밋(미배포) 또는 배포 URL 없음 → 로컬 서버 필요
        url = f"http://localhost:{port}"
    else:
        # 모두 커밋됨 + 배포 URL 존재 → 배포 서버 검수
        url = deployed_url if deployed_url.startswith('http') else f"https://{deployed_url}"

    cats = classify_files(targets)
    all_fns = extract_fns(diff_head, targets) | extract_fns(diff_commit, targets)
    ui_ext = re.compile(r'\.[tj]sx?$|\.css$|\.scss$|\.vue$|\.svelte$')
    deleted_ui = [f for f in deleted if ui_ext.search(f)]

    instructions = build_instructions(cats, deleted_ui, cwd, srv_port) or \
        "변경된 파일과 연관된 기능 직접 테스트 (클릭/입력/데이터 표시 확인)"

    total = len(targets)
    magnitude = 'SMALL' if total <= 3 else ('MEDIUM' if total <= 10 else 'LARGE')
    has_server_side = bool(cats.get('edge_function') or cats.get('migration'))
    lang = detect_lang(cwd, targets)
    delete_warn = " [!DELETE]" if deleted_ui else ""
    if lang == 'ko':
        if server_running:
            server_str = f"{url} (실행중)"
        elif not has_uncommitted and deployed_url:
            server_str = f"{url} (배포 서버)"
        else:
            server_str = f"{url} (중지 — {dev_cmd} 시작 필요)"
        file_unit = "파일"
        server_label, changed_label, cat_label = "서버", "변경", "카테고리"
    else:
        if server_running:
            server_str = f"{url} (running)"
        elif not has_uncommitted and deployed_url:
            server_str = f"{url} (deployed server)"
        else:
            server_str = f"{url} (stopped — run {dev_cmd})"
        file_unit = "files"
        server_label, changed_label, cat_label = "Server", "Changed", "Categories"
    cat_order = ['page','component','api','hook','style','config','store','edge_function','migration','util','type']
    cat_str = ' '.join(f"[{k.upper()}]" for k in cat_order if cats.get(k))
    target_preview = ', '.join(targets[:5]) + (f' +{total-5}' if total > 5 else '')

    # Write full context for stop hook re-entry reminder
    ctx = {
        "flag_cmd": flag_cmd,
        "url": url,
        "server_running": server_running,
        "deployed_url": deployed_url,
        "has_uncommitted": has_uncommitted,
        "can_start_local": can_start_local,
        "fw": fw,
        "dev_cmd": dev_cmd,
        "cwd": cwd,
        "targets": targets[:20],
        "cats": {k: v for k, v in cats.items() if v},
        "magnitude": magnitude,
        "has_server_side": has_server_side,
        "all_fns": sorted(all_fns)[:10],
        "deleted_ui": deleted_ui[:5],
        "instructions": instructions,
        "lang": lang,
    }
    ctx_path = f"/tmp/pw-context-{session_hash}.json"
    with open(ctx_path, 'w') as f:
        json.dump(ctx, f)

    local_url = f"http://localhost:{srv_port if server_running else port}"
    dep_url = (deployed_url if deployed_url.startswith('http') else f"https://{deployed_url}") if deployed_url else None
    if server_running:
        # 로컬 서버 실행 중 → 로컬 검수
        if lang == 'ko':
            auto_action = f"Claude: Playwright로 {local_url} 검수 후 → {flag_cmd}"
        else:
            auto_action = f"Claude: Playwright verify {local_url} → {flag_cmd}"
    elif not has_uncommitted and deployed_url:
        # 모두 커밋됨 + 배포 URL 있음 → 배포 서버 검수
        if lang == 'ko':
            auto_action = f"Claude: Playwright로 {dep_url} (배포 서버) 검수 후 → {flag_cmd}"
        else:
            auto_action = f"Claude: Playwright verify {dep_url} (deployed) → {flag_cmd}"
    else:
        # 미커밋(미배포) 또는 배포 URL 없음 → 로컬 서버 시작 후 검수
        if lang == 'ko':
            auto_action = f"Claude: `{dev_cmd}` 백그라운드 실행(서버 시작) → Playwright로 {local_url} 검수 → {flag_cmd}"
        else:
            auto_action = f"Claude: run `{dev_cmd}` in background → Playwright verify {local_url} → {flag_cmd}"
    reason = (
        f"[PLAYWRIGHT] {magnitude}: {total}{file_unit}{delete_warn} | {fw}\n"
        f"{server_label}: {server_str}\n"
        f"{changed_label}: {target_preview}\n"
        f"{cat_label}: {cat_str or '[UTIL/TYPE]'}\n"
        f"{auto_action}"
    )
    print(json.dumps({"decision": "block", "reason": reason}))

if __name__ == "__main__":
    main()
