export type BucketState = {
  resetAt: number;
  count: number;
};

export class InMemoryRateLimiter {
  private readonly buckets = new Map<string, BucketState>();

  constructor(
    private readonly max: number,
    private readonly windowMs: number,
  ) {}

  take(key: string): void {
    const now = Date.now();
    const current = this.buckets.get(key);
    if (!current || current.resetAt <= now) {
      this.buckets.set(key, { resetAt: now + this.windowMs, count: 1 });
      return;
    }
    current.count += 1;
    if (current.count > this.max) {
      throw new Error('rate_limited');
    }
  }
}
