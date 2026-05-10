# PostgreSQL Connection

Use PGPASSWORD env var (simpler than .pgpass):

```bash
PGPASSWORD="your_password" psql -h "hostname" -p 5432 -U "username" -d "database" -c "SELECT 1"
```

## Supabase example
```bash
PGPASSWORD="$PGPASSWORD" psql \
  -h aws-1-ap-northeast-2.pooler.supabase.com -p 5432 \
  -U postgres.{PROJECT_ID} -d postgres \
  -c "SELECT * FROM your_table LIMIT 5;"
```
