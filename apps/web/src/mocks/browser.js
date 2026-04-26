import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

// Exportar el worker de MSW
export const worker = setupWorker(...handlers);