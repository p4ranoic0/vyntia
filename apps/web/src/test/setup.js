import { expect, afterEach, beforeAll, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';
import { server } from '../mocks/server';

// Extender los matchers de Vitest con los de Testing Library
expect.extend(matchers);

// Configurar MSW
beforeAll(() => {
  // Iniciar el servidor de MSW antes de todas las pruebas
  server.listen({ onUnhandledRequest: 'error' });
});

afterEach(() => {
  // Limpiar después de cada prueba
  cleanup();
  // Resetear los handlers de MSW para que no afecten a otras pruebas
  server.resetHandlers();
});

afterAll(() => {
  // Cerrar el servidor de MSW después de todas las pruebas
  server.close();
});

// Mock para localStorage
class LocalStorageMock {
  constructor() {
    this.store = {};
  }

  clear() {
    this.store = {};
  }

  getItem(key) {
    return this.store[key] || null;
  }

  setItem(key, value) {
    this.store[key] = String(value);
  }

  removeItem(key) {
    delete this.store[key];
  }
}

// Configurar localStorage mock global
global.localStorage = new LocalStorageMock();

// Mock para console.log y otros métodos de console para evitar ruido en las pruebas
global.console = {
  ...console,
  log: vi.fn(),
  error: vi.fn(),
  warn: vi.fn(),
  info: vi.fn(),
};