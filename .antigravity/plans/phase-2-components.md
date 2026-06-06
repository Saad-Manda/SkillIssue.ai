# Phase 2 — Shared Component Library

> **Goal:** Build every reusable primitive and composite component before any page is built. This ensures all pages use consistent patterns and avoid the inline-style sprawl of the current codebase.  
> **Prerequisite:** Phase 1 complete (Tailwind + shadcn/ui + types in place).  
> **Output:** A full component library in `src/components/primitives/` ready for use across all pages.

---

## Component Inventory

| Component | File | Replaces / Fixes |
|---|---|---|
| `AppButton` | `AppButton.tsx` | Old `Button.jsx` — adds variants, sizes, loading spinner, icon-only mode |
| `AppInput` | `AppInput.tsx` | Old `Input.jsx` — adds `htmlFor`, width:100%, hint text, prefix/suffix slots |
| `AppCard` | `AppCard.tsx` | Old `Card.jsx` — removes fixed 440px maxWidth, adds variants |
| `TagInput` | `TagInput.tsx` | Replaces comma-separated text inputs for skills |
| `MetricCard` | `MetricCard.tsx` | NEW — score metric display for Report page |
| `ScoreBar` | `ScoreBar.tsx` | NEW — color-coded progress bar (0–10) |
| `InitialsAvatar` | `InitialsAvatar.tsx` | NEW — avatar with initials fallback |
| `StatusBadge` | `StatusBadge.tsx` | NEW — interview status indicator |
| `ConfirmModal` | `ConfirmModal.tsx` | Replaces `window.confirm()` in Dashboard delete |
| `EmptyState` | `EmptyState.tsx` | NEW — unified empty state pattern |
| `PageHeader` | `../layout/PageHeader.tsx` | NEW — reusable page title + subtitle + actions |
| `ScoreRadarChart` | `ScoreRadarChart.tsx` | NEW — radar chart for 8 metrics in Report |
| `Skeleton variants` | `Skeletons.tsx` | NEW — loading skeletons for each content type |

---

## 2.1 AppButton

**File: `src/components/primitives/AppButton.tsx`**

Variants: `default | outline | ghost | destructive | brand`  
Sizes: `sm | md | lg | icon`

```tsx
"use client";
import { forwardRef } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface AppButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "destructive" | "brand";
  size?: "sm" | "md" | "lg" | "icon";
  isLoading?: boolean;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const variantStyles = {
  default:     "bg-text-main text-white hover:bg-stone-700 focus-visible:ring-text-main",
  outline:     "border border-warm-border bg-white hover:bg-warm-muted text-text-main",
  ghost:       "bg-transparent hover:bg-warm-muted text-text-main",
  destructive: "bg-error text-white hover:bg-red-700 focus-visible:ring-error",
  brand:       "bg-brand-600 text-white hover:bg-brand-700 focus-visible:ring-brand-600 shadow-sm",
};

const sizeStyles = {
  sm:   "h-8  px-3   text-sm   gap-1.5 rounded-md",
  md:   "h-10 px-4   text-sm   gap-2   rounded-lg",
  lg:   "h-11 px-5   text-base gap-2   rounded-lg",
  icon: "h-9  w-9    rounded-lg p-0",
};

export const AppButton = forwardRef<HTMLButtonElement, AppButtonProps>(
  (
    {
      variant = "default",
      size = "md",
      isLoading = false,
      fullWidth = false,
      leftIcon,
      rightIcon,
      children,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || isLoading;

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={cn(
          // Base
          "inline-flex items-center justify-center font-medium",
          "transition-all duration-150 ease-in-out",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          "active:scale-[0.98]",
          // Variants & Sizes
          variantStyles[variant],
          sizeStyles[size],
          // Width
          fullWidth && "w-full",
          className
        )}
        {...props}
      >
        {isLoading ? (
          <>
            <Loader2 size={15} className="animate-spin" />
            {size !== "icon" && <span>Loading…</span>}
          </>
        ) : (
          <>
            {leftIcon}
            {children}
            {rightIcon}
          </>
        )}
      </button>
    );
  }
);
AppButton.displayName = "AppButton";
```

---

## 2.2 AppInput

**File: `src/components/primitives/AppInput.tsx`**

Fixes: `htmlFor` + `id` linking, `width: 100%`, hint text, prefix/suffix icon slots.

