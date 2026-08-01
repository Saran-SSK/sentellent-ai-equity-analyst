"use client";

import { CheckCircle, AlertCircle, Info, XCircle, X } from "lucide-react";

interface ToastProps {
  message: string;
  type: "success" | "error" | "info" | "warning";
  onClose: () => void;
}

export default function Toast({ message, type, onClose }: ToastProps) {
  const iconMap = {
    success: (
      <CheckCircle className="w-5 h-5 text-success flex-shrink-0" />
    ),
    error: <XCircle className="w-5 h-5 text-danger flex-shrink-0" />,
    warning: <AlertCircle className="w-5 h-5 text-warning flex-shrink-0" />,
    info: <Info className="w-5 h-5 text-primary flex-shrink-0" />,
  };

  const bgMap = {
    success: "bg-success/10 border-success/20",
    error: "bg-danger/10 border-danger/20",
    warning: "bg-warning/10 border-warning/20",
    info: "bg-primary/10 border-primary/20",
  };

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-xl border ${bgMap[type]} animate-fade-in`}
    >
      {iconMap[type]}
      <p className="flex-1 text-sm text-text-primary">{message}</p>
      <button
        onClick={onClose}
        className="text-text-tertiary hover:text-text-primary transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
