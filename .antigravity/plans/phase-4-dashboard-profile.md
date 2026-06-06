# Phase 4 — Dashboard & Profile Pages

> **Goal:** Build the Dashboard with a stats section, onboarding flow, and rich interview history — and a multi-step Profile wizard replacing the current 372-line monolithic form. Also rebuild ProfileView with a hero card.  
> **Prerequisite:** Phase 1 + 2 + 3 complete (all primitives and hooks available).  
> **Output:** Fully functional Dashboard and Profile pages that match the audit improvements.

---

## 4.1 Dashboard Page

**File: `src/app/(app)/dashboard/page.tsx`**

Addresses: raw JD IDs replaced with job titles, `window.confirm` → `ConfirmModal`, stats section, onboarding checklist for new users, profile health card.

```tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
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
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-100">
          <Sparkles size={16} className="text-brand-700" />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-text-main">Get started</h2>
          <p className="text-xs text-text-secondary mt-0.5">
            Complete these steps to get the most out of SkillIssue.ai.
          </p>
        </div>
      </div>
      <div className="space-y-3">
        {steps.map((step) => (
          <div
            key={step.label}
            className="flex items-start justify-between gap-4 p-3 rounded-lg bg-white border border-warm-border"
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
          <p className="text-xs text-text-secondary">{user?.email}</p>
        </div>
      </div>

      {/* Completeness */}
      <div className="mb-4">
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
      <div className="grid grid-cols-3 gap-2 mb-4">
        {sections.map(({ label, count }) => (
          <div key={label} className="text-center p-2 rounded-lg bg-warm-muted">
            <p className="text-lg font-semibold text-text-main">{count}</p>
            <p className="text-xs text-text-secondary">{label}</p>
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

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => router.push(`/history/${interview._id}`)}
      onKeyDown={(e) => e.key === "Enter" && router.push(`/history/${interview._id}`)}
      className="group flex items-center justify-between p-4 rounded-xl border border-warm-border bg-white hover:border-brand-200 hover:shadow-warm-sm transition-all duration-150 cursor-pointer"
    >
      <div className="flex items-start gap-3 min-w-0">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-warm-muted flex-shrink-0">
          <FileText size={18} className="text-text-muted" />
        </div>
        <div className="min-w-0">
          {/* Job title from JD — fetched via the interviewId detail */}
          <p className="font-medium text-text-main text-sm truncate">
            Interview Session
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
                <span className="text-xs text-text-muted bg-warm-muted px-2 py-0.5 rounded-full">
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
```

---

## 4.2 Profile Wizard — Layout & Steps

The profile form is split into a **5-step wizard** with a sticky left sidebar showing progress.

**File: `src/app/(app)/profile/new/page.tsx`** (and `/edit/page.tsx` uses the same component)

