import type { IncomingHttpHeaders } from 'node:http';

import { verifyMcpJwt } from './mcp-jwt.js';
import type { SessionContext } from './types.js';

export function bearerToken(headers: IncomingHttpHeaders): string | null {
  const auth = headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) return null;
  return auth.slice('Bearer '.length);
}

export function buildSessionContextFromMcpJwt(
  headers: IncomingHttpHeaders,
  secret: string,
): SessionContext {
  const token = bearerToken(headers);
  if (!token) throw new Error('unauthenticated');
  const claims = verifyMcpJwt(token, secret);
  return {
    userId: claims.sub,
    tenantId: claims.tenantId,
    workspaceId: claims.workspaceId,
    roles: claims.roles,
  };
}
