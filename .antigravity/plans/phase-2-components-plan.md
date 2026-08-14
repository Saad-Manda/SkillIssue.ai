# Feature Plan: phase-2-components-plan

> [!NOTE]
> This plan has been generated through parallel codebase analysis and is optimized for one-pass execution success.

## Feature Overview & Business Value
This phase implements the Next.js 14 frontend shared component library. The library replaces scattered inline styles and raw components with reusable UI primitives and clean layout wrappers, and provides type-safe custom TanStack Query hooks for user profiles, interviews, and session reports. This ensures consistent design patterns, robust error handling, and performance optimizations (such as polling mechanisms for report generation) before building individual pages.

## Architectural Design & Scope
- **Feature Type**: New Capability / Infrastructure Setup
- **Complexity**: High
- **Systems Affected**: UI components library, TanStack Query hooks integration, API utilities
- **Dependencies**: `lucide-react`, `emblor`, `recharts`, `@tanstack/react-query`, `zustand`, `clsx`, `tailwind-merge`

---

## Context References

### Mandatory Codebase Files to Read
- [tailwind.config.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/tailwind.config.ts) - Theme definitions and design tokens
- [src/types/api.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/types/api.ts) - API Request/Response TS interfaces
- [src/store/auth-store.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/store/auth-store.ts) - Zustand auth store selection hook

### New Files to Create
- [frontend-v2/src/lib/utils.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/lib/utils.ts)
- [frontend-v2/src/lib/constants.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/lib/constants.ts)
- [frontend-v2/src/lib/api.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/lib/api.ts)
- [frontend-v2/src/components/primitives/AppButton.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/AppButton.tsx)
- [frontend-v2/src/components/primitives/AppInput.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/AppInput.tsx)
- [frontend-v2/src/components/primitives/AppTextarea.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/AppTextarea.tsx)
- [frontend-v2/src/components/primitives/AppCard.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/AppCard.tsx)
- [frontend-v2/src/components/primitives/TagInput.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/TagInput.tsx)
- [frontend-v2/src/components/primitives/MetricCard.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/MetricCard.tsx)
- [frontend-v2/src/components/primitives/ScoreBar.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/ScoreBar.tsx)
- [frontend-v2/src/components/primitives/ScoreRadarChart.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/ScoreRadarChart.tsx)
- [frontend-v2/src/components/primitives/InitialsAvatar.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/InitialsAvatar.tsx)
- [frontend-v2/src/components/primitives/StatusBadge.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/StatusBadge.tsx)
- [frontend-v2/src/components/primitives/ConfirmModal.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/ConfirmModal.tsx)
- [frontend-v2/src/components/primitives/EmptyState.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/EmptyState.tsx)
- [frontend-v2/src/components/primitives/Skeletons.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/Skeletons.tsx)
- [frontend-v2/src/components/layout/PageHeader.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/layout/PageHeader.tsx)
- [frontend-v2/src/hooks/use-interviews.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/hooks/use-interviews.ts)
- [frontend-v2/src/hooks/use-profile.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/hooks/use-profile.ts)
- [frontend-v2/src/hooks/use-report.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/hooks/use-report.ts)

---

## Step-by-Step Tasks

### Phase 0: Infrastructure Prerequisites
Currently, `frontend-v2/src/lib/` files specified in Phase 1 (such as `utils.ts`, `api.ts`, and `constants.ts`) are missing from the repository branch. We must create them first so that Phase 2 components can compile.

