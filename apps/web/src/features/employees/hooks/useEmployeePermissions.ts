"use client";

import { useAuth } from "@/features/auth/hooks/useAuth";
import { useMemo } from "react";

/**
 * Hook personalizado para manejar permisos específicos de empleados
 * Diferencia entre administradores y empleados normales
 */
export function useEmployeePermissions() {
  const { user, hasRole, hasPermission, hasAnyRole, hasAnyPermission } =
    useAuth();

  const isAdmin = useMemo(() => {
    return hasAnyRole(["Super Administrador", "Administrador RRHH"]);
  }, [hasAnyRole]);

  const isRRHH = useMemo(() => {
    return hasAnyRole([
      "Super Administrador",
      "Administrador RRHH",
      "Analista RRHH",
    ]);
  }, [hasAnyRole]);

  const isSupervisor = useMemo(() => {
    return hasAnyRole(["Jefe de Area"]);
  }, [hasAnyRole]);

  // Verificar si el usuario es empleado normal
  const isEmployee = useMemo(() => {
    return !isAdmin && !isRRHH && !isSupervisor;
  }, [isAdmin, isRRHH, isSupervisor]);

  // Permisos específicos para empleados
  const permissions = useMemo(() => {
    return {
      // Permisos de lectura
      canViewAllEmployees: isAdmin || isRRHH,
      canViewOwnData: true, // Todos pueden ver sus propios datos
      canViewTeamData: isSupervisor || isAdmin || isRRHH,

      // Permisos de escritura
      canEditAllEmployees: isAdmin || isRRHH,
      canEditOwnData: hasPermission("editar_datos_propios") || isEmployee,
      canEditTeamData: isSupervisor || isAdmin || isRRHH,

      // Permisos de creación
      canCreateEmployee: isAdmin || isRRHH,

      // Permisos de eliminación
      canDeleteEmployee: isAdmin,

      // Permisos específicos por tipo de datos
      canEditPersonalData:
        isAdmin ||
        isRRHH ||
        (isEmployee && hasPermission("editar_datos_personales")),
      canEditLaborData: isAdmin || isRRHH,
      canEditAcademicData:
        isAdmin ||
        isRRHH ||
        (isEmployee && hasPermission("editar_datos_academicos")),
      canEditFamilyData:
        isAdmin ||
        isRRHH ||
        (isEmployee && hasPermission("editar_datos_familiares")),

      // Permisos de visualización de datos sensibles
      canViewSalaryData: isAdmin || isRRHH,
      canViewContractData: isAdmin || isRRHH || isSupervisor,
      canViewPersonalDocuments: isAdmin || isRRHH,

      // Permisos de administración
      canManagePermissions: isAdmin,
      canManageRoles: isAdmin,
      canViewReports: isAdmin || isRRHH || isSupervisor,
      canExportData: isAdmin || isRRHH,

      // Permisos de aprobación
      canApproveChanges: isAdmin || isRRHH,
      canApproveDocuments: isAdmin || isRRHH || isSupervisor,
    };
  }, [isAdmin, isRRHH, isSupervisor, isEmployee, hasPermission]);

  // Función para verificar si puede acceder a datos de un empleado específico
  const canAccessEmployeeData = (employeeId: number): boolean => {
    if (!user) return false;

    // Administradores y RRHH pueden acceder a todos los datos
    if (isAdmin || isRRHH) return true;

    // Los empleados solo pueden acceder a sus propios datos
    if (isEmployee && user.empleado?.id === employeeId) return true;

    // Los supervisores pueden acceder a datos de su equipo (esto requeriría lógica adicional)
    // Por ahora, permitimos que los supervisores accedan a todos los datos
    if (isSupervisor) return true;

    return false;
  };

  // Función para verificar si puede editar datos de un empleado específico
  const canEditEmployeeData = (
    employeeId: number,
    dataType: "personal" | "laboral" | "academico" | "familiar",
  ): boolean => {
    if (!user) return false;

    // Administradores y RRHH pueden editar todos los datos
    if (isAdmin || isRRHH) return true;

    // Los empleados solo pueden editar sus propios datos según permisos
    if (isEmployee && user.empleado?.id === employeeId) {
      switch (dataType) {
        case "personal":
          return permissions.canEditPersonalData;
        case "laboral":
          return permissions.canEditLaborData;
        case "academico":
          return permissions.canEditAcademicData;
        case "familiar":
          return permissions.canEditFamilyData;
        default:
          return false;
      }
    }

    return false;
  };

  // Función para obtener el modo de visualización (readonly o editable)
  const getViewMode = (
    employeeId: number,
    dataType: "personal" | "laboral" | "academico" | "familiar",
  ): "readonly" | "editable" => {
    return canEditEmployeeData(employeeId, dataType) ? "editable" : "readonly";
  };

  // Función para verificar si puede ver la lista completa de empleados
  const canViewEmployeeList = (): boolean => {
    return permissions.canViewAllEmployees;
  };

  // Función para obtener el filtro de empleados según permisos
  const getEmployeeFilter = () => {
    if (isAdmin || isRRHH) {
      return "all"; // Puede ver todos los empleados
    }

    if (isSupervisor) {
      return "team"; // Puede ver empleados de su equipo
    }

    return "own"; // Solo puede ver sus propios datos
  };

  return {
    // Estados de rol
    isAdmin,
    isRRHH,
    isSupervisor,
    isEmployee,

    // Permisos generales
    permissions,

    // Funciones de verificación
    canAccessEmployeeData,
    canEditEmployeeData,
    getViewMode,
    canViewEmployeeList,
    getEmployeeFilter,

    // Información del usuario actual
    currentEmployeeId: user?.empleado?.id || null,
    userRoles: user
      ? [
          isAdmin && "admin",
          isRRHH && "rrhh",
          isSupervisor && "supervisor",
          isEmployee && "employee",
        ].filter(Boolean)
      : [],
  };
}

export default useEmployeePermissions;