```tsx
"use client";
import { forwardRef, useId } from "react";
import { cn } from "@/lib/utils";

interface AppInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  prefixIcon?: React.ReactNode;
  suffixIcon?: React.ReactNode;
  containerClassName?: string;
}

export const AppInput = forwardRef<HTMLInputElement, AppInputProps>(
  (
    {
      label,
      hint,
      error,
      prefixIcon,
      suffixIcon,
      containerClassName,
      className,
      id: externalId,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const inputId = externalId ?? generatedId;

    return (
      <div className={cn("flex flex-col gap-1.5 w-full", containerClassName)}>
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium text-text-main"
          >
            {label}
            {props.required && (
              <span className="text-error ml-1" aria-hidden="true">*</span>
            )}
          </label>
        )}

        <div className="relative flex items-center">
          {prefixIcon && (
            <div className="absolute left-3 text-text-muted pointer-events-none">
              {prefixIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            className={cn(
              "w-full rounded-lg border border-warm-border bg-white px-3 py-2.5",
              "text-sm text-text-main placeholder:text-text-muted",
              "transition-colors duration-150",
              "focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-600/20",
              "disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-warm-muted",
              error && "border-error focus:border-error focus:ring-error/20",
              prefixIcon && "pl-10",
              suffixIcon && "pr-10",
              className
            )}
            aria-invalid={!!error}
            aria-describedby={
              error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined
            }
            {...props}
          />

          {suffixIcon && (
            <div className="absolute right-3 text-text-muted">
              {suffixIcon}
            </div>
          )}
        </div>

        {error && (
          <p id={`${inputId}-error`} className="text-xs text-error flex items-center gap-1">
            {error}
          </p>
        )}
        {hint && !error && (
          <p id={`${inputId}-hint`} className="text-xs text-text-muted">
            {hint}
          </p>
        )}
      </div>
    );
  }
);
AppInput.displayName = "AppInput";
```

---

## 2.3 AppTextarea

**File: `src/components/primitives/AppTextarea.tsx`**

Auto-grows with content. Shows character count when `maxLength` provided.

```tsx
"use client";
import { forwardRef, useId } from "react";
import { cn } from "@/lib/utils";

interface AppTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
  error?: string;
  showCount?: boolean;
  containerClassName?: string;
}

export const AppTextarea = forwardRef<HTMLTextAreaElement, AppTextareaProps>(
  ({ label, hint, error, showCount, containerClassName, className, id: externalId, ...props }, ref) => {
    const generatedId = useId();
    const inputId = externalId ?? generatedId;
    const charCount = typeof props.value === "string" ? props.value.length : 0;

    return (
      <div className={cn("flex flex-col gap-1.5 w-full", containerClassName)}>
        {label && (
          <div className="flex justify-between items-center">
            <label htmlFor={inputId} className="text-sm font-medium text-text-main">
              {label}
              {props.required && <span className="text-error ml-1">*</span>}
            </label>
            {showCount && props.maxLength && (
              <span className="text-xs text-text-muted">
                {charCount}/{props.maxLength}
              </span>
            )}
          </div>
        )}

        <textarea
          ref={ref}
          id={inputId}
          className={cn(
            "w-full rounded-lg border border-warm-border bg-white px-3 py-2.5",
            "text-sm text-text-main placeholder:text-text-muted",
            "transition-colors duration-150 resize-y",
            "min-h-[80px] field-sizing-content",
            "focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-600/20",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            error && "border-error focus:border-error focus:ring-error/20",
            className
          )}
          aria-invalid={!!error}
          {...props}
        />

        {error && <p className="text-xs text-error">{error}</p>}
        {hint && !error && <p className="text-xs text-text-muted">{hint}</p>}
      </div>
    );
  }
);
AppTextarea.displayName = "AppTextarea";
```

---

## 2.4 AppCard

**File: `src/components/primitives/AppCard.tsx`**

No fixed maxWidth. Variants: `default | outlined | flat`. Optional `hoverable` prop for interactive cards.

```tsx
import { cn } from "@/lib/utils";

interface AppCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "outlined" | "flat";
  hoverable?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
}

const variantStyles = {
  default:  "bg-white border border-warm-border shadow-warm-sm",
  outlined: "bg-transparent border-2 border-warm-border",
  flat:     "bg-warm-muted border-0",
};

const paddingStyles = {
  none: "",
  sm:   "p-4",
  md:   "p-6",
  lg:   "p-8",
};

export function AppCard({
  variant = "default",
  hoverable = false,
  padding = "md",
  className,
  children,
  ...props
}: AppCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl w-full",
        variantStyles[variant],
        paddingStyles[padding],
        hoverable && "cursor-pointer transition-shadow duration-200 hover:shadow-warm-md hover:border-warm-border/80",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
```