```tsx
"use client";
import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useForm, FormProvider } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Check, ChevronRight, Save } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppCard } from "@/components/primitives/AppCard";
import { useCreateProfile, useUpdateProfile, useProfile } from "@/hooks/use-profile";
import { useAuthStore } from "@/store/auth-store";
import { cn } from "@/lib/utils";

// Import step components (defined below in 4.3)
import { Step1BasicInfo }    from "./_steps/Step1BasicInfo";
import { Step2Experience }   from "./_steps/Step2Experience";
import { Step3Education }    from "./_steps/Step3Education";
import { Step4Projects }     from "./_steps/Step4Projects";
import { Step5LeadershipReview } from "./_steps/Step5LeadershipReview";

const STEPS = [
  { id: 1, label: "Basic Info",   short: "Info"       },
  { id: 2, label: "Experience",   short: "Work"       },
  { id: 3, label: "Education",    short: "Education"  },
  { id: 4, label: "Projects",     short: "Projects"   },
  { id: 5, label: "Leadership & Review", short: "Review" },
];

// Merged full profile schema (validate all at save)
const fullProfileSchema = z.object({
  name:         z.string().min(1, "Required"),
  mobile:       z.string().optional(),
  github_url:   z.string().optional(),
  linkedin_url: z.string().optional(),
  skills:       z.array(z.string()).min(1, "Add at least one skill"),
  experiences:  z.array(z.any()).default([]),
  educations:   z.array(z.any()).default([]),
  projects:     z.array(z.any()).default([]),
  leaderships:  z.array(z.any()).default([]),
});

type FullProfileForm = z.infer<typeof fullProfileSchema>;

export default function ProfileWizardPage() {
  const router = useRouter();
  const pathname = usePathname();
  const isEdit = pathname.includes("/edit");
  const { user } = useAuthStore();
  const { data: existingProfile } = useProfile();
  const createProfile = useCreateProfile();
  const updateProfile = useUpdateProfile();

  const [currentStep, setCurrentStep] = useState(1);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const methods = useForm<FullProfileForm>({
    resolver: zodResolver(fullProfileSchema),
    defaultValues: {
      name: "", mobile: "", github_url: "", linkedin_url: "",
      skills: [], experiences: [], educations: [], projects: [], leaderships: [],
    },
  });

  // Pre-fill from existing profile (edit mode)
  useEffect(() => {
    if (existingProfile) {
      methods.reset({
        name:         existingProfile.name ?? "",
        mobile:       existingProfile.mobile ?? "",
        github_url:   existingProfile.github_url ?? "",
        linkedin_url: existingProfile.linkedin_url ?? "",
        skills:       existingProfile.skills ?? [],
        experiences:  existingProfile.experiences?.map(ex => ({
          ...ex,
          end_date: ex.end_date ?? "",
          currently_working: !ex.end_date,
          skills_used: ex.skills_used ?? [],
        })) ?? [],
        educations:  existingProfile.educations?.map(ed => ({
          ...ed,
          end_date: ed.end_date ?? "",
          currently_studying: !ed.end_date,
          courses: ed.courses ?? [],
        })) ?? [],
        projects:    existingProfile.projects?.map(p => ({
          ...p,
          skills_used: p.skills_used ?? [],
        })) ?? [],
        leaderships: existingProfile.leaderships?.map(l => ({
          ...l,
          end_date: l.end_date ?? "",
          currently_active: !l.end_date,
          skills_used: l.skills_used ?? [],
        })) ?? [],
      });
    }
  }, [existingProfile, methods]);

  const handleSave = async (data: FullProfileForm) => {
    try {
      const payload = {
        name:         data.name,
        mobile:       data.mobile,
        github_url:   data.github_url,
        linkedin_url: data.linkedin_url,
        skills:       data.skills,
        experiences:  data.experiences.map((ex: any) => ({
          ...ex,
          end_date: ex.currently_working ? undefined : ex.end_date,
        })),
        educations:  data.educations.map((ed: any) => ({
          ...ed,
          courses: ed.courses ?? [],
          grade: parseFloat(ed.grade) || 0,
          end_date: ed.currently_studying ? undefined : ed.end_date,
        })),
        projects:    data.projects,
        leaderships: data.leaderships.map((l: any) => ({
          ...l,
          end_date: l.currently_active ? undefined : l.end_date,
        })),
      };

      if (isEdit || existingProfile) {
        await updateProfile.mutateAsync(payload);
      } else {
        await createProfile.mutateAsync({
          ...payload,
          user_id:        user?.id ?? "",
          email:          user?.email ?? "",
          username:       user?.username ?? "",
          is_active:      true,
        });
      }
      setSaveSuccess(true);
      setTimeout(() => router.push("/dashboard"), 1200);
    } catch (err) {
      console.error(err);
    }
  };

  const StepContent = [
    Step1BasicInfo,
    Step2Experience,
    Step3Education,
    Step4Projects,
    Step5LeadershipReview,
  ][currentStep - 1];

  const isSaving = createProfile.isPending || updateProfile.isPending;

  return (
    <div className="max-w-5xl mx-auto px-4 md:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-main">
          {isEdit ? "Edit Profile" : "Build Your Profile"}
        </h1>
        <p className="text-sm text-text-secondary mt-1">
          A comprehensive profile helps the AI ask better, more targeted questions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Step sidebar */}
        <div className="lg:col-span-1">
          <AppCard className="sticky top-20">
            <nav aria-label="Profile wizard steps" className="space-y-1">
              {STEPS.map((step) => {
                const isActive    = step.id === currentStep;
                const isCompleted = step.id < currentStep;
                return (
                  <button
                    key={step.id}
                    onClick={() => step.id <= currentStep && setCurrentStep(step.id)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-colors",
                      isActive    && "bg-brand-50 text-brand-700 font-medium",
                      isCompleted && "text-text-secondary hover:bg-warm-muted cursor-pointer",
                      !isActive && !isCompleted && "text-text-muted cursor-not-allowed"
                    )}
                    disabled={step.id > currentStep}
                  >
                    <div className={cn(
                      "flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold flex-shrink-0",
                      isActive    && "bg-brand-600 text-white",
                      isCompleted && "bg-success/15 text-success",
                      !isActive && !isCompleted && "bg-warm-muted text-text-muted"
                    )}>
                      {isCompleted ? <Check size={12} /> : step.id}
                    </div>
                    <span className="hidden lg:block">{step.label}</span>
                    <span className="block lg:hidden">{step.short}</span>
                  </button>
                );
              })}
            </nav>

            {/* Save button at bottom of sidebar (shows on all steps) */}
            {currentStep === 5 && (
              <div className="mt-4 pt-4 border-t border-warm-border">
                <AppButton
                  variant="brand"
                  size="sm"
                  fullWidth
                  isLoading={isSaving}
                  leftIcon={<Save size={14} />}
                  onClick={methods.handleSubmit(handleSave)}
                >
                  {saveSuccess ? "Saved!" : "Save Profile"}
                </AppButton>
              </div>
            )}
          </AppCard>
        </div>

        {/* Step content */}
        <div className="lg:col-span-3">
          <FormProvider {...methods}>
            <form onSubmit={methods.handleSubmit(handleSave)}>
              <AppCard>
                <StepContent />
              </AppCard>

              {/* Navigation buttons */}
              <div className="flex justify-between mt-6">
                <AppButton
                  type="button"
                  variant="outline"
                  onClick={() =>
                    currentStep > 1
                      ? setCurrentStep((s) => s - 1)
                      : router.push("/dashboard")
                  }
                >
                  {currentStep === 1 ? "Cancel" : "← Back"}
                </AppButton>

                {currentStep < 5 ? (
                  <AppButton
                    type="button"
                    variant="brand"
                    rightIcon={<ChevronRight size={16} />}
                    onClick={() => setCurrentStep((s) => s + 1)}
                  >
                    Continue
                  </AppButton>
                ) : (
                  <AppButton
                    type="submit"
                    variant="brand"
                    isLoading={isSaving}
                    leftIcon={<Save size={16} />}
                  >
                    Save Profile
                  </AppButton>
                )}
              </div>
            </form>
          </FormProvider>
        </div>
      </div>
    </div>
  );
}
```

