import {
  payrollService,
  type CalendarioPagoPayload,
  type ConceptoRemuneracion,
  type ConfiguracionAfp,
  type ConfiguracionUitPayload,
  type DescuentoMasivo,
  type DescuentoMasivoPayload,
  type DetallePlanillaPayload,
  type EstadoBoleta,
  type EstadoCalendario,
  type EstadoDescuento,
  type EstadoDetalle,
  type EstadoPlanilla,
  type ModalidadContrato,
  type PlanillaMensualPayload,
  type VistaPreviaPlanilla,
} from "@/features/payroll/services/payrollService";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ========== Configuración AFP ==========

export function useConfiguracionAfp(params?: {
  vigencia_mes?: string;
  estado?: "activo" | "inactivo";
}) {
  return useQuery({
    queryKey: ["configuracion-afp", params],
    queryFn: () => payrollService.listAfp(params),
  });
}

export function useCreateAfp() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: payrollService.createAfp,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configuracion-afp"] });
    },
  });
}

export function useUpdateAfp() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Partial<ConfiguracionAfp>;
    }) => payrollService.updateAfp(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configuracion-afp"] });
    },
  });
}

export function useDeleteAfp() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.removeAfp(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configuracion-afp"] });
    },
  });
}

// ========== Configuración UIT ==========

export function useConfiguracionUit(params?: {
  anio?: number;
  estado?: "activo" | "inactivo";
  activo?: boolean;
}) {
  return useQuery({
    queryKey: ["configuracion-uit", params],
    queryFn: () => payrollService.listUit(params),
  });
}

export function useGetUit(id: number | null) {
  return useQuery({
    queryKey: ["configuracion-uit", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar una configuración UIT");
      }
      return payrollService.getUit(id);
    },
    enabled: Boolean(id),
  });
}

export function useCreateUit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ConfiguracionUitPayload) =>
      payrollService.createUit(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configuracion-uit"] });
    },
  });
}

export function useUpdateUit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Partial<ConfiguracionUitPayload>;
    }) => payrollService.updateUit(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configuracion-uit"] });
    },
  });
}

export function useDeleteUit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.removeUit(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configuracion-uit"] });
    },
  });
}

export function useActivarUit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.activarUit(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configuracion-uit"] });
    },
  });
}

// ========== Configuración Remuneraciones ==========

export function useConceptosRemuneracion(params?: {
  tipo?: "ingreso" | "descuento";
  estado?: "activo" | "inactivo";
  search?: string;
}) {
  return useQuery({
    queryKey: ["conceptos-remuneracion", params],
    queryFn: () => payrollService.list(params),
  });
}

export function useCreateConcepto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: payrollService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conceptos-remuneracion"] });
    },
  });
}

export function useUpdateConcepto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Partial<ConceptoRemuneracion>;
    }) => payrollService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conceptos-remuneracion"] });
    },
  });
}

export function useDeleteConcepto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conceptos-remuneracion"] });
    },
  });
}

// ========== Planillas Mensuales ==========

export function usePlanillas(params?: {
  periodo?: string;
  modalidad?: ModalidadContrato;
  estado?: EstadoPlanilla;
  meta_presupuestal?: string;
}) {
  return useQuery({
    queryKey: ["planillas-mensuales", params],
    queryFn: () => payrollService.listPlanillas(params),
  });
}

export function usePlanilla(id: number | null) {
  return useQuery({
    queryKey: ["planillas-mensuales", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar una planilla");
      }
      return payrollService.getPlanilla(id);
    },
    enabled: Boolean(id),
  });
}

export function useCreatePlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PlanillaMensualPayload) =>
      payrollService.createPlanilla(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

export function useUpdatePlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Partial<PlanillaMensualPayload>;
    }) => payrollService.updatePlanilla(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

export function useDeletePlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.removePlanilla(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

// Acciones especiales de planilla
export function useGenerarPlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.generarPlanilla(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales", id] });
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
    },
  });
}

export function useRegenerarPlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.regenerarPlanilla(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales", id] });
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
    },
  });
}

export function useCalcularPlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.calcularPlanilla(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales", id] });
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
    },
  });
}

export function usePreviewPlanilla() {
  return useMutation<VistaPreviaPlanilla, unknown, number>({
    mutationFn: (id: number) => payrollService.previewPlanilla(id),
  });
}

export function useAprobarPlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.aprobarPlanilla(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales", id] });
    },
  });
}

export function useEstadisticasPlanilla(id: number | null) {
  return useQuery({
    queryKey: ["planillas-mensuales", id, "estadisticas"],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar una planilla");
      }
      return payrollService.getEstadisticasPlanilla(id);
    },
    enabled: Boolean(id),
  });
}

