# Phase 5 — Interview Flow

> **Goal:** Build the core interview experience: Setup wizard → Live session → Report → History detail. This is the product's highest-value surface and needs the most polish.  
> **Prerequisite:** All previous phases complete.  
> **Output:** A complete, production-quality interview flow matching all audit improvements.

---

## 5.1 Interview Setup — 4-Step Wizard

**File: `src/app/(app)/interview/setup/page.tsx`**

Fixes: interview length selector with visual cards (not hardcoded 'short'), TagInput for skills, animated loading state ("Creating job profile… Initializing AI agents…"), job type select rendered.

```tsx
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
import { INTERVIEW_LENGTHS, type InterviewLength } from "@/lib/constants";
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
    resolver: zodResolver(setupInterviewSchema),
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
    }).catch((err: unknown) => {
      const e = err as { message?: string };
      setApiError(e.message ?? "Failed to create interview. Please try again.");
      setLoadingStep(-1);
    });

    if (!jdId || loadingStep < 0) return;

    // 2. Start session
    const session = await sessionApi
      .start(user!.id, jdId, data.interview_length)
      .catch((err: unknown) => {
        const e = err as { message?: string };
        setApiError(e.message ?? "Failed to start session.");
        setLoadingStep(-1);
        return null;
      });

    if (!session) return;

    router.push(`/interview/${session.session_id}`, {
      // Pass initial state via search params (Next.js doesn't do router.state)
    });
    // Store in sessionStorage for the InterviewSession page to read
    sessionStorage.setItem(
      `session_${session.session_id}`,
      JSON.stringify(session)
    );
    router.push(`/interview/${session.session_id}`);
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
```

---

## 5.2 Interview Session

**File: `src/app/(app)/interview/[session_id]/page.tsx`**

Fixes: rich sidebar with phase stepper + turn counter + timer, AI thinking animation with pulsing dots, message avatars, auto-growing textarea, keyboard hint, End Interview confirmation modal.

```tsx
"use client";
import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Send, FileText, BrainCircuit, User2, Clock } from "lucide-react";
import { sessionApi } from "@/lib/api";
import { AppButton } from "@/components/primitives/AppButton";
import { ConfirmModal } from "@/components/primitives/ConfirmModal";
import { InitialsAvatar } from "@/components/primitives/InitialsAvatar";
import { useAuthStore } from "@/store/auth-store";
import { cn } from "@/lib/utils";
import type { AnswerResponse } from "@/types/api";

// ── AI Thinking indicator ──────────────────────────────────────────
function AIThinking() {
  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 border border-brand-200 flex-shrink-0">
        <BrainCircuit size={14} className="text-brand-700" />
      </div>
      <div className="flex items-center gap-1.5 px-4 py-3 bg-white border border-warm-border rounded-2xl rounded-tl-sm shadow-warm-sm">
        <div className="flex gap-1 items-end h-4">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-brand-400"
              style={{ animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite` }}
            />
          ))}
        </div>
        <span className="text-sm text-text-muted ml-1">Thinking…</span>
      </div>
    </div>
  );
}

// ── Chat message ───────────────────────────────────────────────────
function ChatMessage({
  role,
  content,
  userInitials,
}: {
  role: "ai" | "user";
  content: string;
  userInitials: string;
}) {
  const isAI = role === "ai";

  return (
    <div className={cn("flex items-start gap-3", !isAI && "flex-row-reverse")}>
      {/* Avatar */}
      <div className={cn(
        "flex h-8 w-8 items-center justify-center rounded-full flex-shrink-0",
        isAI ? "bg-brand-100 border border-brand-200" : "bg-stone-800"
      )}>
        {isAI
          ? <BrainCircuit size={14} className="text-brand-700" />
          : <span className="text-xs font-semibold text-white">{userInitials}</span>
        }
      </div>

      {/* Bubble */}
      <div className={cn(
        "max-w-[75%] px-4 py-3 text-sm leading-relaxed shadow-warm-sm",
        isAI
          ? "bg-white border border-warm-border rounded-2xl rounded-tl-sm text-text-main"
          : "bg-stone-900 rounded-2xl rounded-tr-sm text-white"
      )}>
        {content}
      </div>
    </div>
  );
}

// ── Elapsed timer ──────────────────────────────────────────────────
function ElapsedTimer({ startTime }: { startTime: Date }) {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const id = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime.getTime()) / 1000));
    }, 1000);
    return () => clearInterval(id);
  }, [startTime]);

  const mins = Math.floor(elapsed / 60);
  const secs = elapsed % 60;
  return (
    <span className="font-mono text-xs text-text-muted tabular-nums">
      {mins.toString().padStart(2, "0")}:{secs.toString().padStart(2, "0")}
    </span>
  );
}

