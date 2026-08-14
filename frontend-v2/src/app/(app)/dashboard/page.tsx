"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  Plus, History, Calendar, FileText, BarChart2,
  CheckCircle2, Circle, ArrowRight, Sparkles,
} from "lucide-react";
import { useInterviews, useDeleteInterview } from "@/hooks/use-interviews";
import { useProfile } from "@/hooks/use-profile";
import { AppButton } from "@/components/primitives/AppButton";
import { AppCard } from "@/components/primitives/AppCard";
import { EmptyState } from "@/components/primitives/EmptyState";
import { StatusBadge } from "@/components/primitives/StatusBadge";
import { ConfirmModal } from "@/components/primitives/ConfirmModal";
import { InterviewCardSkeleton } from "@/components/primitives/Skeletons";
import { InitialsAvatar } from "@/components/primitives/InitialsAvatar";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuthStore } from "@/store/auth-store";
import { useAuth } from "@/hooks/use-auth";
import { formatDateFull, timeAgo } from "@/lib/utils";
import { jdApi } from "@/lib/api";
import type { Interview } from "@/types/api";

// ── Onboarding checklist (for new users) ───────────────────────────
function OnboardingChecklist({ hasProfile, hasInterviews }: { hasProfile: boolean; hasInterviews: boolean }) {
  const router = useRouter();
  const steps = [
    {
      done: hasProfile,
      label: "Complete your profile",
      description: "Add experiences, skills, and projects so the AI can tailor questions.",
      action: () => router.push(hasProfile ? "/profile" : "/profile/new"),
      actionLabel: hasProfile ? "View Profile" : "Set up Profile",
    },
    {
      done: hasInterviews,
      label: "Complete your first interview",
      description: "Start an AI-powered session with a target job description.",
      action: () => router.push("/interview/setup"),
      actionLabel: "Start Interview",
    },
  ];

  if (hasProfile && hasInterviews) return null;

  return (
    <AppCard className="border-brand-200 bg-brand-50/50 mb-6">
      <div className="flex items-start gap-3 mb-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-100 flex-shrink-0">
          <Sparkles size={16} className="text-brand-700" />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-text-main">Get started</h2>
          <p className="text-xs text-text-secondary mt-0.5 font-sans">
            Complete these steps to get the most out of SkillIssue.ai.
          </p>
        </div>
      </div>
      <div className="space-y-3">
        {steps.map((step) => (
          <div
            key={step.label}
            className="flex items-start justify-between gap-4 p-3 rounded-lg bg-white border border-warm-border font-sans"
          >
            <div className="flex items-start gap-3">
              {step.done ? (
                <CheckCircle2 size={18} className="text-success mt-0.5 flex-shrink-0" />
              ) : (
                <Circle size={18} className="text-text-muted mt-0.5 flex-shrink-0" />
              )}
              <div>
                <p className={`text-sm font-medium ${step.done ? "line-through text-text-muted" : "text-text-main"}`}>
                  {step.label}
                </p>
                {!step.done && (
                  <p className="text-xs text-text-secondary mt-0.5">{step.description}</p>
                )}
              </div>
            </div>
            {!step.done && (
              <AppButton
                variant="outline"
                size="sm"
                onClick={step.action}
                rightIcon={<ArrowRight size={12} />}
                className="flex-shrink-0"
              >
                {step.actionLabel}
              </AppButton>
            )}
          </div>
        ))}
      </div>
    </AppCard>
  );
}

// ── Profile health card ─────────────────────────────────────────────
function ProfileHealthCard() {
  const { data: profile } = useProfile();
  const { user } = useAuthStore();
  const router = useRouter();

  const sections = [
    { label: "Experiences", count: profile?.experiences?.length ?? 0 },
    { label: "Projects",    count: profile?.projects?.length    ?? 0 },
    { label: "Skills",      count: profile?.skills?.length      ?? 0 },
  ];

  // Calculate profile completeness score (simple heuristic)
  const completeness = Math.min(
    100,
    (profile?.name ? 20 : 0) +
    (profile?.skills?.length ? 20 : 0) +
    (profile?.experiences?.length ? 25 : 0) +
    (profile?.educations?.length ? 15 : 0) +
    (profile?.projects?.length ? 20 : 0)
  );

  return (
    <AppCard className="h-full">
      <div className="flex items-center gap-3 mb-4">
        <InitialsAvatar name={profile?.name ?? user?.username} size="lg" />
        <div className="min-w-0">
          <p className="font-semibold text-text-main truncate">
            {profile?.name ?? user?.username ?? "Your Profile"}
          </p>
          <p className="text-xs text-text-secondary truncate font-sans">{user?.email}</p>
        </div>
      </div>

      {/* Completeness */}
      <div className="mb-4 font-sans">
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-xs font-medium text-text-secondary">Profile completeness</span>
          <span className="text-xs font-semibold text-brand-700">{completeness}%</span>
        </div>
        <div className="h-1.5 w-full rounded-full bg-warm-muted overflow-hidden">
          <div
            className="h-full bg-brand-500 rounded-full transition-all duration-700"
            style={{ width: `${completeness}%` }}
          />
        </div>
        {completeness < 80 && (
          <p className="text-xs text-text-muted mt-1.5">
            Add more details to improve AI question quality.
          </p>
        )}
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-3 gap-2 mb-4 font-sans text-center">
        {sections.map(({ label, count }) => (
          <div key={label} className="p-2 rounded-lg bg-warm-muted">
            <p className="text-lg font-semibold text-text-main">{count}</p>
            <p className="text-xxs sm:text-xs text-text-secondary truncate">{label}</p>
          </div>
        ))}
      </div>

      <AppButton
        variant="outline"
        size="sm"
        fullWidth
        onClick={() => router.push(profile ? "/profile" : "/profile/new")}
      >
        {profile ? "View Profile" : "Set Up Profile"}
      </AppButton>
    </AppCard>
  );
}

