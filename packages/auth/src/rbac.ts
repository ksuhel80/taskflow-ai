import type { Permission } from './permissions.js';
import { ROLE_PERMISSIONS } from './permissions.js';
import type { SessionContext } from './types.js';

export function resolvePermissions(roles: string[]): Set<Permission> {
  const out = new Set<Permission>();
  for (const role of roles) {
    for (const perm of ROLE_PERMISSIONS[role] ?? []) out.add(perm);
  }
  return out;
}

export function hasPermission(ctx: SessionContext, permission: Permission): boolean {
  return resolvePermissions(ctx.roles).has(permission);
}

export function enforceWorkspaceIsolation(
  ctx: SessionContext,
  workspaceId: string | undefined,
): void {
  if (!workspaceId) throw new Error('workspace_id_required');
  if (ctx.workspaceId && ctx.workspaceId !== workspaceId) {
    throw new Error('workspace_forbidden');
  }
}
