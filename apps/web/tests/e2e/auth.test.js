import { test, expect } from '@playwright/test';

test.describe('Autenticación y Permisos', () => {
  test.beforeEach(async ({ page }) => {
    // Interceptar las llamadas a la API para analizar las respuestas
    await page.route('**/api/v1/auth/login/', async (route) => {
      const response = await route.fetch();
      const json = await response.json();
      console.log('Login response:', json);
      await route.fulfill({ response });
    });
    
    await page.route('**/api/v1/auth/menu/', async (route) => {
      const response = await route.fetch();
      const json = await response.json();
      console.log('Menu response:', json);
      await route.fulfill({ response });
    });
    
    await page.route('**/api/v1/auth/menu-structure/', async (route) => {
      const response = await route.fetch();
      const json = await response.json();
      console.log('Menu structure response:', json);
      await route.fulfill({ response });
    });
    
    await page.route('**/api/v1/auth/permissions-structure/', async (route) => {
      const response = await route.fetch();
      const json = await response.json();
      console.log('Permissions structure response:', json);
      await route.fulfill({ response });
    });
  });

  test('Debería iniciar sesión correctamente y verificar permisos', async ({ page }) => {
    // Navegar a la página de inicio
    await page.goto('/');
    
    // Realizar login
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin');
    await page.click('button[type="submit"]');
    
    // Esperar a que se complete el login y se redirija al dashboard
    await page.waitForURL('**/dashboard');
    
    // Verificar que estamos en el dashboard
    expect(page.url()).toContain('/dashboard');
    
    // Verificar que el token se ha guardado en localStorage
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
    
    // Abrir el panel de depuración
    await page.getByText('Debug').click();
    
    // Verificar que el panel de depuración está visible
    await expect(page.locator('[data-testid="debug-panel"]')).toBeVisible();
    
    // Verificar que los componentes de depuración están visibles
    await expect(page.locator('[data-testid="user-permissions-debug"]')).toBeVisible();
    await expect(page.locator('[data-testid="menu-permissions-debug"]')).toBeVisible();
    
    // Capturar y verificar permisos de usuario
    const userPermissions = await page.evaluate(() => {
      const permissions = localStorage.getItem('userPermissions');
      return permissions ? JSON.parse(permissions) : null;
    });
    
    console.log('User permissions:', userPermissions);
    expect(userPermissions).toBeTruthy();
    
    // Tomar una captura de pantalla del panel de depuración
    await page.screenshot({ path: 'debug-panel.png', fullPage: false });
  });
});