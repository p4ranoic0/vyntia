/**
 * React Query Configuration
 *
 * Centraliza la configuración de React Query y proporciona configuraciones
 * predeterminadas óptimas para la aplicación.
 */

import { DefaultOptions, QueryClient } from "@tanstack/react-query";

const queryConfig: DefaultOptions = {
  queries: {
    // No reintentar automáticamente en error (evita UX de reintento automático)
    retry: 1,
    // Cache datos por 5 minutos
    staleTime: 5 * 60 * 1000,
    // Usar cache si lo tenemos, actualizar en background
    gcTime: 10 * 60 * 1000,
  },
  mutations: {
    // No reintentar automáticamente mutations
    retry: 0,
  },
};

export const queryClient = new QueryClient({
  defaultOptions: queryConfig,
});
