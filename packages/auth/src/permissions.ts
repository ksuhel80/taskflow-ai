export type Permission =
  | 'workspace:read'
  | 'workspace:write'
  | 'project:read'
  | 'project:write'
  | 'task:read'
  | 'task:write'
  | 'sprint:read'
  | 'sprint:write'
  | 'ai:workflow:run'
  | 'ai:approval:decide'
  | 'audit:read'
  | 'mcp:call';

export const ROLE_PERMISSIONS: Record<string, Permission[]> = {
  owner: [
    'workspace:read',
    'workspace:write',
    'project:read',
    'project:write',
    'task:read',
    'task:write',
    'sprint:read',
    'sprint:write',
    'ai:workflow:run',
    'ai:approval:decide',
    'audit:read',
    'mcp:call',
  ],
  admin: [
    'workspace:read',
    'workspace:write',
    'project:read',
    'project:write',
    'task:read',
    'task:write',
    'sprint:read',
    'sprint:write',
    'ai:workflow:run',
    'ai:approval:decide',
    'audit:read',
    'mcp:call',
  ],
  member: [
    'workspace:read',
    'project:read',
    'project:write',
    'task:read',
    'task:write',
    'sprint:read',
    'ai:workflow:run',
    'mcp:call',
  ],
  viewer: ['workspace:read', 'project:read', 'task:read', 'sprint:read'],
};
