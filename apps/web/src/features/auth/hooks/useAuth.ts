import { useContext } from 'react'
import { AuthContext } from '@/features/auth/context/AuthContextInstance'

/**
 * Hook personalizado para acceder al contexto de autenticación
 * @returns {AuthContextType} El contexto de autenticación
 * @throws {Error} Si se usa fuera del AuthProvider
 */
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}