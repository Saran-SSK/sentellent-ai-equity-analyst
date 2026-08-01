"use client";

import { ReactNode } from "react";
import { ArrowUp, ArrowDown } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  change?: number;
  icon?: ReactNode;
  trend?: "up" | "down" | "neutral";
}

export default function StatCard({
  label,
  value,
  change,
  icon,
  trend,
}: StatCardProps) {
  const getTrendColor = () => {
    if (!trend) return "text-text-tertiary";
    if (trend === "up") return "text-success";
    if (trend === "down") return "text-danger";
    return "text-text-tertiary";
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend === "up") return <ArrowUp className="w-4 h-4" />;
    if (trend === "down") return <ArrowDown className="w-4 h-4" />;
    return null;
  };

  return (
    <div className="card-base">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-text-tertiary text-sm font-medium mb-2">{label}</p>
          <h3 className="text-2xl font-bold text-text-primary">{value}</h3>
        </div>
        {icon && <div className="text-primary text-2xl">{icon}</div>}
      </div>

      {change !== undefined && (
        <div className={`flex items-center gap-1 ${getTrendColor()}`}>
          {getTrendIcon()}
          <span className="text-sm font-medium">
            {change > 0 ? "+" : ""}
            {change.toFixed(2)}%
          </span>
        </div>
      )}
    </div>
  );
}
