"use client"

import { useState, useEffect } from "react"
import { TrendingUp, TrendingDown, DollarSign, PieChart, Loader2, List } from "lucide-react"
import StatCard from "@/components/cards/StatCard"
import NewsCard from "@/components/cards/NewsCard"
import { MOCK_NEWS } from "@/utils/mockData"
import { useRouter } from "next/navigation"
import Link from "next/link"

interface BackendWatchlist {
  id: number;
  name: string;
  companies: any[];
}

interface BackendPortfolio {
  id: number;
  name: string;
  holdings: any[];
}

export default function DashboardPage() {
  const [watchlists, setWatchlists] = useState<BackendWatchlist[]>([])
  const [portfolios, setPortfolios] = useState<BackendPortfolio[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token")
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  const fetchData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

      const [watchlistsRes, portfoliosRes] = await Promise.all([
        fetch(`${backendUrl}/api/v1/watchlists`, { headers: getAuthHeaders() }),
        fetch(`${backendUrl}/api/v1/portfolios`, { headers: getAuthHeaders() }),
      ])

      if (watchlistsRes.status === 401 || portfoliosRes.status === 401) {
        router.push("/signin")
        return
      }

      if (!watchlistsRes.ok || !portfoliosRes.ok) {
        throw new Error("Failed to fetch data")
      }

      const watchlistsData: BackendWatchlist[] = await watchlistsRes.json()
      const portfoliosData: BackendPortfolio[] = await portfoliosRes.json()

      setWatchlists(watchlistsData)
      setPortfolios(portfoliosData)
    } catch (err) {
      setError("Failed to load dashboard data")
      console.error("Error fetching data:", err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const totalWatchlists = watchlists.length
  const totalPortfolios = portfolios.length
  const totalHoldings = portfolios.reduce((sum, p) => sum + p.holdings.length, 0)
  const recentPortfolio = portfolios.length > 0 ? portfolios[0].name : "None"

  const stats = [
    {
      label: "Total Watchlists",
      value: totalWatchlists.toString(),
      icon: <List className="w-6 h-6" />,
    },
    {
      label: "Total Portfolios",
      value: totalPortfolios.toString(),
      icon: <PieChart className="w-6 h-6" />,
    },
    {
      label: "Total Holdings",
      value: totalHoldings.toString(),
      icon: <DollarSign className="w-6 h-6" />,
    },
    {
      label: "Recent Portfolio",
      value: recentPortfolio,
      icon: <TrendingUp className="w-6 h-6" />,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Dashboard</h1>
        <p className="text-text-tertiary mt-1">Welcome back! Here's your portfolio overview.</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-lg bg-danger/10 border border-danger/30 text-danger">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((stat) => (
              <StatCard key={stat.label} {...stat} />
            ))}
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Watchlists */}
            <div className="lg:col-span-2">
              <div className="card-base">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-text-primary">Watchlists</h2>
                  <Link href="/watchlists" className="text-sm text-primary hover:text-primary/80 transition-colors">
                    View All
                  </Link>
                </div>
                {watchlists.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-2">📋</div>
                    <p className="text-text-tertiary">No watchlists yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {watchlists.slice(0, 5).map((watchlist) => (
                      <Link key={watchlist.id} href={`/watchlists/${watchlist.id}`}>
                        <div className="flex items-center justify-between p-3 rounded-lg bg-background hover:bg-card transition-colors">
                          <div>
                            <div className="font-medium text-text-primary">{watchlist.name}</div>
                            <div className="text-xs text-text-tertiary">
                              {watchlist.companies.length} {watchlist.companies.length === 1 ? 'company' : 'companies'}
                            </div>
                          </div>
                          <div className="text-text-tertiary">→</div>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Market News */}
            <div>
              <div className="card-base">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-text-primary">Market News</h2>
                  <Link href="/market-news" className="text-sm text-primary hover:text-primary/80 transition-colors">
                    View All
                  </Link>
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
              <Link key="analyze" href="/ai" className="p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-all text-left">
                <div className="text-primary mb-2">📊</div>
                <div className="text-sm font-medium text-text-primary">Analyze Stock</div>
                <div className="text-xs text-text-tertiary">Get AI insights</div>
              </Link>
              <Link key="watchlist" href="/watchlists" className="p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-all text-left">
                <div className="text-primary mb-2">📈</div>
                <div className="text-sm font-medium text-text-primary">Create Watchlist</div>
                <div className="text-xs text-text-tertiary">Track stocks</div>
              </Link>
              <Link key="news" href="/market-news" className="p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-all text-left">
                <div className="text-primary mb-2">📰</div>
                <div className="text-sm font-medium text-text-primary">Market News</div>
                <div className="text-xs text-text-tertiary">Latest updates</div>
              </Link>
              <Link key="research" href="/research" className="p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-all text-left">
                <div className="text-primary mb-2">🔬</div>
                <div className="text-sm font-medium text-text-primary">Research</div>
                <div className="text-xs text-text-tertiary">Deep dive</div>
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