---

## 2.5 TagInput (Skill Chips)

**File: `src/components/primitives/TagInput.tsx`**

Uses `emblor` library for the tag chip behavior. Wraps it in the app's design language.

```tsx
"use client";
import { useId } from "react";
import { TagInput as EmblorTagInput, Tag } from "emblor";
import { cn } from "@/lib/utils";

interface TagInputProps {
  label?: string;
  hint?: string;
  error?: string;
  tags: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  maxTags?: number;
  className?: string;
}

export function TagInput({
  label,
  hint,
  error,
  tags,
  onChange,
  placeholder = "Type and press Enter…",
  maxTags = 20,
  className,
}: TagInputProps) {
  const id = useId();
  const tagObjects: Tag[] = tags.map((t, i) => ({ id: String(i), text: t }));

  return (
    <div className={cn("flex flex-col gap-1.5 w-full", className)}>
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-text-main">
          {label}
        </label>
      )}

      <EmblorTagInput
        id={id}
        tags={tagObjects}
        setTags={(newTags) => {
          const arr = (typeof newTags === "function" ? newTags(tagObjects) : newTags);
          onChange(arr.map((t) => t.text));
        }}
        placeholder={placeholder}
        maxTags={maxTags}
        styleClasses={{
          input: cn(
            "min-w-[120px] bg-transparent text-sm text-text-main placeholder:text-text-muted",
            "focus:outline-none"
          ),
          tag: {
            body: "inline-flex items-center gap-1 px-2.5 py-1 bg-brand-100 text-brand-800 text-xs font-medium rounded-full border border-brand-200",
            closeButton: "text-brand-600 hover:text-brand-800 ml-1",
          },
          inlineTagsContainer: cn(
            "flex flex-wrap gap-1.5 w-full min-h-[42px] px-3 py-2",
            "rounded-lg border border-warm-border bg-white",
            "focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-600/20",
            "transition-colors duration-150",
            error && "border-error focus-within:ring-error/20"
          ),
        }}
        inputFieldPosition="inline"
      />

      {error && <p className="text-xs text-error">{error}</p>}
      {hint && !error && (
        <p className="text-xs text-text-muted">{hint}</p>
      )}
    </div>
  );
}
```

---

## 2.6 MetricCard (Report Score Card)

**File: `src/components/primitives/MetricCard.tsx`**

Each of the 8 metrics gets its own card with label, score, color bar, and tooltip.

```tsx
import { cn, getScoreColor, getScoreBg, getScoreLabel } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { InfoIcon } from "lucide-react";
import { ScoreBar } from "./ScoreBar";

interface MetricCardProps {
  label: string;        // e.g. "QAR"
  fullName: string;     // e.g. "Question-Answer Relevance"
  description: string;  // Tooltip text
  score: number;        // 0–10
  maxScore?: number;
  className?: string;
}

export function MetricCard({
  label,
  fullName,
  description,
  score,
  maxScore = 10,
  className,
}: MetricCardProps) {
  const normalized = Math.min(Math.max(score, 0), maxScore);
  const displayScore = normalized.toFixed(1);

  return (
    <div
      className={cn(
        "rounded-xl border p-4 flex flex-col gap-3 transition-shadow hover:shadow-warm-md",
        getScoreBg(normalized),
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <span className="text-xs font-semibold uppercase tracking-widest text-text-muted">
            {label}
          </span>
          <p className="text-sm font-medium text-text-main mt-0.5 leading-tight">
            {fullName}
          </p>
        </div>

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="text-text-muted hover:text-text-secondary transition-colors mt-0.5">
                <InfoIcon size={14} />
              </button>
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-[220px] text-xs">
              {description}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      {/* Score */}
      <div className="flex items-end gap-2">
        <span className={cn("text-3xl font-bold tabular-nums", getScoreColor(normalized))}>
          {displayScore}
        </span>
        <span className="text-xs text-text-muted mb-1">/ {maxScore}</span>
        <span className={cn("ml-auto text-xs font-medium", getScoreColor(normalized))}>
          {getScoreLabel(normalized)}
        </span>
      </div>

      {/* Progress bar */}
      <ScoreBar score={normalized} maxScore={maxScore} />
    </div>
  );
}
```

---

## 2.7 ScoreBar

