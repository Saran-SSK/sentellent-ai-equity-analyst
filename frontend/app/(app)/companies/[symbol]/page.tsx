"use client"

import { useState, useEffect } from "react"
import { ArrowLeft, Loader2, Plus, TrendingUp, TrendingDown, Building2, Globe, DollarSign, BarChart3, Calendar } from "lucide-react"
import { useRouter, useParams } from "next/navigation"
import Link from "next/link"
import { formatCurrency, formatPercent, formatDate, formatNumber } from "@/utils/format"
import NewsCard from "@/components/cards/NewsCard"

interface CompanyProfile {
  id: number
  name: string
  ticker: string
  exchange: string
  sector: string
  industry: string
  description: string
  website: string
  market_cap: number
  employees: number | null
  founded_year: number | null
}

interface Watchlist {
  id: number
  name: string
  companies: any[]
}

interface CompanyQuote {
  symbol: string
  current_price: number | null
  change: number | null
  change_percent: number | null
  open: number | null
  high: number | null
  low: number | null
  volume: number | null
  market_cap: number | null
  pe_ratio: number | null
  eps: number | null
  week_52_high: number | null
  week_52_low: number | null
}

interface CompanyFinancials {
  symbol: string
  revenue: number | null
  net_income: number | null
  total_assets: number | null
  total_liabilities: number | null
  shareholders_equity: number | null
  operating_cash_flow: number | null
  free_cash_flow: number | null
  year: number
}

interface CompanyNews {
  id: string
  headline: string
  source: string
  publishedAt: string
  sentiment: "positive" | "negative" | "neutral"
  link: string
  summary: string
  companies: string[]
}

