import { z } from 'zod';

import { verifyJwt, type JwtVerifierConfig } from '../auth/jwt.js';
import type { AuthContext } from '../auth/types.js';

export const bearerTokenSchema = z
  .string()
  .transform((s) => s.trim())
  .refine((s) => s.length > 0, 'missing token');

export function authFromAuthorizationHeader(
  authHeader: string | undefined,
  cfg: JwtVerifierConfig,
): AuthContext {
  const raw = authHeader ?? '';
  const token = raw.startsWith('Bearer ') ? raw.slice('Bearer '.length) : '';
  const parsed = bearerTokenSchema.safeParse(token);
  if (!parsed.success) {
    throw new Error('missing_bearer_token');
  }
  return verifyJwt(parsed.data, cfg);
}
