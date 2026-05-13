import { McpError } from '../errors/types.js';

export type RateLimitKey = string;

export type RateLimiter = {
  take: (key: RateLimitKey) => void;
};

export type InMemoryRateLimiterConfig = {
  windowMs: number;
  max: number;
};

/**
 * Simple per-process limiter. For production, replace with Redis-backed limiter.
 */
export function createInMemoryRateLimiter(cfg: InMemoryRateLimiterConfig): RateLimiter {
  const buckets = new Map<string, { resetAt: number; count: number }>();

  return {
    take(key: string) {
      const now = Date.now();
      const bucket = buckets.get(key);
      if (!bucket || bucket.resetAt <= now) {
        buckets.set(key, { resetAt: now + cfg.windowMs, count: 1 });
        return;
      }
      bucket.count += 1;
      if (bucket.count > cfg.max) {
        throw new McpError('RATE_LIMITED', 'Rate limit exceeded', {
          status: 429,
          details: { windowMs: cfg.windowMs, max: cfg.max },
        });
      }
    },
  };
}
