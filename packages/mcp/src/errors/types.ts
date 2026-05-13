export type ErrorCode =
  | 'UNAUTHENTICATED'
  | 'UNAUTHORIZED'
  | 'WORKSPACE_FORBIDDEN'
  | 'VALIDATION_FAILED'
  | 'RATE_LIMITED'
  | 'INTERNAL_ERROR';

export class McpError extends Error {
  public readonly code: ErrorCode;
  public readonly status: number;
  public readonly details?: Record<string, unknown>;

  constructor(
    code: ErrorCode,
    message: string,
    opts?: { status?: number; details?: Record<string, unknown> },
  ) {
    super(message);
    this.code = code;
    this.status = opts?.status ?? 500;
    this.details = opts?.details;
  }
}
