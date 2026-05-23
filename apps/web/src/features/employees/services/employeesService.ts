import { apiClient } from "@/shared/api/api";
import { getErrorMessage } from "@/shared/api/errorUtils";
import {
  extractCollection,
  normalizeEmployee,
} from "@/shared/api/apiNormalizers";

// Interfaces para empleados
export interface Employee {
  id: string;
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
    id: string;
    organo: string;
    siglas: string;
  };
  cargo?: {
    id: string;
    nombre: string;
    descripcion?: string;
  };
  fecha_ingreso?: string;
  estado?: string;
  usuario?: {
    id: string;
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
  id?: string;
  empleado_id: string;
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
  id?: string;
  empleado_id: string;
  area_id: string;
  cargo_id?: string;
  fecha_ingreso: string;
  tipo_contrato?: string;
  modalidad_trabajo?: string;
  horario_trabajo?: string;
  salario_base?: number;
  estado: string;
  fecha_cese?: string;
  motivo_cese?: string;
  supervisor_id?: string;
}

export interface DatosFamiliares {
  id?: string;
  empleado_id: string;
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
  id?: string;
  empleado_id: string;
  nivel_educativo: string;
  institucion: string;
  titulo_obtenido?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  estado_estudio: string;
  documento_sustentatorio?: string;
}

// Batch import (#130)
export interface BatchImportRowError {
  row: number;
  errors: Record<string, unknown>;
}

export interface BatchImportResult {
  created: number;
  errors: BatchImportRowError[];
}

// Servicio para gestión de empleados
export const employeesService = {
  /**
   * Obtener lista de empleados con filtros opcionales
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- filter params are open-ended; caller controls shape
  async getAll(params?: Record<string, any>) {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any -- raw paginated response from DRF
      const response = await apiClient.get<any>("/api/v1/employees/", {
        params,
      });

      const employees = extractCollection(response.data);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any -- normalizeEmployee maps raw backend shape
      return employees.map((employee: any) => normalizeEmployee(employee));
    } catch (error) {
      // Error fetching employees
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Obtener empleado por ID
   */
  async getById(id: string) {
    try {
      const response = await apiClient.get(`/api/v1/employees/${id}/`);
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
        "/api/v1/employees/",
        employeeData,
      );
      return response.data;
    } catch (error) {
      console.error("Error creating employee:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Importar empleados masivamente desde un CSV (#130).
   *
   * Validación todo-o-nada en el backend: si alguna fila falla (HTTP 422),
   * no se crea ningún empleado y se devuelve el reporte de errores por fila.
   * Tanto el caso exitoso (201) como el rechazado (422) se normalizan al
   * mismo shape { created, errors } para que el componente lo muestre igual.
   */
  async batchImport(file: File): Promise<BatchImportResult> {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await apiClient.post<{ data: BatchImportResult }>(
        "/api/v1/employees/batch-import/",
        formData,
      );
      return response.data.data;
    } catch (error) {
      // 422 = filas con errores de validación; el reporte viene en .errors
      const response = (
        error as {
          response?: { status?: number; data?: { errors?: BatchImportResult } };
        }
      ).response;
      if (response?.status === 422 && response.data?.errors) {
        return response.data.errors;
      }
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Actualizar empleado
   */
  async update(id: string, employeeData: Partial<Employee>) {
    try {
      const response = await apiClient.patch(
        `/api/v1/employees/${id}/`,
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
  async delete(id: string) {
    try {
      const response = await apiClient.delete(`/api/v1/employees/${id}/`);
      return response.data;
    } catch (error) {
      console.error("Error deleting employee:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  // Servicios para datos personales
  datosPersonales: {
    async get(empleadoId: string) {
      try {
        const response = await apiClient.get(
          `/api/v1/employees/${empleadoId}/`,
        );
        return response.data;
      } catch (error) {
        console.error("Error fetching personal data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async update(empleadoId: string, data: Partial<DatosPersonales>) {
      try {
        const response = await apiClient.patch(
          `/api/v1/employees/${empleadoId}/`,
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
    async get(empleadoId: string) {
      try {
        const response = await apiClient.get(`/api/v1/employment-data/`, {
          params: { empleado: empleadoId },
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching work data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async update(recordId: string, data: Partial<DatosLaborales>) {
      try {
        const response = await apiClient.patch(
          `/api/v1/employment-data/${recordId}/`,
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
    async getAll(empleadoId: string) {
      try {
        const response = await apiClient.get(`/api/v1/family-members/`, {
          params: { empleado: empleadoId },
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching family data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async create(empleadoId: string, data: Partial<DatosFamiliares>) {
      try {
        const response = await apiClient.post(
          `/api/v1/family-members/`,
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
      _empleadoId: string,
      id: string,
      data: Partial<DatosFamiliares>,
    ) {
      try {
        const response = await apiClient.patch(
          `/api/v1/family-members/${id}/`,
          data,
        );
        return response.data;
      } catch (error) {
        console.error("Error updating family data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async delete(_empleadoId: string, id: string) {
      try {
        const response = await apiClient.delete(
          `/api/v1/family-members/${id}/`,
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
    async getAll(empleadoId: string) {
      try {
        const response = await apiClient.get(`/api/v1/academic-records/`, {
          params: { empleado: empleadoId },
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching academic data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async create(empleadoId: string, data: Partial<DatosAcademicos>) {
      try {
        const response = await apiClient.post(
          `/api/v1/academic-records/`,
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
      _empleadoId: string,
      id: string,
      data: Partial<DatosAcademicos>,
    ) {
      try {
        const response = await apiClient.patch(
          `/api/v1/academic-records/${id}/`,
          data,
        );
        return response.data;
      } catch (error) {
        console.error("Error updating academic data:", error);
        throw new Error(getErrorMessage(error));
      }
    },

    async delete(_empleadoId: string, id: string) {
      try {
        const response = await apiClient.delete(
          `/api/v1/academic-records/${id}/`,
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
    async descargarReporteIntegral(empleadoId: string): Promise<void> {
      try {
        const response = await apiClient.getBlob(
          `/api/v1/employees/${empleadoId}/reporte_integral/`,
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
      empleadoId: string,
      seccion: "personal" | "laboral" | "academico" | "familiar",
    ): Promise<void> {
      try {
        const response = await apiClient.getBlob(
          `/api/v1/employees/${empleadoId}/reporte_seccion/`,
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
