import { useState, useCallback } from 'react'

/**
 * Hook para gestionar estados de carga
 * Proporciona funciones para iniciar y detener la carga, así como el estado actual
 * 
 * @returns {Object} Objeto con el estado de carga y funciones para controlarlo
 */
export function useLoading() {
  const [isLoading, setIsLoading] = useState(false)

  const startLoading = useCallback(() => {
    setIsLoading(true)
  }, [])

  const stopLoading = useCallback(() => {
    setIsLoading(false)
  }, [])

  return {
    isLoading,
    startLoading,
    stopLoading
  }
}