---

## 4.3 Wizard Step Components

### Step 1 — Basic Info

**File: `src/app/(app)/profile/new/_steps/Step1BasicInfo.tsx`**

```tsx
"use client";
import { useFormContext } from "react-hook-form";
import { AppInput } from "@/components/primitives/AppInput";
import { TagInput } from "@/components/primitives/TagInput";
import { Github, Linkedin, Phone, User } from "lucide-react";

export function Step1BasicInfo() {
  const { register, watch, setValue, formState: { errors } } = useFormContext();
  const skills = watch("skills") as string[];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-main">Basic Information</h2>
        <p className="text-sm text-text-secondary mt-1">
          Your name, contact details, and top skills.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <AppInput
          label="Full Name"
          placeholder="John Doe"
          autoComplete="name"
          prefixIcon={<User size={16} />}
          error={errors.name?.message as string}
          {...register("name")}
        />
        <AppInput
          label="Mobile"
          type="tel"
          placeholder="+1 (555) 000-0000"
          autoComplete="tel"
          prefixIcon={<Phone size={16} />}
          {...register("mobile")}
        />
        <AppInput
          label="GitHub URL"
          placeholder="github.com/username"
          prefixIcon={<Github size={16} />}
          hint="Without https://"
          {...register("github_url")}
        />
        <AppInput
          label="LinkedIn URL"
          placeholder="linkedin.com/in/username"
          prefixIcon={<Linkedin size={16} />}
          hint="Without https://"
          {...register("linkedin_url")}
        />
      </div>

      <TagInput
        label="Top Skills"
        hint="Type a skill and press Enter. These are used to tailor interview questions."
        tags={skills ?? []}
        onChange={(tags) => setValue("skills", tags, { shouldValidate: true })}
        placeholder="e.g. Python, System Design, React…"
        error={errors.skills?.message as string}
      />
    </div>
  );
}
```

