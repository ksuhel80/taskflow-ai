import { z } from 'zod';

export const authEnvSchema = z.object({
  AUTH_SECRET: z.string().min(32),
  AUTH_GOOGLE_ID: z.string().min(1),
  AUTH_GOOGLE_SECRET: z.string().min(1),
  AUTH_GITHUB_ID: z.string().min(1),
  AUTH_GITHUB_SECRET: z.string().min(1),
  AUTH_EMAIL_FROM: z.string().email(),
});

export type AuthEnv = z.infer<typeof authEnvSchema>;

/**
 * Returns framework-agnostic Auth.js provider config shape.
 * Next.js app can adapt this into `auth.ts` / route handlers.
 */
export function buildAuthJsConfig(env: NodeJS.ProcessEnv) {
  const cfg = authEnvSchema.parse({
    AUTH_SECRET: env['AUTH_SECRET'],
    AUTH_GOOGLE_ID: env['AUTH_GOOGLE_ID'],
    AUTH_GOOGLE_SECRET: env['AUTH_GOOGLE_SECRET'],
    AUTH_GITHUB_ID: env['AUTH_GITHUB_ID'],
    AUTH_GITHUB_SECRET: env['AUTH_GITHUB_SECRET'],
    AUTH_EMAIL_FROM: env['AUTH_EMAIL_FROM'],
  });

  return {
    secret: cfg.AUTH_SECRET,
    providers: [
      {
        id: 'google',
        clientId: cfg.AUTH_GOOGLE_ID,
        clientSecret: cfg.AUTH_GOOGLE_SECRET,
      },
      {
        id: 'github',
        clientId: cfg.AUTH_GITHUB_ID,
        clientSecret: cfg.AUTH_GITHUB_SECRET,
      },
      {
        id: 'email',
        from: cfg.AUTH_EMAIL_FROM,
        // OTP is enforced by custom verify token logic and rate limiting in app layer.
      },
    ],
    session: { strategy: 'jwt' as const },
    callbacks: {
      // Placeholder callback contract; concrete implementation in apps/web.
      session: 'attach tenant/roles/workspace claims',
      jwt: 'enrich token with claims',
    },
  };
}
