# Hub Telemetry Relay (M1517)

Private Cloudflare Worker that hides Turso URL/token from public hub client code.

## Deploy

```bash
cd /home/desk-1/.hub/relay
npm install -g wrangler      # if not already
wrangler login                # browser auth
wrangler secret put TURSO_URL    # paste: https://hub-jaytoone.aws-us-west-2.turso.io
wrangler secret put TURSO_TOKEN  # paste: <existing HUB_TELEMETRY_TOKEN value>
wrangler secret put RELAY_SECRET # OPTIONAL: random string to gate abuse
wrangler deploy
```

Output: `https://hub-telemetry-relay.<your-subdomain>.workers.dev`

## Configure hub client

Set environment variable on every hub install:
```bash
export HUB_RELAY_URL=https://hub-telemetry-relay.<your-subdomain>.workers.dev
# optional:
export HUB_RELAY_SECRET=<same as wrangler secret RELAY_SECRET>
```

When `HUB_RELAY_URL` is set, `_send_session_aggregate` posts to relay instead of Turso directly.
When not set, falls back to direct Turso (legacy, only safe on private/trusted clients).

## Verify

```bash
curl -X POST https://hub-telemetry-relay.<your-subdomain>.workers.dev/v1/session-aggregate \
  -H 'Content-Type: application/json' \
  -d '{"schema_version":"v1","install_id":"test","ts_date":"2026-06-25","action_count":1}'
# {"ok":true}

curl https://hub-telemetry-relay.<your-subdomain>.workers.dev/health
# {"ok":true,"service":"hub-telemetry-relay"}
```

## Why this exists

Before: public PyPI/GitHub source contained Turso URL + rw token → anyone could read or insert.
After: client only knows the relay URL. Turso credentials live only in Worker secrets.
Token rotation: update `wrangler secret put TURSO_TOKEN` — no client redeploy needed.