// ── Interview history item ──────────────────────────────────────────
function InterviewCard({
  interview,
  onDelete,
}: {
  interview: Interview;
  onDelete: (id: string) => void;
}) {
  const router = useRouter();
  
  // Job title from JD — fetched dynamically
  const { data: jd } = useQuery({
    queryKey: ["jd", interview.jd_id],
    queryFn: () => jdApi.get(interview.jd_id),
    enabled: !!interview.jd_id,
  });

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => router.push(`/history/${interview._id}`)}
      onKeyDown={(e) => e.key === "Enter" && router.push(`/history/${interview._id}`)}
      className="group flex items-center justify-between p-4 rounded-xl border border-warm-border bg-white hover:border-brand-200 hover:shadow-warm-sm transition-all duration-150 cursor-pointer font-sans"
    >
      <div className="flex items-start gap-3 min-w-0">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-warm-muted flex-shrink-0">
          <FileText size={18} className="text-text-muted" />
        </div>
        <div className="min-w-0">
          <p className="font-semibold text-text-main text-sm truncate">
            {jd?.job_title ?? "Interview Session"}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <Calendar size={12} className="text-text-muted flex-shrink-0" />
            <span className="text-xs text-text-secondary">{timeAgo(interview.conducted_on)}</span>
            <span className="text-xs text-text-muted hidden sm:inline">
              • {formatDateFull(interview.conducted_on)}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 flex-shrink-0 ml-4">
        <StatusBadge status={interview.report ? "completed" : "abandoned"} />
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(interview._id);
          }}
          className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-md text-text-muted hover:text-error hover:bg-error/10"
          aria-label="Delete interview"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 6h18" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" /><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
          </svg>
        </button>
        <ArrowRight size={14} className="text-text-muted group-hover:text-brand-600 transition-colors" />
      </div>
    </div>
  );
}

// ── Main Dashboard ─────────────────────────────────────────────────
export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { data: interviews = [], isLoading } = useInterviews();
  const { data: profile } = useProfile();
  const deleteMutation = useDeleteInterview();

  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    await deleteMutation.mutateAsync(deleteTarget);
    setDeleteTarget(null);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 md:px-8 py-8">
      <PageHeader
        title={`Good day, ${profile?.name?.split(" ")[0] ?? user?.username ?? "there"} 👋`}
        subtitle="Ready for your next round? Your AI interviewer is waiting."
        actions={
          <AppButton
            variant="brand"
            leftIcon={<Plus size={16} />}
            onClick={() => router.push("/interview/setup")}
          >
            New Interview
          </AppButton>
        }
      />

      {/* Onboarding checklist (hidden once both tasks done) */}
      <OnboardingChecklist
        hasProfile={!!profile}
        hasInterviews={interviews.length > 0}
      />

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile sidebar */}
        <div className="lg:col-span-1">
          <ProfileHealthCard />
        </div>

        {/* Interview history */}
        <div className="lg:col-span-2">
          <AppCard padding="none">
            <div className="flex items-center justify-between px-6 py-4 border-b border-warm-border">
              <div className="flex items-center gap-2">
                <History size={18} className="text-text-secondary" />
                <h2 className="font-semibold text-text-main">Recent Interviews</h2>
              </div>
              {interviews.length > 0 && (
                <span className="text-xs font-semibold text-text-muted bg-warm-muted px-2 py-0.5 rounded-full font-sans">
                  {interviews.length} total
                </span>
              )}
            </div>

            <div className="p-4 space-y-3">
              {isLoading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <InterviewCardSkeleton key={i} />
                ))
              ) : interviews.length === 0 ? (
                <EmptyState
                  icon={BarChart2}
                  title="No interviews yet"
                  description="Start a session with any job description to get your first AI-scored interview and readiness report."
                  action={
                    <AppButton
                      variant="brand"
                      size="sm"
                      onClick={() => router.push("/interview/setup")}
                      leftIcon={<Plus size={14} />}
                    >
                      Start First Interview
                    </AppButton>
                  }
                />
              ) : (
                interviews.map((inv) => (
                  <InterviewCard
                    key={inv._id}
                    interview={inv}
                    onDelete={(id) => setDeleteTarget(id)}
                  />
                ))
              )}
            </div>
          </AppCard>
        </div>
      </div>

      {/* Delete confirmation modal */}
      <ConfirmModal
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete interview?"
        description="This will permanently remove the interview session and its report. This action cannot be undone."
        confirmLabel="Yes, delete"
        isLoading={deleteMutation.isPending}
        onConfirm={handleDeleteConfirm}
      />
    </div>
  );
}
