import { apiClient } from "@/lib/api";

export type TipoConceptoRemuneracion = "ingreso" | "descuento";

export interface ConceptoRemuneracion {
  configuracion_id: number;
  tipo: TipoConceptoRemuneracion;
  codigo: string;
  nombre: string;
  descripcion?: string;
  porcentaje: number;
  monto_fijo: number;
  aplica_base_imponible: boolean;
  orden: number;
  status: "activo" | "inactivo";
  es_activo?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ConceptoRemuneracionPayload {
  tipo: TipoConceptoRemuneracion;
  codigo: string;
  nombre: string;
  descripcion?: string;
  porcentaje?: number;
  monto_fijo?: number;
  aplica_base_imponible?: boolean;
  orden?: number;
  status?: "activo" | "inactivo";
}

interface ListParams {
  tipo?: TipoConceptoRemuneracion;
  estado?: "activo" | "inactivo";
  search?: string;
}

export interface ConfiguracionAfp {
  afp_config_id: number;
  afp_nombre: string;
  vigencia_mes: string;
  aporte_obligatorio_pct: number;
  comision_flujo_pct: number;
  comision_mixta_pct: number;
  prima_seguro_pct: number;
  remuneracion_max_asegurable: number;
  status: "activo" | "inactivo";
  es_activo?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ConfiguracionAfpPayload {
  afp_nombre: string;
  vigencia_mes: string;
  aporte_obligatorio_pct: number;
  comision_flujo_pct: number;
  comision_mixta_pct: number;
  prima_seguro_pct: number;
  remuneracion_max_asegurable: number;
  status: "activo" | "inactivo";
}

export interface ConfiguracionUit {
  configuracion_uit_id: number;
  anio: number;
  valor_uit: number;
  tope_renta_cuarta_uit: number;
  porcentaje_renta_cuarta: number;
  status: "activo" | "inactivo";
  estado_texto?: string;
  es_activo?: boolean;
  tope_renta_cuarta_soles: number;
  essalud_cas_mensual: number;
  created_by?: number;
  created_by_nombre?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ConfiguracionUitPayload {
  anio: number;
  valor_uit: number;
  tope_renta_cuarta_uit?: number;
  porcentaje_renta_cuarta?: number;
  status?: "activo" | "inactivo";
}

// ========== Planillas Mensuales ==========

export type ModalidadContrato =
  | "CAS"
  | "CAP"
  | "NOMBRADO"
  | "PRACTICANTE"
  | "TERCERO";
export type EstadoPlanilla =
  | "borrador"
  | "generada"
  | "calculada"
  | "aprobada"
  | "pagada"
  | "anulada";
export type EstadoDetalle = "activo" | "anulado";
export type EstadoDescuento =
  | "pendiente"
  | "procesado"
  | "aplicado"
  | "anulado";
export type EstadoBoleta = "generada" | "enviada" | "vista" | "descargada";
export type EstadoCalendario = "programado" | "ejecutado" | "cancelado";

export interface PlanillaMensual {
  planilla_id: number;
  periodo: string;
  modalidad?: string;
  meta_presupuestal?: string;
  descripcion?: string;
  total_trabajadores?: number;
  total_remuneracion_bruta?: number;
  total_ingresos?: number;
  total_descuentos?: number;
  total_neto_pagar?: number;
  total_neto?: number;
  total_essalud?: number;
  total_aporte_afp?: number;
  total_onp?: number;
  status?: EstadoPlanilla;
  estado_texto?: string;
  fecha_generacion?: string;
  fecha_aprobacion?: string;
  fecha_pago?: string;
  usuario_generacion?: Record<string, unknown>;
  usuario_aprobacion?: Record<string, unknown>;
  created_by?: Record<string, unknown>;
  aprobado_por?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface PlanillaMensualPayload {
  periodo: string;
  modalidad: ModalidadContrato;
  meta_presupuestal: string;
  descripcion?: string;
  status?: EstadoPlanilla;
}

export interface DetallePlanilla {
  detalle_id: number;
  planilla: {
    planilla_id: number;
    periodo: string;
    modalidad: ModalidadContrato;
  };
  empleado: {
    empleado_id: number;
    dni: string;
    nombres_completos: string;
    area_nombre: string;
  };
  area_nombre: string;
  cargo: string;
  dni: string;
  sistema_pensiones: string;
  tipo_comision_afp: string;
  dias_laborados: number;
  dias_subsidiados: number;
  remuneracion_basica: number;
  asignacion_familiar: number;
  bonificacion_especial: number;
  otras_bonificaciones: number;
  total_ingresos: number;
  total_haberes: number;
  aporte_afp_obligatorio: number;
  comision_afp: number;
  prima_seguro_afp: number;
  total_afp: number;
  aporte_onp: number;
  essalud: number;
  renta_quinta_categoria: number;
  total_descuentos: number;
  neto_pagar: number;
  aporte_essalud: number;
  aporte_afp_empleador: number;
  status: EstadoDetalle;
  estado_texto?: string;
  banco?: string;
  numero_cuenta?: string;
  observaciones?: string;
  created_at: string;
  updated_at: string;
}

export interface DetallePlanillaPayload {
  planilla_id: number;
  empleado_id: number;
  dias_laborados?: number;
  dias_subsidiados?: number;
  remuneracion_basica?: number;
  observaciones?: string;
}

export interface DescuentoMasivo {
  descuento_masivo_id: number;
  periodo: string;
  configuracion_concepto?: {
    configuracion_id: number;
    nombre: string;
    codigo: string;
  };
  archivo_origen: string;
  total_registros: number;
  registros_procesados: number;
  registros_error: number;
  monto_total: number;
  status: EstadoDescuento;
  estado_texto?: string;
  errores_log?: string;
  usuario_carga?: {
    usuario_id: number;
    username: string;
    nombres_completos: string;
  };
  fecha_carga: string;
  fecha_procesado?: string;
  updated_at: string;
}

export interface DescuentoMasivoPayload {
  periodo: string;
  configuracion_concepto_id: number;
  archivo_origen: File | string;
}

export interface BoletaPago {
  boleta_id: number;
  detalle_planilla: {
    detalle_id: number;
    planilla_periodo: string;
  };
  empleado?: {
    empleado_id: number;
    dni: string;
    nombres_completos: string;
  };
  empleado_nombre?: string;
  empleado_dni?: string;
  periodo: string;
  total_ingresos: number;
  total_descuentos: number;
  neto_pagar: number;
  status: EstadoBoleta;
  estado_texto?: string;
  pdf_url?: string;
  hash_documento?: string;
  fecha_generacion: string;
  fecha_envio?: string;
  fecha_visualizacion?: string;
}

export interface CalendarioPago {
  calendario_id: number;
  periodo: string;
  descripcion: string;
  fecha_pago_programada: string;
  fecha_pago_real?: string;
  modalidad: ModalidadContrato;
  meta_presupuestal?: string;
  status: EstadoCalendario;
  estado_texto?: string;
  observaciones?: string;
  created_by?: {
    usuario_id: number;
    username: string;
  };
  created_at: string;
}

export interface CalendarioPagoPayload {
  periodo: string;
  descripcion: string;
  fecha_pago_programada: string;
  modalidad: ModalidadContrato;
  meta_presupuestal?: string;
  observaciones?: string;
}

export interface EstadisticasPlanilla {
  total_trabajadores: number;
  total_ingresos: number;
  total_descuentos: number;
  total_neto: number;
  total_essalud: number;
  total_afp: number;
  promedio_remuneracion: number;
  detalles_por_area?: Array<{
    area: string;
    trabajadores: number;
    total_ingresos: number;
    total_neto: number;
  }>;
}

interface ApiEnvelope<T> {
  data?: T;
  results?: T;
}

function extractList(responseData: unknown): ConceptoRemuneracion[] {
  if (Array.isArray(responseData)) return responseData;

  const envelope = responseData as ApiEnvelope<ConceptoRemuneracion[]>;
  if (Array.isArray(envelope?.data)) return envelope.data;
  if (Array.isArray(envelope?.results)) return envelope.results;
  return [];
}

function extractTypedList<T>(responseData: unknown): T[] {
  if (Array.isArray(responseData)) return responseData as T[];
  const envelope = responseData as ApiEnvelope<T[]>;
  if (Array.isArray(envelope?.data)) return envelope.data;
  if (Array.isArray(envelope?.results)) return envelope.results;
  return [];
}

export const payrollService = {
  async list(params?: ListParams): Promise<ConceptoRemuneracion[]> {
    const response = await apiClient.get(
      "/api/v1/payroll/compensation-configurations/",
      {
        params,
      },
    );
    return extractList(response.data);
  },

  async create(
    payload: ConceptoRemuneracionPayload,
  ): Promise<ConceptoRemuneracion> {
    const response = await apiClient.post<ApiEnvelope<ConceptoRemuneracion>>(
      "/api/v1/payroll/compensation-configurations/",
      payload,
    );
    return (
      response.data.data || (response.data as unknown as ConceptoRemuneracion)
    );
  },

  async update(
    id: number,
    payload: Partial<ConceptoRemuneracionPayload>,
  ): Promise<ConceptoRemuneracion> {
    const response = await apiClient.patch<ApiEnvelope<ConceptoRemuneracion>>(
      `/api/v1/payroll/compensation-configurations/${id}/`,
      payload,
    );
    return (
      response.data.data || (response.data as unknown as ConceptoRemuneracion)
    );
  },

  async remove(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/payroll/compensation-configurations/${id}/`);
  },

  async listAfp(params?: {
    vigencia_mes?: string;
    estado?: "activo" | "inactivo";
  }): Promise<ConfiguracionAfp[]> {
    const response = await apiClient.get("/api/v1/payroll/afp-configurations/", {
      params,
    });
    return extractTypedList<ConfiguracionAfp>(response.data);
  },

  async createAfp(payload: ConfiguracionAfpPayload): Promise<ConfiguracionAfp> {
    const response = await apiClient.post<ApiEnvelope<ConfiguracionAfp>>(
      "/api/v1/payroll/afp-configurations/",
      payload,
    );
    return response.data.data || (response.data as unknown as ConfiguracionAfp);
  },

  async updateAfp(
    id: number,
    payload: Partial<ConfiguracionAfpPayload>,
  ): Promise<ConfiguracionAfp> {
    const response = await apiClient.patch<ApiEnvelope<ConfiguracionAfp>>(
      `/api/v1/payroll/afp-configurations/${id}/`,
      payload,
    );
    return response.data.data || (response.data as unknown as ConfiguracionAfp);
  },

  async removeAfp(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/payroll/afp-configurations/${id}/`);
  },

