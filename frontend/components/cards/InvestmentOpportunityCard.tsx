import Link from "next/link"
import { ArrowRight, TrendingUp } from "lucide-react"
import { formatCurrency, formatNumber, getSentimentColor } from "@/utils/format"

interface OpportunityItem {
  symbol: string
  name: string
  description: string
  current_price: number | null
  market_cap: number | null
  sector: string
  sentiment: string
  why_recommended: string[]
  score?: number
}

interface InvestmentOpportunityCardProps {
  opportunity: OpportunityItem
  showScore?: boolean
  showViewButton?: boolean
}

export default function InvestmentOpportunityCard({
  opportunity,
  showScore = false,
  showViewButton = false,
}: InvestmentOpportunityCardProps) {
  const sentiment = opportunity.sentiment?.toLowerCase() || "neutral"
  const sentimentClass = getSentimentColor(sentiment as "positive" | "neutral" | "negative")

  return (
    <div className="rounded-2xl border border-border/70 bg-card/80 p-4 shadow-sm hover:border-primary/30 transition-all">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-base font-semibold text-text-primary">{opportunity.name}</h3>
            <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${sentimentClass}`}>
              {opportunity.sentiment}
            </span>
          </div>
          <p className="mt-2 text-sm text-text-secondary leading-relaxed">{opportunity.description}</p>
        </div>
        {showViewButton && (
          <Link
            href={`/companies/${encodeURIComponent(opportunity.symbol)}`}
            className="inline-flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/10 px-3 py-2 text-sm font-medium text-primary transition-colors hover:bg-primary/20"
          >
            View Company
            <ArrowRight className="h-4 w-4" />
          </Link>
        )}
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <div className="text-text-tertiary">Current Price</div>
          <div className="font-semibold text-text-primary">{formatCurrency(opportunity.current_price)}</div>
        </div>
        <div>
          <div className="text-text-tertiary">Market Cap</div>
          <div className="font-semibold text-text-primary">{formatCurrency(opportunity.market_cap)}</div>
        </div>
        <div>
          <div className="text-text-tertiary">Sector</div>
          <div className="font-semibold text-text-primary">{opportunity.sector || "N/A"}</div>
        </div>
        <div>
          <div className="text-text-tertiary">{showScore ? "Recommendation Score" : "View"}</div>
          <div className="font-semibold text-text-primary">
            {showScore ? `${opportunity.score ?? 0}` : formatNumber(opportunity.market_cap)}
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {opportunity.why_recommended.map((reason) => (
          <span
            key={reason}
            className="rounded-full border border-border/70 bg-background px-2.5 py-1 text-xs font-medium text-text-secondary"
          >
            {reason}
          </span>
        ))}
      </div>
    </div>
  )
}
