import { useState, useEffect } from 'react'

/**
 * Hook personalizado para implementar debouncing
 * @param value - El valor a debounce
 * @param delay - El retraso en milisegundos
 * @returns El valor debounced
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    // Crear un timer que actualice el valor debounced después del delay
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    // Limpiar el timeout si el valor cambia antes de que se complete el delay
    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}