  // ========== Configuración UIT ==========

  async listUit(params?: {
    anio?: number;
    estado?: "activo" | "inactivo";
    activo?: boolean;
  }): Promise<ConfiguracionUit[]> {
    let requestParams = params;
    if (params && Object.hasOwn(params, "activo")) {
      requestParams = {
        ...params,
        activo: String(params.activo),
      } as unknown as typeof params;
    }

    const response = await apiClient.get("/api/v1/payroll/tax-parameters/", {
      params: requestParams,
    });
    return extractTypedList<ConfiguracionUit>(response.data);
  },

  async getUit(id: number): Promise<ConfiguracionUit> {
    const response = await apiClient.get<ApiEnvelope<ConfiguracionUit>>(
      `/api/v1/payroll/tax-parameters/${id}/`,
    );
    return response.data.data || (response.data as unknown as ConfiguracionUit);
  },

  async createUit(payload: ConfiguracionUitPayload): Promise<ConfiguracionUit> {
    const response = await apiClient.post<ApiEnvelope<ConfiguracionUit>>(
      "/api/v1/payroll/tax-parameters/",
      payload,
    );
    return response.data.data || (response.data as unknown as ConfiguracionUit);
  },

  async updateUit(
    id: number,
    payload: Partial<ConfiguracionUitPayload>,
  ): Promise<ConfiguracionUit> {
    const response = await apiClient.patch<ApiEnvelope<ConfiguracionUit>>(
      `/api/v1/payroll/tax-parameters/${id}/`,
      payload,
    );
    return response.data.data || (response.data as unknown as ConfiguracionUit);
  },

