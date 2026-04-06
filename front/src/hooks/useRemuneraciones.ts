import {
  remuneracionesService,
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
} from "@/services/remuneracionesService";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// ========== Configuración AFP ==========

export function useConfiguracionAfp(params?: {
  vigencia_mes?: string;
  estado?: "activo" | "inactivo";
}) {
  return useQuery({
    queryKey: ["configuracion-afp", params],
    queryFn: () => remuneracionesService.listAfp(params),
  });
}

export function useCreateAfp() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: remuneracionesService.createAfp,
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
    }) => remuneracionesService.updateAfp(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configuracion-afp"] });
    },
  });
}

export function useDeleteAfp() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.removeAfp(id),
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
    queryFn: () => remuneracionesService.listUit(params),
  });
}

export function useGetUit(id: number | null) {
  return useQuery({
    queryKey: ["configuracion-uit", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar una configuración UIT");
      }
      return remuneracionesService.getUit(id);
    },
    enabled: Boolean(id),
  });
}

export function useCreateUit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ConfiguracionUitPayload) =>
      remuneracionesService.createUit(data),
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
    }) => remuneracionesService.updateUit(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configuracion-uit"] });
    },
  });
}

export function useDeleteUit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.removeUit(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configuracion-uit"] });
    },
  });
}

export function useActivarUit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.activarUit(id),
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
    queryFn: () => remuneracionesService.list(params),
  });
}

export function useCreateConcepto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: remuneracionesService.create,
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
    }) => remuneracionesService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conceptos-remuneracion"] });
    },
  });
}

export function useDeleteConcepto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.remove(id),
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
    queryFn: () => remuneracionesService.listPlanillas(params),
  });
}

export function usePlanilla(id: number | null) {
  return useQuery({
    queryKey: ["planillas-mensuales", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar una planilla");
      }
      return remuneracionesService.getPlanilla(id);
    },
    enabled: Boolean(id),
  });
}

export function useCreatePlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PlanillaMensualPayload) =>
      remuneracionesService.createPlanilla(data),
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
    }) => remuneracionesService.updatePlanilla(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

export function useDeletePlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.removePlanilla(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

// Acciones especiales de planilla
export function useGenerarPlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.generarPlanilla(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales", id] });
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
    },
  });
}

export function useRegenerarPlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.regenerarPlanilla(id),
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
    mutationFn: (id: number) => remuneracionesService.calcularPlanilla(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales", id] });
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
    },
  });
}

export function usePreviewPlanilla() {
  return useMutation<VistaPreviaPlanilla, unknown, number>({
    mutationFn: (id: number) => remuneracionesService.previewPlanilla(id),
  });
}

export function useAprobarPlanilla() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.aprobarPlanilla(id),
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
      return remuneracionesService.getEstadisticasPlanilla(id);
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
    queryFn: () => remuneracionesService.listDetalles(params),
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
      return remuneracionesService.getDetalle(id);
    },
    enabled: Boolean(id),
  });
}

export function useCreateDetalle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: DetallePlanillaPayload) =>
      remuneracionesService.createDetalle(data),
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
    }) => remuneracionesService.updateDetalle(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
      queryClient.invalidateQueries({ queryKey: ["planillas-mensuales"] });
    },
  });
}

export function useDeleteDetalle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.removeDetalle(id),
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
    queryFn: () => remuneracionesService.listDescuentos(params),
  });
}

export function useDescuentoMasivo(id: number | null) {
  return useQuery({
    queryKey: ["descuentos-masivos", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar un descuento");
      }
      return remuneracionesService.getDescuento(id);
    },
    enabled: Boolean(id),
  });
}

export function useCreateDescuento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: DescuentoMasivoPayload) =>
      remuneracionesService.createDescuento(data),
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
    }) => remuneracionesService.updateDescuento(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["descuentos-masivos"] });
    },
  });
}

export function useDeleteDescuento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.removeDescuento(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["descuentos-masivos"] });
      queryClient.invalidateQueries({ queryKey: ["detalles-planilla"] });
    },
  });
}

export function useProcesarDescuento() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.procesarDescuento(id),
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
    mutationFn: (id: number) => remuneracionesService.anularDescuento(id),
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
      remuneracionesService.generarBoletas(planillaId),
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
    queryFn: () => remuneracionesService.listBoletas(params),
  });
}

export function useBoleta(id: number | null) {
  return useQuery({
    queryKey: ["boletas-pago", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar una boleta");
      }
      return remuneracionesService.getBoleta(id);
    },
    enabled: Boolean(id),
  });
}

export function useDownloadBoletaPdf() {
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.downloadBoletaPdf(id),
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
      remuneracionesService.descargaMasivaBoletas(planillaId),
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
    queryFn: () => remuneracionesService.listCalendarios(params),
  });
}

export function useCalendarioPago(id: number | null) {
  return useQuery({
    queryKey: ["calendarios-pago", id],
    queryFn: () => {
      if (!id) {
        throw new Error("Debe indicar un calendario");
      }
      return remuneracionesService.getCalendario(id);
    },
    enabled: Boolean(id),
  });
}

export function useCreateCalendario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CalendarioPagoPayload) =>
      remuneracionesService.createCalendario(data),
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
    }) => remuneracionesService.updateCalendario(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendarios-pago"] });
    },
  });
}

export function useDeleteCalendario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => remuneracionesService.removeCalendario(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendarios-pago"] });
    },
  });
}
