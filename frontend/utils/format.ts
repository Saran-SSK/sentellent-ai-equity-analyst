export function formatCurrency(value: number): string {
  if (value >= 1000000) {
    return `₹${(value / 1000000).toFixed(2)} Cr`;
  }
  if (value >= 100000) {
    return `₹${(value / 100000).toFixed(2)} L`;
  }
  return `₹${value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatNumber(value: number): string {
  return value.toLocaleString("en-IN", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
}

export function formatPercent(value: number): string {
  return `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
}

export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatTime(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatDateTime(date: string | Date): string {
  return `${formatDate(date)} ${formatTime(date)}`;
}

export function formatVolume(volume: number): string {
  if (volume >= 1000000) {
    return `${(volume / 1000000).toFixed(2)}M`;
  }
  if (volume >= 1000) {
    return `${(volume / 1000).toFixed(2)}K`;
  }
  return formatNumber(volume);
}

export function getChangeColor(change: number): string {
  if (change > 0) return "text-success";
  if (change < 0) return "text-danger";
  return "text-text-tertiary";
}

export function getSentimentColor(
  sentiment: "positive" | "neutral" | "negative"
): string {
  switch (sentiment) {
    case "positive":
      return "bg-success/10 text-success";
    case "negative":
      return "bg-danger/10 text-danger";
    default:
      return "bg-warning/10 text-warning";
  }
}
