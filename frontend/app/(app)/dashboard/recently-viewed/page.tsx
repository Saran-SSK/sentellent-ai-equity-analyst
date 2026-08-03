"use client"

import { useState, useEffect } from "react"
import { ArrowLeft, Loader2, ChevronRight } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

interface RecentlyViewedCompany {
  symbol: string
  name: string
  sector: string
  sentiment: string
}

export default function RecentlyViewedPage() {
  const router = useRouter()
  const [recentlyViewed, setRecentlyViewed] = useState<RecentlyViewedCompany[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token")
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  const fetchRecentlyViewed = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

      const response = await fetch(
        `${backendUrl}/api/v1/companies/recently-viewed?limit=10`,
        { headers: getAuthHeaders() }
      )

      if (response.status === 401) {
        router.push("/signin")
        return
      }

      if (!response.ok) {
        throw new Error("Failed to fetch recently viewed companies")
      }

      const data: RecentlyViewedCompany[] = await response.json()
      setRecentlyViewed(data)
    } catch (err) {
      setError("Failed to load recently viewed companies")
      console.error("Error fetching recently viewed:", err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchRecentlyViewed()
  }, [])

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link href="/dashboard" className="flex items-center gap-2 text-text-tertiary hover:text-primary transition-colors mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
        <h1 className="text-2xl font-bold text-text-primary">Recently Viewed Companies</h1>
        <p className="text-text-tertiary mt-1">
          Your recently explored companies, ordered by most recent.
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-lg bg-danger/10 border border-danger/30 text-danger mb-6">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="flex items-center gap-3 p-4 rounded-xl bg-surface-secondary animate-pulse">
              <div className="flex-1 min-w-0">
                <div className="h-5 bg-surface-tertiary rounded w-1/2 mb-2"></div>
                <div className="h-4 bg-surface-tertiary rounded w-1/3"></div>
              </div>
              <div className="h-6 bg-surface-tertiary rounded w-16"></div>
              <div className="w-5 h-5 bg-surface-tertiary rounded"></div>
            </div>
          ))}
        </div>
      ) : recentlyViewed.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">👁️</div>
          <h2 className="text-xl font-semibold text-text-primary mb-2">No recently viewed companies</h2>
          <p className="text-text-tertiary mb-6">Companies you explore will appear here for quick access.</p>
          <Link
            href="/companies"
            className="btn-primary inline-flex items-center gap-2"
          >
            Explore Companies
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {recentlyViewed.map((company) => (
            <Link
              key={company.symbol}
              href={`/companies/${company.symbol}`}
              className="flex items-center gap-4 p-4 rounded-xl bg-surface-secondary hover:bg-surface-tertiary transition-colors group"
            >
              <div className="flex-1 min-w-0">
                <div className="text-base font-medium text-text-primary truncate">{company.name}</div>
                <div className="text-sm text-text-tertiary">{company.sector}</div>
              </div>
              <div className={`text-sm px-3 py-1 rounded-full ${
                company.sentiment === "positive" ? "bg-success/10 text-success" :
                company.sentiment === "negative" ? "bg-danger/10 text-danger" :
                "bg-neutral/10 text-neutral"
              }`}>
                {company.sentiment}
              </div>
              <ChevronRight className="w-5 h-5 text-text-tertiary group-hover:text-primary transition-colors flex-shrink-0" />
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