// ========== Detalles de Planilla ==========

export function useDetallesPlanilla(params?: {
  planilla?: number;
  empleado?: number;
  estado?: EstadoDetalle;
}) {
  return useQuery({
    queryKey: ["detalles-planilla", params],
    queryFn: () => payrollService.listDetalles(params),
    enabled: !!params?.planilla, // Solo cargar si hay una planilla seleccionada
  });
}

export function useDetallePlanilla(id: number | null) {
  return useQuery({
    queryKey: ["detalles-planilla", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar un detalle");
      }
      return payrollService.getDetalle(id);
    },
    enabled: Boolean(id),
  });
}

export function useCreateDetalle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: DetallePlanillaPayload) =>
      payrollService.createDetalle(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

export function useUpdateDetalle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Partial<DetallePlanillaPayload>;
    }) => payrollService.updateDetalle(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

export function useDeleteDetalle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.removeDetalle(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

// ========== Descuentos Masivos ==========

export function useDescuentosMasivos(params?: {
  periodo?: string;
  estado?: EstadoDescuento;
}) {
  return useQuery({
    queryKey: ["descuentos-masivos", params],
    queryFn: () => payrollService.listDescuentos(params),
  });
}

export function useDescuentoMasivo(id: number | null) {
  return useQuery({
    queryKey: ["descuentos-masivos", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar un descuento");
      }
      return payrollService.getDescuento(id);
    },
    enabled: Boolean(id),
  });
}

export function useCreateDescuento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: DescuentoMasivoPayload) =>
      payrollService.createDescuento(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["descuentos-masivos"] });
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
    },
  });
}

export function useUpdateDescuento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Partial<DescuentoMasivo>;
    }) => payrollService.updateDescuento(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["descuentos-masivos"] });
    },
  });
}

export function useDeleteDescuento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.removeDescuento(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["descuentos-masivos"] });
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
    },
  });
}

export function useProcesarDescuento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.procesarDescuento(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["descuentos-masivos"] });
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

export function useAnularDescuento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.anularDescuento(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["descuentos-masivos"] });
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

// ========== Boletas de Pago ==========

export function useGenerarBoletas() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (planillaId: number) =>
      payrollService.generarBoletas(planillaId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["boletas-pago"] });
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

export function useBoletas(params?: {
  empleado?: number;
  periodo?: string;
  estado?: EstadoBoleta;
}) {
  return useQuery({
    queryKey: ["boletas-pago", params],
    queryFn: () => payrollService.listBoletas(params),
  });
}

export function useBoleta(id: number | null) {
  return useQuery({
    queryKey: ["boletas-pago", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar una boleta");
      }
      return payrollService.getBoleta(id);
    },
    enabled: Boolean(id),
  });
}

export function useDownloadBoletaPdf() {
  return useMutation({
    mutationFn: (id: number) => payrollService.downloadBoletaPdf(id),
    onSuccess: (blob, id) => {
      // Crear URL del blob y descargar automáticamente
      const url = globalThis.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `boleta-pago-${id}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      globalThis.URL.revokeObjectURL(url);
    },
  });
}

export function useDescargaMasivaBoletas() {
  return useMutation({
    mutationFn: (planillaId: number) =>
      payrollService.descargaMasivaBoletas(planillaId),
    onSuccess: (blob, planillaId) => {
      const url = globalThis.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `boletas-planilla-${planillaId}.zip`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      globalThis.URL.revokeObjectURL(url);
    },
  });
}

// ========== Calendarios de Pago ==========

export function useCalendariosPago(params?: {
  periodo?: string;
  modalidad?: ModalidadContrato;
  estado?: EstadoCalendario;
}) {
  return useQuery({
    queryKey: ["calendarios-pago", params],
    queryFn: () => payrollService.listCalendarios(params),
  });
}

export function useCalendarioPago(id: number | null) {
  return useQuery({
    queryKey: ["calendarios-pago", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar un calendario");
      }
      return payrollService.getCalendario(id);
    },
    enabled: Boolean(id),
  });
}

export function useCreateCalendario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CalendarioPagoPayload) =>
      payrollService.createCalendario(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendarios-pago"] });
    },
  });
}

export function useUpdateCalendario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Partial<CalendarioPagoPayload>;
    }) => payrollService.updateCalendario(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendarios-pago"] });
    },
  });
}

export function useDeleteCalendario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => payrollService.removeCalendario(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendarios-pago"] });
    },
  });
}
