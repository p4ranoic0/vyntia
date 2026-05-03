import { apiClient } from "@/lib/api";
import { getErrorMessage } from "@/lib/errorUtils";

export interface Contrato {
  contrato_id: number;
  empleado: number;
  empleado_detalle?: {
    empleado_id: number;
    nombres_empleado: string;
    apellido_paterno: string;
    apellido_materno: string;
    nombre_completo: string;
  };
  area: number;
  area_detalle?: {
    area_id: number;
    nombre: string;
  };
  numero_contrato: string;
  numero_adenda?: string | null;
  tipo_documento: string;
  tipo_documento_texto?: string;
  fecha_inicio: string;
  fecha_fin?: string | null;
  fecha_firma?: string | null;
  salario_bruto: number;
  salario_neto?: number | null;
  cargo: string;
  jornada_laboral: string;
  jornada_texto?: string;
  funciones?: string | null;
  lugar_trabajo?: string | null;
  horario_trabajo?: string | null;
  observaciones?: string | null;
  status: string;
  estado_texto?: string;
  documento_generado: boolean;
  created_at: string;
  updated_at: string;
  // Campos calculados
  dias_hasta_vencimiento?: number | null;
  esta_vigente?: boolean;
  esta_vencido?: boolean;
  duracion_dias?: number | null;
  duracion_meses?: number | null;
  es_contrato_inicial?: boolean;
  es_adenda?: boolean;
}

export interface ContratoListItem {
  contrato_id: number;
  numero_contrato: string;
  numero_adenda?: string | null;
  empleado: number;
  empleado_nombre: string;
  area_nombre: string;
  tipo_documento: string;
  tipo_documento_texto: string;
  fecha_inicio: string;
  fecha_fin?: string | null;
  salario_bruto: number;
  salario_neto?: number | null;
  cargo: string;
  status: string;
  estado_texto: string;
  dias_hasta_vencimiento?: number | null;
  esta_vigente?: boolean;
}

export interface ContratoFormData {
  empleado: number;
  area: number;
  numero_contrato?: string;
  numero_adenda?: string;
  tipo_documento: string;
  fecha_inicio: string;
  fecha_fin?: string;
  fecha_firma?: string;
  salario_bruto: number;
  cargo: string;
  jornada_laboral?: string;
  funciones?: string;
  lugar_trabajo?: string;
  horario_trabajo?: string;
  observaciones?: string;
}

export interface ContratoFilters {
  empleado_id?: number;
  area_id?: number;
  tipo_documento?: string;
  estado?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
}

export const TIPO_CONTRATO_LABELS: Record<string, string> = {
  // CAS - D.L. 1057
  CAS_INDETERMINADO: "CAS a Plazo Indeterminado",
  CAS_DETERMINADO: "CAS a Plazo Determinado",
  CAS_SUPLENCIA: "CAS a Plazo Determinado Suplencia",
  // D.Leg. 728
  LEY_728_FIJO: "Ley 728 a Plazo Fijo",
  LEY_728_FIJO_SUPLENCIA: "Ley 728 a Plazo Fijo Suplencia",
  LEY_728_INDETERMINADO: "Ley 728 a Plazo Indeterminado",
  // D.Leg. 276
  LEY_276_INDETERMINADO: "Ley 276 a Plazo Indeterminado",
  // Adendas
  ADENDA_SALARIAL: "Adenda Salarial",
  ADENDA_CARGO: "Adenda de Cambio de Cargo",
  ADENDA_HORARIO: "Adenda de Cambio de Horario",
  ADENDA_EXTENSION: "Adenda de Extension",
};

export const TIPOS_REQUIEREN_FECHA_FIN = new Set([
  "CAS_DETERMINADO",
  "CAS_SUPLENCIA",
  "LEY_728_FIJO",
  "LEY_728_FIJO_SUPLENCIA",
]);

export const ESTADO_CONTRATO_LABELS: Record<string, string> = {
  BORRADOR: "Borrador",
  PENDIENTE: "Pendiente de Firma",
  ACTIVO: "Activo",
  VENCIDO: "Vencido",
  TERMINADO: "Terminado",
  ANULADO: "Anulado",
};

export const JORNADA_LABELS: Record<string, string> = {
  COMPLETA: "Jornada Completa",
  PARCIAL: "Jornada Parcial",
  REDUCIDA: "Jornada Reducida",
  FLEXIBLE: "Jornada Flexible",
};

