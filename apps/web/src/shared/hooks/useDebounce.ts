/**
 * useDebounce Hook - SHARED
 *
 * Hook que debouncea un valor.
 *
 * Uso:
 * const [search, setSearch] = useState('')
 * const debouncedSearch = useDebounce(search, 500)
 *
 * useEffect(() => {
 *   // Solo se ejecuta 500ms después de que search cambie
 *   searchEmpleados(debouncedSearch)
 * }, [debouncedSearch])
 */

import { useEffect, useState } from "react";

export function useDebounce<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}
