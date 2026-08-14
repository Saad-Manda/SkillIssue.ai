"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm, FormProvider } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ChevronRight, Loader2, BrainCircuit, Check } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppCard } from "@/components/primitives/AppCard";
import { AppInput } from "@/components/primitives/AppInput";
import { AppTextarea } from "@/components/primitives/AppTextarea";
import { TagInput } from "@/components/primitives/TagInput";
import { useAuthStore } from "@/store/auth-store";
import { jdApi, sessionApi } from "@/lib/api";
import { INTERVIEW_LENGTHS } from "@/lib/constants";
import { setupInterviewSchema, type SetupInterviewForm } from "@/lib/validation";
import { cn } from "@/lib/utils";

// ── Interview Length Card ──────────────────────────────────────────
function LengthCard({
  option,
  selected,
  onSelect,
}: {
  option: typeof INTERVIEW_LENGTHS[number];
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={cn(
        "flex flex-col gap-2 p-4 rounded-xl border-2 text-left transition-all duration-150 cursor-pointer w-full",
        selected
          ? "border-brand-500 bg-brand-50 shadow-brand"
          : "border-warm-border bg-white hover:border-brand-200 hover:bg-brand-50/30"
      )}
    >
      <div className="flex items-center justify-between">
        <span className="font-semibold text-text-main">{option.label}</span>
        {selected && (
          <div className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-600">
            <Check size={12} className="text-white" />
          </div>
        )}
      </div>
      <div className="flex items-center gap-2">
        <span className="text-lg font-bold text-brand-700">{option.duration}</span>
        <span className="text-xs text-text-muted">· {option.questions}</span>
      </div>
      <p className="text-xs text-text-secondary">{option.description}</p>
    </button>
  );
}

