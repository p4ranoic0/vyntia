// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// -- This is a parent command --
Cypress.Commands.add('login', (username = 'admin', password = 'admin') => {
  cy.visit('/');
  cy.get('input[name="username"]').type(username);
  cy.get('input[name="password"]').type(password);
  cy.get('button[type="submit"]').click();
  
  // Esperar a que se complete el login y se redirija al dashboard
  cy.url().should('include', '/dashboard');
  
  // Guardar el token en localStorage para futuras pruebas
  cy.window().then((win) => {
    const token = win.localStorage.getItem('token');
    if (token) {
      cy.log(`Login exitoso, token obtenido: ${token.substring(0, 15)}...`);
    }
  });
});

// Comando para verificar permisos de usuario
Cypress.Commands.add('checkUserPermissions', () => {
  cy.window().then((win) => {
    // Acceder a la consola del navegador para verificar permisos
    const userPermissions = win.localStorage.getItem('userPermissions');
    if (userPermissions) {
      cy.log(`Permisos del usuario: ${userPermissions}`);
      return JSON.parse(userPermissions);
    }
    return null;
  });
});

// Comando para abrir el panel de depuración
Cypress.Commands.add('openDebugPanel', () => {
  cy.get('button').contains('Debug').click();
  cy.get('[data-testid="debug-panel"]').should('be.visible');
});

// Comando para capturar logs de consola
Cypress.Commands.add('captureConsoleLogs', () => {
  cy.window().then((win) => {
    cy.spy(win.console, 'log').as('consoleLog');
    cy.spy(win.console, 'error').as('consoleError');
    cy.spy(win.console, 'warn').as('consoleWarn');
  });
});