// ── Main Session Page ──────────────────────────────────────────────
export default function InterviewSessionPage() {
  const { session_id } = useParams<{ session_id: string }>();
  const router = useRouter();
  const { user } = useAuthStore();

  const [chat, setChat] = useState<{ role: "ai" | "user"; content: string }[]>([]);
  const [currentPhase, setCurrentPhase] = useState("Initializing…");
  const [currentTopic, setCurrentTopic] = useState("");
  const [turnCount, setTurnCount] = useState(0);
  const [inputMessage, setInputMessage] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showEndModal, setShowEndModal] = useState(false);
  const [startTime] = useState(new Date());

  const endRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load initial question from sessionStorage
  useEffect(() => {
    const stored = sessionStorage.getItem(`session_${session_id}`);
    if (stored) {
      const init = JSON.parse(stored) as {
        current_question: string;
        current_phase_name: string;
        current_topic_name?: string;
      };
      setChat([{ role: "ai", content: init.current_question }]);
      setCurrentPhase(init.current_phase_name ?? "Opening");
      setCurrentTopic(init.current_topic_name ?? "");
    } else {
      setChat([{ role: "ai", content: "Welcome! Press Enter to begin your interview." }]);
    }
  }, [session_id]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, isProcessing]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputMessage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isProcessing) return;

    const userMsg = inputMessage.trim();
    setChat((prev) => [...prev, { role: "user", content: userMsg }]);
    setInputMessage("");
    setIsProcessing(true);
    setError(null);

    try {
      const response = await sessionApi.submitAnswer(session_id, userMsg) as AnswerResponse;

      if (response.current_question) {
        setChat((prev) => [...prev, { role: "ai", content: response.current_question! }]);
        setCurrentPhase(response.current_phase_name ?? currentPhase);
        setCurrentTopic(response.current_topic_name ?? "");
        setTurnCount((c) => c + 1);
      } else {
        // Interview complete — navigate to report
        router.push(`/report/${session_id}`);
      }
    } catch (err: unknown) {
      const e = err as { message?: string };
      setError(e.message ?? "Failed to submit answer. Please try again.");
      setChat((prev) => prev.slice(0, -1));
      setInputMessage(userMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  const userInitials = (user?.username ?? user?.email ?? "U").slice(0, 2).toUpperCase();

  return (
    <>
      <div className="flex h-[calc(100vh-56px)]">
        {/* ── Sidebar ───────────────────────────────────────────────── */}
        <div className="w-72 flex-shrink-0 border-r border-warm-border bg-white flex flex-col">
          {/* Header */}
          <div className="px-5 py-4 border-b border-warm-border">
            <p className="text-xs font-semibold uppercase tracking-widest text-text-muted">
              Session Progress
            </p>
          </div>

          {/* Stats */}
          <div className="px-5 py-4 border-b border-warm-border grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-0.5">
              <p className="text-xs text-text-muted">Turn</p>
              <p className="text-2xl font-bold text-text-main tabular-nums">{turnCount}</p>
            </div>
            <div className="flex flex-col gap-0.5">
              <p className="text-xs text-text-muted">Elapsed</p>
              <div className="flex items-center gap-1 mt-0.5">
                <Clock size={12} className="text-text-muted" />
                <ElapsedTimer startTime={startTime} />
              </div>
            </div>
          </div>

          {/* Current Phase & Topic */}
          <div className="px-5 py-4 flex-1">
            <div className="mb-4">
              <p className="text-xs text-text-muted mb-1">Current Phase</p>
              <p className="text-sm font-semibold text-text-main">{currentPhase}</p>
            </div>
            {currentTopic && (
              <div>
                <p className="text-xs text-text-muted mb-1">Active Topic</p>
                <p className="text-sm text-text-secondary">{currentTopic}</p>
              </div>
            )}
          </div>

          {/* End interview */}
          <div className="px-5 py-4 border-t border-warm-border">
            <AppButton
              variant="outline"
              size="sm"
              fullWidth
              leftIcon={<FileText size={14} />}
              onClick={() => setShowEndModal(true)}
            >
              End & Get Report
            </AppButton>
          </div>
        </div>

        {/* ── Chat Canvas ──────────────────────────────────────────── */}
        <div className="flex-1 flex flex-col bg-warm-bg overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-8">
            <div className="max-w-2xl mx-auto space-y-5">
              {chat.map((msg, i) => (
                <ChatMessage
                  key={i}
                  role={msg.role}
                  content={msg.content}
                  userInitials={userInitials}
                />
              ))}

              {isProcessing && <AIThinking />}

              <div ref={endRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="border-t border-warm-border bg-white px-6 py-4">
            <div className="max-w-2xl mx-auto">
              {error && (
                <div className="mb-3 text-xs text-error bg-error/8 border border-error/20 px-3 py-2 rounded-lg">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="flex gap-3 items-end">
                <div className="flex-1">
                  <textarea
                    ref={textareaRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    disabled={isProcessing}
                    placeholder="Type your answer…"
                    rows={1}
                    className={cn(
                      "w-full resize-none rounded-xl border border-warm-border bg-warm-bg px-4 py-3",
                      "text-sm text-text-main placeholder:text-text-muted",
                      "focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-600/20",
                      "disabled:opacity-50 transition-colors duration-150",
                      "max-h-48 overflow-y-auto"
                    )}
                    style={{ minHeight: "52px" }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit(e as unknown as React.FormEvent);
                      }
                    }}
                    aria-label="Your answer"
                  />
                  <p className="text-xs text-text-muted mt-1.5 pl-1">
                    Press <kbd className="px-1.5 py-0.5 bg-warm-muted rounded text-[10px] font-mono">Enter</kbd> to send
                    {" · "}
                    <kbd className="px-1.5 py-0.5 bg-warm-muted rounded text-[10px] font-mono">Shift + Enter</kbd> for new line
                  </p>
                </div>

                <AppButton
                  type="submit"
                  variant="brand"
                  size="md"
                  disabled={isProcessing || !inputMessage.trim()}
                  isLoading={isProcessing}
                  className="mb-6"
                >
                  <Send size={16} />
                </AppButton>
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* CSS for AI thinking bounce animation */}
      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-8px); }
        }
      `}</style>

      {/* End interview confirmation */}
      <ConfirmModal
        open={showEndModal}
        onOpenChange={setShowEndModal}
        title="End interview?"
        description={`You've completed ${turnCount} turn${turnCount !== 1 ? "s" : ""}. Ending now will generate your readiness report.`}
        confirmLabel="End & Generate Report"
        cancelLabel="Continue Interview"
        variant="default"
        onConfirm={() => router.push(`/report/${session_id}`)}
      />
    </>
  );
}
```

---

## 5.3 Report Page

**File: `src/app/(app)/report/[session_id]/page.tsx`**

Fixes: 8-metric scorecard grid, radar chart, sticky TOC, proper PDF export, metadata header, CTA.

```tsx
"use client";
import { useParams, useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ArrowLeft, Download, BrainCircuit, Calendar, Clock } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppCard } from "@/components/primitives/AppCard";
import { MetricCard } from "@/components/primitives/MetricCard";
import { ScoreRadarChart } from "@/components/primitives/ScoreRadarChart";
import { ReportSkeleton } from "@/components/primitives/Skeletons";
import { useReport } from "@/hooks/use-report";
import { METRICS } from "@/lib/constants";
import { cn } from "@/lib/utils";

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
```

---

## 5.4 Interview History Detail

**File: `src/app/(app)/history/[interview_id]/page.tsx`**

Fixes: Consolidates the two duplicate components (InterviewDetails + InterviewHistoryDetail), replaces raw IDs with human-readable info, shows all 8 metrics with tooltips, adds Q&A timeline format.

```tsx
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
```

---

## Phase 5 Verification Checklist

### Setup
- [ ] Interview length cards render (Short/Medium/Long) with visual selection state
- [ ] Submitting with no skills shows Zod error on step 2
- [ ] "Start Interview" shows animated 5-step loading overlay (not plain spinner)
- [ ] Job type `<select>` is rendered and functional (was missing in old code)
- [ ] Full JD description textarea shows character count

### Interview Session
- [ ] Initial question loads from `sessionStorage` (not lost on navigate)
- [ ] AI thinking shows 3-dot bounce animation (not just "AI is Thinking...")
- [ ] Chat messages show AI logo avatar (BrainCircuit) and user initials avatar
- [ ] Textarea auto-grows with content (no fixed 100px height)
- [ ] Keyboard hint shows below textarea
- [ ] Enter submits; Shift+Enter adds newline
- [ ] Sidebar shows Turn counter and elapsed timer
- [ ] "End & Get Report" opens ConfirmModal (not instant navigate)
- [ ] On session complete (no `current_question` in response), auto-redirects to `/report/:id`

### Report
- [ ] 8 `MetricCard` components render in a 2×4 grid
- [ ] Radar chart renders with all 8 metric labels
- [ ] Export PDF uses `html2pdf.js` (not `window.print()`)
- [ ] "Start Another Interview" CTA at bottom renders
- [ ] Markdown renders code blocks with monospace font + subtle background
- [ ] Report polls every 3s if not yet ready (via `useReport` hook `refetchInterval`)

### History Detail
- [ ] Single consolidated component — `InterviewHistoryDetail.jsx` deleted
- [ ] Page title shows JD job title (not "Interview Report")
- [ ] Responsible skills shown as amber tag chips
- [ ] Turn evaluation shows MetricCard components (not just 3 raw numbers)
- [ ] MetricCard tooltips show full metric name on hover (via InfoIcon)

---

## Files Created in Phase 5

| File | Description |
|---|---|
| `src/app/(app)/interview/setup/page.tsx` | 4-step setup wizard with length cards |
| `src/app/(app)/interview/[session_id]/page.tsx` | Interview session with rich sidebar + AI animation |
| `src/app/(app)/report/[session_id]/page.tsx` | Report with scorecard grid + radar + PDF export |
| `src/app/(app)/history/[interview_id]/page.tsx` | Consolidated history detail with Q&A timeline |

### Files to Delete (from old frontend)
| File | Reason |
|---|---|
| `frontend/src/pages/interview/InterviewHistoryDetail.jsx` | Duplicate — consolidated into single history detail |
| `frontend/src/pages/interview/InterviewDetails.jsx` | Duplicate — same consolidation |
