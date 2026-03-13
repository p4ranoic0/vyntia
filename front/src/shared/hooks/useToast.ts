/**
 * useToast Hook - SHARED
 *
 * Hook genérico para mostrar notificaciones toast.
 *
 * Uso:
 * const { toast } = useToast()
 * toast.success('Guardado exitosamente')
 * toast.error('Ocurrió un error')
 * toast.info('Información')
 * toast.warning('Cuidado')
 */

import { useToast as useChakraToast } from "@/components/ui/use-toast";
import { useCallback } from "react";

type ToastType = "success" | "error" | "info" | "warning";

interface ToastOptions {
  duration?: number;
  isClosable?: boolean;
}

export const useToast = () => {
  const toast = useChakraToast();

  const showToast = useCallback(
    (
      title: string,
      description?: string,
      type: ToastType = "info",
      options: ToastOptions = {},
    ) => {
      const { duration = 3000, isClosable = true } = options;

      toast({
        title,
        description,
        status: type,
        duration,
        isClosable,
        position: "bottom-right",
      });
    },
    [toast],
  );

  return {
    toast: {
      success: (title: string, description?: string) =>
        showToast(title, description, "success"),
      error: (title: string, description?: string) =>
        showToast(title, description, "error"),
      info: (title: string, description?: string) =>
        showToast(title, description, "info"),
      warning: (title: string, description?: string) =>
        showToast(title, description, "warning"),
    },
  };
};
