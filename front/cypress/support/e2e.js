// ***********************************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands';

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Configuración para capturar logs de consola
Cypress.on('window:before:load', (win) => {
  // Capturar logs de consola
  const originalConsoleLog = win.console.log;
  const originalConsoleError = win.console.error;
  const originalConsoleWarn = win.console.warn;

  win.console.log = (...args) => {
    // Enviar logs al panel de Cypress
    Cypress.log({
      name: 'console.log',
      message: args.join(' '),
    });
    return originalConsoleLog.apply(win.console, args);
  };

  win.console.error = (...args) => {
    Cypress.log({
      name: 'console.error',
      message: args.join(' '),
    });
    return originalConsoleError.apply(win.console, args);
  };

  win.console.warn = (...args) => {
    Cypress.log({
      name: 'console.warn',
      message: args.join(' '),
    });
    return originalConsoleWarn.apply(win.console, args);
  };
});