import { apiClient } from "@/lib/api";
import { getErrorMessage } from "@/lib/errorUtils";
import {
  extractCollection,
  normalizeEmployee,
} from "@/services/normalizers/rrhhNormalizers";

// Interfaces para empleados
export interface Employee {
  id: number;
  nombres: string;
  ape_paterno: string;
  ape_materno: string;
  dni: string;
  telefono?: string;
  email?: string;
  fecha_nacimiento?: string;
  direccion?: string;
  estado_civil?: string;
  genero?: string;
  area: {
    id: number;
    organo: string;
    siglas: string;
  };
  cargo?: {
    id: number;
    nombre: string;
    descripcion?: string;
  };
  fecha_ingreso?: string;
  estado?: string;
  usuario?: {
    id: number;
    username: string;
    email: string;
  };
  tiene_suspension_renta_cuarta_vigente?: boolean;
  fecha_inicio_suspension_renta?: string;
  fecha_fin_suspension_renta?: string;
  documento_suspension_renta?: string;
}

// Interfaces para datos específicos del empleado
export interface DatosPersonales {
  id?: number;
  empleado_id: number;
  nombres: string;
  ape_paterno: string;
  ape_materno: string;
  dni: string;
  telefono?: string;
  email_personal?: string;
  fecha_nacimiento?: string;
  lugar_nacimiento?: string;
  direccion?: string;
  distrito?: string;
  provincia?: string;
  departamento?: string;
  estado_civil?: string;
  genero?: string;
  nacionalidad?: string;
  tipo_sangre?: string;
  contacto_emergencia?: string;
  telefono_emergencia?: string;
}

export interface DatosLaborales {
  id?: number;
  empleado_id: number;
  area_id: number;
  cargo_id?: number;
  fecha_ingreso: string;
  tipo_contrato?: string;
  modalidad_trabajo?: string;
  horario_trabajo?: string;
  salario_base?: number;
  estado: string;
  fecha_cese?: string;
  motivo_cese?: string;
  supervisor_id?: number;
}

export interface DatosFamiliares {
  id?: number;
  empleado_id: number;
  nombre_familiar: string;
  apellidos_familiar: string;
  parentesco: string;
  dni_familiar?: string;
  fecha_nacimiento_familiar?: string;
  telefono_familiar?: string;
  es_beneficiario: boolean;
  es_contacto_emergencia: boolean;
}

export interface DatosAcademicos {
  id?: number;
  empleado_id: number;
  nivel_educativo: string;
  institucion: string;
  titulo_obtenido?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  estado_estudio: string;
  documento_sustentatorio?: string;
}

