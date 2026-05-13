# `@taskflow-ai/database`

Shared database primitives for TaskFlow AI (Prisma + PostgreSQL).

This package is responsible for:
- Prisma schema + generators
- Prisma migration/seeding workflow (docs + seed stub)
- Canonical data model for multi-tenant audit logs, AI agent tracking,
  workflow persistence, and memory storage (pgvector).

Feature/business logic lives in `apps/*` and service packages; this module
contains shared persistence contracts only.

