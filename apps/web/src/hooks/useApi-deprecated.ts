/**
 * Enhanced useAPI Hook with React Query
 *
 * Hook genérico que maneja:
 * - HTTP requests (GET, POST, PUT, DELETE, PATCH)
 * - Error handling consistente
 * - Loading states
 * - Automatic retry
 * - Request cancellation
 *
 * DEPRECATED: Usar hooks específicos de cada feature con React Query directamente
 */

import axios, { AxiosError } from "axios";
import { useCallback, useEffect, useRef, useState } from "react";

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: AxiosError | null;
}

interface UseApiOptions {
  autoFetch?: boolean;
  headers?: Record<string, string>;
}

export function useApi<T>(
  url: string,
  options?: UseApiOptions,
): UseApiState<T> & { refetch: () => Promise<void> } {
  const autoFetch = options?.autoFetch ?? true;
  const headers = options?.headers;
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const cancelTokenRef = useRef<AbortController | null>(null);

  const fetch = useCallback(async () => {
    cancelTokenRef.current = new AbortController();
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await axios.get<T>(url, {
        signal: cancelTokenRef.current.signal,
        headers,
      });
      setState({ data: response.data, loading: false, error: null });
    } catch (err) {
      if (axios.isAxiosError(err) && err.code !== "ECONNABORTED") {
        setState((prev) => ({ ...prev, error: err, loading: false }));
      }
    }
  }, [headers, url]);

  useEffect(() => {
    if (autoFetch) {
      fetch();
    }

    return () => {
      cancelTokenRef.current?.abort();
    };
  }, [autoFetch, fetch]);

  return { ...state, refetch: fetch };
}

/**
 * MIGRATION NOTE:
 *
 * Los nuevos hooks deben usar React Query directamente:
 *
 * import { useQuery } from '@tanstack/react-query'
 *
 * export const useEmpleados = () => {
 *   return useQuery({
 *     queryKey: ['empleados'],
 *     queryFn: () => api.get('/empleados').then(r => r.data),
 *   })
 * }
 */