// Servicio para gestión de empleados
export const employeesService = {
  /**
   * Obtener lista de empleados con filtros opcionales
   */
  async getAll(params?: Record<string, any>) {
    try {
      const response = await apiClient.get<any>("/api/v1/rrhh/empleados/", {
        params,
      });

      const employees = extractCollection(response.data);
      return employees.map((employee: any) => normalizeEmployee(employee));
    } catch (error) {
      // Error fetching employees
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Obtener empleado por ID
   */
  async getById(id: number) {
    try {
      const response = await apiClient.get(`/api/v1/rrhh/empleados/${id}/`);
      return response.data;
    } catch (error) {
      console.error("Error fetching employee:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Crear nuevo empleado
   */
  async create(employeeData: Partial<Employee>) {
    try {
      const response = await apiClient.post(
        "/api/v1/rrhh/empleados/",
        employeeData,
      );
      return response.data;
    } catch (error) {
      console.error("Error creating employee:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Actualizar empleado
   */
  async update(id: number, employeeData: Partial<Employee>) {
    try {
      const response = await apiClient.patch(
        `/api/v1/rrhh/empleados/${id}/`,
        employeeData,
      );
      return response.data;
    } catch (error) {
      console.error("Error updating employee:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Eliminar empleado
   */
  async delete(id: number) {
    try {
      const response = await apiClient.delete(`/api/v1/rrhh/empleados/${id}/`);
      return response.data;
    } catch (error) {
      console.error("Error deleting employee:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  // Servicios para datos personales
  datosPersonales: {
    async get(empleadoId: number) {
      try {
        const response = await apiClient.get(
          `/api/v1/rrhh/empleados/${empleadoId}/`,
        );
        return response.data;
      } catch (error) {
        console.error("Error fetching personal data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async update(empleadoId: number, data: Partial<DatosPersonales>) {
      try {
        const response = await apiClient.patch(
          `/api/v1/rrhh/empleados/${empleadoId}/`,
          data,
        );
        return response.data;
      } catch (error) {
        console.error("Error updating personal data:", error);
        throw new Error(getErrorMessage(error));
      }
    },
  },

  // Servicios para datos laborales
  datosLaborales: {
    async get(empleadoId: number) {
      try {
        const response = await apiClient.get(`/api/v1/rrhh/datos-laborales/`, {
          params: { empleado: empleadoId },
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching work data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async update(recordId: number, data: Partial<DatosLaborales>) {
      try {
        const response = await apiClient.patch(
          `/api/v1/rrhh/datos-laborales/${recordId}/`,
          data,
        );
        return response.data;
      } catch (error) {
        console.error("Error updating work data:", error);
        throw new Error(getErrorMessage(error));
      }
    },
  },

  // Servicios para datos familiares
  datosFamiliares: {
    async getAll(empleadoId: number) {
      try {
        const response = await apiClient.get(`/api/v1/rrhh/datos-familiares/`, {
          params: { empleado: empleadoId },
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching family data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async create(empleadoId: number, data: Partial<DatosFamiliares>) {
      try {
        const response = await apiClient.post(
          `/api/v1/rrhh/datos-familiares/`,
          {
            ...data,
            empleado: empleadoId,
          },
        );
        return response.data;
      } catch (error) {
        console.error("Error creating family data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async update(
      _empleadoId: number,
      id: number,
      data: Partial<DatosFamiliares>,
    ) {
      try {
        const response = await apiClient.patch(
          `/api/v1/rrhh/datos-familiares/${id}/`,
          data,
        );
        return response.data;
      } catch (error) {
        console.error("Error updating family data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async delete(_empleadoId: number, id: number) {
      try {
        const response = await apiClient.delete(
          `/api/v1/rrhh/datos-familiares/${id}/`,
        );
        return response.data;
      } catch (error) {
        console.error("Error deleting family data:", error);
        throw new Error(getErrorMessage(error));
      }
    },
  },

  // Servicios para datos académicos
  datosAcademicos: {
    async getAll(empleadoId: number) {
      try {
        const response = await apiClient.get(`/api/v1/rrhh/datos-academicos/`, {
          params: { empleado: empleadoId },
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching academic data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async create(empleadoId: number, data: Partial<DatosAcademicos>) {
      try {
        const response = await apiClient.post(
          `/api/v1/rrhh/datos-academicos/`,
          {
            ...data,
            empleado: empleadoId,
          },
        );
        return response.data;
      } catch (error) {
        console.error("Error creating academic data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async update(
      _empleadoId: number,
      id: number,
      data: Partial<DatosAcademicos>,
    ) {
      try {
        const response = await apiClient.patch(
          `/api/v1/rrhh/datos-academicos/${id}/`,
          data,
        );
        return response.data;
      } catch (error) {
        console.error("Error updating academic data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async delete(_empleadoId: number, id: number) {
      try {
        const response = await apiClient.delete(
          `/api/v1/rrhh/datos-academicos/${id}/`,
        );
        return response.data;
      } catch (error) {
        console.error("Error deleting academic data:", error);
        throw new Error(getErrorMessage(error));
      }
    },
  },

  // Servicios para reportes PDF
  reportes: {
    async descargarReporteIntegral(empleadoId: number): Promise<void> {
      try {
        const response = await apiClient.getBlob(
          `/api/v1/rrhh/empleados/${empleadoId}/reporte_integral/`,
        );
        const blob = new Blob([response.data], { type: "application/pdf" });
        const url = globalThis.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `reporte_integral_${empleadoId}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        globalThis.URL.revokeObjectURL(url);
      } catch (error) {
        console.error("Error downloading integral report:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async descargarReporteSeccion(
      empleadoId: number,
      seccion: "personal" | "laboral" | "academico" | "familiar",
    ): Promise<void> {
      try {
        const response = await apiClient.getBlob(
          `/api/v1/rrhh/empleados/${empleadoId}/reporte_seccion/`,
          { seccion },
        );
        const blob = new Blob([response.data], { type: "application/pdf" });
        const url = globalThis.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `reporte_${seccion}_${empleadoId}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        globalThis.URL.revokeObjectURL(url);
      } catch (error) {
        console.error("Error downloading section report:", error);
        throw new Error(getErrorMessage(error));
      }
    },
  },
};
