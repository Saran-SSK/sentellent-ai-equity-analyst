import { useCallback } from "react";
import { useContext } from "react";
import { ToastContext } from "@/components/providers/ToastProvider";

export interface ToastOptions {
  duration?: number;
  type?: "success" | "error" | "info" | "warning";
}

export function useToast() {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }

  const toast = useCallback(
    (message: string, options: ToastOptions = {}) => {
      context.show(message, options);
    },
    [context]
  );

  return { toast };
}