// ── Setup Loading Overlay ─────────────────────────────────────────
function SetupLoadingOverlay({ step }: { step: number }) {
  const loadingSteps = [
    "Creating job profile…",
    "Analyzing required skills…",
    "Initializing AI agents…",
    "Generating interview plan…",
    "Preparing your first question…",
  ];

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-warm-bg/95 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-6 max-w-sm text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-600 shadow-warm-lg">
          <BrainCircuit size={28} className="text-white animate-pulse" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-text-main">Setting up your interview</h2>
          <p className="text-sm text-text-secondary mt-2">
            This takes a moment while our AI plans your personalized session.
          </p>
        </div>

        {/* Progress steps */}
        <div className="w-full space-y-2">
          {loadingSteps.slice(0, step + 1).map((s, i) => (
            <div key={i} className="flex items-center gap-3 text-sm">
              {i < step ? (
                <div className="h-5 w-5 rounded-full bg-success flex items-center justify-center flex-shrink-0">
                  <Check size={12} className="text-white" />
                </div>
              ) : (
                <Loader2 size={18} className="text-brand-600 animate-spin flex-shrink-0" />
              )}
              <span className={i < step ? "text-text-muted line-through" : "text-text-main font-medium"}>
                {s}
              </span>
            </div>
          ))}
        </div>

        {/* Progress bar */}
        <div className="w-full h-1 bg-warm-border rounded-full overflow-hidden">
          <div
            className="h-full bg-brand-500 rounded-full transition-all duration-700"
            style={{ width: `${((step + 1) / loadingSteps.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}

// ── Main Setup Page ────────────────────────────────────────────────
const STEPS = [
  { id: 1, label: "Job Details" },
  { id: 2, label: "Skills" },
  { id: 3, label: "Configuration" },
  { id: 4, label: "Review" },
];

export default function SetupInterviewPage() {
  const router = useRouter();
  const { user } = useAuthStore();

  const [currentStep, setCurrentStep] = useState(1);
  const [loadingStep, setLoadingStep] = useState(-1); // -1 = not loading
  const [apiError, setApiError] = useState<string | null>(null);

  const methods = useForm<SetupInterviewForm>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(setupInterviewSchema) as any,
    defaultValues: {
      job_title: "",
      job_type: "full_time",
      min_experience: 0,
      required_qualification: "Bachelors",
      required_skills: [],
      responsibilities: "",
      description: "",
      interview_length: "medium",
    },
  });

  const { register, watch, setValue, handleSubmit, formState: { errors } } = methods;
  const formData = watch();

  const simulateLoadingSteps = async (fn: () => Promise<void>) => {
    setLoadingStep(0);
    await new Promise((r) => setTimeout(r, 800));
    setLoadingStep(1);
    await fn(); // Actual API call happens at step 2
    setLoadingStep(2);
    await new Promise((r) => setTimeout(r, 600));
    setLoadingStep(3);
    await new Promise((r) => setTimeout(r, 600));
    setLoadingStep(4);
    await new Promise((r) => setTimeout(r, 400));
  };

  const onSubmit = async (data: SetupInterviewForm) => {
    setApiError(null);
    let jdId: string | null = null;

    try {
      await simulateLoadingSteps(async () => {
        // 1. Create JD
        const respsArray = data.responsibilities
          ? data.responsibilities.split("\n").filter(Boolean)
          : ["General responsibilities"];

        const jdResult = await jdApi.create({
          job_title:              data.job_title,
          job_type:               data.job_type,
          min_experience:         data.min_experience,
          required_skills:        data.required_skills,
          responsibilities:       respsArray,
          required_qualification: data.required_qualification,
          description:            data.description,
        });
        jdId = jdResult.jd_id;
      });
    } catch (err: unknown) {
      const e = err as { message?: string };
      setApiError(e.message ?? "Failed to create interview. Please try again.");
      setLoadingStep(-1);
      return;
    }

    if (!jdId) return;

    // 2. Start session
    try {
      const session = await sessionApi.start(user!.id, jdId, data.interview_length);

      // Store in sessionStorage for the InterviewSession page to read
      sessionStorage.setItem(
        `session_${session.session_id}`,
        JSON.stringify(session)
      );

      router.push(`/interview/${session.session_id}`);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setApiError(e.message ?? "Failed to start session.");
      setLoadingStep(-1);
    }
  };

  return (
    <FormProvider {...methods}>
      <div className="max-w-3xl mx-auto px-4 md:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-text-main">Set Up Interview</h1>
          <p className="text-sm text-text-secondary mt-1">
            Describe the role you&apos;re preparing for — our AI will build a tailored session.
          </p>
        </div>

        {/* Step progress bar */}
        <div className="flex items-center gap-2 mb-8">
          {STEPS.map((step, i) => (
            <div key={step.id} className="flex items-center gap-2 flex-1">
              <div className={cn(
                "flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold flex-shrink-0 transition-colors",
                step.id < currentStep  && "bg-success text-white",
                step.id === currentStep && "bg-brand-600 text-white",
                step.id > currentStep  && "bg-warm-muted text-text-muted"
              )}>
                {step.id < currentStep ? <Check size={12} /> : step.id}
              </div>
              <span className={cn(
                "text-sm hidden sm:block",
                step.id === currentStep ? "font-medium text-text-main" : "text-text-muted"
              )}>
                {step.label}
              </span>
              {i < STEPS.length - 1 && (
                <div className={cn(
                  "flex-1 h-px mx-2",
                  step.id < currentStep ? "bg-success" : "bg-warm-border"
                )} />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <form onSubmit={handleSubmit(onSubmit)}>
          <AppCard>
            {/* Step 1 — Job Details */}
            {currentStep === 1 && (
              <div className="space-y-5">
                <div>
                  <h2 className="text-lg font-semibold text-text-main">Job Details</h2>
                  <p className="text-sm text-text-secondary mt-1">Basic information about the role.</p>
                </div>

                <AppInput
                  label="Job Title"
                  placeholder="e.g. Senior Frontend Engineer"
                  error={errors.job_title?.message}
                  {...register("job_title")}
                  required
                />

                <div className="grid grid-cols-2 gap-4">
                  <AppInput
                    label="Min. Experience (years)"
                    type="number"
                    min={0}
                    step={0.5}
                    error={errors.min_experience?.message}
                    {...register("min_experience")}
                  />
                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-text-main">Job Type</label>
                    <select
                      className="w-full rounded-lg border border-warm-border bg-white px-3 py-2.5 text-sm text-text-main focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-600/20"
                      {...register("job_type")}
                    >
                      <option value="full_time">Full-time</option>
                      <option value="part_time">Part-time</option>
                    </select>
                  </div>
                </div>

                <AppInput
                  label="Required Qualification"
                  placeholder="e.g. Bachelors in Computer Science"
                  {...register("required_qualification")}
                />

                <AppTextarea
                  label="Key Responsibilities (one per line)"
                  placeholder={"Develop scalable React components…\nLead code reviews…"}
                  hint="Optional — helps the AI understand the role better."
                  {...register("responsibilities")}
                />
              </div>
            )}

            {/* Step 2 — Skills */}
            {currentStep === 2 && (
              <div className="space-y-5">
                <div>
                  <h2 className="text-lg font-semibold text-text-main">Required Skills</h2>
                  <p className="text-sm text-text-secondary mt-1">
                    Add the technical and soft skills required for this role.
                  </p>
                </div>

                <TagInput
                  label="Required Skills"
                  tags={formData.required_skills}
                  onChange={(tags) => setValue("required_skills", tags, { shouldValidate: true })}
                  placeholder="React, TypeScript, GraphQL…"
                  error={errors.required_skills?.message}
                  hint="Press Enter after each skill. The more skills you add, the better the AI can probe."
                />

                <AppTextarea
                  label="Full Job Description (Optional)"
                  placeholder="Paste the complete job description here for maximum context…"
                  hint="Optional but highly recommended. The AI uses this as context for all questions."
                  showCount
                  maxLength={5000}
                  {...register("description")}
                />
              </div>
            )}

            {/* Step 3 — Interview Configuration */}
            {currentStep === 3 && (
              <div className="space-y-5">
                <div>
                  <h2 className="text-lg font-semibold text-text-main">Interview Configuration</h2>
                  <p className="text-sm text-text-secondary mt-1">
                    Choose the interview length that fits your available time.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {INTERVIEW_LENGTHS.map((opt) => (
                    <LengthCard
                      key={opt.value}
                      option={opt}
                      selected={formData.interview_length === opt.value}
                      onSelect={() => setValue("interview_length", opt.value)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Step 4 — Review */}
            {currentStep === 4 && (
              <div className="space-y-5">
                <div>
                  <h2 className="text-lg font-semibold text-text-main">Review & Start</h2>
                  <p className="text-sm text-text-secondary mt-1">
                    Confirm the details below then start your interview.
                  </p>
                </div>

                {apiError && (
                  <div className="rounded-lg bg-error/8 border border-error/20 px-4 py-3">
                    <p className="text-sm text-error">{apiError}</p>
                  </div>
                )}

                <div className="space-y-3 rounded-xl border border-warm-border p-4 bg-warm-muted/50">
                  <ReviewRow label="Job Title"       value={formData.job_title} />
                  <ReviewRow label="Job Type"        value={formData.job_type === "full_time" ? "Full-time" : "Part-time"} />
                  <ReviewRow label="Experience"      value={`${formData.min_experience} years`} />
                  <ReviewRow label="Qualification"   value={formData.required_qualification} />
                  <ReviewRow
                    label="Skills"
                    value={formData.required_skills.length > 0
                      ? formData.required_skills.join(", ")
                      : "None added"}
                  />
                  <ReviewRow
                    label="Interview Length"
                    value={INTERVIEW_LENGTHS.find((l) => l.value === formData.interview_length)?.label ?? "Medium"}
                    subValue={INTERVIEW_LENGTHS.find((l) => l.value === formData.interview_length)?.duration}
                  />
                </div>
              </div>
            )}
          </AppCard>

          {/* Navigation */}
          <div className="flex justify-between mt-6">
            <AppButton
              type="button"
              variant="outline"
              onClick={() => currentStep > 1 ? setCurrentStep((s) => s - 1) : router.push("/dashboard")}
            >
              {currentStep === 1 ? "Cancel" : "← Back"}
            </AppButton>

            {currentStep < 4 ? (
              <AppButton
                type="button"
                variant="brand"
                rightIcon={<ChevronRight size={16} />}
                onClick={() => setCurrentStep((s) => s + 1)}
              >
                Continue
              </AppButton>
            ) : (
              <AppButton type="submit" variant="brand" size="lg">
                Start Interview
              </AppButton>
            )}
          </div>
        </form>
      </div>

      {/* Loading overlay */}
      {loadingStep >= 0 && <SetupLoadingOverlay step={loadingStep} />}
    </FormProvider>
  );
}

function ReviewRow({ label, value, subValue }: { label: string; value: string; subValue?: string }) {
  return (
    <div className="flex justify-between items-baseline gap-4 py-1.5 border-b border-warm-border last:border-0">
      <span className="text-sm font-medium text-text-secondary flex-shrink-0">{label}</span>
      <span className="text-sm text-text-main text-right">
        {value}
        {subValue && <span className="text-text-muted ml-1.5">({subValue})</span>}
      </span>
    </div>
  );
}
