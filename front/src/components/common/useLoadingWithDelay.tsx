import { useState, useCallback, useRef, useEffect } from 'react'

/**
 * Hook para gestionar estados de carga con un retraso configurable
 * Útil para evitar parpadeos en cargas rápidas o mostrar indicadores solo después de cierto tiempo
 * 
 * @param {number} delayMs - Tiempo de retraso en milisegundos antes de mostrar el estado de carga
 * @returns {Object} Objeto con el estado de carga y funciones para controlarlo
 */
export function useLoadingWithDelay(delayMs = 1000) {
  const [isLoading, setIsLoading] = useState(false)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  
  // Limpiar el temporizador al desmontar el componente
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
      }
    }
  }, [])

  const startLoading = useCallback(() => {
    // Si ya hay un temporizador activo, lo limpiamos
    if (timerRef.current) {
      clearTimeout(timerRef.current)
    }
    
    // Configuramos un nuevo temporizador para activar el estado de carga después del retraso
    timerRef.current = setTimeout(() => {
      setIsLoading(true)
    }, delayMs)
  }, [delayMs])

  const stopLoading = useCallback(() => {
    // Limpiamos el temporizador si existe
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
    
    // Desactivamos el estado de carga
    setIsLoading(false)
  }, [])

  return {
    isLoading,
    startLoading,
    stopLoading
  }
}