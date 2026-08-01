"use client";

import { useState } from "react";
import { Newspaper } from "lucide-react";
import NewsCard from "@/components/cards/NewsCard";
import Badge from "@/components/ui/Badge";
import { MOCK_NEWS } from "@/utils/mockData";

export default function MarketNewsPage() {
  const [filter, setFilter] = useState<"all" | "positive" | "negative" | "neutral">("all");

  const filteredNews =
    filter === "all"
      ? MOCK_NEWS
      : MOCK_NEWS.filter((article) => article.sentiment === filter);

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <Newspaper className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold text-text-primary">Market News</h1>
        </div>
        <p className="text-text-tertiary">
          Latest news and updates from Indian equity markets
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        {(
          ["all", "positive", "negative", "neutral"] as const
        ).map((option) => (
          <button
            key={option}
            onClick={() => setFilter(option)}
            className={`px-4 py-2 rounded-xl font-medium transition-all ${
              filter === option
                ? "bg-primary text-white"
                : "bg-card border border-border text-text-secondary hover:text-text-primary"
            }`}
          >
            {option.charAt(0).toUpperCase() + option.slice(1)}
          </button>
        ))}
      </div>

      {/* News Feed */}
      <div className="space-y-4">
        {filteredNews.length > 0 ? (
          filteredNews.map((article) => (
            <NewsCard key={article.id} article={article} />
          ))
        ) : (
          <div className="text-center py-12">
            <p className="text-text-tertiary">No news articles found</p>
          </div>
        )}
      </div>

      {/* Load More */}
      <div className="text-center">
        <button className="btn-secondary">Load More Articles</button>
      </div>
    </div>
  );
}
