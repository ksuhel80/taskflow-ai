export type AuthProvider = 'google' | 'github' | 'email_otp';

export type UserIdentity = {
  userId: string;
  tenantId: string;
  workspaceId?: string;
  email?: string;
  roles: string[];
};

export type SessionContext = UserIdentity & {
  requestId?: string;
  traceId?: string;
};

export type ApiKeyAuthContext = {
  keyId: string;
  tenantId: string;
  workspaceId?: string;
  scopes: string[];
};
