import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Genera las iniciales a partir de nombres y apellidos
 * @param nombres - Nombres del usuario
 * @param apellidos - Apellidos del usuario (opcional)
 * @returns Las iniciales en mayúsculas
 */
export function getInitials(nombres: string, apellidos?: string): string {
  const firstInitial = nombres?.charAt(0)?.toUpperCase() || ''
  const lastInitial = apellidos?.charAt(0)?.toUpperCase() || ''
  return `${firstInitial}${lastInitial}`
}