  async removeUit(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/payroll/tax-parameters/${id}/`);
  },

  async activarUit(id: number): Promise<ConfiguracionUit> {
    const response = await apiClient.post<ApiEnvelope<ConfiguracionUit>>(
      `/api/v1/payroll/tax-parameters/${id}/activar/`,
    );
    return response.data.data || (response.data as unknown as ConfiguracionUit);
  },

  // ========== Planillas Mensuales ==========

  async listPlanillas(params?: {
    periodo?: string;
    modalidad?: ModalidadContrato;
    estado?: EstadoPlanilla;
    meta_presupuestal?: string;
  }): Promise<PlanillaMensual[]> {
    const response = await apiClient.get("/api/v1/payroll/monthly-runs/", {
      params,
    });
    return extractTypedList<PlanillaMensual>(response.data);
  },

  async getPlanilla(id: number): Promise<PlanillaMensual> {
    const response = await apiClient.get<ApiEnvelope<PlanillaMensual>>(
      `/api/v1/payroll/monthly-runs/${id}/`,
    );
    return response.data.data || (response.data as unknown as PlanillaMensual);
  },

  async createPlanilla(
    payload: PlanillaMensualPayload,
  ): Promise<PlanillaMensual> {
    const response = await apiClient.post<ApiEnvelope<PlanillaMensual>>(
      "/api/v1/payroll/monthly-runs/",
      payload,
    );
    return response.data.data || (response.data as unknown as PlanillaMensual);
  },

  async updatePlanilla(
    id: number,
    payload: Partial<PlanillaMensualPayload>,
  ): Promise<PlanillaMensual> {
    const response = await apiClient.patch<ApiEnvelope<PlanillaMensual>>(
      `/api/v1/payroll/monthly-runs/${id}/`,
      payload,
    );
    return response.data.data || (response.data as unknown as PlanillaMensual);
  },

  async removePlanilla(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/payroll/monthly-runs/${id}/`);
  },

