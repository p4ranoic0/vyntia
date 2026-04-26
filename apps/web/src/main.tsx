import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Mocks deshabilitados - usando API real del backend
// if (process.env.NODE_ENV === 'development') {
//   import('./mocks');
// }

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
