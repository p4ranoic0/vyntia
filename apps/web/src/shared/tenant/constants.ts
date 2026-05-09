/**
 * Reserved subdomains that NEVER resolve to a tenant.
 * Mirrors apps/api/apps/tenancy/constants.py RESERVED_SUBDOMAINS.
 */
export const RESERVED_SUBDOMAINS = new Set<string>([
  'admin',     // admin.vyntia.pe — Vyntia staff panel
  'app',       // app.vyntia.pe — workspace switcher
  'www',       // www.vyntia.pe — marketing
  'api',       // api.vyntia.pe — public API alias
  'docs',
  'status',
  'blog',
  'mail',
  'support',
  'help',
  'vyntia',
  // local/dev
  'localhost',
  '127',
  '0',
])
