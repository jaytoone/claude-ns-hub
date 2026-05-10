// Playwright smoke test — node ~/.claude/snippets/pw-smoke.js [URL]
// Usage: node pw-smoke.js http://localhost:3000
const { chromium } = require('playwright');
const url = process.argv[2] || 'http://localhost:3000';
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage();
  const errors = [];
  p.on('console', m => m.type() === 'error' && errors.push(m.text()));
  p.on('requestfailed', r => errors.push('FAILED: ' + r.url()));
  const resp = await p.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
  const title = await p.title();
  const btns = await p.getByRole('button').count();
  const links = await p.getByRole('link').count();
  await p.screenshot({ path: '/tmp/smoke.png' });
  await b.close();
  console.log(`URL: ${url}  HTTP: ${resp.status()}  title: "${title}"`);
  console.log(`roles: buttons=${btns} links=${links}`);
  console.log(`errors: ${errors.length ? errors.slice(0,3).join(' | ') : 'none'}`);
  console.log(errors.length === 0 ? 'PASS' : 'WARN');
})();
