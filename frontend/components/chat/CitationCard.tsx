"use client";

import { Citation } from "@/types";
import { formatDate } from "@/utils/format";
import { ExternalLink, ChevronDown } from "lucide-react";
import { useState } from "react";

interface CitationCardProps {
  citation: Citation;
}

export default function CitationCard({ citation }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-border rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 bg-card hover:bg-sidebar transition-colors text-left flex items-start justify-between gap-3"
      >
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-text-primary mb-1 line-clamp-1">
            {citation.title}
          </h4>
          <div className="flex items-center gap-2 text-xs text-text-tertiary">
            <span>{citation.source}</span>
            <span>•</span>
            <span>{formatDate(citation.publishedAt)}</span>
          </div>
        </div>
        <ChevronDown
          className={`w-4 h-4 text-text-tertiary flex-shrink-0 transition-transform ${
            expanded ? "rotate-180" : ""
          }`}
        />
      </button>

      {expanded && (
        <div className="p-4 border-t border-border bg-background">
          <p className="text-sm text-text-secondary mb-4">{citation.snippet}</p>
          <a
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm text-primary hover:opacity-70 transition-opacity"
          >
            Read more <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      )}
    </div>
  );
}
