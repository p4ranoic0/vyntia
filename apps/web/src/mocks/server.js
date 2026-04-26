import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Configurar el servidor de MSW para pruebas
export const server = setupServer(...handlers);