#### Task 0.1: CREATE `frontend-v2/src/lib/utils.ts`
- **IMPLEMENT**: Utility functions including class mergers, date formatting, and score helpers.
- **CODE**:
```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "Present";
  try {
    return format(new Date(dateStr), "MMM yyyy");
  } catch {
    return dateStr;
  }
}

export function formatDateFull(dateStr?: string | null): string {
  if (!dateStr) return "";
  try {
    return format(new Date(dateStr), "d MMM yyyy, h:mm a");
  } catch {
    return dateStr;
  }
}

export function timeAgo(dateStr?: string | null): string {
  if (!dateStr) return "";
  try {
    return formatDistanceToNow(new Date(dateStr), { addSuffix: true });
  } catch {
    return dateStr;
  }
}

export function getScoreColor(score: number): string {
  if (score >= 8)  return "text-success";
  if (score >= 6)  return "text-warning";
  if (score >= 4)  return "text-orange-500";
  return "text-error";
}

export function getScoreBg(score: number): string {
  if (score >= 8)  return "bg-success/10 border-success/20";
  if (score >= 6)  return "bg-warning/10 border-warning/20";
  if (score >= 4)  return "bg-orange-50   border-orange-200";
  return "bg-error/10 border-error/20";
}

export function getScoreLabel(score: number): string {
  if (score >= 8)  return "Excellent";
  if (score >= 6)  return "Good";
  if (score >= 4)  return "Average";
  return "Needs Work";
}

export function getInitials(name?: string | null): string {
  if (!name) return "?";
  return name
    .split(" ")
    .slice(0, 2)
    .map((n) => n[0]?.toUpperCase() ?? "")
    .join("");
}

export function truncate(str: string, maxLen: number): string {
  return str.length > maxLen ? `${str.slice(0, maxLen)}…` : str;
}

export function toDateInput(value?: string | null): string {
  return typeof value === "string" ? value.split("T")[0] : "";
}
```
- **VALIDATION**: Check file syntax by compiling.

#### Task 0.2: CREATE `frontend-v2/src/lib/constants.ts`
- **IMPLEMENT**: Constant lists for metrics, interview lengths, and employment/location types.
- **CODE**:
```typescript
export const METRICS = [
  {
    key: "relevance_score",
    label: "QAR",
    fullName: "Question-Answer Relevance",
    description: "How directly your answer addressed the question asked.",
    maxScore: 10,
  },
  {
    key: "technical_depth_score",
    label: "TDS",
    fullName: "Technical Depth Score",
    description: "Depth and accuracy of technical knowledge demonstrated.",
    maxScore: 10,
  },
  {
    key: "answer_confidence_score",
    label: "ACS",
    fullName: "Answer Confidence Score",
    description: "Confidence and certainty in your responses.",
    maxScore: 10,
  },
  {
    key: "structure_score",
    label: "SS",
    fullName: "Structure Score",
    description: "How well-organized and logical your answer was.",
    maxScore: 10,
  },
  {
    key: "clarity_score",
    label: "CCS",
    fullName: "Clarity & Communication Score",
    description: "Clarity and precision of language used.",
    maxScore: 10,
  },
  {
    key: "completeness_score",
    label: "FARQ",
    fullName: "Full Answer to Requirements Quality",
    description: "Whether your answer fully addressed all parts of the question.",
    maxScore: 10,
  },
  {
    key: "rfd_score",
    label: "RFD",
    fullName: "Resume-to-Fact Discrepancy",
    description: "Consistency between your resume claims and live answers.",
    maxScore: 10,
  },
  {
    key: "star_score",
    label: "STAR",
    fullName: "STAR Framework Adherence",
    description: "How well you used Situation-Task-Action-Result structure.",
    maxScore: 10,
  },
] as const;

export type MetricKey = typeof METRICS[number]["key"];

export const INTERVIEW_LENGTHS = [
  {
    value: "short" as const,
    label: "Short",
    duration: "~15 min",
    questions: "8–10 questions",
    description: "Quick assessment — great for warm-up sessions.",
  },
  {
    value: "medium" as const,
    label: "Medium",
    duration: "~30 min",
    questions: "15–20 questions",
    description: "Standard depth — mimics a typical first round.",
  },
  {
    value: "long" as const,
    label: "Long",
    duration: "~45 min",
    questions: "25–30 questions",
    description: "Deep dive — full technical and behavioral coverage.",
  },
] as const;

export type InterviewLength = "short" | "medium" | "long";

export const EMP_TYPE_LABELS: Record<string, string> = {
  full_time: "Full-time",
  part_time: "Part-time",
};

export const LOC_TYPE_LABELS: Record<string, string> = {
  onsite: "On-site",
  remote: "Remote",
  hybrid: "Hybrid",
};
```
- **VALIDATION**: Check compile sanity.