export const ESTADO_CONTRATO_BADGE: Record<string, string> = {
  BORRADOR: "bg-gray-100 text-gray-800",
  PENDIENTE: "bg-yellow-100 text-yellow-800",
  ACTIVO: "bg-green-100 text-green-800",
  VENCIDO: "bg-red-100 text-red-800",
  TERMINADO: "bg-blue-100 text-blue-800",
  ANULADO: "bg-red-100 text-red-800",
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function extractData(raw: any) {
  return raw?.data?.results ?? raw?.results ?? raw?.data ?? raw;
}

export const contractsService = {
  async getAll(filters?: ContratoFilters): Promise<ContratoListItem[]> {
    try {
      const params: Record<string, string | number> = {};
      if (filters?.empleado_id) params.empleado_id = filters.empleado_id;
      if (filters?.area_id) params.area_id = filters.area_id;
      if (filters?.tipo_documento)
        params.tipo_documento = filters.tipo_documento;
      if (filters?.estado) params.estado = filters.estado;
      if (filters?.fecha_inicio) params.fecha_inicio = filters.fecha_inicio;
      if (filters?.fecha_fin) params.fecha_fin = filters.fecha_fin;
      const response = await apiClient.get(
        "/api/v1/contracts/",
        params,
      );
      const data = extractData(response.data);
      return Array.isArray(data) ? data : [];
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  async getByEmpleado(empleadoId: number): Promise<ContratoListItem[]> {
    return this.getAll({ empleado_id: empleadoId });
  },

  async getById(id: number): Promise<Contrato> {
    try {
      const response = await apiClient.get(
        `/api/v1/contracts/${id}/`,
      );
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data;
      return raw?.data ?? raw;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  async create(data: ContratoFormData): Promise<Contrato> {
    try {
      const response = await apiClient.post(
        "/api/v1/contracts/",
        data,
      );
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data;
      return raw?.data ?? raw;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  async update(id: number, data: Partial<ContratoFormData>): Promise<Contrato> {
    try {
      const response = await apiClient.patch(
        `/api/v1/contracts/${id}/`,
        data,
      );
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data;
      return raw?.data ?? raw;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  async getEstadisticas(): Promise<Record<string, unknown>> {
    try {
      const response = await apiClient.get(
        "/api/v1/contracts/estadisticas/",
      );
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data;
      return raw?.data ?? raw;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  async getAlertasVencimiento(dias = 30): Promise<ContratoListItem[]> {
    try {
      const response = await apiClient.get(
        "/api/v1/contracts/alertas_vencimiento/",
        { dias },
      );
      const data = extractData(response.data);
      return Array.isArray(data) ? data : [];
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  async renovar(
    id: number,
    data: {
      fecha_inicio: string;
      fecha_fin?: string;
      salario_bruto?: number;
      observaciones?: string;
    },
  ): Promise<Contrato> {
    try {
      const response = await apiClient.post(
        `/api/v1/contracts/${id}/renovar_contrato/`,
        data,
      );
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data;
      return raw?.data ?? raw;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  async generarCertificado(data: {
    empleado_id: number;
    tipo_certificado?: string;
    proposito?: string;
    incluir_salario?: boolean;
    formato?: string;
    guardar_documento?: boolean;
  }): Promise<{
    documento_id?: number;
    archivo_url?: string;
    nombre_archivo?: string;
    numero_certificado?: string;
  }> {
    try {
      const response = await apiClient.post(
        "/api/v1/documents/documents/generar-certificado/",
        data,
      );
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data;
      return raw?.data ?? raw;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  async generarContratoPdf(data: {
    contrato_id: number;
    formato?: string;
    guardar_documento?: boolean;
  }): Promise<{
    documento_id?: number;
    archivo_url?: string;
    nombre_archivo?: string;
  }> {
    try {
      const response = await apiClient.post(
        "/api/v1/documents/documents/generar-contrato/",
        data,
      );
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data;
      return raw?.data ?? raw;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  async generarAdendaPdf(data: {
    adenda_id: number;
    formato?: string;
    guardar_documento?: boolean;
  }): Promise<{
    documento_id?: number;
    archivo_url?: string;
    nombre_archivo?: string;
  }> {
    try {
      const response = await apiClient.post(
        "/api/v1/documents/documents/generar-adenda/",
        data,
      );
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = response.data;
      return raw?.data ?? raw;
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};
