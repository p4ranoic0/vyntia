import { apiClient } from "@/shared/api/api";
import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- open-ended filter params from API consumers
  [key: string]: any;
}

export function useEmpleados(params?: PaginationParams) {
  const transformedParams = params
    ? {
        ...params,
        ...(params.estado === "true" && { estado: "activo" }),
        ...(params.estado === "false" && { estado: "inactivo" }),
      }
    : params;

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
    // React Query v5: `keepPreviousData: true` (v4) was removed and is ignored
    // silently. Without this the query key change on every debounced search term
    // produces a fresh pending query, the page falls back to its full skeleton,
    // and the search input unmounts — losing focus mid-typing.
    placeholderData: keepPreviousData,
  });
}

export function useCreateEmpleado() {
  const queryClient = useQueryClient();
  return useMutation({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API client accepts any employee shape
    mutationFn: (data: any) => apiClient.createEmpleado(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["empleados"] }),
  });
}

export function useUpdateEmpleado() {
  const queryClient = useQueryClient();
  return useMutation({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- API client accepts any employee patch shape
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      apiClient.updateEmpleado(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["empleados"] }),
  });
}

export function useDeleteEmpleado() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.deleteEmpleado(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["empleados"] }),
  });
}
