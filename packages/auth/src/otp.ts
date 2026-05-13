import crypto from 'node:crypto';

export function generateEmailOtp(length = 6): string {
  const digits = '0123456789';
  let out = '';
  const bytes = crypto.randomBytes(length);
  for (const b of bytes) out += digits[b % 10];
  return out;
}

export function hashOtp(otp: string, secret: string): string {
  return crypto.createHmac('sha256', secret).update(otp).digest('hex');
}
