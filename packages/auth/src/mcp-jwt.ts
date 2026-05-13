import jwt from 'jsonwebtoken';
import { z } from 'zod';

const mcpClaimsSchema = z.object({
  sub: z.string().min(1),
  tenantId: z.string().min(1),
  workspaceId: z.string().optional(),
  roles: z.array(z.string()).default([]),
  scopes: z.array(z.string()).default([]),
});

export type McpJwtClaims = z.infer<typeof mcpClaimsSchema>;

export function verifyMcpJwt(
  token: string,
  secret: string,
  opts?: { issuer?: string; audience?: string },
) {
  const decoded = jwt.verify(token, secret, {
    issuer: opts?.issuer,
    audience: opts?.audience,
  });
  return mcpClaimsSchema.parse(decoded);
}
