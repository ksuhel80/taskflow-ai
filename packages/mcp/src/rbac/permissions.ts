export type Permission =
  | 'tasks:read'
  | 'tasks:write'
  | 'sprints:write'
  | 'memory:search'
  | 'team:load:read'
  | 'risk:alerts:read';

export const roleToPermissions: Record<string, Permission[]> = {
  admin: [
    'tasks:read',
    'tasks:write',
    'sprints:write',
    'memory:search',
    'team:load:read',
    'risk:alerts:read',
  ],
  member: ['tasks:read', 'tasks:write', 'memory:search', 'team:load:read'],
  viewer: ['tasks:read', 'team:load:read', 'risk:alerts:read'],
};
