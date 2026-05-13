import jwt from 'jsonwebtoken';
import { z } from 'zod';

import { McpError } from '../errors/types.js';
import type { AuthContext, JwtClaims } from './types.js';

const jwtClaimsSchema = z.object({
  sub: z.string().min(1),
  tenantId: z.string().min(1),
  roles: z.array(z.string().min(1)).default([]),
  workspaces: z.array(z.string().min(1)).optional(),
  iat: z.number().optional(),
  exp: z.number().optional(),
  iss: z.string().optional(),
  aud: z.string().optional(),
});

export type JwtVerifierConfig = {
  jwtSecret: string;
  issuer?: string;
  audience?: string;
};

export function verifyJwt(token: string, cfg: JwtVerifierConfig): AuthContext {
  try {
    const decoded = jwt.verify(token, cfg.jwtSecret, {
      issuer: cfg.issuer,
      audience: cfg.audience,
    });

    const claims = jwtClaimsSchema.parse(decoded) satisfies JwtClaims;
    return {
      userId: claims.sub,
      tenantId: claims.tenantId,
      roles: claims.roles,
      allowedWorkspaces: claims.workspaces,
    };
  } catch (err) {
    throw new McpError('UNAUTHENTICATED', 'Invalid or expired JWT', {
      status: 401,
      details: { reason: err instanceof Error ? err.message : String(err) },
    });
  }
}
