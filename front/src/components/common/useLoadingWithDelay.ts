import { useState, useCallback, useEffect } from 'react'

/**
 * Hook personalizado para manejar estados de loading con retraso
 * @param initialState Estado inicial del loading (default: false)
 * @param delayMs Tiempo de retraso en milisegundos (default: 500ms)
 * @returns Objeto con el estado de loading y funciones para controlarlo
 */
export function useLoadingWithDelay(initialState = false, delayMs = 500) {
  const [isLoading, setIsLoading] = useState(initialState)
  const [shouldLoad, setShouldLoad] = useState(initialState)
  
  // Efecto para manejar el retraso en la carga
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>
    
    if (shouldLoad) {
      // Iniciar el loading después del retraso
      timer = setTimeout(() => {
        setIsLoading(true)
      }, delayMs)
    } else {
      // Detener el loading inmediatamente
      setIsLoading(false)
    }
    
    return () => {
      clearTimeout(timer)
    }
  }, [shouldLoad, delayMs])
  
  const startLoading = useCallback(() => setShouldLoad(true), [])
  const stopLoading = useCallback(() => setShouldLoad(false), [])
  const toggleLoading = useCallback(() => setShouldLoad(prev => !prev), [])
  
  return {
    isLoading,
    startLoading,
    stopLoading,
    toggleLoading,
    setIsLoading: setShouldLoad
  }
}