#### Task 0.3: CREATE `frontend-v2/src/lib/api.ts`
- **IMPLEMENT**: Async typed fetch requests using TypeScript interfaces.
- **CODE**:
```typescript
import {
  UserProfile,
  CreateProfilePayload,
  CreateJDPayload,
  JDResponse,
  SessionStartResponse,
  AnswerResponse,
  Interview,
  InterviewDetail,
} from "../types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options?: RequestInit,
  token?: string | null
): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options?.headers,
  };

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new ApiError(res.status, err.detail ?? "Request failed");
  }

  if (res.status === 204) return {} as T;
  return res.json() as Promise<T>;
}

export const authApi = {
  signup: (data: { username: string; email: string; password: string }) =>
    request<{ signup_token: string }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (data: { username: string; email: string; password: string }) =>
    request<{ access_token: string; user_id: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  logout: (token: string) =>
    request<void>("/auth/logout", { method: "POST" }, token),
};

export const usersApi = {
  getProfile: (userId: string, token: string) =>
    request<UserProfile>(`/users/${userId}`, {}, token),

  createProfile: (data: CreateProfilePayload, signupToken: string) =>
    request<UserProfile>(`/users/?signup_token=${signupToken}`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateProfile: (userId: string, data: Partial<CreateProfilePayload>, token: string) =>
    request<UserProfile>(`/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }, token),
};