**File: `src/components/primitives/ScoreBar.tsx`**

```tsx
import { cn } from "@/lib/utils";

interface ScoreBarProps {
  score: number;
  maxScore?: number;
  height?: "sm" | "md";
  className?: string;
}

export function ScoreBar({ score, maxScore = 10, height = "sm", className }: ScoreBarProps) {
  const pct = Math.min(Math.max((score / maxScore) * 100, 0), 100);

  const barColor =
    score >= 8 ? "bg-success" :
    score >= 6 ? "bg-warning" :
    score >= 4 ? "bg-orange-500" :
    "bg-error";

  return (
    <div
      className={cn(
        "w-full rounded-full bg-black/5 overflow-hidden",
        height === "sm" ? "h-1.5" : "h-2.5",
        className
      )}
    >
      <div
        className={cn("h-full rounded-full transition-all duration-500 ease-out", barColor)}
        style={{ width: `${pct}%` }}
        role="progressbar"
        aria-valuenow={score}
        aria-valuemin={0}
        aria-valuemax={maxScore}
      />
    </div>
  );
}
```

---

## 2.8 ScoreRadarChart (Report — 8 Metrics Radar)

**File: `src/components/primitives/ScoreRadarChart.tsx`**

Uses Recharts (included via shadcn chart). Renders all 8 metrics in a radar chart.

```tsx
"use client";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";
import type { METRICS } from "@/lib/constants";

type MetricEntry = {
  metric: string; // short label
  score: number;
  fullMark: number;
};

interface ScoreRadarChartProps {
  scores: Record<string, number | undefined>;
  metrics: typeof METRICS;
}

export function ScoreRadarChart({ scores, metrics }: ScoreRadarChartProps) {
  const data: MetricEntry[] = metrics.map((m) => ({
    metric: m.label,
    score: scores[m.key] ?? 0,
    fullMark: m.maxScore,
  }));

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} margin={{ top: 16, right: 24, bottom: 16, left: 24 }}>
          <PolarGrid stroke="#E8E5DF" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: "#78716C", fontSize: 12, fontWeight: 500 }}
          />
          <Radar
            dataKey="score"
            stroke="#D97706"
            fill="#D97706"
            fillOpacity={0.18}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## 2.9 InitialsAvatar

**File: `src/components/primitives/InitialsAvatar.tsx`**

```tsx
import { cn, getInitials } from "@/lib/utils";

interface InitialsAvatarProps {
  name?: string | null;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

const sizeStyles = {
  sm:  "h-7  w-7  text-xs",
  md:  "h-9  w-9  text-sm",
  lg:  "h-11 w-11 text-base",
  xl:  "h-16 w-16 text-xl",
};

export function InitialsAvatar({ name, size = "md", className }: InitialsAvatarProps) {
  const initials = getInitials(name);

  return (
    <div
      className={cn(
        "rounded-full bg-brand-100 text-brand-800 font-semibold",
        "flex items-center justify-center flex-shrink-0 select-none",
        "border border-brand-200",
        sizeStyles[size],
        className
      )}
      aria-label={name ?? "User"}
    >
      {initials}
    </div>
  );
}
```

---

## 2.10 StatusBadge (Interview Status)

**File: `src/components/primitives/StatusBadge.tsx`**

```tsx
import { cn } from "@/lib/utils";
import { CheckCircle2, AlertTriangle, Clock } from "lucide-react";

type InterviewStatus = "completed" | "abandoned" | "in_progress" | "unknown";

interface StatusBadgeProps {
  status: InterviewStatus;
  className?: string;
}

const STATUS_CONFIG = {
  completed:   { label: "Completed",   icon: CheckCircle2,  class: "bg-success/10 text-success  border-success/20"  },
  abandoned:   { label: "Abandoned",   icon: AlertTriangle, class: "bg-warning/10 text-warning  border-warning/20"  },
  in_progress: { label: "In Progress", icon: Clock,         class: "bg-info/10    text-info     border-info/20"     },
  unknown:     { label: "Unknown",     icon: Clock,         class: "bg-warm-muted text-text-muted border-warm-border"},
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.unknown;
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 text-xs font-medium",
        "px-2.5 py-1 rounded-full border",
        config.class,
        className
      )}
    >
      <Icon size={12} />
      {config.label}
    </span>
  );
}
```

---

## 2.11 ConfirmModal

**File: `src/components/primitives/ConfirmModal.tsx`**

Replaces all `window.confirm()` calls. Accessible, styled, composable.

```tsx
"use client";
import {
  Dialog, DialogContent, DialogHeader,
  DialogTitle, DialogDescription, DialogFooter,
} from "@/components/ui/dialog";
import { AppButton } from "./AppButton";
import { AlertTriangle } from "lucide-react";

