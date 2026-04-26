/// <reference types="cypress" />

describe('Autenticación y Permisos', () => {
  beforeEach(() => {
    // Interceptar las llamadas a la API para analizar las respuestas
    cy.intercept('POST', '/api/v1/auth/login/').as('loginRequest');
    cy.intercept('GET', '/api/v1/auth/menu/').as('menuRequest');
    cy.intercept('GET', '/api/v1/auth/menu-structure/').as('menuStructureRequest');
    cy.intercept('GET', '/api/v1/auth/permissions-structure/').as('permissionsStructureRequest');
    
    // Capturar logs de consola
    cy.captureConsoleLogs();
  });

  it('Debería iniciar sesión correctamente y verificar permisos', () => {
    // Login automático
    cy.login('admin', 'admin');
    
    // Verificar que la petición de login fue exitosa
    cy.wait('@loginRequest').its('response.statusCode').should('eq', 200);
    
    // Verificar que se cargó el menú correctamente
    cy.wait('@menuRequest').its('response.statusCode').should('eq', 200);
    
    // Verificar que se cargó la estructura del menú
    cy.wait('@menuStructureRequest').then((interception) => {
      // Verificar el código de estado
      expect(interception.response.statusCode).to.eq(200);
      
      // Verificar que la respuesta contiene la estructura del menú
      expect(interception.response.body).to.have.property('menu_structure');
      
      // Imprimir la estructura del menú en la consola
      cy.log('Estructura del menú:', interception.response.body.menu_structure);
    });
    
    // Verificar que se cargó la estructura de permisos
    cy.wait('@permissionsStructureRequest').then((interception) => {
      // Verificar el código de estado
      expect(interception.response.statusCode).to.eq(200);
      
      // Verificar que la respuesta contiene la estructura de permisos
      expect(interception.response.body).to.have.property('permissions_structure');
      
      // Imprimir la estructura de permisos en la consola
      cy.log('Estructura de permisos:', interception.response.body.permissions_structure);
    });
    
    // Abrir el panel de depuración
    cy.get('button').contains('Debug').click();
    
    // Verificar que el panel de depuración muestra la información correcta
    cy.get('[data-testid="debug-panel"]').should('be.visible');
    cy.get('[data-testid="user-permissions-debug"]').should('be.visible');
    cy.get('[data-testid="menu-permissions-debug"]').should('be.visible');
    
    // Verificar permisos de usuario
    cy.checkUserPermissions().then((permissions) => {
      if (permissions) {
        cy.log('Permisos verificados correctamente');
      }
    });
  });
});