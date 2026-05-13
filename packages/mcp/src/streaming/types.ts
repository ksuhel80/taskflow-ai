export type StreamEvent =
  | { type: 'progress'; message: string; pct?: number; meta?: Record<string, unknown> }
  | { type: 'result'; message: string; meta?: Record<string, unknown> };

export type StreamEmitter = {
  emit: (evt: StreamEvent) => void;
};
