"use client";

import { useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import DataTable, { Column } from "@/components/tables/DataTable";
import StatCard from "@/components/cards/StatCard";
import { MOCK_PORTFOLIO } from "@/utils/mockData";
import { PortfolioHolding } from "@/types";
import {
  formatCurrency,
  formatPercent,
  getChangeColor,
  formatNumber,
} from "@/utils/format";
import { TrendingUp, TrendingDown } from "lucide-react";

export default function PortfolioPage() {
  const portfolio = MOCK_PORTFOLIO;

  // Chart data for performance
  const performanceData = [
    { month: "Jan", value: 550000 },
    { month: "Feb", value: 580000 },
    { month: "Mar", value: 600000 },
    { month: "Apr", value: 620000 },
    { month: "May", value: 650000 },
    { month: "Jun", value: 670000 },
    { month: "Jul", value: 695000 },
    { month: "Aug", value: 720000 },
    { month: "Sep", value: 695000 },
    { month: "Oct", value: 715000 },
    { month: "Nov", value: 740000 },
    { month: "Dec", value: 750000 },
  ];

  const columns: Column<PortfolioHolding>[] = [
    {
      key: "stock",
      label: "Stock",
      render: (value: any) => (
        <div>
          <div className="font-semibold text-text-primary">{value.ticker}</div>
          <div className="text-xs text-text-tertiary">{value.company}</div>
        </div>
      ),
      width: "200px",
    },
    {
      key: "quantity",
      label: "Quantity",
      render: (value) => formatNumber(value as number),
    },
    {
      key: "averagePrice",
      label: "Avg Price",
      render: (value) => formatCurrency(value as number),
    },
    {
      key: "currentPrice",
      label: "Current Price",
      render: (value) => formatCurrency(value as number),
    },
    {
      key: "value",
      label: "Value",
      render: (value) => formatCurrency(value as number),
    },
    {
      key: "gainLossPercent",
      label: "Gain/Loss %",
      render: (value, row) => (
        <span className={getChangeColor((row as PortfolioHolding).gainLoss)}>
          {formatPercent((value as number))}
        </span>
      ),
    },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-text-primary mb-2">
          Portfolio
        </h1>
        <p className="text-text-tertiary">Track and manage your investments</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          label="Total Value"
          value={formatCurrency(portfolio.totalValue)}
          change={portfolio.totalGainLossPercent}
          trend={portfolio.totalGainLoss >= 0 ? "up" : "down"}
          icon={<TrendingUp className="w-6 h-6" />}
        />
        <StatCard
          label="Total Invested"
          value={formatCurrency(portfolio.totalInvested)}
        />
        <StatCard
          label="Total Gain/Loss"
          value={formatCurrency(portfolio.totalGainLoss)}
          trend={portfolio.totalGainLoss >= 0 ? "up" : "down"}
        />
        <StatCard
          label="Holdings"
          value={portfolio.holdings.length.toString()}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Performance Chart */}
        <div className="lg:col-span-2 card-base">
          <h2 className="text-xl font-semibold text-text-primary mb-6">
            Portfolio Performance
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
              <XAxis stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#111827",
                  border: "1px solid #1F2937",
                  borderRadius: "8px",
                }}
                labelStyle={{ color: "#FFFFFF" }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#2563EB"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Sector Allocation */}
        <div className="card-base">
          <h2 className="text-xl font-semibold text-text-primary mb-6">
            Sector Allocation
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={portfolio.sectorAllocation}
                dataKey="value"
                nameKey="sector"
                cx="50%"
                cy="50%"
                outerRadius={80}
              >
                {portfolio.sectorAllocation.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#111827",
                  border: "1px solid #1F2937",
                  borderRadius: "8px",
                }}
                labelStyle={{ color: "#FFFFFF" }}
              />
            </PieChart>
          </ResponsiveContainer>

          {/* Legend */}
          <div className="space-y-2 mt-6">
            {portfolio.sectorAllocation.map((sector) => (
              <div key={sector.sector} className="flex items-center gap-3">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: sector.color }}
                />
                <div className="flex-1">
                  <div className="text-sm text-text-primary">
                    {sector.sector}
                  </div>
                  <div className="text-xs text-text-tertiary">
                    {sector.percent.toFixed(1)}%
                  </div>
                </div>
                <div className="text-sm font-semibold text-text-primary">
                  {formatCurrency(sector.value)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Holdings Table */}
      <div className="card-base">
        <h2 className="text-xl font-semibold text-text-primary mb-6">
          Current Holdings
        </h2>
        <DataTable columns={columns} data={portfolio.holdings} />
      </div>
    </div>
  );
}
