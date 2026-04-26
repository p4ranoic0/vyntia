import { apiClient } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// Interface for paginated API response
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Interface for pagination parameters
export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  [key: string]: any;
}

export function useEmpleados(params?: PaginationParams) {
  // Transformar parámetros para compatibilidad con el backend
  const transformedParams = params
    ? {
        ...params,
        // Convertir estado boolean a string esperado por el backend
        ...(params.estado === "true" && { estado: "activo" }),
        ...(params.estado === "false" && { estado: "inactivo" }),
      }
    : params;

  // Filtrar valores undefined/null para evitar enviar params vacíos al backend
  const cleanParams = transformedParams
    ? Object.fromEntries(
        Object.entries(transformedParams).filter(
          ([, v]) => v !== undefined && v !== null && v !== "",
        ),
      )
    : transformedParams;

  return useQuery({
    queryKey: ["empleados", cleanParams],
    queryFn: () => apiClient.getEmpleados(cleanParams),
    keepPreviousData: true, // Keep previous data while loading new page
  });
}

export function useCreateEmpleado() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: any) => apiClient.createEmpleado(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["empleados"] });
    },
  });
}

export function useUpdateEmpleado() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      apiClient.updateEmpleado(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["empleados"] });
    },
  });
}

export function useDeleteEmpleado() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => apiClient.deleteEmpleado(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["empleados"] });
    },
  });
}

// Similar hooks for other entities
export function useAreas(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["areas", params],
    queryFn: () => apiClient.getAreas(params),
  });
}

export function useBoletas(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["boletas", params],
    queryFn: () => apiClient.getBoletas(params),
  });
}

export function useUsuarios(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["usuarios", params],
    queryFn: () => apiClient.getUsuarios(params),
  });
}

export function useRoles(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["roles", params],
    queryFn: () => apiClient.getRoles(params),
  });
}
