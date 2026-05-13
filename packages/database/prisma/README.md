# Prisma (PostgreSQL + pgvector)

## Requirements

- PostgreSQL database
- `pgvector` extension enabled

## pgvector extension

Enable the extension in the *first* migration (or manually once):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The Prisma schema stores embeddings using an `Unsupported("vector(1536)")` type.

## Environment variables

This Prisma schema expects:

- `DATABASE_URL` (required)

## Common commands

- Generate client:
  - `npm run prisma:generate`
- Create migrations locally:
  - `npm run prisma:migrate`
- Deploy migrations in CI/CD:
  - `npm run prisma:migrate:deploy`

## Multi-tenant notes

This design uses a single shared Postgres schema with `tenant_id` columns on all tenant-scoped tables.
Tenant isolation can be strengthened later with PostgreSQL RLS, but the Prisma schema already
models `tenant_id` everywhere required.

