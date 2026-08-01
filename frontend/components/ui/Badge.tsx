"use client";

interface BadgeProps {
  children: string;
  variant?: "default" | "success" | "danger" | "warning" | "info";
  size?: "sm" | "md";
}

export default function Badge({
  children,
  variant = "default",
  size = "md",
}: BadgeProps) {
  const variantMap = {
    default: "bg-primary/10 text-primary",
    success: "bg-success/10 text-success",
    danger: "bg-danger/10 text-danger",
    warning: "bg-warning/10 text-warning",
    info: "bg-primary/10 text-primary",
  };

  const sizeMap = {
    sm: "px-2 py-1 text-xs",
    md: "px-3 py-1.5 text-sm",
  };

  return (
    <span
      className={`inline-block rounded-full font-medium ${variantMap[variant]} ${sizeMap[size]}`}
    >
      {children}
    </span>
  );
}
