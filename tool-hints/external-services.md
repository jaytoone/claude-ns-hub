# External Services Safety Checklists

**Core rule**: Never mix up projects. Always verify `.env.local` before connecting.

---

## Supabase Connection Checklist

1. **Pre-connection verification**
   ```bash
   grep "SUPABASE_DB_URL\|SUPABASE_PROJECT_REF" .env.local
   supabase projects list
   ```

2. **Explicit validation on DB connect**
   - ✅ Parse project ID from `SUPABASE_DB_URL` in `.env.local`
   - ✅ Confirm `postgres.{PROJECT_ID}` format
   - ✅ After first query: `SELECT current_database(), current_user;`
   - ❌ Blindly reuse connection info from previous sessions
   - ❌ Arbitrarily pick from the project list

3. **On error: check connection first**
   - Table/function not found → suspect wrong project connection first
   - Migration state mismatch → re-verify connected project
   - RLS errors → confirm correct project, then check permissions

---

## Vercel Deployment Checklist

1. **Pre-deployment verification**
   ```bash
   cat vercel.json | grep "name"
   vercel ls
   cat .vercel/project.json
   ```

2. **Validation**
   - ✅ Confirm correct project with `vercel ls` before deploying
   - ✅ Use `vercel --prod` explicitly for production
   - ❌ Deploy to production without approval

---

## Other Services (Railway/Render/etc.)

- Use service-specific CLI to confirm linked project
- Parse project info from environment variables
- Validate project ID in endpoint URL before API calls
- Clearly distinguish production / staging / development

---

## Quick Verification Commands

```bash
# Supabase — check current project
grep SUPABASE_PROJECT_REF .env.local
supabase projects list | grep "●"

# Vercel — check current project
vercel ls --json | jq '.name'
```