export default function CompanyDetailPage() {
  const params = useParams()
  const symbol = params.symbol as string
  const router = useRouter()

  const [profile, setProfile] = useState<CompanyProfile | null>(null)
  const [quote, setQuote] = useState<CompanyQuote | null>(null)
  const [financials, setFinancials] = useState<CompanyFinancials | null>(null)
  const [news, setNews] = useState<CompanyNews[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddToWatchlist, setShowAddToWatchlist] = useState(false)
  const [showAddToPortfolio, setShowAddToPortfolio] = useState(false)
  const [watchlists, setWatchlists] = useState<Watchlist[]>([])
  const [selectedWatchlistId, setSelectedWatchlistId] = useState<number | null>(null)
  const [isAddingToWatchlist, setIsAddingToWatchlist] = useState(false)
  const [watchlistError, setWatchlistError] = useState<string | null>(null)

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token")
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  const trackCompanyView = async (companySymbol: string) => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const token = localStorage.getItem("access_token")
      console.log("Tracking company view:", companySymbol)
      
      const response = await fetch(`${backendUrl}/api/v1/companies/${encodeURIComponent(companySymbol)}/viewed`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      })
      
      if (response.ok) {
        console.log("Company view tracked successfully")
      } else {
        console.error("Failed to track company view:", response.status, response.statusText)
      }
    } catch (err) {
      console.error("Failed to track company view", err)
    }
  }

  const fetchCompanyData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

      const [profileRes, quoteRes, financialsRes, newsRes] = await Promise.all([
        fetch(`${backendUrl}/api/v1/companies/${symbol}/profile`, { headers: getAuthHeaders() }),
        fetch(`${backendUrl}/api/v1/companies/${symbol}/quote`, { headers: getAuthHeaders() }),
        fetch(`${backendUrl}/api/v1/companies/${symbol}/financials`, { headers: getAuthHeaders() }),
        fetch(`${backendUrl}/api/v1/companies/${symbol}/news?from_date=${getFromDate()}&to_date=${getToDate()}`, { headers: getAuthHeaders() }),
      ])

      if (profileRes.status === 401 || quoteRes.status === 401 || financialsRes.status === 401 || newsRes.status === 401) {
        router.push("/signin")
        return
      }

      if (profileRes.status === 404) {
        setError("Company not found")
        return
      }

      if (!profileRes.ok || !quoteRes.ok || !financialsRes.ok || !newsRes.ok) {
        throw new Error("Failed to fetch company data")
      }

      const profileData: CompanyProfile = await profileRes.json()
      const quoteData: CompanyQuote = await quoteRes.json()
      const financialsData: CompanyFinancials = await financialsRes.json()
      const newsData: CompanyNews[] = await newsRes.json()

      setProfile(profileData)
      setQuote(quoteData)
      setFinancials(financialsData)
      setNews(newsData)
      await trackCompanyView(symbol)
    } catch (err) {
      setError("Failed to load company data")
      console.error("Error fetching company data:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const getFromDate = () => {
    const date = new Date()
    date.setDate(date.getDate() - 30)
    return date.toISOString().split('T')[0]
  }

  const getToDate = () => {
    return new Date().toISOString().split('T')[0]
  }

  useEffect(() => {
    if (symbol) {
      fetchCompanyData()
    }
  }, [symbol])

  const fetchWatchlists = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${backendUrl}/api/v1/watchlists`, {
        headers: getAuthHeaders(),
      })

      if (response.status === 401) {
        router.push("/signin")
        return
      }

      if (!response.ok) {
        throw new Error("Failed to fetch watchlists")
      }

      const data: Watchlist[] = await response.json()
      setWatchlists(data)
      setWatchlistError(null)
    } catch (err) {
      setWatchlistError("Failed to load watchlists")
      console.error("Error fetching watchlists:", err)
    }
  }

  const handleAddToWatchlist = async () => {
    if (!selectedWatchlistId || !profile) {
      return
    }

    setIsAddingToWatchlist(true)
    setWatchlistError(null)

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(
        `${backendUrl}/api/v1/watchlists/${selectedWatchlistId}/companies`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({ company_id: profile.id }),
        }
      )

      if (response.status === 401) {
        router.push("/signin")
        return
      }

      if (response.status === 409) {
        setWatchlistError("This company is already in the selected watchlist")
        setIsAddingToWatchlist(false)
        return
      }

      if (!response.ok) {
        throw new Error("Failed to add company to watchlist")
      }

      // Success
      setShowAddToWatchlist(false)
      setSelectedWatchlistId(null)
      setWatchlists([])
    } catch (err) {
      setWatchlistError("Failed to add company to watchlist")
      console.error("Error adding to watchlist:", err)
    } finally {
      setIsAddingToWatchlist(false)
    }
  }

  const handleOpenWatchlistModal = () => {
    setShowAddToWatchlist(true)
    setSelectedWatchlistId(null)
    setWatchlistError(null)
    fetchWatchlists()
  }

  if (isLoading) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <div className="mb-6">
          <Link href="/companies" className="flex items-center gap-2 text-text-tertiary hover:text-primary transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Search
          </Link>
        </div>
        <div className="p-8 rounded-lg bg-danger/10 border border-danger/30 text-danger text-center">
          {error}
        </div>
      </div>
    )
  }

  if (!profile || !quote) {
    return null
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <Link href="/companies" className="flex items-center gap-2 text-text-tertiary hover:text-primary transition-colors mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Search
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-text-primary">{profile.name}</h1>
              <span className="px-3 py-1 rounded-lg bg-primary/20 text-primary font-semibold">
                {profile.ticker}
              </span>
            </div>
            <div className="flex items-center gap-4 text-text-tertiary">
              <span>{profile.exchange || 'N/A'}</span>
              <span>•</span>
              <span>{profile.sector || 'N/A'}</span>
              <span>•</span>
              <span>{profile.industry || 'N/A'}</span>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleOpenWatchlistModal}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add to Watchlist
            </button>
            <button
              onClick={() => setShowAddToPortfolio(true)}
              className="px-4 py-2 rounded-lg border border-border text-text-primary hover:bg-card transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add to Portfolio
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-lg bg-danger/10 border border-danger/30 text-danger">
          {error}
        </div>
      )}

      {/* Price Card */}
      <div className="card-base">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-4xl font-bold text-text-primary mb-2">
              {formatCurrency(quote.current_price)}
            </div>
            <div className={`flex items-center gap-2 ${quote.change != null && quote.change >= 0 ? 'text-success' : quote.change != null && quote.change < 0 ? 'text-danger' : 'text-text-tertiary'}`}>
              {quote.change != null && quote.change >= 0 ? (
                <TrendingUp className="w-5 h-5" />
              ) : quote.change != null && quote.change < 0 ? (
                <TrendingDown className="w-5 h-5" />
              ) : null}
              <span className="font-semibold">
                {quote.change != null ? (quote.change >= 0 ? '+' : '') + formatCurrency(quote.change) : 'N/A'}
              </span>
              <span className="font-semibold">
                ({quote.change_percent != null ? (quote.change_percent >= 0 ? '+' : '') + formatPercent(quote.change_percent) : 'N/A'})
              </span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <div className="text-sm text-text-tertiary mb-1">Market Cap</div>
              <div className="text-lg font-semibold text-text-primary">
                {formatCurrency(quote.market_cap)}
              </div>
            </div>
            <div>
              <div className="text-sm text-text-tertiary mb-1">Volume</div>
              <div className="text-lg font-semibold text-text-primary">
                {formatNumber(quote.volume)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="card-base">
          <div className="flex items-center gap-2 text-text-tertiary mb-2">
            <DollarSign className="w-4 h-4" />
            <span className="text-sm">PE Ratio</span>
          </div>
          <div className="text-xl font-bold text-text-primary">
            {quote.pe_ratio != null ? quote.pe_ratio.toFixed(2) : 'N/A'}
          </div>
        </div>
        <div className="card-base">
          <div className="flex items-center gap-2 text-text-tertiary mb-2">
            <DollarSign className="w-4 h-4" />
            <span className="text-sm">EPS</span>
          </div>
          <div className="text-xl font-bold text-text-primary">
            {formatCurrency(quote.eps)}
          </div>
        </div>
        <div className="card-base">
          <div className="flex items-center gap-2 text-text-tertiary mb-2">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm">52W High</span>
          </div>
          <div className="text-xl font-bold text-text-primary">
            {formatCurrency(quote.week_52_high)}
          </div>
        </div>
        <div className="card-base">
          <div className="flex items-center gap-2 text-text-tertiary mb-2">
            <TrendingDown className="w-4 h-4" />
            <span className="text-sm">52W Low</span>
          </div>
          <div className="text-xl font-bold text-text-primary">
            {formatCurrency(quote.week_52_low)}
          </div>
        </div>
        <div className="card-base">
          <div className="flex items-center gap-2 text-text-tertiary mb-2">
            <BarChart3 className="w-4 h-4" />
            <span className="text-sm">Open</span>
          </div>
          <div className="text-xl font-bold text-text-primary">
            {formatCurrency(quote.open)}
          </div>
        </div>
        <div className="card-base">
          <div className="flex items-center gap-2 text-text-tertiary mb-2">
            <BarChart3 className="w-4 h-4" />
            <span className="text-sm">Day Range</span>
          </div>
          <div className="text-xl font-bold text-text-primary">
            {formatCurrency(quote.low)} - {formatCurrency(quote.high)}
          </div>
        </div>
      </div>

      {/* Company Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-base">
          <h2 className="text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
            <Building2 className="w-5 h-5" />
            About
          </h2>
          <p className="text-text-secondary mb-6 leading-relaxed">
            {profile.description || 'No description available'}
          </p>
          <div className="space-y-3">
            {profile.website && (
              <div className="flex items-center gap-3">
                <Globe className="w-5 h-5 text-text-tertiary" />
                <a
                  href={profile.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:text-primary/80 transition-colors"
                >
                  {profile.website}
                </a>
              </div>
            )}
            <div className="flex items-center gap-3">
              <Building2 className="w-5 h-5 text-text-tertiary" />
              <span className="text-text-secondary">
                {profile.employees != null ? formatNumber(profile.employees) + ' employees' : 'N/A employees'}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <Calendar className="w-5 h-5 text-text-tertiary" />
              <span className="text-text-secondary">
                {profile.founded_year != null ? 'Founded in ' + profile.founded_year : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {financials && (
          <div className="card-base">
            <h2 className="text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Financials ({financials.year || 'N/A'})
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 rounded-lg bg-background">
                <span className="text-text-secondary">Revenue</span>
                <span className="font-semibold text-text-primary">
                  {formatCurrency(financials.revenue)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-background">
                <span className="text-text-secondary">Net Income</span>
                <span className="font-semibold text-text-primary">
                  {formatCurrency(financials.net_income)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-background">
                <span className="text-text-secondary">Total Assets</span>
                <span className="font-semibold text-text-primary">
                  {formatCurrency(financials.total_assets)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-background">
                <span className="text-text-secondary">Total Liabilities</span>
                <span className="font-semibold text-text-primary">
                  {formatCurrency(financials.total_liabilities)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-background">
                <span className="text-text-secondary">Shareholders Equity</span>
                <span className="font-semibold text-text-primary">
                  {formatCurrency(financials.shareholders_equity)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-background">
                <span className="text-text-secondary">Operating Cash Flow</span>
                <span className="font-semibold text-text-primary">
                  {formatCurrency(financials.operating_cash_flow)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-background">
                <span className="text-text-secondary">Free Cash Flow</span>
                <span className="font-semibold text-text-primary">
                  {formatCurrency(financials.free_cash_flow)}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Latest News */}
      <div className="card-base">
        <h2 className="text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5" />
          Latest News (Last 30 Days)
        </h2>
        {news.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">📰</div>
            <p className="text-text-tertiary">No recent news available</p>
          </div>
        ) : (
          <div className="space-y-3">
            {news.map((article) => (
              <NewsCard key={article.id} article={article} />
            ))}
          </div>
        )}
      </div>

      {/* Add to Watchlist Modal */}
      {showAddToWatchlist && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card-base max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold text-text-primary mb-4">
              Add to Watchlist
            </h3>
            <p className="text-text-secondary mb-6">
              Select a watchlist to add {profile.ticker} to:
            </p>
            
            {watchlistError && (
              <div className="mb-4 p-3 rounded-lg bg-danger/10 border border-danger/30 text-danger text-sm">
                {watchlistError}
              </div>
            )}
            
            {watchlists.length === 0 && !watchlistError ? (
              <div className="p-4 rounded-lg bg-background text-text-tertiary text-center mb-6">
                <div className="text-4xl mb-2">📋</div>
                <p>No watchlists found</p>
                <p className="text-sm mt-1">Create a watchlist first to add companies</p>
              </div>
            ) : (
              <div className="space-y-2 mb-6">
                {watchlists.map((watchlist) => (
                  <button
                    key={watchlist.id}
                    onClick={() => setSelectedWatchlistId(watchlist.id)}
                    className={`w-full p-3 rounded-lg border transition-all text-left ${
                      selectedWatchlistId === watchlist.id
                        ? "border-primary bg-primary/10"
                        : "border-border bg-background hover:border-primary/30"
                    }`}
                  >
                    <div className="font-medium text-text-primary">{watchlist.name}</div>
                    <div className="text-xs text-text-tertiary">
                      {watchlist.companies.length} {watchlist.companies.length === 1 ? 'company' : 'companies'}
                    </div>
                  </button>
                ))}
              </div>
            )}
            
            <div className="flex gap-2">
              <button
                onClick={() => setShowAddToWatchlist(false)}
                className="flex-1 px-4 py-2 rounded-lg border border-border text-text-primary hover:bg-card transition-colors"
                disabled={isAddingToWatchlist}
              >
                Cancel
              </button>
              <button
                onClick={handleAddToWatchlist}
                disabled={!selectedWatchlistId || isAddingToWatchlist || watchlists.length === 0}
                className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAddingToWatchlist ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Adding...
                  </span>
                ) : (
                  "Add"
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add to Portfolio Modal */}
      {showAddToPortfolio && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card-base max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold text-text-primary mb-4">
              Add to Portfolio
            </h3>
            <p className="text-text-secondary mb-6">
              Add {profile.ticker} to your portfolio:
            </p>
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm text-text-secondary mb-2">Quantity</label>
                <input
                  type="number"
                  placeholder="Number of shares"
                  className="input-base"
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Average Buy Price</label>
                <input
                  type="number"
                  placeholder="Average buy price"
                  className="input-base"
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Purchase Date</label>
                <input
                  type="date"
                  className="input-base"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowAddToPortfolio(false)}
                className="flex-1 px-4 py-2 rounded-lg border border-border text-text-primary hover:bg-card transition-colors"
              >
                Cancel
              </button>
              <button className="flex-1 btn-primary">
                Add
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
