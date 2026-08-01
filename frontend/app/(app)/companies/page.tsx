"use client"

import { useState, useEffect, useCallback } from "react"
import { Search, Loader2, Building2 } from "lucide-react"
import { useRouter } from "next/navigation"
import Link from "next/link"

interface SearchResult {
  symbol: string
  name: string
}

export default function CompaniesPage() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token")
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  const searchCompanies = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([])
      return
    }

    setIsLoading(true)
    setError(null)
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${backendUrl}/api/v1/companies/search?q=${encodeURIComponent(searchQuery)}`, {
        headers: getAuthHeaders(),
      })

      if (response.status === 401) {
        router.push("/signin")
        return
      }

      if (response.status === 404) {
        setResults([])
        return
      }

      if (!response.ok) {
        throw new Error("Failed to search companies")
      }

      const data: SearchResult[] = await response.json()
      setResults(data)
    } catch (err) {
      setError("Failed to search companies")
      console.error("Error searching companies:", err)
      setResults([])
    } finally {
      setIsLoading(false)
    }
  }, [router])

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      searchCompanies(query)
    }, 300)

    return () => clearTimeout(timer)
  }, [query, searchCompanies])

  const handleSelectCompany = (symbol: string) => {
    router.push(`/companies/${symbol}`)
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary mb-2">
          Company Search
        </h1>
        <p className="text-text-tertiary">
          Search for companies to view detailed information and analysis
        </p>
      </div>

      {/* Search Bar */}
      <div className="relative mb-8">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-tertiary" />
          <input
            type="text"
            placeholder="Search by company name or ticker (e.g., TCS, Reliance, HDFC)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="input-base pl-12"
            autoFocus
          />
          {isLoading && (
            <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-primary animate-spin" />
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 rounded-lg bg-danger/10 border border-danger/30 text-danger">
          {error}
        </div>
      )}

      {/* Search Results */}
      {query && !isLoading && results.length === 0 && (
        <div className="text-center py-12">
          <Building2 className="w-16 h-16 text-text-tertiary mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-text-primary mb-2">
            No companies found
          </h3>
          <p className="text-text-tertiary">
            Try searching with a different company name or ticker
          </p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-text-tertiary">
            {results.length} {results.length === 1 ? 'result' : 'results'} found
          </p>
          {results.map((company) => (
            <button
              key={company.symbol}
              onClick={() => handleSelectCompany(company.symbol)}
              className="w-full p-4 rounded-lg bg-card border border-border hover:border-primary/30 transition-all text-left group"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-text-primary group-hover:text-primary transition-colors">
                      {company.name}
                    </h3>
                    <span className="px-2 py-1 rounded-md bg-background text-xs font-medium text-text-secondary">
                      {company.symbol}
                    </span>
                  </div>
                </div>
                <div className="text-text-tertiary group-hover:text-primary transition-colors">
                  →
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {!query && (
        <div className="text-center py-12">
          <Building2 className="w-16 h-16 text-text-tertiary mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-text-primary mb-2">
            Search for companies
          </h3>
          <p className="text-text-tertiary">
            Enter a company name or ticker to get started
          </p>
        </div>
      )}
    </div>
  )
}
