export type AuditEvent = {
  ts: string;
  actor: { userId: string; tenantId: string };
  workspaceId: string;
  tool: string;
  action: 'call';
  ok: boolean;
  errorCode?: string;
  durationMs: number;
  inputHash?: string;
  meta?: Record<string, unknown>;
};

export type AuditLogger = {
  log: (evt: AuditEvent) => void | Promise<void>;
};

export function createConsoleAuditLogger(): AuditLogger {
  return {
    async log(evt) {
      // Production should send to DB/queue. Console is a safe default.
      // Ensure evt is redacted-safe.
      // eslint-disable-next-line no-console
      console.log(JSON.stringify({ kind: 'audit', ...evt }));
    },
  };
}
