# TaskFlow AI - Enterprise Security Architecture

This document defines enterprise-grade security architecture across:

- `apps/web` (Auth.js + OAuth/OTP sessions)
- `apps/ai-runtime` (service/workflow authorization and approvals)
- `packages/mcp` (JWT auth for API/tool calls)

Security goals:

- strong authentication
- role-based authorization
- strict workspace isolation
- auditable actions
- rate-limited APIs
- secure webhook ingestion
- human approval for sensitive AI actions

---

## 1) Auth Architecture

## 1.1 Identity flows

User authentication providers:

- Google OAuth
- GitHub OAuth
- Email OTP (passwordless)

Session strategy:

- Auth.js session with JWT strategy
- JWT enriched with:
  - `tenantId`
  - `workspaceId` (active workspace context)
  - `roles`

Provider configuration is centralized in:

- `packages/auth/src/authjs.ts`

## 1.2 Auth components

- `packages/auth/src/authjs.ts`
  - provider/env validation and Auth.js config builder
- `packages/auth/src/otp.ts`
  - OTP generation + secure hashing
- `packages/auth/src/mcp-jwt.ts`
  - JWT validation utilities for MCP/API channels

---

## 2) Middleware Design

Core middleware utilities:

- `packages/auth/src/middleware.ts`
  - extracts bearer token
  - verifies MCP JWT
  - builds `SessionContext`

Expected runtime middleware layers:

1. request id / trace id
2. auth middleware (session/JWT resolve)
3. workspace isolation middleware
4. permission guard middleware
5. rate limiter
6. audit log emission

---

## 3) RBAC System

RBAC is centralized in:

- `packages/auth/src/permissions.ts`
  - role -> permission map
- `packages/auth/src/rbac.ts`
  - permission resolution
  - workspace isolation checks

Core roles:

- `owner`
- `admin`
- `member`
- `viewer`

Permission checks are capability-based (not endpoint hardcoded).

---

## 4) Permission Guards

Guard utilities:

- `packages/auth/src/guards.ts`

Guard contract:

- verify workspace isolation first
- then verify permission
- fail closed (`permission_denied:*`)

Usage pattern:

1. resolve `SessionContext`
2. call `guard({ ctx, workspaceId, permission })`
3. continue only on success

---

## 5) Audit Logging System

Security audit contracts:

- `packages/auth/src/audit.ts`

Tracked events include:

- login success/failure
- authorization denials
- webhook verification outcomes
- AI approval requested/decided

Event shape includes:

- actor metadata
- tenant/workspace scope
- request/ip metadata
- action + outcome

Production recommendation:

- replace console logger with append-only DB/outbox sink
- forward to SIEM for detection and compliance

---

## 6) AI Action Approval System

Approval contracts:

- `packages/auth/src/approval.ts`

Defines:

- approval request schema
- approval decision schema

Security rule:

- sensitive AI actions (publish, mass updates, external side effects) require explicit approval
- approval decisions must be auditable and tied to user identity

---

## 7) API Security Strategy

## 7.1 JWT auth for MCP

- MCP endpoints require bearer JWT with tenant/workspace claims
- verify using `verifyMcpJwt()` in `packages/auth/src/mcp-jwt.ts`
- enforce role/scope checks before tool execution

## 7.2 Workspace isolation

- every protected operation requires `workspaceId`
- cross-workspace access is denied unless explicitly allowed in claims/policy

## 7.3 API rate limiting

- `packages/auth/src/rate-limit.ts` provides in-memory baseline limiter
- production should use shared Redis-backed rate limiter for multi-instance consistency

## 7.4 Secure webhooks

- `packages/auth/src/webhooks.ts`
  - HMAC signing
  - timing-safe signature verification

Webhook controls:

- signature verification mandatory
- replay protection via timestamp + nonce cache
- strict source allow-lists and route-specific secrets

---

## 8) Threat Model Priorities

Primary risks addressed:

- token theft / session abuse
- lateral access across workspaces
- permission escalation
- abusive API traffic
- spoofed webhook events
- unsafe AI autonomous side effects

Hardening recommendations:

- short JWT TTL + refresh policy
- rotate webhook and API secrets
- mandatory MFA policy for privileged roles (future)
- anomaly detection on auth and approval events
