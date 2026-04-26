/**
 * Utilidad para realizar login automático durante el desarrollo y pruebas
 * 
 * Este script permite realizar un login automático en la aplicación,
 * útil para desarrollo y pruebas manuales.
 */

import axios from 'axios';
import Cookies from 'js-cookie';

/**
 * Realiza un login automático con las credenciales proporcionadas
 * @param {string} username - Nombre de usuario (por defecto 'admin')
 * @param {string} password - Contraseña (por defecto 'admin')
 * @param {string} apiUrl - URL base de la API (por defecto 'http://localhost:8000')
 * @returns {Promise<Object>} - Objeto con el resultado del login
 */
export const autoLogin = async (username = 'admin', password = 'admin', apiUrl = 'http://localhost:8000') => {
  try {
    // Realizar la petición de login
    const response = await axios.post(`${apiUrl}/api/v1/auth/login/`, {
      username,
      password,
    });

    // Extraer el token y otros datos de la respuesta
    const payload = response.data?.data || response.data;
    const { access, refresh, user } = payload;

    // Guardar tokens y user_data en localStorage y cookies
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user_data', JSON.stringify({
      user,
      roles: payload.roles || [],
      permissions: payload.permissions || [],
      modules: payload.modules || [],
    }));
    Cookies.set('access_token', access, { expires: 1 });
    Cookies.set('refresh_token', refresh, { expires: 1 });

    // Obtener el menú del usuario
    await fetchUserMenu(access, apiUrl);

    // Obtener la estructura del menú y permisos (para depuración)
    await fetchMenuStructure(access, apiUrl);
    await fetchPermissionsStructure(access, apiUrl);

    console.log('Login automático exitoso:', user.username);
    return { success: true, user, token: access };
  } catch (error) {
    console.error('Error en login automático:', error.response?.data || error.message);
    return { success: false, error: error.response?.data || error.message };
  }
};

/**
 * Obtiene el menú del usuario autenticado
 * @param {string} token - Token de autenticación
 * @param {string} apiUrl - URL base de la API
 * @returns {Promise<Object>} - Objeto con el menú del usuario
 */
export const fetchUserMenu = async (token, apiUrl = 'http://localhost:8000') => {
  try {
    const response = await axios.get(`${apiUrl}/api/v1/auth/menu/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    // Guardar el menú en localStorage
    localStorage.setItem('userMenu', JSON.stringify(response.data));
    console.log('Menú del usuario cargado correctamente');
    return response.data;
  } catch (error) {
    console.error('Error al obtener el menú del usuario:', error.response?.data || error.message);
    return null;
  }
};

/**
 * Obtiene la estructura completa del menú (para depuración)
 * @param {string} token - Token de autenticación
 * @param {string} apiUrl - URL base de la API
 * @returns {Promise<Object>} - Objeto con la estructura del menú
 */
export const fetchMenuStructure = async (token, apiUrl = 'http://localhost:8000') => {
  try {
    const response = await axios.get(`${apiUrl}/api/v1/auth/menu-structure/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    // Guardar la estructura del menú en localStorage
    localStorage.setItem('menuStructure', JSON.stringify(response.data));
    console.log('Estructura del menú cargada correctamente');
    return response.data;
  } catch (error) {
    console.error('Error al obtener la estructura del menú:', error.response?.data || error.message);
    return null;
  }
};

/**
 * Obtiene la estructura completa de permisos (para depuración)
 * @param {string} token - Token de autenticación
 * @param {string} apiUrl - URL base de la API
 * @returns {Promise<Object>} - Objeto con la estructura de permisos
 */
export const fetchPermissionsStructure = async (token, apiUrl = 'http://localhost:8000') => {
  try {
    const response = await axios.get(`${apiUrl}/api/v1/auth/permissions-structure/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    // Guardar la estructura de permisos en localStorage
    localStorage.setItem('permissionsStructure', JSON.stringify(response.data));
    console.log('Estructura de permisos cargada correctamente');
    return response.data;
  } catch (error) {
    console.error('Error al obtener la estructura de permisos:', error.response?.data || error.message);
    return null;
  }
};

/**
 * Verifica si hay un usuario autenticado
 * @returns {boolean} - true si hay un usuario autenticado, false en caso contrario
 */
export const isAuthenticated = () => {
  const token = localStorage.getItem('access_token') || Cookies.get('access_token');
  return !!token;
};

/**
 * Cierra la sesión del usuario
 */
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_data');
  localStorage.removeItem('userMenu');
  localStorage.removeItem('menuStructure');
  localStorage.removeItem('permissionsStructure');
  Cookies.remove('access_token');
  Cookies.remove('refresh_token');
  console.log('Sesión cerrada correctamente');
};

// Exportar todas las funciones
export default {
  autoLogin,
  fetchUserMenu,
  fetchMenuStructure,
  fetchPermissionsStructure,
  isAuthenticated,
  logout,
};
