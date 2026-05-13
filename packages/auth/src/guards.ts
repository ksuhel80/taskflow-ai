import type { Permission } from './permissions.js';
import { enforceWorkspaceIsolation, hasPermission } from './rbac.js';
import type { SessionContext } from './types.js';

export type GuardInput = {
  ctx: SessionContext;
  workspaceId?: string;
  permission: Permission;
};

export function guard(input: GuardInput): void {
  enforceWorkspaceIsolation(input.ctx, input.workspaceId);
  if (!hasPermission(input.ctx, input.permission)) {
    throw new Error(`permission_denied:${input.permission}`);
  }
}
