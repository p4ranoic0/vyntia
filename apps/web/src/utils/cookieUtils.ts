/**
 * Utilidades para manejo de cookies en el navegador
 */

/**
 * Establece una cookie en el navegador
 */
export function setCookie(name: string, value: string, days: number = 7): void {
  const expires = new Date()
  expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000))
  
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`
}

/**
 * Obtiene el valor de una cookie por su nombre
 */
export function getCookie(name: string): string | null {
  const nameEQ = name + "="
  const ca = document.cookie.split(';')
  
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i]
    while (c.charAt(0) === ' ') c = c.substring(1, c.length)
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length)
  }
  
  return null
}

/**
 * Elimina una cookie por su nombre
 */
export function deleteCookie(name: string): void {
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`
}

/**
 * Verifica si una cookie existe
 */
export function hasCookie(name: string): boolean {
  return getCookie(name) !== null
}

/**
 * Verifica si las cookies de autenticación están presentes
 */
export function hasAuthCookies(): boolean {
  return hasCookie('access_token') && hasCookie('refresh_token')
}

/**
 * Limpia todas las cookies de autenticación
 */
export function clearAuthCookies(): void {
  deleteCookie('access_token')
  deleteCookie('refresh_token')
}