"use client";

import { Stock } from "@/types";
import { formatCurrency, formatPercent, getChangeColor } from "@/utils/format";
import { TrendingUp, TrendingDown } from "lucide-react";

interface StockCardProps {
  stock: Stock;
  showSector?: boolean;
  onClick?: () => void;
}

export default function StockCard({ stock, showSector = true, onClick }: StockCardProps) {
  const isPositive = stock.change >= 0;

  return (
    <div
      onClick={onClick}
      className="card-base cursor-pointer"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h4 className="font-semibold text-text-primary">{stock.ticker}</h4>
          <p className="text-sm text-text-tertiary">{stock.company}</p>
        </div>
        {isPositive ? (
          <TrendingUp className="w-5 h-5 text-success" />
        ) : (
          <TrendingDown className="w-5 h-5 text-danger" />
        )}
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-text-tertiary text-xs mb-1">Price</p>
          <p className="text-xl font-bold text-text-primary">
            {formatCurrency(stock.currentPrice)}
          </p>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-text-tertiary text-xs mb-1">Change</p>
            <p className={`font-semibold ${getChangeColor(stock.change)}`}>
              {formatPercent(stock.changePercent)}
            </p>
          </div>

          {showSector && (
            <div>
              <p className="text-text-tertiary text-xs mb-1">Sector</p>
              <p className="text-sm font-medium text-text-primary">
                {stock.sector}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
