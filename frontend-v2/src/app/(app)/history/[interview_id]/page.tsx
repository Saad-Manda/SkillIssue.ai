"use client";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft, Briefcase, ChevronDown, ChevronUp, MessageSquare, FileText,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AppButton } from "@/components/primitives/AppButton";
import { AppCard } from "@/components/primitives/AppCard";
import { MetricCard } from "@/components/primitives/MetricCard";
import { EmptyState } from "@/components/primitives/EmptyState";
import { useInterviewDetail } from "@/hooks/use-interviews";
import { METRICS } from "@/lib/constants";
import { formatDateFull } from "@/lib/utils";
import { useState } from "react";

export default function InterviewHistoryDetailPage() {
  const { interview_id } = useParams<{ interview_id: string }>();
  const router = useRouter();
  const { data, isLoading, isError } = useInterviewDetail(interview_id);
  const [showJd, setShowJd] = useState(false);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-text-secondary text-sm">
        Loading interview details…
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <p className="text-text-secondary mb-4">Interview not found.</p>
        <AppButton variant="outline" onClick={() => router.push("/dashboard")}>
          Back to Dashboard
        </AppButton>
      </div>
    );
  }

  const { interview, jd } = data;

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-8 space-y-6">
      {/* Header */}
      <div>
        <AppButton
          variant="ghost"
          size="sm"
          leftIcon={<ArrowLeft size={14} />}
          onClick={() => router.push("/dashboard")}
          className="mb-4"
        >
          Back to Dashboard
        </AppButton>
        <h1 className="text-2xl font-semibold text-text-main">
          {jd?.job_title ?? "Interview Session"}
        </h1>
        <p className="text-sm text-text-secondary mt-1">
          {formatDateFull(interview.conducted_on)}
        </p>
      </div>

      {/* JD Accordion */}
      {jd && (
        <AppCard>
          <button
            className="flex w-full items-center justify-between gap-2 text-left"
            onClick={() => setShowJd((v) => !v)}
            aria-expanded={showJd}
          >
            <div className="flex items-center gap-2 font-medium text-text-main text-sm">
              <Briefcase size={16} className="text-brand-600" />
              {jd.job_title} · {jd.min_experience}+ years experience
            </div>
            {showJd ? <ChevronUp size={16} className="text-text-muted" /> : <ChevronDown size={16} className="text-text-muted" />}
          </button>

          {showJd && (
            <div className="mt-4 pt-4 border-t border-warm-border space-y-3 text-sm">
              <div>
                <p className="font-medium text-text-main mb-1">Required Skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {jd.required_skills?.map((s) => (
                    <span key={s} className="px-2.5 py-1 bg-brand-50 text-brand-700 text-xs rounded-full border border-brand-200">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
              {jd.responsibilities?.length > 0 && (
                <div>
                  <p className="font-medium text-text-main mb-1">Key Responsibilities</p>
                  <ul className="list-disc pl-5 space-y-1 text-text-secondary">
                    {jd.responsibilities.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}
        </AppCard>
      )}

      {/* AI Report */}
      {interview.report && (
        <AppCard>
          <div className="flex items-center gap-2 mb-4">
            <FileText size={18} className="text-brand-600" />
            <h2 className="text-lg font-semibold text-text-main">AI Readiness Report</h2>
          </div>
          <div className="prose-report">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{interview.report}</ReactMarkdown>
          </div>
        </AppCard>
      )}

      {/* Chat History — Q&A Timeline */}
      <AppCard>
        <div className="flex items-center gap-2 mb-6">
          <MessageSquare size={18} className="text-brand-600" />
          <h2 className="text-lg font-semibold text-text-main">
            Session Transcript ({interview.chat_history?.length ?? 0} turns)
          </h2>
        </div>

        {!interview.chat_history?.length ? (
          <EmptyState
            icon={MessageSquare}
            title="No transcript available"
            description="The session transcript could not be retrieved."
          />
        ) : (
          <div className="space-y-6">
            {interview.chat_history.map((turn, i) => (
              <div key={turn.chat_id ?? i} className="space-y-4">
                {/* Turn header */}
                <div className="flex items-center gap-3">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-warm-muted text-xs font-semibold text-text-muted flex-shrink-0">
                    {i + 1}
                  </div>
                  {turn.phase_name && (
                    <span className="text-xs font-medium text-text-muted uppercase tracking-wide">
                      Phase: {turn.phase_name}
                    </span>
                  )}
                </div>

                {/* Question */}
                <div className="pl-9">
                  <p className="text-xs font-semibold text-brand-700 uppercase tracking-wide mb-1.5">
                    Interviewer
                  </p>
                  <p className="text-sm text-text-main leading-relaxed bg-brand-50 border border-brand-100 rounded-lg px-4 py-3">
                    {turn.question}
                  </p>
                </div>

                {/* Response */}
                <div className="pl-9">
                  <p className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-1.5">
                    Your Answer
                  </p>
                  <p className="text-sm text-text-secondary leading-relaxed px-4 py-3 border-l-2 border-warm-border">
                    {turn.response}
                  </p>
                </div>

                {/* Metrics */}
                {turn.metrics && (
                  <div className="pl-9">
                    <p className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-3">
                      Turn Evaluation
                    </p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {METRICS.filter((m) =>
                        turn.metrics![m.key as keyof typeof turn.metrics] !== undefined
                      ).map((metric) => (
                        <MetricCard
                          key={metric.key}
                          label={metric.label}
                          fullName={metric.fullName}
                          description={metric.description}
                          score={(turn.metrics![metric.key as keyof typeof turn.metrics] as number) ?? 0}
                        />
                      ))}
                    </div>
                    {turn.metrics.feedback && (
                      <blockquote className="mt-3 pl-4 border-l-2 border-brand-300 text-sm text-text-secondary italic">
                        {turn.metrics.feedback}
                      </blockquote>
                    )}
                  </div>
                )}

                {i < interview.chat_history.length - 1 && (
                  <div className="border-b border-warm-border" />
                )}
              </div>
            ))}
          </div>
        )}
      </AppCard>

      {/* Retry CTA */}
      <div className="p-6 rounded-xl bg-brand-50 border border-brand-200 text-center">
        <h3 className="font-semibold text-text-main mb-1">Want to improve?</h3>
        <p className="text-sm text-text-secondary mb-4">
          Practice the same role again with a fresh interview session.
        </p>
        <AppButton variant="brand" onClick={() => router.push("/interview/setup")}>
          Start New Interview
        </AppButton>
      </div>
    </div>
  );
}
