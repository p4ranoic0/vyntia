import { apiClient } from "@/lib/api";
import axios from "axios";

export interface OnboardingStatus {
  onboarding_id: number;
  empleado: number;
  empleado_nombre: string;
  empleado_documento: string;
  usuario: number;
  usuario_username: string;
  estado_onboarding: string;
  datos_personales_completos: boolean;
  datos_laborales_completos: boolean;
  dni_subido: boolean;
  declaraciones_juradas_subidas: boolean;
  certificados_academicos_subidos: boolean;
  certificados_trabajo_subidos: boolean;
  documentos_familiares_subidos: boolean;
  progreso_porcentaje: number;
  items_pendientes: string[];
  documentos_pendientes: Array<{
    tipo_documento: string;
    categoria: string;
    label: string;
  }>;
  validado_por: number | null;
  fecha_validacion: string | null;
  observaciones: string | null;
  email_bienvenida_enviado: boolean;
  fecha_email_bienvenida: string | null;
  fecha_inicio: string;
  fecha_completado: string | null;
}

export interface OnboardingCreateData {
  nombres_empleado: string;
  apellido_paterno: string;
  apellido_materno?: string;
  numero_documento: string;
  correo_personal: string;
  genero_empleado?: string;
  fecha_nacimiento?: string;
}

export interface OnboardingCreateResponse extends OnboardingStatus {
  username: string;
  email_enviado: boolean;
}

const ESTADO_LABELS: Record<string, string> = {
  pendiente_datos: "Pendiente de Datos",
  pendiente_documentos: "Pendiente de Documentos",
  pendiente_validacion: "Pendiente de Validacion",
  observado: "Observado",
  completado: "Completado",
};

export function getEstadoLabel(estado: string): string {
  return ESTADO_LABELS[estado] || estado;
}

export const onboardingService = {
  async getMiOnboarding(): Promise<OnboardingStatus | null> {
    try {
      const response = await apiClient.get(
        "/api/v1/onboarding/processes/mi-onboarding/",
      );
      return response.data?.data || response.data;
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 404) return null;
      throw err;
    }
  },

  async getAll(
    params?: Record<string, any>,
  ): Promise<{ results: OnboardingStatus[]; count: number }> {
    const response = await apiClient.get("/api/v1/onboarding/processes/", params);
    const rawData = response.data;
    const items = Array.isArray(rawData?.data) ? rawData.data : [];
    const pagination = rawData?.meta?.pagination || {};
    return {
      results: items,
      count: pagination.total_items || items.length,
    };
  },

  async getById(id: number): Promise<OnboardingStatus> {
    const response = await apiClient.get(`/api/v1/onboarding/processes/${id}/`);
    return response.data?.data || response.data;
  },

  async crear(data: OnboardingCreateData): Promise<OnboardingCreateResponse> {
    const response = await apiClient.post("/api/v1/onboarding/processes/", data);
    return response.data?.data || response.data;
  },

  async validar(
    id: number,
    accion: "aprobar" | "rechazar",
    observaciones?: string,
  ): Promise<OnboardingStatus> {
    const response = await apiClient.post(
      `/api/v1/onboarding/processes/${id}/validar/`,
      {
        accion,
        observaciones: observaciones || "",
      },
    );
    return response.data?.data || response.data;
  },

  async reenviarEmail(id: number): Promise<void> {
    await apiClient.post(`/api/v1/onboarding/processes/${id}/reenviar_email/`, {});
  },

  async actualizarEstado(id: number): Promise<OnboardingStatus> {
    const response = await apiClient.post(
      `/api/v1/onboarding/processes/${id}/actualizar-estado/`,
      {},
    );
    return response.data?.data || response.data;
  },
};
