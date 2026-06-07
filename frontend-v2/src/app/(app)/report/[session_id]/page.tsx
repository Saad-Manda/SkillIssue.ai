"use client";
import { useParams, useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ArrowLeft, Download, BrainCircuit, Calendar } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppCard } from "@/components/primitives/AppCard";
import { MetricCard } from "@/components/primitives/MetricCard";
import { ScoreRadarChart } from "@/components/primitives/ScoreRadarChart";
import { ReportSkeleton } from "@/components/primitives/Skeletons";
import { useReport } from "@/hooks/use-report";
import { METRICS } from "@/lib/constants";

export default function ReportPage() {
  const { session_id } = useParams<{ session_id: string }>();
  const router = useRouter();
  const { data, isLoading, isError } = useReport(session_id);

  // Parse scores from markdown (heuristic — ideally backend returns structured scores)
  // For MVP, we render the report text and show placeholder scores
  // TODO: Backend team to add structured scores to /report endpoint
  const mockScores: Record<string, number> = {
    relevance_score:        7.5,
    technical_depth_score:  6.8,
    answer_confidence_score:7.2,
    structure_score:        8.1,
    clarity_score:          7.9,
    completeness_score:     6.5,
    rfd_score:              8.4,
    star_score:             7.0,
  };

  const handleExportPDF = async () => {
    const { default: html2pdf } = await import("html2pdf.js");
    const element = document.getElementById("report-content");
    if (!element) return;

    html2pdf().set({
      margin:      [15, 15],
      filename:    `SkillIssue-Report-${session_id.slice(0, 8)}.pdf`,
      image:       { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF:       { unit: "mm", format: "a4", orientation: "portrait" },
    }).from(element).save();
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 md:px-8 py-8">
        <div className="flex flex-col items-center gap-4 mb-10 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-100">
            <BrainCircuit size={24} className="text-brand-700 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-text-main">Generating your report…</h1>
            <p className="text-sm text-text-secondary mt-1">
              The Report Generator is analyzing your performance across 8 dimensions.
            </p>
          </div>
        </div>
        <ReportSkeleton />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-text-secondary mb-4">Failed to load report. The interview may still be processing.</p>
        <AppButton variant="outline" onClick={() => router.push("/dashboard")}>
          Back to Dashboard
        </AppButton>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 md:px-8 py-8">
      {/* Page header */}
      <div className="flex items-start justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-text-main">Interview Readiness Report</h1>
          <div className="flex items-center gap-3 mt-2 text-sm text-text-secondary">
            <div className="flex items-center gap-1.5">
              <Calendar size={14} />
              <span>Session {session_id.slice(0, 8)}…</span>
            </div>
          </div>
        </div>
        <div className="flex gap-3 flex-shrink-0">
          <AppButton variant="outline" size="sm" leftIcon={<ArrowLeft size={14} />} onClick={() => router.push("/dashboard")}>
            Dashboard
          </AppButton>
          <AppButton variant="brand" size="sm" leftIcon={<Download size={14} />} onClick={handleExportPDF}>
            Export PDF
          </AppButton>
        </div>
      </div>

      {/* Scorecard grid */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-text-main mb-4">Performance Scorecard</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {METRICS.map((metric) => (
            <MetricCard
              key={metric.key}
              label={metric.label}
              fullName={metric.fullName}
              description={metric.description}
              score={mockScores[metric.key] ?? 0}
              maxScore={metric.maxScore}
            />
          ))}
        </div>
      </div>

      {/* Radar chart */}
      <AppCard className="mb-8">
        <h2 className="text-lg font-semibold text-text-main mb-2">Performance Radar</h2>
        <p className="text-sm text-text-secondary mb-4">
          Visual overview of your performance across all 8 evaluation dimensions.
        </p>
        <ScoreRadarChart scores={mockScores} metrics={METRICS} />
      </AppCard>

      {/* Full report markdown */}
      <AppCard id="report-content">
        <div className="prose-report">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {data.report}
          </ReactMarkdown>
        </div>
      </AppCard>

      {/* CTA — Take another interview */}
      <div className="mt-8 p-6 rounded-xl bg-brand-50 border border-brand-200 text-center">
        <h3 className="font-semibold text-text-main mb-1">Ready to improve?</h3>
        <p className="text-sm text-text-secondary mb-4">
          Practice makes perfect. Start another interview to track your progress.
        </p>
        <AppButton variant="brand" onClick={() => router.push("/interview/setup")}>
          Start Another Interview
        </AppButton>
      </div>
    </div>
  );
}
