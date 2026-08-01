"use client"

import { TrendingUp, TrendingDown, DollarSign, PieChart } from "lucide-react"
import StatCard from "@/components/cards/StatCard"
import StockCard from "@/components/cards/StockCard"
import NewsCard from "@/components/cards/NewsCard"
import { MOCK_STOCKS, MOCK_NEWS } from "@/utils/mockData"

export default function DashboardPage() {
  const stats = [
    {
      label: "Portfolio Value",
      value: "₹12,45,678",
      change: 12.5,
      trend: "up" as const,
      icon: <DollarSign />,
    },
    {
      label: "Today's P&L",
      value: "+₹8,234",
      change: 2.3,
      trend: "up" as const,
      icon: <TrendingUp />,
    },
    {
      label: "Total Returns",
      value: "₹1,45,678",
      change: 15.8,
      trend: "up" as const,
      icon: <PieChart />,
    },
    {
      label: "Nifty 50",
      value: "19,234.50",
      change: -0.5,
      trend: "down" as const,
      icon: <TrendingDown />,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Dashboard</h1>
        <p className="text-text-tertiary mt-1">Welcome back! Here's your portfolio overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <StatCard key={stat.label} {...stat} />
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Watchlist */}
        <div className="lg:col-span-2">
          <div className="card-base">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">Watchlist</h2>
              <button className="text-sm text-primary hover:text-primary/80 transition-colors">
                View All
              </button>
            </div>
            <div className="space-y-3">
              {MOCK_STOCKS.slice(0, 5).map((stock) => (
                <StockCard key={stock.symbol} stock={stock} />
              ))}
            </div>
          </div>
        </div>

        {/* Market News */}
        <div>
          <div className="card-base">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-text-primary">Market News</h2>
              <button className="text-sm text-primary hover:text-primary/80 transition-colors">
                View All
              </button>
            </div>
            <div className="space-y-3">
              {MOCK_NEWS.slice(0, 4).map((news) => (
                <NewsCard key={news.id} article={news} />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card-base">
        <h2 className="text-lg font-semibold text-text-primary mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button key="analyze" className="p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-all text-left">
            <div className="text-primary mb-2">📊</div>
            <div className="text-sm font-medium text-text-primary">Analyze Stock</div>
            <div className="text-xs text-text-tertiary">Get AI insights</div>
          </button>
          <button key="watchlist" className="p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-all text-left">
            <div className="text-primary mb-2">📈</div>
            <div className="text-sm font-medium text-text-primary">Create Watchlist</div>
            <div className="text-xs text-text-tertiary">Track stocks</div>
          </button>
          <button key="news" className="p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-all text-left">
            <div className="text-primary mb-2">📰</div>
            <div className="text-sm font-medium text-text-primary">Market News</div>
            <div className="text-xs text-text-tertiary">Latest updates</div>
          </button>
          <button key="research" className="p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-all text-left">
            <div className="text-primary mb-2">🔬</div>
            <div className="text-sm font-medium text-text-primary">Research</div>
            <div className="text-xs text-text-tertiary">Deep dive</div>
          </button>
        </div>
      </div>
    </div>
  )
}
