/**
 * Utilidades para el manejo de errores en la aplicación
 */

/**
 * Extrae el mensaje de error de una respuesta de error de axios
 * @param error - El objeto de error de axios
 * @param defaultMessage - Mensaje por defecto si no se puede extraer el error
 * @returns El mensaje de error formateado
 */
export function getErrorMessage(error: any, defaultMessage: string = 'Ha ocurrido un error inesperado'): string {
  // Si el error tiene una respuesta del servidor
  if (error.response?.data) {
    const data = error.response.data
    
    // Priorizar el campo 'errors' que contiene el mensaje específico
    if (data.errors) {
      // Si errors es un string, devolverlo directamente
      if (typeof data.errors === 'string') {
        return data.errors
      }
      
      // Si errors es un objeto con campos específicos
      if (typeof data.errors === 'object') {
        // Obtener el primer error de validación
        const firstErrorKey = Object.keys(data.errors)[0]
        if (firstErrorKey && data.errors[firstErrorKey]) {
          const errorValue = data.errors[firstErrorKey]
          return Array.isArray(errorValue) ? errorValue[0] : errorValue
        }
      }
    }
    
    // Si no hay errors, usar el campo 'message'
    if (data.message) {
      return data.message
    }
    
    // Si hay un detail (común en DRF)
    if (data.detail) {
      return data.detail
    }
  }
  
  // Si el error tiene un mensaje directo
  if (error.message) {
    return error.message
  }
  
  // Mensaje por defecto
  return defaultMessage
}

/**
 * Determina si un error es de autenticación (401)
 * @param error - El objeto de error
 * @returns true si es un error de autenticación
 */
export function isAuthError(error: any): boolean {
  return error.response?.status === 401
}

/**
 * Determina si un error es de autorización (403)
 * @param error - El objeto de error
 * @returns true si es un error de autorización
 */
export function isAuthorizationError(error: any): boolean {
  return error.response?.status === 403
}

/**
 * Determina si un error es de validación (400 o 422)
 * @param error - El objeto de error
 * @returns true si es un error de validación
 */
export function isValidationError(error: any): boolean {
  return error.response?.status === 400 || error.response?.status === 422
}

/**
 * Determina si un error es del servidor (5xx)
 * @param error - El objeto de error
 * @returns true si es un error del servidor
 */
export function isServerError(error: any): boolean {
  const status = error.response?.status
  return status >= 500 && status < 600
}