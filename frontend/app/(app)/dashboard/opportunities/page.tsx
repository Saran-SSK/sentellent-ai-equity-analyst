"use client"

import { useEffect, useState } from "react"
import { ArrowLeft, Loader2 } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import InvestmentOpportunityCard from "@/components/cards/InvestmentOpportunityCard"

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

export default function OpportunitiesPage() {
  const router = useRouter()
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        const token = localStorage.getItem("access_token")
        const response = await fetch(`${backendUrl}/api/v1/companies/recommendations?limit=12`, {
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        })

        if (response.status === 401) {
          router.push("/signin")
          return
        }

        if (!response.ok) {
          throw new Error("Failed to load recommendations")
        }

        const data = await response.json()
        setRecommendations(data)
      } catch (err) {
        setError("Failed to load recommendations")
        console.error(err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchRecommendations()
  }, [router])

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center gap-3">
        <Link href="/dashboard" className="inline-flex items-center gap-2 text-text-tertiary hover:text-primary transition-colors">
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Link>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Investment Opportunities</h1>
          <p className="text-sm text-text-tertiary">All recommendations ranked by your personalized score.</p>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-danger/30 bg-danger/10 p-4 text-danger">{error}</div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {recommendations.map((opportunity) => (
            <InvestmentOpportunityCard key={opportunity.symbol} opportunity={opportunity} showScore showViewButton />
          ))}
        </div>
      )}
    </div>
  )
}
