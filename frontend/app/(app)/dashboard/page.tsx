"use client"

import { useState, useEffect } from "react"
import { TrendingUp, DollarSign, PieChart, Loader2, List, Plus, Briefcase, Sparkles, ArrowUp } from "lucide-react"
import StatCard from "@/components/cards/StatCard"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useSession } from "next-auth/react"

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
  const { data: session } = useSession()
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
        <p className="text-text-tertiary mt-1">
          Welcome back, {session?.user?.name || ""} 👋 Here's your portfolio overview.
        </p>
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
          <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_320px] gap-6 items-start">
            {/* Left Column */}
            <div className="space-y-6">
              {/* Personalized Market News */}
              <div className="card-base">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-text-primary">Personalized Market News</h2>
                </div>
                <div className="text-sm text-text-tertiary">
                  Your watchlists and portfolio context will be reflected here as part of the dashboard experience.
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="card-base">
                <h2 className="text-lg font-semibold text-text-primary mb-4">Quick Actions</h2>
                <div className="space-y-3">
                  <Link href="/watchlists" className="flex items-center gap-3 p-4 rounded-xl bg-gradient-to-r from-primary/15 to-blue-600/15 hover:from-primary/25 hover:to-blue-600/25 transition-all w-full border border-primary/20">
                    <div className="w-10 h-10 rounded-lg bg-primary/30 flex items-center justify-center flex-shrink-0">
                      <Plus className="w-5 h-5 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-text-primary">Create Watchlist</div>
                      <div className="text-xs text-text-tertiary">Track your stocks</div>
                    </div>
                  </Link>
                  <Link href="/portfolio" className="flex items-center gap-3 p-4 rounded-xl bg-gradient-to-r from-primary/15 to-blue-600/15 hover:from-primary/25 hover:to-blue-600/25 transition-all w-full border border-primary/20">
                    <div className="w-10 h-10 rounded-lg bg-primary/30 flex items-center justify-center flex-shrink-0">
                      <Briefcase className="w-5 h-5 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-text-primary">Update Portfolio</div>
                      <div className="text-xs text-text-tertiary">Manage holdings</div>
                    </div>
                  </Link>
                </div>
              </div>

              {/* AI Research Ready */}
              <Link href="/chat" className="card-base block hover:border-primary/30 transition-all group">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-text-primary group-hover:text-primary transition-colors">AI Research Ready</div>
                    <div className="text-xs text-text-tertiary">Start analyzing stocks</div>
                  </div>
                  <ArrowUp className="w-5 h-5 text-text-tertiary group-hover:text-primary transition-colors" />
                </div>
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
