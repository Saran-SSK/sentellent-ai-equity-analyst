"use client";

import { BookOpen, Calendar, Zap } from "lucide-react";
import { MOCK_RESEARCH_REPORTS } from "@/utils/mockData";
import { formatDate } from "@/utils/format";
import Badge from "@/components/ui/Badge";

export default function ResearchPage() {
  const aiReports = MOCK_RESEARCH_REPORTS.filter((r) => r.aiGenerated);
  const manualReports = MOCK_RESEARCH_REPORTS.filter((r) => !r.aiGenerated);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <BookOpen className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold text-text-primary">Research</h1>
        </div>
        <p className="text-text-tertiary">
          Explore stock analysis, sector reports, and market insights
        </p>
      </div>

      {/* AI Generated Reports */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Zap className="w-5 h-5 text-primary" />
          <h2 className="text-2xl font-bold text-text-primary">
            AI Generated Reports
          </h2>
        </div>

        {aiReports.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {aiReports.map((report) => (
              <div key={report.id} className="card-base cursor-pointer hover:border-primary/30">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-text-primary">
                    {report.title}
                  </h3>
                  <Badge variant="success" size="sm">
                    AI Generated
                  </Badge>
                </div>

                {report.company && (
                  <p className="text-sm text-text-tertiary mb-3">
                    {report.company}
                  </p>
                )}

                <p className="text-sm text-text-secondary mb-4 line-clamp-2">
                  {report.content}
                </p>

                <div className="flex items-center gap-2 text-xs text-text-tertiary">
                  <Calendar className="w-3 h-3" />
                  {formatDate(report.createdAt)}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 card-base">
            <p className="text-text-tertiary">No AI generated reports yet</p>
          </div>
        )}
      </div>

      {/* Manual Reports */}
      <div>
        <h2 className="text-2xl font-bold text-text-primary mb-4">
          Saved Research
        </h2>

        {manualReports.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {manualReports.map((report) => (
              <div key={report.id} className="card-base cursor-pointer hover:border-primary/30">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-text-primary">
                    {report.title}
                  </h3>
                  <Badge variant="info" size="sm">
                    Manual
                  </Badge>
                </div>

                {report.company && (
                  <p className="text-sm text-text-tertiary mb-3">
                    {report.company}
                  </p>
                )}

                <p className="text-sm text-text-secondary mb-4 line-clamp-2">
                  {report.content}
                </p>

                <div className="flex items-center gap-2 text-xs text-text-tertiary">
                  <Calendar className="w-3 h-3" />
                  {formatDate(report.createdAt)}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 card-base">
            <p className="text-text-tertiary">No saved research yet</p>
          </div>
        )}
      </div>

      {/* Empty State for No Research */}
      {MOCK_RESEARCH_REPORTS.length === 0 && (
        <div className="text-center py-16 card-base">
          <BookOpen className="w-12 h-12 text-text-tertiary mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-semibold text-text-primary mb-2">
            No Research Reports
          </h3>
          <p className="text-text-tertiary mb-4">
            Start by asking the AI analyst or creating your own research
          </p>
        </div>
      )}
    </div>
  );
}
