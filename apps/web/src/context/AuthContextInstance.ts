import { createContext } from 'react'
import { AuthContextType } from './AuthContextType'

/**
 * Contexto de autenticación
 */
export const AuthContext = createContext<AuthContextType | undefined>(undefined)