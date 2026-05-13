export type SecurityAuditEvent = {
  ts: string;
  tenantId: string;
  workspaceId?: string;
  actorType: 'user' | 'api_key' | 'system';
  actorId?: string;
  action:
    | 'auth.login'
    | 'auth.logout'
    | 'auth.failed'
    | 'rbac.denied'
    | 'webhook.verified'
    | 'webhook.rejected'
    | 'ai.approval.requested'
    | 'ai.approval.decided';
  ok: boolean;
  requestId?: string;
  ip?: string;
  metadata?: Record<string, unknown>;
};

export interface SecurityAuditLogger {
  log(evt: SecurityAuditEvent): Promise<void> | void;
}

export class ConsoleSecurityAuditLogger implements SecurityAuditLogger {
  log(evt: SecurityAuditEvent): void {
    // Replace with DB/outbox logger in production.
    // eslint-disable-next-line no-console
    console.log(JSON.stringify({ type: 'security_audit', ...evt }));
  }
}
