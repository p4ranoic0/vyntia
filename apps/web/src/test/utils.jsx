import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Crear un cliente de React Query para pruebas
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0,
    },
  },
  logger: {
    log: console.log,
    warn: console.warn,
    error: () => {},
  },
});

// Renderizar componentes con todos los proveedores necesarios
export function renderWithProviders(ui, options = {}) {
  const queryClient = createTestQueryClient();
  
  function Wrapper({ children }) {
    return (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryClientProvider>
    );
  }
  
  return render(ui, { wrapper: Wrapper, ...options });
}

// Simular el localStorage para pruebas
export function setupLocalStorage(initialState = {}) {
  // Guardar la implementación original
  const originalLocalStorage = global.localStorage;
  
  // Configurar el estado inicial
  Object.keys(initialState).forEach(key => {
    localStorage.setItem(key, JSON.stringify(initialState[key]));
  });
  
  // Función para restaurar el localStorage original
  return () => {
    global.localStorage = originalLocalStorage;
  };
}

// Simular un usuario autenticado
export function setupAuthenticatedUser(userData = {}) {
  const defaultUser = {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    first_name: 'Admin',
    last_name: 'User',
    is_active: true,
    is_staff: true,
    is_superuser: true,
    roles: ['admin'],
    permissions: ['view_user', 'add_user', 'change_user', 'delete_user'],
  };
  
  const user = { ...defaultUser, ...userData };
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNTE2MjM5MDIyfQ.L8i6g3PfcHlioHCCPURC9pmXT7gdJpx3kOoyAfNUwCc';
  
  localStorage.setItem('auth_token', token);
  localStorage.setItem('user', JSON.stringify(user));
  
  return { user, token };
}

// Limpiar el localStorage después de las pruebas
export function cleanupAuth() {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
  localStorage.removeItem('menu');
  localStorage.removeItem('permissions');
}