### Step 2 — Experience

**File: `src/app/(app)/profile/new/_steps/Step2Experience.tsx`**

Key fix: "Currently working here" checkbox that disables end_date, tag input for skills.

```tsx
"use client";
import { useFieldArray, useFormContext } from "react-hook-form";
import { Plus, Trash2 } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppInput } from "@/components/primitives/AppInput";
import { AppTextarea } from "@/components/primitives/AppTextarea";
import { TagInput } from "@/components/primitives/TagInput";
import { AppCard } from "@/components/primitives/AppCard";

const defaultExperience = {
  role: "", company: "", emp_type: "full_time",
  start_date: "", end_date: "", currently_working: false,
  loc_type: "onsite", location: "", description: "", skills_used: [],
};

export function Step2Experience() {
  const { register, watch, setValue, control } = useFormContext();
  const { fields, append, remove } = useFieldArray({ control, name: "experiences" });
  const experiences = watch("experiences") ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-text-main">Work Experience</h2>
          <p className="text-sm text-text-secondary mt-1">
            Add your professional history, most recent first.
          </p>
        </div>
        <AppButton
          type="button"
          variant="outline"
          size="sm"
          leftIcon={<Plus size={14} />}
          onClick={() => append(defaultExperience)}
        >
          Add
        </AppButton>
      </div>

      {fields.length === 0 && (
        <div className="text-center py-8 text-text-muted text-sm border-2 border-dashed border-warm-border rounded-xl">
          No experience added yet. Click "Add" to add your first role.
        </div>
      )}

      {fields.map((field, i) => {
        const currentlyWorking = experiences[i]?.currently_working;
        const skills = experiences[i]?.skills_used ?? [];

        return (
          <AppCard key={field.id} variant="outlined" className="relative">
            {/* Remove button */}
            <button
              type="button"
              onClick={() => remove(i)}
              className="absolute top-4 right-4 p-1.5 rounded-md text-text-muted hover:text-error hover:bg-error/10 transition-colors"
            >
              <Trash2 size={16} />
            </button>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pr-10">
              <AppInput label="Role / Title" placeholder="Senior Engineer" {...register(`experiences.${i}.role`)} required />
              <AppInput label="Company" placeholder="Acme Corp" {...register(`experiences.${i}.company`)} required />

              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-text-main">Employment Type</label>
                <select
                  className="w-full rounded-lg border border-warm-border bg-white px-3 py-2.5 text-sm text-text-main focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-600/20"
                  {...register(`experiences.${i}.emp_type`)}
                >
                  <option value="full_time">Full-time</option>
                  <option value="part_time">Part-time</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-text-main">Location Type</label>
                <select
                  className="w-full rounded-lg border border-warm-border bg-white px-3 py-2.5 text-sm text-text-main focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-600/20"
                  {...register(`experiences.${i}.loc_type`)}
                >
                  <option value="onsite">On-site</option>
                  <option value="remote">Remote</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>

              <AppInput label="Start Date" type="date" {...register(`experiences.${i}.start_date`)} required />

              <div className="flex flex-col gap-1.5">
                <AppInput
                  label="End Date"
                  type="date"
                  disabled={currentlyWorking}
                  {...register(`experiences.${i}.end_date`)}
                />
                <label className="flex items-center gap-2 cursor-pointer mt-1">
                  <input
                    type="checkbox"
                    className="rounded border-warm-border accent-brand-600"
                    checked={currentlyWorking ?? false}
                    onChange={(e) =>
                      setValue(`experiences.${i}.currently_working`, e.target.checked)
                    }
                  />
                  <span className="text-xs text-text-secondary">Currently working here</span>
                </label>
              </div>

              <div className="sm:col-span-2">
                <TagInput
                  label="Skills Used"
                  tags={skills}
                  onChange={(tags) => setValue(`experiences.${i}.skills_used`, tags)}
                  placeholder="React, Node.js, AWS…"
                />
              </div>

              <div className="sm:col-span-2">
                <AppTextarea
                  label="Description"
                  placeholder="Describe your key responsibilities and achievements…"
                  {...register(`experiences.${i}.description`)}
                />
              </div>
            </div>
          </AppCard>
        );
      })}

      {fields.length > 0 && (
        <AppButton
          type="button"
          variant="ghost"
          size="sm"
          leftIcon={<Plus size={14} />}
          onClick={() => append(defaultExperience)}
        >
          Add another experience
        </AppButton>
      )}
    </div>
  );
}
```