interface ConfirmModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title?: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "default" | "destructive";
  isLoading?: boolean;
  onConfirm: () => void;
}

export function ConfirmModal({
  open,
  onOpenChange,
  title = "Are you sure?",
  description = "This action cannot be undone.",
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  variant = "destructive",
  isLoading = false,
  onConfirm,
}: ConfirmModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md bg-white border-warm-border">
        <DialogHeader className="gap-3">
          {variant === "destructive" && (
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-error/10">
              <AlertTriangle size={20} className="text-error" />
            </div>
          )}
          <DialogTitle className="text-text-main">{title}</DialogTitle>
          {description && (
            <DialogDescription className="text-text-secondary text-sm">
              {description}
            </DialogDescription>
          )}
        </DialogHeader>
        <DialogFooter className="gap-2 sm:gap-2">
          <AppButton
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            {cancelLabel}
          </AppButton>
          <AppButton
            variant={variant === "destructive" ? "destructive" : "brand"}
            isLoading={isLoading}
            onClick={onConfirm}
          >
            {confirmLabel}
          </AppButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

---

## 2.12 EmptyState

**File: `src/components/primitives/EmptyState.tsx`**

```tsx
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center py-16 px-8",
        className
      )}
    >
      {Icon && (
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-warm-muted">
          <Icon size={28} className="text-text-muted" />
        </div>
      )}
      <h3 className="text-lg font-semibold text-text-main mb-2">{title}</h3>
      {description && (
        <p className="text-sm text-text-secondary max-w-xs mb-6">{description}</p>
      )}
      {action}
    </div>
  );
}
```

---

## 2.13 PageHeader

**File: `src/components/layout/PageHeader.tsx`**

```tsx
import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  className?: string;
}

export function PageHeader({ title, subtitle, actions, className }: PageHeaderProps) {
  return (
    <div className={cn("flex items-start justify-between gap-4 mb-8", className)}>
      <div>
        <h1 className="text-2xl font-semibold text-text-main tracking-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="text-sm text-text-secondary mt-1">{subtitle}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-3 flex-shrink-0">{actions}</div>}
    </div>
  );
}
```

---

## 2.14 Skeleton Variants

**File: `src/components/primitives/Skeletons.tsx`**

```tsx
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

// Interview history card skeleton
export function InterviewCardSkeleton() {
  return (
    <div className="flex items-center justify-between p-4 rounded-xl border border-warm-border bg-white">
      <div className="flex flex-col gap-2 flex-1">
        <Skeleton className="h-4 w-32 bg-warm-muted" />
        <Skeleton className="h-3 w-48 bg-warm-muted" />
      </div>
      <Skeleton className="h-7 w-20 rounded-full bg-warm-muted" />
    </div>
  );
}

// Profile section skeleton
export function ProfileSectionSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-5 w-48 bg-warm-muted" />
      <Skeleton className="h-4 w-full bg-warm-muted" />
      <Skeleton className="h-4 w-3/4 bg-warm-muted" />
    </div>
  );
}

// Metric card skeleton (for report loading)
export function MetricCardSkeleton() {
  return (
    <div className="rounded-xl border border-warm-border p-4 space-y-3">
      <div className="flex justify-between">
        <Skeleton className="h-3 w-10 bg-warm-muted" />
        <Skeleton className="h-3 w-3 rounded-full bg-warm-muted" />
      </div>
      <Skeleton className="h-4 w-3/4 bg-warm-muted" />
      <Skeleton className="h-8 w-16 bg-warm-muted" />
      <Skeleton className="h-1.5 w-full rounded-full bg-warm-muted" />
    </div>
  );
}

// Full report loading skeleton
export function ReportSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <MetricCardSkeleton key={i} />
        ))}
      </div>
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className={cn("h-4 bg-warm-muted", i % 2 === 0 ? "w-full" : "w-4/5")} />
        ))}
      </div>
    </div>
  );
}
```

---

## 2.15 TanStack Query Hooks

**File: `src/hooks/use-interviews.ts`**

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { interviewApi, jdApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";

export function useInterviews() {
  const { user } = useAuthStore();
  return useQuery({
    queryKey: ["interviews", user?.id],
    queryFn: () => interviewApi.getAll(user!.id),
    enabled: !!user?.id,
  });
}

export function useInterviewDetail(interviewId: string) {
  const { user } = useAuthStore();
  return useQuery({
    queryKey: ["interview", interviewId],
    queryFn: async () => {
      const interview = await interviewApi.getDetails(user!.id, interviewId);
      let jd = null;
      if (interview.jd_id) {
        jd = await jdApi.get(interview.jd_id).catch(() => null);
      }
      return { interview, jd };
    },
    enabled: !!user?.id && !!interviewId,
  });
}

export function useDeleteInterview() {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  return useMutation({
    mutationFn: (interviewId: string) => interviewApi.delete(interviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interviews", user?.id] });
    },
  });
}
```

**File: `src/hooks/use-profile.ts`**

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import type { CreateProfilePayload } from "@/types/api";

export function useProfile() {
  const { user, token } = useAuthStore();
  return useQuery({
    queryKey: ["profile", user?.id],
    queryFn: () => usersApi.getProfile(user!.id, token!),
    enabled: !!user?.id && !!token,
    retry: false,  // Don't retry 404 (new user)
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const { user, token } = useAuthStore();
  return useMutation({
    mutationFn: (data: Partial<CreateProfilePayload>) =>
      usersApi.updateProfile(user!.id, data, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile", user?.id] });
    },
  });
}

export function useCreateProfile() {
  const { signupToken, updateUser } = useAuthStore();
  return useMutation({
    mutationFn: (data: CreateProfilePayload) =>
      usersApi.createProfile(data, signupToken ?? ""),
    onSuccess: (result) => {
      updateUser({ id: result.user_id, email: result.email });
    },
  });
}
```

**File: `src/hooks/use-report.ts`**

```typescript
import { useQuery } from "@tanstack/react-query";
import { sessionApi } from "@/lib/api";

export function useReport(sessionId: string) {
  return useQuery({
    queryKey: ["report", sessionId],
    queryFn: () => sessionApi.getReport(sessionId),
    enabled: !!sessionId,
    // Poll every 3s until report arrives (handles async generation)
    refetchInterval: (data) => (data?.report ? false : 3000),
    refetchIntervalInBackground: false,
    retry: 3,
  });
}
```

---

## Phase 2 Verification Checklist

- [ ] All primitive components render without TypeScript errors
- [ ] `AppButton` hover state uses `e.currentTarget` (not `e.target`) — bug fixed
- [ ] `AppInput` labels correctly focus the input via `htmlFor/id`
- [ ] `TagInput` adds chips on Enter, removes on `×` click
- [ ] `ConfirmModal` traps focus and closes on Escape
- [ ] `MetricCard` renders all score colors correctly for 0, 5, 7, 9
- [ ] `ScoreBar` fills proportionally (50% bar for score 5/10)
- [ ] `InitialsAvatar` shows "JD" for "John Doe"
- [ ] `EmptyState` renders with and without action button
- [ ] All components pass basic accessibility checks (labels, ARIA)

---

## Files Created in Phase 2

| File | Description |
|---|---|
| `src/components/primitives/AppButton.tsx` | Multi-variant button with loading state |
| `src/components/primitives/AppInput.tsx` | Accessible labeled input |
| `src/components/primitives/AppTextarea.tsx` | Auto-growing textarea |
| `src/components/primitives/AppCard.tsx` | Flexible card container |
| `src/components/primitives/TagInput.tsx` | Skill chip tag input |
| `src/components/primitives/MetricCard.tsx` | Score metric card (report) |
| `src/components/primitives/ScoreBar.tsx` | Color-coded progress bar |
| `src/components/primitives/ScoreRadarChart.tsx` | 8-metric radar chart |
| `src/components/primitives/InitialsAvatar.tsx` | User avatar with initials |
| `src/components/primitives/StatusBadge.tsx` | Interview status badge |
| `src/components/primitives/ConfirmModal.tsx` | Accessible confirmation dialog |
| `src/components/primitives/EmptyState.tsx` | Unified empty state |
| `src/components/primitives/Skeletons.tsx` | Loading skeleton variants |
| `src/components/layout/PageHeader.tsx` | Page title/subtitle/actions |
| `src/hooks/use-interviews.ts` | TanStack Query interview hooks |
| `src/hooks/use-profile.ts` | TanStack Query profile hooks |
| `src/hooks/use-report.ts` | TanStack Query report hook (with polling) |