  // Acciones especiales de planilla
  async generarPlanilla(
    id: number,
  ): Promise<{
    message: string;
    empleados_agregados: number;
    total_empleados: number;
  }> {
    const response = await apiClient.post(
      `/api/v1/payroll/monthly-runs/${id}/generar_planilla/`,
    );
    return (response.data as any).data || response.data;
  },

  async regenerarPlanilla(id: number): Promise<{ message: string }> {
    const response = await apiClient.post(
      `/api/v1/payroll/monthly-runs/${id}/regenerar/`,
    );
    return (response.data as any).data || response.data;
  },

  async calcularPlanilla(id: number): Promise<{ message: string }> {
    const response = await apiClient.post(
      `/api/v1/payroll/monthly-runs/${id}/calcular_planilla/`,
    );
    return (response.data as any).data || response.data;
  },

  async previewPlanilla(id: number): Promise<VistaPreviaPlanilla> {
    const response = await apiClient.post(
      `/api/v1/payroll/monthly-runs/${id}/preview/`,
    );
    return (response.data as any).data || response.data;
  },

  async aprobarPlanilla(id: number): Promise<PlanillaMensual> {
    const response = await apiClient.post<ApiEnvelope<PlanillaMensual>>(
      `/api/v1/payroll/monthly-runs/${id}/aprobar_planilla/`,
    );
    return response.data.data || (response.data as unknown as PlanillaMensual);
  },

  async getEstadisticasPlanilla(id: number): Promise<EstadisticasPlanilla> {
    const response = await apiClient.get(
      `/api/v1/payroll/monthly-runs/${id}/estadisticas/`,
    );
    return (response.data as any).data || response.data;
  },

  // ========== Detalles de Planilla ==========

  async listDetalles(params?: {
    planilla?: number;
    empleado?: number;
    estado?: EstadoDetalle;
  }): Promise<DetallePlanilla[]> {
    const response = await apiClient.get("/api/v1/payroll/details/", {
      params,
    });
    return extractTypedList<DetallePlanilla>(response.data);
  },

  async getDetalle(id: number): Promise<DetallePlanilla> {
    const response = await apiClient.get<ApiEnvelope<DetallePlanilla>>(
      `/api/v1/payroll/details/${id}/`,
    );
    return response.data.data || (response.data as unknown as DetallePlanilla);
  },

  async createDetalle(
    payload: DetallePlanillaPayload,
  ): Promise<DetallePlanilla> {
    const response = await apiClient.post<ApiEnvelope<DetallePlanilla>>(
      "/api/v1/payroll/details/",
      payload,
    );
    return response.data.data || (response.data as unknown as DetallePlanilla);
  },

  async updateDetalle(
    id: number,
    payload: Partial<DetallePlanillaPayload>,
  ): Promise<DetallePlanilla> {
    const response = await apiClient.patch<ApiEnvelope<DetallePlanilla>>(
      `/api/v1/payroll/details/${id}/`,
      payload,
    );
    return response.data.data || (response.data as unknown as DetallePlanilla);
  },