export const jdApi = {
  create: (data: CreateJDPayload) =>
    request<{ jd_id: string }>("/jd/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  get: (jdId: string) =>
    request<JDResponse>(`/jd/${jdId}`),
};

export const sessionApi = {
  start: (userId: string, jdId: string, length: "short" | "medium" | "long") =>
    request<SessionStartResponse>(
      `/session/user/${userId}/jd/${jdId}/length/${length}`
    ),

  submitAnswer: (sessionId: string, answer: string) =>
    request<AnswerResponse>(`/session/${sessionId}/answer`, {
      method: "POST",
      body: JSON.stringify({ answer }),
    }),

  getReport: (sessionId: string) =>
    request<{ report: string }>(`/session/${sessionId}/report`),
};

export const interviewApi = {
  getAll: (userId: string) =>
    request<Interview[]>(`/interview/${userId}`),

  getDetails: (userId: string, interviewId: string) =>
    request<InterviewDetail>(`/interview/${userId}/${interviewId}`),

  delete: (interviewId: string) =>
    request<void>(`/interview/${interviewId}`, { method: "DELETE" }),
};
```
- **VALIDATION**: Check compiler sanity.

---

### Phase 1: Shared Primitive Components

#### Task 1.1: CREATE `frontend-v2/src/components/primitives/AppButton.tsx`
- **IMPLEMENT**: Multi-variant button supporting `default | outline | ghost | destructive | brand` and sizes, including loading states and icons.
- **VALIDATION**: Compile check in `frontend-v2` directory.

#### Task 1.2: CREATE `frontend-v2/src/components/primitives/AppInput.tsx`
- **IMPLEMENT**: Labeled wrapper around standard inputs incorporating `htmlFor/id` relationships, hint text, error message states, and slot icons.
- **VALIDATION**: Compile check.

#### Task 1.3: CREATE `frontend-v2/src/components/primitives/AppTextarea.tsx`
- **IMPLEMENT**: Auto-growing textarea layout with validation errors, label, and character limit indicators.
- **VALIDATION**: Compile check.

#### Task 1.4: CREATE `frontend-v2/src/components/primitives/AppCard.tsx`
- **IMPLEMENT**: General card container replacing fixed constraints with adaptive layouts. Supports variants: `default | outlined | flat` and `hoverable` prop.
- **VALIDATION**: Compile check.

#### Task 1.5: CREATE `frontend-v2/src/components/primitives/TagInput.tsx`
- **IMPLEMENT**: Skills tags chip rendering component using the `emblor` npm package.
- **VALIDATION**: Compile check.

#### Task 1.6: CREATE `frontend-v2/src/components/primitives/MetricCard.tsx`
- **IMPLEMENT**: Score cards displaying short metrics with full names, dynamic color coding, descriptions inside tooltips, and ScoreBars.
- **VALIDATION**: Compile check.

#### Task 1.7: CREATE `frontend-v2/src/components/primitives/ScoreBar.tsx`
- **IMPLEMENT**: Dynamic sub-indicator bar displaying color transitions based on score (Excellent, Good, Average, Needs Work).
- **VALIDATION**: Compile check.

#### Task 1.8: CREATE `frontend-v2/src/components/primitives/ScoreRadarChart.tsx`
- **IMPLEMENT**: Interactive 8-axis radar visualization component utilizing Recharts hooks.
- **VALIDATION**: Compile check.

#### Task 1.9: CREATE `frontend-v2/src/components/primitives/InitialsAvatar.tsx`
- **IMPLEMENT**: Avatar circles fallback displaying custom user initials using helper utils.
- **VALIDATION**: Compile check.

#### Task 1.10: CREATE `frontend-v2/src/components/primitives/StatusBadge.tsx`
- **IMPLEMENT**: Color-coded and icon-indicated badge representing `completed | abandoned | in_progress` status.
- **VALIDATION**: Compile check.

#### Task 1.11: CREATE `frontend-v2/src/components/primitives/ConfirmModal.tsx`
- **IMPLEMENT**: Custom dialog modal implementing the `@/components/ui/dialog` shadcn container to replace generic `window.confirm`.
- **VALIDATION**: Compile check.

#### Task 1.12: CREATE `frontend-v2/src/components/primitives/EmptyState.tsx`
- **IMPLEMENT**: Common empty listing layouts with Lucide icon wrappers, titles, captions, and call-to-actions.
- **VALIDATION**: Compile check.

#### Task 1.13: CREATE `frontend-v2/src/components/primitives/Skeletons.tsx`
- **IMPLEMENT**: Loading skeleton placeholders for profile details, reports, and historic grids.
- **VALIDATION**: Compile check.

#### Task 1.14: CREATE `frontend-v2/src/components/layout/PageHeader.tsx`
- **IMPLEMENT**: Standardized header configuration displaying pages title, subtitle desc, and optional header action triggers.
- **VALIDATION**: Compile check.

---

### Phase 2: React Query Integration Hooks

#### Task 2.1: CREATE `frontend-v2/src/hooks/use-interviews.ts`
- **IMPLEMENT**: Interview fetching details and deletion mutations using TanStack Query hooks.
- **VALIDATION**: Compile check.

#### Task 2.2: CREATE `frontend-v2/src/hooks/use-profile.ts`
- **IMPLEMENT**: TanStack Query CRUD hooks for reading and writing user profile configurations.
- **VALIDATION**: Compile check.

#### Task 2.3: CREATE `frontend-v2/src/hooks/use-report.ts`
- **IMPLEMENT**: Query fetch report hooks utilizing an automatic 3-second polling callback interval until compilation succeeds.
- **VALIDATION**: Compile check.

---

## Test & Manual Validation Checklist

### Automated Validation Commands
From the `frontend-v2` directory:
```bash
# Check syntax & types
npx tsc --noEmit
```

### Manual Validation Steps
1. Verify each primitive component loads, layout is responsive, and no TypeScript types are broken.
2. Confirm the hook parameters resolve to actual query methods.
3. Validate that `MetricCard` handles color bounds correctly (0-3.9 red, 4-5.9 orange, 6-7.9 amber, 8-10 green).
4. Verify the radar chart scales from 0-10 properly across all 8 metrics.

### Acceptance Criteria Checklist
- [ ] All primitive components compile without typescript/lint errors.
- [ ] `TagInput` allows adding and deleting skill chips interactively.
- [ ] `ConfirmModal` overlays focus states properly and closes cleanly.
- [ ] Hooks utilize correct API endpoints and query keys.
- [ ] Missing utility and constant files are resolved correctly.
