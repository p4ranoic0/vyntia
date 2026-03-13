import { useState, useCallback } from 'react'

/**
 * Hook personalizado para manejar estados de loading
 * @param initialState Estado inicial del loading (default: false)
 * @returns Objeto con el estado de loading y funciones para controlarlo
 */
export function useLoading(initialState = false) {
  const [isLoading, setIsLoading] = useState(initialState)
  
  const startLoading = useCallback(() => setIsLoading(true), [])
  const stopLoading = useCallback(() => setIsLoading(false), [])
  const toggleLoading = useCallback(() => setIsLoading(prev => !prev), [])
  
  return {
    isLoading,
    startLoading,
    stopLoading,
    toggleLoading,
    setIsLoading
  }
}