  async removeDetalle(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/payroll/details/${id}/`);
  },

  // ========== Descuentos Masivos ==========

  async listDescuentos(params?: {
    periodo?: string;
    estado?: EstadoDescuento;
  }): Promise<DescuentoMasivo[]> {
    const response = await apiClient.get("/api/v1/payroll/mass-deductions/", {
      params,
    });
    return extractTypedList<DescuentoMasivo>(response.data);
  },

  async getDescuento(id: number): Promise<DescuentoMasivo> {
    const response = await apiClient.get<ApiEnvelope<DescuentoMasivo>>(
      `/api/v1/payroll/mass-deductions/${id}/`,
    );
    return response.data.data || (response.data as unknown as DescuentoMasivo);
  },

  async createDescuento(
    payload: DescuentoMasivoPayload,
  ): Promise<DescuentoMasivo> {
    const formData = new FormData();
    formData.append("periodo", payload.periodo);
    formData.append(
      "configuracion_concepto",
      payload.configuracion_concepto_id.toString(),
    );
    if (payload.archivo_origen instanceof File) {
      formData.append("archivo_origen", payload.archivo_origen);
    }

    const response = await apiClient.post<ApiEnvelope<DescuentoMasivo>>(
      "/api/v1/payroll/mass-deductions/",
      formData,
    );
    return response.data.data || (response.data as unknown as DescuentoMasivo);
  },

  async updateDescuento(
    id: number,
    payload: Partial<Omit<DescuentoMasivoPayload, "archivo_origen">>,
  ): Promise<DescuentoMasivo> {
    const response = await apiClient.patch<ApiEnvelope<DescuentoMasivo>>(
      `/api/v1/payroll/mass-deductions/${id}/`,
      payload,
    );
    return response.data.data || (response.data as unknown as DescuentoMasivo);
  },

  async removeDescuento(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/payroll/mass-deductions/${id}/`);
  },

  async procesarDescuento(id: number): Promise<{
    total_registros: number;
    registros_procesados: number;
    registros_error: number;
    monto_total: string;
    errores: string[];
  }> {
    const response = await apiClient.post(
      `/api/v1/payroll/mass-deductions/${id}/procesar/`,
    );
    return (response.data as any).data || response.data;
  },

  async anularDescuento(id: number): Promise<{
    conceptos_eliminados: number;
  }> {
    const response = await apiClient.post(
      `/api/v1/payroll/mass-deductions/${id}/anular/`,
    );
    return (response.data as any).data || response.data;
  },

  // ========== Boletas de Pago ==========

  async generarBoletas(planillaId: number): Promise<{
    planilla_id: number;
    periodo: string;
    boletas_creadas: number;
    boletas_existentes: number;
    total: number;
  }> {
    const response = await apiClient.post(
      `/api/v1/payroll/monthly-runs/${planillaId}/generar_boletas/`,
    );
    return (response.data as any).data || response.data;
  },

  async listBoletas(params?: {
    empleado?: number;
    periodo?: string;
    estado?: EstadoBoleta;
  }): Promise<BoletaPago[]> {
    const response = await apiClient.get("/api/v1/payroll/payslips/", {
      params,
    });
    return extractTypedList<BoletaPago>(response.data);
  },

  async getBoleta(id: number): Promise<BoletaPago> {
    const response = await apiClient.get<ApiEnvelope<BoletaPago>>(
      `/api/v1/payroll/payslips/${id}/`,
    );
    return response.data.data || (response.data as unknown as BoletaPago);
  },

  async downloadBoletaPdf(id: number): Promise<Blob> {
    const response = await apiClient.get(
      `/api/v1/payroll/payslips/${id}/pdf/`,
      {
        responseType: "blob",
      },
    );
    return response.data as Blob;
  },

  async descargaMasivaBoletas(planillaId: number): Promise<Blob> {
    const response = await apiClient.getBlob(
      `/api/v1/payroll/payslips/descarga-masiva/`,
      { planilla_id: planillaId },
    );
    return response.data;
  },

  // ========== Calendarios de Pago ==========

  async listCalendarios(params?: {
    periodo?: string;
    modalidad?: ModalidadContrato;
    estado?: EstadoCalendario;
  }): Promise<CalendarioPago[]> {
    const response = await apiClient.get("/api/v1/payroll/payment-schedules/", {
      params,
    });
    return extractTypedList<CalendarioPago>(response.data);
  },

  async getCalendario(id: number): Promise<CalendarioPago> {
    const response = await apiClient.get<ApiEnvelope<CalendarioPago>>(
      `/api/v1/payroll/payment-schedules/${id}/`,
    );
    return response.data.data || (response.data as unknown as CalendarioPago);
  },

  async createCalendario(
    payload: CalendarioPagoPayload,
  ): Promise<CalendarioPago> {
    const response = await apiClient.post<ApiEnvelope<CalendarioPago>>(
      "/api/v1/payroll/payment-schedules/",
      payload,
    );
    return response.data.data || (response.data as unknown as CalendarioPago);
  },

  async updateCalendario(
    id: number,
    payload: Partial<CalendarioPagoPayload>,
  ): Promise<CalendarioPago> {
    const response = await apiClient.patch<ApiEnvelope<CalendarioPago>>(
      `/api/v1/payroll/payment-schedules/${id}/`,
      payload,
    );
    return response.data.data || (response.data as unknown as CalendarioPago);
  },

  async removeCalendario(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/payroll/payment-schedules/${id}/`);
  },
};
