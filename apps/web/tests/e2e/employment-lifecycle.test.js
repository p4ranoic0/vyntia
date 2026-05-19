// @ts-check
/**
 * Full employment lifecycle E2E (Module 03 happy path) — ADR-B.5 release gate.
 *
 * Drives the seeded tenant through hire -> onboarding -> desplazamiento -> cese
 * end-to-end against the real backend + frontend dev servers. SKIPPED by
 * default because the test:
 *   - Requires the `seed_lifecycle_e2e` management command to have run
 *     against a local dev DB (provisions tenant + admin + minimal catalog).
 *   - Requires `apps/api` running on :8000 and `apps/web` running on :5173.
 *   - Mutates DB state — should not run in shared environments.
 *
 * To run locally:
 *   cd apps/api && python manage.py seed_lifecycle_e2e --settings=vyntia.settings.development
 *   cd apps/web && RUN_LIFECYCLE_E2E=1 npx playwright test tests/e2e/employment-lifecycle.test.js
 *
 * Trace + screenshots land in apps/web/playwright-report/ on failure.
 *
 * Spec: docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md § 8
 * ADR: .planning/audit-B/ADRS.md § ADR-B.5
 * Backlog: .planning/audit-B/BACKLOG.md item #132
 */

import { expect, test } from '@playwright/test';

const RUN = process.env.RUN_LIFECYCLE_E2E === '1';

const ADMIN = {
  username: 'admin_lifecycle',
  password: 'LifecyclePass123!',
};

// Mirror of seed_lifecycle_e2e SEED_OUTPUT shape. Hardcoded to keep the test
// independent of stdout parsing; the seed command is the source of truth.
const SEED = {
  positionCode: 'DEV-SR-01',
  departmentSiglas: 'TI',
};

const EMPLOYEE = {
  nombres: 'Lifecycle',
  apellidoPaterno: 'TestApPat',
  apellidoMaterno: 'TestApMat',
  dni: '99999999',
  email: `lifecycle.empleado.${Date.now()}@lifecycle.test`,
};

