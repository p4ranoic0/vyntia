import { apiClient } from "@/shared/api/api";
import { useQuery } from "@tanstack/react-query";

export function useAreas(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["areas", params],
    queryFn: () => apiClient.getAreas(params),
  });
}
