"use client"

import { useState, useEffect } from "react"
import {
  TrendingUp,
  IndianRupee,
  PieChart,
  Loader2,
  List,
  Sparkles,
  ArrowUp,
  ChevronRight,
} from "lucide-react"
import StatCard from "@/components/cards/StatCard"
import InvestmentOpportunityCard from "@/components/cards/InvestmentOpportunityCard"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useSession } from "next-auth/react"

interface BackendWatchlist {
  id: number;
  name: string;
  companies: unknown[];
}

interface BackendPortfolio {
  id: number;
  name: string;
  holdings: Array<{
    symbol: string;
    quantity: number;
    average_buy_price: number;
  }>;
}

interface RecommendationItem {
  symbol: string
  name: string
  description: string
  current_price: number | null
  market_cap: number | null
  sector: string
  sentiment: string
  why_recommended: string[]
  score: number
}

interface RecentlyViewedCompany {
  symbol: string
  name: string
  sector: string
  sentiment: string
}

export default function DashboardPage() {
  const { data: session } = useSession()
  const [watchlists, setWatchlists] = useState<BackendWatchlist[]>([])
  const [portfolios, setPortfolios] = useState<BackendPortfolio[]>([])
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([])
  const [recentlyViewed, setRecentlyViewed] = useState<RecentlyViewedCompany[]>([])
  const [totalPortfolioValue, setTotalPortfolioValue] = useState<number>(0)
  const [isLoadingDashboard, setIsLoadingDashboard] = useState(true)
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(true)
  const [isLoadingRecentlyViewed, setIsLoadingRecentlyViewed] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token")
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  const fetchDashboardData = async () => {
    try {
      setIsLoadingDashboard(true)
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

      // Calculate total portfolio value
      await calculatePortfolioValue(portfoliosData)

    } catch (err) {
      setError("Failed to load dashboard data")
      console.error("Error fetching data:", err)
    } finally {
      setIsLoadingDashboard(false)
    }
  }

  const calculatePortfolioValue = async (portfolioData: BackendPortfolio[]) => {
    let totalValue = 0
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

    console.log("Calculating portfolio value for", portfolioData.length, "portfolios")
    console.log("Portfolio data:", JSON.stringify(portfolioData, null, 2))

    for (const portfolio of portfolioData) {
      console.log(`Processing portfolio: ${portfolio.name} with ${portfolio.holdings.length} holdings`)
      
      for (const holding of portfolio.holdings) {
        console.log(`Holding: symbol=${holding.symbol}, quantity=${holding.quantity}, average_buy_price=${holding.average_buy_price}`)
        
        try {
          const quoteRes = await fetch(
            `${backendUrl}/api/v1/companies/${holding.symbol}/quote`,
            { headers: getAuthHeaders() }
          )
          
          if (quoteRes.ok) {
            const quote = await quoteRes.json()
            const currentPrice = quote.current_price
            // Use current price if available and valid, otherwise fall back to buy price
            const priceToUse = (currentPrice && currentPrice > 0) ? currentPrice : (holding.average_buy_price || 0)
            const holdingValue = priceToUse * holding.quantity
            totalValue += holdingValue
            console.log(`${holding.symbol}: current_price=${currentPrice}, price_used=${priceToUse}, quantity=${holding.quantity}, value=${holdingValue}, running_total=${totalValue}`)
          } else {
            // Fallback to buy price if live quote fails
            const buyPrice = holding.average_buy_price || 0
            const holdingValue = buyPrice * holding.quantity
            totalValue += holdingValue
            console.log(`${holding.symbol}: Using buy price fallback=${buyPrice}, quantity=${holding.quantity}, value=${holdingValue}, running_total=${totalValue}`)
          }
        } catch (err) {
          console.error(`Error fetching quote for ${holding.symbol}:`, err)
          // Fallback to buy price on error
          const buyPrice = holding.average_buy_price || 0
          const holdingValue = buyPrice * holding.quantity
          totalValue += holdingValue
          console.log(`${holding.symbol}: Error - using buy price fallback=${buyPrice}, quantity=${holding.quantity}, value=${holdingValue}, running_total=${totalValue}`)
        }
      }
    }

    console.log("Total portfolio value calculated:", totalValue)
    setTotalPortfolioValue(totalValue)
  }

  const formatIndianCurrency = (value: number) => {
    if (value === 0) return "₹0"
    
    // Indian numbering system: Lakhs (1,00,000) and Crores (1,00,00,000)
    if (value >= 10000000) {
      return `₹${(value / 10000000).toFixed(2)} Cr`
    } else if (value >= 100000) {
      return `₹${(value / 100000).toFixed(2)} L`
    } else {
      return `₹${value.toLocaleString('en-IN')}`
    }
  }

  const fetchRecommendations = async () => {
    try {
      setIsLoadingRecommendations(true)
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

      const recommendationsRes = await fetch(
        `${backendUrl}/api/v1/companies/recommendations?limit=3`, 
        { headers: getAuthHeaders() }
      )

      if (recommendationsRes.ok) {
        const recommendationsData: RecommendationItem[] = await recommendationsRes.json()
        setRecommendations(recommendationsData)
      }
    } catch (err) {
      console.error("Error fetching recommendations:", err)
    } finally {
      setIsLoadingRecommendations(false)
    }
  }

  const fetchRecentlyViewed = async () => {
    try {
      setIsLoadingRecentlyViewed(true)
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

      console.log("Fetching recently viewed companies...")
      const recentlyViewedRes = await fetch(
        `${backendUrl}/api/v1/companies/recently-viewed?limit=3`,
        { headers: getAuthHeaders() }
      )

      console.log("Recently viewed response status:", recentlyViewedRes.status)
      
      if (recentlyViewedRes.ok) {
        const recentlyViewedData: RecentlyViewedCompany[] = await recentlyViewedRes.json()
        console.log("Recently viewed data:", recentlyViewedData)
        setRecentlyViewed(recentlyViewedData)
      } else {
        console.error("Failed to fetch recently viewed:", recentlyViewedRes.status, recentlyViewedRes.statusText)
      }
    } catch (err) {
      console.error("Error fetching recently viewed:", err)
    } finally {
      setIsLoadingRecentlyViewed(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    fetchRecommendations()
    fetchRecentlyViewed()
  }, [])

  const totalWatchlists = watchlists.length
  const totalPortfolios = portfolios.length
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
      value: formatIndianCurrency(totalPortfolioValue),
      icon: <IndianRupee className="w-6 h-6" />,
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
          Welcome back, {session?.user?.name || ""} 👋 Here&apos;s your portfolio overview.
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-lg bg-danger/10 border border-danger/30 text-danger">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoadingDashboard ? (
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
              {/* Investment Opportunities */}
              <div className="card-base">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-text-primary">Investment Opportunities</h2>
                  <Link href="/dashboard/opportunities" className="text-sm font-medium text-primary hover:text-primary/80 transition-colors">
                    View All
                  </Link>
                </div>
                <div className="space-y-3">
                  {isLoadingRecommendations ? (
                    // Loading skeleton matching InvestmentOpportunityCard layout
                    <>
                      <div className="rounded-2xl border border-border/70 bg-card/80 p-4">
                        <div className="flex items-start justify-between gap-3 mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="h-5 bg-surface-tertiary rounded w-1/3 animate-pulse"></div>
                              <div className="h-6 bg-surface-tertiary rounded-full w-16 animate-pulse"></div>
                            </div>
                            <div className="h-4 bg-surface-tertiary rounded w-full animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-2/3 mt-2 animate-pulse"></div>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3 mb-4">
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          <div className="h-6 bg-surface-tertiary rounded-full w-20 animate-pulse"></div>
                          <div className="h-6 bg-surface-tertiary rounded-full w-24 animate-pulse"></div>
                          <div className="h-6 bg-surface-tertiary rounded-full w-16 animate-pulse"></div>
                        </div>
                      </div>
                      <div className="rounded-2xl border border-border/70 bg-card/80 p-4">
                        <div className="flex items-start justify-between gap-3 mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="h-5 bg-surface-tertiary rounded w-1/3 animate-pulse"></div>
                              <div className="h-6 bg-surface-tertiary rounded-full w-16 animate-pulse"></div>
                            </div>
                            <div className="h-4 bg-surface-tertiary rounded w-full animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-2/3 mt-2 animate-pulse"></div>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3 mb-4">
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          <div className="h-6 bg-surface-tertiary rounded-full w-20 animate-pulse"></div>
                          <div className="h-6 bg-surface-tertiary rounded-full w-24 animate-pulse"></div>
                          <div className="h-6 bg-surface-tertiary rounded-full w-16 animate-pulse"></div>
                        </div>
                      </div>
                      <div className="rounded-2xl border border-border/70 bg-card/80 p-4">
                        <div className="flex items-start justify-between gap-3 mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="h-5 bg-surface-tertiary rounded w-1/3 animate-pulse"></div>
                              <div className="h-6 bg-surface-tertiary rounded-full w-16 animate-pulse"></div>
                            </div>
                            <div className="h-4 bg-surface-tertiary rounded w-full animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-2/3 mt-2 animate-pulse"></div>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3 mb-4">
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                          <div>
                            <div className="h-3 bg-surface-tertiary rounded w-1/2 mb-2 animate-pulse"></div>
                            <div className="h-4 bg-surface-tertiary rounded w-3/4 animate-pulse"></div>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          <div className="h-6 bg-surface-tertiary rounded-full w-20 animate-pulse"></div>
                          <div className="h-6 bg-surface-tertiary rounded-full w-24 animate-pulse"></div>
                          <div className="h-6 bg-surface-tertiary rounded-full w-16 animate-pulse"></div>
                        </div>
                      </div>
                    </>
                  ) : recommendations.length === 0 ? (
                    <div className="text-sm text-text-tertiary">No recommendations available right now.</div>
                  ) : (
                    recommendations.map((opportunity) => (
                      <InvestmentOpportunityCard key={opportunity.symbol} opportunity={opportunity} />
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
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

              {/* Recently Viewed */}
              <div className="card-base p-4">
                <div className="mb-4">
                  <h2 className="text-lg font-semibold text-text-primary">Recently Viewed</h2>
                </div>
                <div className="flex flex-col gap-3">
                  {isLoadingRecentlyViewed ? (
                    Array.from({ length: 3 }).map((_, index) => (
                      <div key={index} className="flex items-center gap-3 rounded-lg border border-border/70 bg-surface-secondary p-3 animate-pulse">
                        <div className="flex-1 min-w-0">
                          <div className="h-4 w-2/3 rounded bg-surface-tertiary mb-2"></div>
                          <div className="h-3 w-1/2 rounded bg-surface-tertiary"></div>
                        </div>
                        <div className="h-6 w-16 rounded-full bg-surface-tertiary"></div>
                      </div>
                    ))
                  ) : recentlyViewed.length === 0 ? (
                    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border/70 bg-background/60 px-4 py-8 text-center">
                      <p className="font-medium text-text-primary">No recently viewed companies yet.</p>
                      <p className="mt-2 text-sm text-text-tertiary">Start researching companies to see them here.</p>
                    </div>
                  ) : (
                    Array.from({ length: 3 }).map((_, i) => {
                      const company = recentlyViewed[i]

                      if (!company) {
                        return (
                          <div
                            key={i}
                            className="rounded-lg border border-border/70 bg-background"
                          />
                        )
                      }

                      return (
                        <Link
                          key={company.symbol}
                          href={`/companies/${encodeURIComponent(company.symbol)}`}
                          className="flex items-center justify-between gap-3 rounded-lg border border-border/70 bg-background p-3 transition-colors hover:border-primary/30 hover:bg-primary/5"
                        >
                          <div className="min-w-0">
                            <div className="text-sm font-medium text-text-primary truncate">{company.name}</div>
                            <div className="text-xs text-text-tertiary">{company.sector}</div>
                          </div>
                          <span className={`rounded-full px-2 py-1 text-xs font-medium ${company.sentiment.toLowerCase() === 'positive' ? 'bg-success/10 text-success' : company.sentiment.toLowerCase() === 'negative' ? 'bg-danger/10 text-danger' : 'bg-warning/10 text-warning'}`}>
                            {company.sentiment}
                          </span>
                          <ChevronRight className="w-4 h-4 text-text-tertiary flex-shrink-0" />
                        </Link>
                      )
                    })
                  )}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
