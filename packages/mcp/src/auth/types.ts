export type JwtClaims = {
  sub: string; // user id
  tenantId: string;
  roles: string[];
  // Optional workspace allow-list; enforcement still requires per-call check.
  workspaces?: string[];
  iat?: number;
  exp?: number;
  iss?: string;
  aud?: string;
};

export type AuthContext = {
  userId: string;
  tenantId: string;
  roles: string[];
  allowedWorkspaces?: string[];
};

export type McpSubject = {
  sub: string;
  /** Human-readable subject identifier if available. */
  email?: string;
};

export type McpWorkspace = {
  workspaceId: string;
  tenantId: string;
};

export type McpRole = 'admin' | 'manager' | 'member' | 'viewer';

export type McpAuthContext = {
  subject: McpSubject;
  workspace: McpWorkspace;
  roles: McpRole[];
  /** Stable request correlation id (generated per request). */
  requestId: string;
  /** JWT `jti` when available. */
  tokenId?: string;
};
