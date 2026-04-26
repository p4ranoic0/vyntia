// Componentes de loading y skeletons
export { LoadingSpinner } from './LoadingSpinner'
export { LoadingPage, LoadingSection, LoadingButton } from './LoadingPage'
export { 
  Skeleton,
  UserCardSkeleton,
  TableSkeleton,
  FormSkeleton,
  StatsSkeleton,
  ListSkeleton,
  DashboardSkeleton,
  SidebarSkeleton
} from './LoadingSkeleton'

// Otros componentes comunes
export { DataTable } from './DataTable'
export { ProfileImage } from './ProfileImage'

// Tipos y utilidades para loading
export type LoadingVariant = 'default' | 'dots' | 'pulse' | 'bounce' | 'rotate'
export type LoadingSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
export type LoadingColor = 'primary' | 'secondary' | 'accent' | 'muted'

/**
 * Hook personalizado para manejar estados de loading
 */
import { useState, useCallback } from 'react'

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

/**
 * Hook para simular loading con delay
 */
export function useLoadingWithDelay(delay = 1000) {
  const { isLoading, startLoading, stopLoading } = useLoading()
  
  const simulateLoading = useCallback(async () => {
    startLoading()
    await new Promise(resolve => setTimeout(resolve, delay))
    stopLoading()
  }, [delay, startLoading, stopLoading])
  
  return {
    isLoading,
    simulateLoading,
    startLoading,
    stopLoading
  }
}