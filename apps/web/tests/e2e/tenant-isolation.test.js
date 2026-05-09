// @ts-check
/**
 * Cross-tenant isolation E2E smoke tests (C.8 spec § 9.3).
 *
 * These tests are SKIPPED by default because they require:
 *  - A running backend (`apps/api` dev server on :8000) with two seeded
 *    tenants (`acme.vyntia.pe` and `beta.vyntia.pe`) plus at least one
 *    member each.
 *  - Local hosts-file entries OR a wildcard DNS proxy mapping
 *    `*.vyntia.pe` to 127.0.0.1.
 *  - `RUN_TENANT_E2E=1` env var set.
 *
 * To run locally:
 *   RUN_TENANT_E2E=1 npx playwright test tests/e2e/tenant-isolation.test.js
 *
 * To set up the seed:
 *   cd apps/api && python manage.py seed_tenant_e2e   (NOT YET IMPLEMENTED;
 *   see docs/operations/provision-tenant.md to provision manually for now.)
 *
 * Spec: docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md § 9.3
 */

import { expect, test } from '@playwright/test';

const RUN = process.env.RUN_TENANT_E2E === '1';

const TENANT_A = {
  host: 'acme.vyntia.pe',
  username: 'admin@acme.test',
  password: 'AcmePass123!',
};

const TENANT_B = {
  host: 'beta.vyntia.pe',
  username: 'admin@beta.test',
  password: 'BetaPass123!',
};

test.describe('Cross-tenant isolation', () => {
  test.skip(!RUN, 'Requires multi-tenant seed + hosts entries; set RUN_TENANT_E2E=1 to enable');

  test('user logged into tenant A cannot access tenant B by URL hop', async ({ page, context }) => {
    // Log in to tenant A
    await page.goto(`http://${TENANT_A.host}:5173/login`);
    await page.fill('[name="username"]', TENANT_A.username);
    await page.fill('[name="password"]', TENANT_A.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(`http://${TENANT_A.host}:5173/`);

    // Capture the access token (stored in localStorage by the auth flow)
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token, 'should have logged in').toBeTruthy();

    // Now hop to tenant B with the same token. The apiClient guard should
    // detect mismatch (token.tenant_slug !== "beta") and clear it; the
    // app should redirect to login.
    await page.goto(`http://${TENANT_B.host}:5173/`);
    // Either we land on login (token cleared client-side) or we get a
    // 401 from the backend rejected by TenantAuthMiddleware. Both are
    // valid outcomes — the contract is "user does NOT see tenant B data".
    await expect(page).toHaveURL(/login/i, { timeout: 5_000 });
  });

  test('workspace switcher on app.vyntia.pe lists only user\'s memberships', async ({ page }) => {
    // This requires a user that is a member of >=1 workspace.
    await page.goto('http://app.vyntia.pe:5173/login');
    await page.fill('[name="username"]', TENANT_A.username);
    await page.fill('[name="password"]', TENANT_A.password);
    await page.click('button[type="submit"]');
    // After login on app.vyntia.pe the user lands on WorkspacesPage (catchall)
    await page.waitForURL(/\/(workspaces|$)/);

    // Verify the workspace card for tenant A renders, but NOT for tenant B.
    await expect(page.getByText(TENANT_A.host.split('.')[0], { exact: false })).toBeVisible();
    await expect(page.getByText(TENANT_B.host.split('.')[0], { exact: false })).not.toBeVisible();
  });

  test('impersonation banner is visible on every page during a SupportSession', async ({ page }) => {
    // Pre-condition: an impersonation JWT for tenant A is in localStorage.
    // In a real run this would be obtained via the admin API; here we
    // mock it by setting localStorage manually.
    //
    // The JWT below is a fixture token with payload:
    //   { "tenant_slug": "acme", "impersonated_by": "vyntia_staff_1",
    //     "support_session_id": "abc-123" }
    const FIXTURE_IMPERSONATION_TOKEN =
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfc2x1ZyI6ImFjbWUiLCJpbXBlcnNvbmF0ZWRfYnkiOiJ2eW50aWFfc3RhZmZfMSIsInN1cHBvcnRfc2Vzc2lvbl9pZCI6ImFiYy0xMjMifQ.fake';

    await page.goto(`http://${TENANT_A.host}:5173/login`);
    await page.evaluate((tok) => {
      localStorage.setItem('access_token', tok);
    }, FIXTURE_IMPERSONATION_TOKEN);

    // Navigate to a couple of pages and verify the banner is sticky.
    for (const path of ['/', '/empleados', '/legajo']) {
      await page.goto(`http://${TENANT_A.host}:5173${path}`);
      await expect(page.getByRole('alert', { name: /sesión de soporte vyntia/i }))
        .toBeVisible({ timeout: 5_000 });
    }
  });
});
