/**
 * Seed entrypoint (stub).
 *
 * Architecture-only: implement idempotent upserts for global catalogs later.
 */
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();
async function main() {
  // Intentionally empty seed logic for now.
  // Use upserts + unique constraints to keep this seed idempotent.
  console.log('database seed stub: no-op');
}
main()
  .catch((err) => {
    console.error(err);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
//# sourceMappingURL=seed.js.map