test.describe('Employment Lifecycle (Module 03 full path)', () => {
  test.skip(
    !RUN,
    'Heavy E2E; requires seed_lifecycle_e2e + running dev servers. Set RUN_LIFECYCLE_E2E=1 to enable.',
  );

  test.setTimeout(180_000);

  test('admin drives an empleado through hire -> onboarding -> desplazamiento -> cese', async ({ page }) => {
    // ───────────────────────── Step 1: Login ─────────────────────────
    await page.goto('/login');
    await page.getByLabel(/usuario|username/i).fill(ADMIN.username);
    await page.getByLabel(/contraseña|password/i).fill(ADMIN.password);
    await Promise.all([
      page.waitForResponse((r) => r.url().includes('/api/v1/auth/login') && r.status() === 200),
      page.getByRole('button', { name: /ingresar|iniciar sesi[oó]n|login/i }).click(),
    ]);
    await expect(page).toHaveURL(/\/(dashboard|inicio|home|$)/);

    // ───────────────────────── Step 2: Create empleado ───────────────
    await page.goto('/empleados');
    await page.getByRole('button', { name: /nuevo empleado|crear empleado|nuevo/i }).first().click();

    await page.getByLabel(/nombres/i).first().fill(EMPLOYEE.nombres);
    await page.getByLabel(/apellido paterno/i).fill(EMPLOYEE.apellidoPaterno);
    await page.getByLabel(/apellido materno/i).fill(EMPLOYEE.apellidoMaterno);
    await page.getByLabel(/dni|documento/i).first().fill(EMPLOYEE.dni);
    const emailField = page.getByLabel(/email|correo/i).first();
    if (await emailField.count()) await emailField.fill(EMPLOYEE.email);

    const createEmployeeResponse = page.waitForResponse(
      (r) => r.url().includes('/api/v1/employees/') && r.request().method() === 'POST' && r.status() < 400,
    );
    await page.getByRole('button', { name: /guardar|crear|registrar/i }).first().click();
    const empResp = await createEmployeeResponse;
    const empData = await empResp.json();
    const employeeId = empData?.id ?? empData?.data?.id ?? empData?.empleado_id;
    expect(employeeId, 'employee id returned by API').toBeTruthy();

    // ───────────────────────── Step 3: Issue contract ────────────────
    await page.goto('/contratos');
    await page.getByRole('button', { name: /nuevo contrato|crear contrato/i }).first().click();

    // Pick the empleado we just created
    const empleadoCombo = page.getByLabel(/empleado/i).first();
    await empleadoCombo.click();
    await page.getByRole('option', { name: new RegExp(EMPLOYEE.nombres, 'i') }).first().click();

    // Tipo INDEFINIDO + position
    const tipoCombo = page.getByLabel(/tipo de contrato|tipo/i).first();
    await tipoCombo.click();
    await page.getByRole('option', { name: /indefinido/i }).first().click();

    // Fecha inicio = hoy
    const today = new Date().toISOString().slice(0, 10);
    const fechaInicio = page.getByLabel(/fecha inicio|fecha de inicio/i).first();
    if (await fechaInicio.count()) await fechaInicio.fill(today);

    const createContractResponse = page.waitForResponse(
      (r) => r.url().includes('/api/v1/contracts/') && r.request().method() === 'POST' && r.status() < 400,
    );
    await page.getByRole('button', { name: /guardar|crear|registrar/i }).first().click();
    await createContractResponse;

    // ───────────────────────── Step 4: Onboarding kick-off ──────────
    await page.goto('/onboarding/admin');
    await page.getByRole('button', { name: /nuevo proceso|iniciar onboarding|crear/i }).first().click();
    const empleadoOnbCombo = page.getByLabel(/empleado/i).first();
    await empleadoOnbCombo.click();
    await page.getByRole('option', { name: new RegExp(EMPLOYEE.nombres, 'i') }).first().click();
    const startOnboardingResponse = page.waitForResponse(
      (r) => r.url().includes('/api/v1/onboarding/') && r.request().method() === 'POST' && r.status() < 400,
    );
    await page.getByRole('button', { name: /iniciar|guardar|crear/i }).first().click();
    await startOnboardingResponse;

    // ───────────────────────── Step 5: Desplazamiento (rotación) ────
    await page.goto('/organizacion/desplazamientos');
    await page.getByRole('button', { name: /nuevo desplazamiento|crear|registrar/i }).first().click();
    const empleadoDispCombo = page.getByLabel(/empleado/i).first();
    await empleadoDispCombo.click();
    await page.getByRole('option', { name: new RegExp(EMPLOYEE.nombres, 'i') }).first().click();
    const tipoDispCombo = page.getByLabel(/tipo|modalidad/i).first();
    await tipoDispCombo.click();
    await page.getByRole('option', { name: /rotaci[oó]n/i }).first().click();
    const createDispResponse = page.waitForResponse(
      (r) => r.url().includes('/api/v1/organization/displacements/') && r.request().method() === 'POST' && r.status() < 400,
    );
    await page.getByRole('button', { name: /guardar|registrar|crear/i }).first().click();
    await createDispResponse;

    // ───────────────────────── Step 6: Desvinculación + liquidación ─
    await page.goto('/contratos/desvinculacion');
    await page.getByRole('button', { name: /iniciar cese|nuevo cese|crear/i }).first().click();
    const empleadoCeseCombo = page.getByLabel(/empleado|contrato/i).first();
    await empleadoCeseCombo.click();
    await page.getByRole('option', { name: new RegExp(EMPLOYEE.nombres, 'i') }).first().click();
    const causalCombo = page.getByLabel(/causal/i).first();
    await causalCombo.click();
    await page.getByRole('option', { name: /renuncia/i }).first().click();
    const initiateTermResponse = page.waitForResponse(
      (r) => r.url().includes('/api/v1/terminations/') && r.request().method() === 'POST' && r.status() < 400,
    );
    await page.getByRole('button', { name: /iniciar|guardar|crear/i }).first().click();
    await initiateTermResponse;

    // Compute settlement
    const computeResponse = page.waitForResponse(
      (r) => r.url().includes('/compute') && r.request().method() === 'POST' && r.status() < 400,
    );
    await page.getByRole('button', { name: /calcular liquidaci[oó]n|compute/i }).first().click();
    await computeResponse;

    // Mark paid + liquidate (causal renuncia -> 3 components: CTS + vac_truncas + grat_trunca, no indemnización)
    const liquidateResponse = page.waitForResponse(
      (r) => r.url().includes('/liquidate') && r.request().method() === 'POST' && r.status() < 400,
    );
    await page.getByRole('button', { name: /liquidar|marcar pagado|liquidate/i }).first().click();
    await liquidateResponse;

    // ───────────────────────── Step 7: Final assertions ──────────────
    await page.goto('/empleados');
    const empleadoCard = page.getByText(new RegExp(EMPLOYEE.nombres, 'i')).first();
    await expect(empleadoCard).toBeVisible();
    // Status badges may render as "Cesado" / "Terminado" / "Inactivo" depending on copy
    await expect(page.getByText(/cesado|terminado|inactivo|liquidad/i).first()).toBeVisible();
  });
});
