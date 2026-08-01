"use client";

import { NewsArticle } from "@/types";
import { formatDate, getSentimentColor } from "@/utils/format";
import { ExternalLink } from "lucide-react";
import Badge from "@/components/ui/Badge";

interface NewsCardProps {
  article: NewsArticle;
}

export default function NewsCard({ article }: NewsCardProps) {
  return (
    <div className="card-base">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <a
            href={article.link}
            target="_blank"
            rel="noopener noreferrer"
            className="text-lg font-semibold text-text-primary hover:text-primary transition-colors"
          >
            {article.headline}
          </a>
        </div>
        <a
          href={article.link}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:opacity-70 transition-opacity ml-2"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      <p className="text-text-tertiary text-sm mb-4 line-clamp-2">
        {article.summary}
      </p>

      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3 text-xs text-text-tertiary">
          <span>{article.source}</span>
          <span>•</span>
          <span>{formatDate(article.publishedAt)}</span>
        </div>

        <Badge
          variant={
            article.sentiment === "positive"
              ? "success"
              : article.sentiment === "negative"
                ? "danger"
                : "info"
          }
          size="sm"
        >
          {article.sentiment.charAt(0).toUpperCase() + article.sentiment.slice(1)}
        </Badge>
      </div>

      {article.companies.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-4 pt-3 border-t border-border">
          {article.companies.map((company) => (
            <Badge key={company} size="sm">
              {company}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
