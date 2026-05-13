import { McpError } from '../errors/types.js';
import type { AuthContext } from '../auth/types.js';
import type { Permission } from './permissions.js';
import { roleToPermissions } from './permissions.js';

export function permissionsForRoles(roles: string[]): Set<Permission> {
  const perms = new Set<Permission>();
  for (const role of roles) {
    const p = roleToPermissions[role] ?? [];
    for (const perm of p) perms.add(perm);
  }
  return perms;
}

export function requirePermission(auth: AuthContext, permission: Permission): void {
  const perms = permissionsForRoles(auth.roles);
  if (!perms.has(permission)) {
    throw new McpError('UNAUTHORIZED', `Missing permission: ${permission}`, {
      status: 403,
      details: { roles: auth.roles, permission },
    });
  }
}

export function requireWorkspaceAccess(auth: AuthContext, workspaceId: string): void {
  if (!workspaceId) {
    throw new McpError('VALIDATION_FAILED', 'workspaceId is required', { status: 400 });
  }
  if (auth.allowedWorkspaces && !auth.allowedWorkspaces.includes(workspaceId)) {
    throw new McpError('WORKSPACE_FORBIDDEN', 'Workspace access denied', {
      status: 403,
      details: { workspaceId },
    });
  }
}