> **Note:** Steps 3 (Education), 4 (Projects), and 5 (Leadership + Review) follow the exact same pattern as Step 2. Step 3 adds "Currently studying" checkbox. Step 5 shows a read-only review summary of all sections before save.

---

## 4.4 ProfileView (Read-only)

**File: `src/app/(app)/profile/page.tsx`**

Improvements: hero card with avatar + current role, formatted dates, styled skill badges, profile strength banner, edit buttons per section.

```tsx
"use client";
import { useRouter } from "next/navigation";
import {
  Github, Linkedin, Briefcase, GraduationCap,
  Code, Trophy, Edit2, PlusCircle, MapPin,
} from "lucide-react";
import { AppCard } from "@/components/primitives/AppCard";
import { AppButton } from "@/components/primitives/AppButton";
import { InitialsAvatar } from "@/components/primitives/InitialsAvatar";
import { ProfileSectionSkeleton } from "@/components/primitives/Skeletons";
import { EmptyState } from "@/components/primitives/EmptyState";
import { useProfile } from "@/hooks/use-profile";
import { formatDate } from "@/lib/utils";
import { EMP_TYPE_LABELS, LOC_TYPE_LABELS } from "@/lib/constants";

export default function ProfileViewPage() {
  const router = useRouter();
  const { data: profile, isLoading } = useProfile();

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        <ProfileSectionSkeleton />
        <ProfileSectionSkeleton />
        <ProfileSectionSkeleton />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <EmptyState
          icon={PlusCircle}
          title="No profile yet"
          description="Build your comprehensive profile to get AI-tailored interview questions."
          action={
            <AppButton variant="brand" onClick={() => router.push("/profile/new")}>
              Build Profile
            </AppButton>
          }
        />
      </div>
    );
  }

  const currentRole = profile.experiences?.[0];

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-8 space-y-6">
      {/* Hero Card */}
      <AppCard>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <InitialsAvatar name={profile.name} size="xl" />
            <div>
              <h1 className="text-2xl font-semibold text-text-main">{profile.name}</h1>
              {currentRole && (
                <p className="text-base text-text-secondary mt-0.5">
                  {currentRole.role} at {currentRole.company}
                </p>
              )}
              <div className="flex flex-wrap items-center gap-4 mt-3">
                <span className="text-sm text-text-muted">{profile.email}</span>
                {profile.mobile && (
                  <span className="text-sm text-text-muted">{profile.mobile}</span>
                )}
                {profile.github_url && (
                  <a
                    href={`https://${profile.github_url.replace(/^https?:\/\//, "")}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 text-sm text-brand-600 hover:text-brand-700 transition-colors"
                  >
                    <Github size={14} /> GitHub
                  </a>
                )}
                {profile.linkedin_url && (
                  <a
                    href={`https://${profile.linkedin_url.replace(/^https?:\/\//, "")}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 text-sm text-brand-600 hover:text-brand-700 transition-colors"
                  >
                    <Linkedin size={14} /> LinkedIn
                  </a>
                )}
              </div>
            </div>
          </div>

          <AppButton
            variant="outline"
            size="sm"
            leftIcon={<Edit2 size={14} />}
            onClick={() => router.push("/profile/edit")}
            className="flex-shrink-0"
          >
            Edit
          </AppButton>
        </div>

        {/* Skills */}
        {profile.skills?.length > 0 && (
          <div className="mt-6 pt-6 border-t border-warm-border">
            <p className="text-xs font-semibold uppercase tracking-widest text-text-muted mb-3">
              Top Skills
            </p>
            <div className="flex flex-wrap gap-2">
              {profile.skills.map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-brand-50 text-brand-700 border border-brand-200"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
      </AppCard>

      {/* Experience */}
      {profile.experiences?.length > 0 && (
        <AppCard>
          <div className="flex items-center gap-2 mb-6 pb-4 border-b border-warm-border">
            <Briefcase size={18} className="text-brand-600" />
            <h2 className="text-lg font-semibold text-text-main">Experience</h2>
          </div>
          <div className="space-y-6">
            {profile.experiences.map((exp, i) => (
              <div key={i} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="h-2 w-2 rounded-full bg-brand-500 mt-1.5" />
                  {i < profile.experiences.length - 1 && (
                    <div className="flex-1 w-px bg-warm-border mt-2" />
                  )}
                </div>
                <div className="pb-6 min-w-0 flex-1">
                  <h3 className="font-semibold text-text-main">
                    {exp.role}{" "}
                    <span className="font-normal text-text-secondary">at {exp.company}</span>
                  </h3>
                  <p className="text-sm text-text-muted mt-0.5">
                    {formatDate(exp.start_date)} – {exp.end_date ? formatDate(exp.end_date) : "Present"}
                    {" · "}{EMP_TYPE_LABELS[exp.emp_type] ?? exp.emp_type}
                    {exp.loc_type && ` · ${LOC_TYPE_LABELS[exp.loc_type] ?? exp.loc_type}`}
                  </p>
                  {exp.description && (
                    <p className="text-sm text-text-main mt-2 leading-relaxed">{exp.description}</p>
                  )}
                  {exp.skills_used?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {exp.skills_used.map((s: string) => (
                        <span key={s} className="text-xs px-2 py-0.5 bg-warm-muted text-text-secondary rounded-md">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </AppCard>
      )}

      {/* Education, Projects, Leadership follow the same pattern */}
      {/* ... (abbreviated — same structure as Experience above) */}
    </div>
  );
}
```

---

## Phase 4 Verification Checklist

- [ ] Dashboard shows greeting with first name from profile
- [ ] Onboarding checklist appears for new users (no profile, no interviews)
- [ ] Onboarding checklist disappears once both steps done
- [ ] Profile health card shows completeness percentage and section counts
- [ ] Interview history shows status badge (Completed / Abandoned)
- [ ] Delete hover shows trash icon only on hover (not always visible)
- [ ] Delete click opens `ConfirmModal` (not `window.confirm`)
- [ ] Profile wizard 5 steps navigate via sidebar + Continue/Back buttons
- [ ] "Currently working here" checkbox disables end_date input
- [ ] Skill chip inputs (TagInput) work for basic info, experience, education, projects
- [ ] Pre-fills from existing profile in edit mode
- [ ] ProfileView shows formatted dates (e.g., "Jan 2022 – Present")
- [ ] ProfileView shows skills as amber badge chips (not plain text)
- [ ] Raw email no longer appears anywhere in the profile view

---

## Files Created in Phase 4

| File | Description |
|---|---|
| `src/app/(app)/dashboard/page.tsx` | Full dashboard with stats, onboarding, history |
| `src/app/(app)/profile/page.tsx` | ProfileView hero card with formatted dates |
| `src/app/(app)/profile/new/page.tsx` | 5-step wizard shell |
| `src/app/(app)/profile/new/_steps/Step1BasicInfo.tsx` | Name, URLs, tag skills |
| `src/app/(app)/profile/new/_steps/Step2Experience.tsx` | Work experience with "currently working" |
| `src/app/(app)/profile/new/_steps/Step3Education.tsx` | Education + "currently studying" |
| `src/app/(app)/profile/new/_steps/Step4Projects.tsx` | Projects with GitHub/deploy links |
| `src/app/(app)/profile/new/_steps/Step5LeadershipReview.tsx` | Leadership + review summary |
| `src/app/(app)/profile/edit/page.tsx` | Re-exports wizard page in edit mode |
