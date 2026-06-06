# Phase 1 — Foundation & Infrastructure

> **Goal:** Bootstrap the Next.js 14 app with Tailwind CSS v3, shadcn/ui, Zustand, TanStack Query, and all global infrastructure (providers, middleware, token system, directory scaffold).  
> **Prerequisite:** None. This is the first phase.  
> **Output:** A running Next.js app that renders a blank layout with correct theme, font, and routing structure.

---

## 1.1 Project Scaffolding

### Command Sequence

```bash
# From the project root (SkillIssue.ai/)
npx create-next-app@latest frontend-v2 \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --no-turbopack

cd frontend-v2

# Install shadcn/ui
npx shadcn@latest init
# → Choose: Default style, Zinc base color (we'll override), CSS variables: Yes

# Core dependencies
npm install zustand @tanstack/react-query lucide-react \
  date-fns react-markdown remark-gfm \
  clsx tailwind-merge framer-motion \
  emblor recharts html2pdf.js

# Dev dependencies
npm install -D @types/node
```

### shadcn/ui components to install upfront

```bash
npx shadcn@latest add button card input label \
  badge dialog sheet tabs separator toast \
  form select textarea progress skeleton \
  avatar dropdown-menu alert tooltip \
  popover command chart
```

---

## 1.2 Directory Structure

```
frontend-v2/
├── src/
│   ├── app/
│   │   ├── (auth)/                          # Route group — no navbar
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── signup/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx                   # Auth layout (centered card)
│   │   ├── (app)/                           # Route group — with navbar
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── profile/
│   │   │   │   ├── page.tsx                 # ProfileView
│   │   │   │   ├── new/page.tsx             # Profile create wizard
│   │   │   │   └── edit/page.tsx            # Profile edit wizard
│   │   │   ├── interview/
│   │   │   │   ├── setup/page.tsx           # SetupInterview wizard
│   │   │   │   └── [session_id]/page.tsx    # InterviewSession
│   │   │   ├── report/
│   │   │   │   └── [session_id]/page.tsx    # Report
│   │   │   ├── history/
│   │   │   │   └── [interview_id]/page.tsx  # Interview history detail
│   │   │   └── layout.tsx                   # App layout (navbar + main)
│   │   ├── globals.css                      # Tailwind base + token overrides
│   │   ├── layout.tsx                       # Root layout (providers)
│   │   └── page.tsx                         # Redirect to /dashboard or /login
│   ├── components/
│   │   ├── ui/                              # shadcn/ui (auto-generated, do not edit)
│   │   ├── primitives/                      # Lightly extended shadcn wrappers
│   │   │   ├── AppButton.tsx
│   │   │   ├── AppInput.tsx
│   │   │   ├── AppCard.tsx
│   │   │   ├── TagInput.tsx                 # emblor-based skill chip input
│   │   │   ├── MetricCard.tsx               # Score metric card (report)
│   │   │   ├── ScoreBar.tsx                 # Colored progress bar (0-10 scale)
│   │   │   ├── InitialsAvatar.tsx           # Initials-based avatar circle
│   │   │   ├── StatusBadge.tsx              # Interview status badge
│   │   │   ├── ConfirmModal.tsx             # Replace window.confirm()
│   │   │   └── EmptyState.tsx              # Unified empty state
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── UserMenu.tsx                 # Avatar + dropdown
│   │   │   └── PageHeader.tsx              # Reusable page title + subtitle
│   │   └── providers/
│   │       ├── QueryProvider.tsx            # TanStack Query
│   │       ├── ThemeProvider.tsx            # next-themes or custom
│   │       └── Providers.tsx               # Combines all providers
│   ├── hooks/
│   │   ├── use-auth.ts                      # Zustand auth selector hook
│   │   ├── use-interviews.ts                # TanStack Query: interview list
│   │   ├── use-profile.ts                   # TanStack Query: profile CRUD
│   │   └── use-report.ts                    # TanStack Query: report fetch + poll
│   ├── lib/
│   │   ├── api.ts                           # Typed API client (wraps fetch)
│   │   ├── utils.ts                         # cn() + date formatters + misc
│   │   └── constants.ts                     # Metric definitions, enum maps
│   ├── store/
│   │   └── auth-store.ts                    # Zustand auth store
│   └── types/
│       ├── api.ts                           # API response types
│       └── index.ts                         # Shared types
├── middleware.ts                            # Route protection
├── tailwind.config.ts                       # Full token system
├── next.config.ts
└── tsconfig.json
```

---

## 1.3 Tailwind Configuration (Full Token System)

**File: `tailwind.config.ts`**

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // Warm Neutrals — Light Theme Foundation
        "warm-bg": "#FAFAF8",
        "warm-surface": "#FFFFFF",
        "warm-border": "#E8E5DF",
        "warm-muted": "#F5F3EE",

        // Text hierarchy
        "text-main": "#1C1917",      // stone-900
        "text-secondary": "#78716C", // stone-500
        "text-muted": "#A8A29E",     // stone-400

        // Brand Accent — Amber
        brand: {
          50:  "#FFFBEB",
          100: "#FEF3C7",
          200: "#FDE68A",
          300: "#FCD34D",
          400: "#FBBF24",
          500: "#F59E0B",
          600: "#D97706",  // PRIMARY
          700: "#B45309",  // HOVER
          800: "#92400E",
          900: "#78350F",
        },

        // Semantic colors
        success: { DEFAULT: "#059669", light: "#D1FAE5", border: "#6EE7B7" },
        warning: { DEFAULT: "#D97706", light: "#FEF3C7", border: "#FCD34D" },
        error:   { DEFAULT: "#DC2626", light: "#FEE2E2", border: "#FCA5A5" },
        info:    { DEFAULT: "#2563EB", light: "#DBEAFE", border: "#93C5FD" },

        // Score metric colors (for the 8 metrics)
        score: {
          excellent: "#059669",  // 8-10
          good:      "#D97706",  // 6-7.9
          average:   "#EA580C",  // 4-5.9
          poor:      "#DC2626",  // 0-3.9
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        serif: ["Instrument Serif", "Georgia", "serif"],
        mono:  ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        "display":  ["2.25rem", { lineHeight: "2.5rem",  fontWeight: "700" }],
        "heading":  ["1.5rem",  { lineHeight: "2rem",    fontWeight: "600" }],
        "subhead":  ["1.125rem",{ lineHeight: "1.75rem", fontWeight: "600" }],
        "body":     ["1rem",    { lineHeight: "1.625rem",fontWeight: "400" }],
        "small":    ["0.875rem",{ lineHeight: "1.25rem", fontWeight: "400" }],
        "micro":    ["0.75rem", { lineHeight: "1rem",    fontWeight: "400" }],
      },
      borderRadius: {
        "sm":  "0.25rem",
        "md":  "0.375rem",
        "lg":  "0.5rem",
        "xl":  "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
        "full":"9999px",
      },
      boxShadow: {
        "warm-sm": "0 1px 2px 0 rgba(28, 25, 23, 0.05)",
        "warm-md": "0 4px 6px -1px rgba(28, 25, 23, 0.08), 0 2px 4px -1px rgba(28, 25, 23, 0.04)",
        "warm-lg": "0 10px 15px -3px rgba(28, 25, 23, 0.08), 0 4px 6px -2px rgba(28, 25, 23, 0.03)",
        "warm-xl": "0 20px 25px -5px rgba(28, 25, 23, 0.08), 0 10px 10px -5px rgba(28, 25, 23, 0.02)",
        "brand":   "0 0 0 3px rgba(217, 119, 6, 0.12)",  // focus ring
      },
      spacing: {
        "4.5": "1.125rem",
        "13":  "3.25rem",
        "18":  "4.5rem",
        "72":  "18rem",
        "84":  "21rem",
        "88":  "22rem",
        "96":  "24rem",
        "128": "32rem",
      },
      animation: {
        "fade-in":     "fadeIn 0.3s ease-out",
        "slide-up":    "slideUp 0.35s ease-out",
        "pulse-brand": "pulseBrand 2s ease-in-out infinite",
        "spin-slow":   "spin 2s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%":   { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseBrand: {
          "0%, 100%": { opacity: "1" },
          "50%":      { opacity: "0.6" },
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

---

## 1.4 Global CSS

**File: `src/app/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── shadcn/ui CSS variables (light theme = default) ── */
@layer base {
  :root {
    --background:   250 250 248;   /* warm-bg */
    --foreground:   28 25 23;      /* text-main */
    --card:         255 255 255;
    --card-foreground: 28 25 23;
    --popover:      255 255 255;
    --popover-foreground: 28 25 23;
    --primary:      217 119 6;     /* brand-600 amber */
    --primary-foreground: 255 255 255;
    --secondary:    245 243 238;   /* warm-muted */
    --secondary-foreground: 28 25 23;
    --muted:        245 243 238;
    --muted-foreground: 120 113 108; /* text-secondary */
    --accent:       254 243 199;   /* brand-100 */
    --accent-foreground: 120 62 8; /* brand-800 */
    --destructive:  220 38 38;
    --destructive-foreground: 255 255 255;
    --border:       232 229 223;   /* warm-border */
    --input:        232 229 223;
    --ring:         217 119 6;     /* brand-600 */
    --radius:       0.5rem;
  }

  /* ── Dark mode override ── */
  .dark {
    --background:   28 25 23;
    --foreground:   250 250 248;
    --card:         41 37 36;
    --card-foreground: 250 250 248;
    --popover:      41 37 36;
    --popover-foreground: 250 250 248;
    --primary:      251 191 36;    /* brand-400 — lighter in dark */
    --primary-foreground: 28 25 23;
    --secondary:    68 64 60;
    --secondary-foreground: 245 243 238;
    --muted:        68 64 60;
    --muted-foreground: 168 162 158;
    --accent:       92 72 19;
    --accent-foreground: 251 191 36;
    --destructive:  185 28 28;
    --destructive-foreground: 254 226 226;
    --border:       68 64 60;
    --input:        68 64 60;
    --ring:         251 191 36;
  }

  * {
    @apply border-border;
  }

  body {
    @apply bg-warm-bg text-text-main font-sans antialiased;
    font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
  }

  h1, h2, h3 {
    @apply font-sans font-semibold tracking-tight text-text-main;
  }

  /* ── Scrollbar styling (minimal) ── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { @apply bg-warm-muted; }
  ::-webkit-scrollbar-thumb { @apply bg-warm-border rounded-full; }
  ::-webkit-scrollbar-thumb:hover { @apply bg-text-muted; }

  /* ── Focus ring (brand color) ── */
  :focus-visible {
    @apply outline-none ring-2 ring-brand-600 ring-offset-2 ring-offset-white;
  }

  /* ── Markdown body (for report) ── */
  .prose-report {
    @apply text-text-main leading-relaxed;
  }
  .prose-report h1 {
    @apply text-2xl font-semibold mt-8 mb-4 pb-3 border-b border-warm-border;
  }
  .prose-report h2 {
    @apply text-xl font-semibold mt-6 mb-3;
  }
  .prose-report h3 {
    @apply text-lg font-medium mt-4 mb-2;
  }
  .prose-report p {
    @apply mb-4 text-base text-text-main;
  }
  .prose-report ul {
    @apply mb-4 pl-6 space-y-1 list-disc;
  }
  .prose-report li {
    @apply text-base text-text-main;
  }
  .prose-report strong {
    @apply font-semibold text-text-main;
  }
  .prose-report code {
    @apply font-mono text-sm bg-warm-muted px-1.5 py-0.5 rounded text-brand-700;
  }
  .prose-report pre {
    @apply font-mono text-sm bg-warm-muted p-4 rounded-lg overflow-x-auto my-4 border border-warm-border;
  }
  .prose-report table {
    @apply w-full text-sm border-collapse my-4;
  }
  .prose-report th {
    @apply text-left font-medium text-text-secondary bg-warm-muted px-3 py-2 border border-warm-border;
  }
  .prose-report td {
    @apply px-3 py-2 border border-warm-border;
  }
}

/* ── Utility classes ── */
@layer utilities {
  .animate-fade-in  { animation: fadeIn  0.3s  ease-out; }
  .animate-slide-up { animation: slideUp 0.35s ease-out; }

  @keyframes fadeIn  { from { opacity: 0; }                          to { opacity: 1; } }
  @keyframes slideUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

  /* Textarea auto-resize base */
  .textarea-auto {
    field-sizing: content;
    min-height: 60px;
  }
}
```

---

## 1.5 Zustand Auth Store

**File: `src/store/auth-store.ts`**

```typescript
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  email: string;
  username: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  signupToken: string | null;   // Temporary token used in createUserProfile
  isAuthenticated: boolean;

  setAuth: (token: string, user: User) => void;
  setSignupToken: (token: string) => void;
  clearAuth: () => void;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      signupToken: null,
      isAuthenticated: false,

      setAuth: (token, user) => set({ token, user, isAuthenticated: true }),
      setSignupToken: (signupToken) => set({ signupToken }),
      clearAuth: () => set({ token: null, user: null, isAuthenticated: false }),
      updateUser: (partialUser) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...partialUser } : null,
        })),
    }),
    {
      name: "skillissue-auth",  // localStorage key
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        signupToken: state.signupToken,
      }),
    }
  )
);
```

---

## 1.6 Typed API Client

**File: `src/lib/api.ts`**

```typescript
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

  // Handle 204 No Content
  if (res.status === 204) return {} as T;
  return res.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────────────
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

// ── Users / Profile ───────────────────────────────────────────────────
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

// ── Job Descriptions ──────────────────────────────────────────────────
export const jdApi = {
  create: (data: CreateJDPayload) =>
    request<{ jd_id: string }>("/jd/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  get: (jdId: string) =>
    request<JDResponse>(`/jd/${jdId}`),
};

// ── Sessions / Interview ──────────────────────────────────────────────
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

// ── Interview History ─────────────────────────────────────────────────
export const interviewApi = {
  getAll: (userId: string) =>
    request<Interview[]>(`/interview/${userId}`),

  getDetails: (userId: string, interviewId: string) =>
    request<InterviewDetail>(`/interview/${userId}/${interviewId}`),

  delete: (interviewId: string) =>
    request<void>(`/interview/${interviewId}`, { method: "DELETE" }),
};
```

---

## 1.7 Types

**File: `src/types/api.ts`**

```typescript
// Auth
export interface User {
  id: string;
  email: string;
  username: string;
}

// Profile
export interface Experience {
  experience_id?: string;
  role: string;
  company: string;
  emp_type: "full_time" | "part_time";
  start_date: string;
  end_date?: string;
  loc_type: "onsite" | "remote" | "hybrid";
  location?: string;
  description?: string;
  skills_used: string[];
}

export interface Education {
  education_id?: string;
  institute_name: string;
  degree: string;
  grade: number;
  courses: string[];
  start_date: string;
  end_date?: string;
}

export interface Project {
  project_id?: string;
  title: string;
  description: string;
  skills_used: string[];
  github_url?: string;
  deployed_url?: string;
}

export interface Leadership {
  leadership_id?: string;
  committee_name: string;
  position: string;
  skills_used: string[];
  description?: string;
  start_date: string;
  end_date?: string;
}

export interface UserProfile {
  user_id: string;
  name: string;
  email: string;
  username?: string;
  mobile?: string;
  github_url?: string;
  linkedin_url?: string;
  skills: string[];
  experiences: Experience[];
  educations: Education[];
  projects: Project[];
  leaderships: Leadership[];
}

export type CreateProfilePayload = Omit<UserProfile, "user_id"> & {
  user_id?: string;
  hashed_password?: string;
  is_active?: boolean;
};

// JD
export interface CreateJDPayload {
  job_title: string;
  job_type: "full_time" | "part_time";
  min_experience: number;
  required_skills: string[];
  responsibilities: string[];
  required_qualification: string;
  description?: string;
}

export interface JDResponse extends CreateJDPayload {
  jd_id: string;
}

// Session
export interface SessionStartResponse {
  session_id: string;
  current_question: string;
  current_phase_name: string;
  current_topic_name?: string;
  current_topic_id?: string;
}

export interface AnswerResponse {
  current_question?: string;
  current_phase_name?: string;
  current_topic_name?: string;
  current_topic_id?: string;
  is_complete?: boolean;
}

// Interview History
export interface Interview {
  _id: string;
  session_id: string;
  jd_id: string;
  user_id: string;
  conducted_on: string;
  report?: string;
}

export interface ChatTurn {
  chat_id?: string;
  question: string;
  response: string;
  phase_name?: string;
  topic_id?: string;
  metrics?: {
    relevance_score?: number;
    clarity_score?: number;
    completeness_score?: number;
    technical_depth_score?: number;
    answer_confidence_score?: number;
    star_score?: number;
    feedback?: string;
  };
}

export interface InterviewDetail extends Interview {
  chat_history: ChatTurn[];
}
```

---

## 1.8 Utility Functions

**File: `src/lib/utils.ts`**

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow } from "date-fns";

// ── Tailwind class merger ───────────────────────────────────────────
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ── Date formatting ────────────────────────────────────────────────
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

// ── Score helpers ──────────────────────────────────────────────────
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

// ── String helpers ─────────────────────────────────────────────────
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

// ── Local date input helper ────────────────────────────────────────
export function toDateInput(value?: string | null): string {
  return typeof value === "string" ? value.split("T")[0] : "";
}
```

---

## 1.9 Constants

**File: `src/lib/constants.ts`**

```typescript
// Interview metrics — full name, abbreviation, description
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

// Interview length options
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

// Employment types
export const EMP_TYPE_LABELS: Record<string, string> = {
  full_time: "Full-time",
  part_time: "Part-time",
};

// Location types
export const LOC_TYPE_LABELS: Record<string, string> = {
  onsite: "On-site",
  remote: "Remote",
  hybrid: "Hybrid",
};
```

---

## 1.10 Next.js Middleware (Route Protection)

**File: `middleware.ts`** (at project root)

```typescript
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/signup"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths without auth check
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Check for auth token in localStorage via a cookie mirror
  // NOTE: We can't read localStorage in middleware (server-side).
  // Strategy: On login, we ALSO set a lightweight cookie "skillissue-authed=1"
  // (non-HttpOnly, no sensitive data) just to signal auth state in middleware.
  const isAuthed = request.cookies.get("skillissue-authed")?.value === "1";

  if (!isAuthed && !pathname.startsWith("/_next")) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirectTo", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

> **Note on Middleware Auth:** Since Next.js middleware runs on the edge (server), it cannot access `localStorage`. The solution is: after setting the JWT in Zustand/localStorage, also set a cookie `skillissue-authed=1` (just a presence flag — no token). The actual JWT security is maintained via Zustand.

---

## 1.11 Root Layout & Providers

**File: `src/app/layout.tsx`**

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers/Providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SkillIssue.ai — AI-Powered Mock Interviews",
  description:
    "Get context-aware, AI-driven mock interviews tailored to your profile and target job description. Understand exactly where you stand before the real interview.",
  keywords: ["mock interview", "AI interview prep", "job interview practice"],
  openGraph: {
    title: "SkillIssue.ai",
    description: "AI-Powered Mock Interviewer Platform",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

**File: `src/components/providers/Providers.tsx`**

```tsx
"use client";
import { QueryProvider } from "./QueryProvider";
import { Toaster } from "@/components/ui/toaster";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryProvider>
      {children}
      <Toaster />
    </QueryProvider>
  );
}
```

**File: `src/components/providers/QueryProvider.tsx`**

```tsx
"use client";
import { QueryClient, QueryClientProvider, QueryCache } from "@tanstack/react-query";
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,     // 1 minute
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
        queryCache: new QueryCache({
          onError: (error: unknown) => {
            const err = error as { status?: number };
            if (err?.status === 401) {
              // Token expired — clear auth and redirect
              if (typeof window !== "undefined") {
                localStorage.removeItem("skillissue-auth");
                window.location.href = "/login";
              }
            }
          },
        }),
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
```

---

## 1.12 `.env.local` Template

```bash
# Copy to .env.local — never commit real values
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Phase 1 Verification Checklist

- [ ] `npm run dev` starts without errors on `http://localhost:3000`
- [ ] Navigating to `/` redirects to `/login` (middleware working)
- [ ] Tailwind classes resolve correctly (brand-600 = amber color)
- [ ] Inter font loads from Google Fonts (no FOUT flash)
- [ ] shadcn/ui Button component renders with correct warm styling
- [ ] TypeScript compiles with 0 errors: `npm run build`
- [ ] Zustand store persists to `localStorage` key `skillissue-auth`
- [ ] TanStack Query devtools available in dev mode

---

## Files Created in Phase 1

| File | Purpose |
|---|---|
| `frontend-v2/` (directory) | New Next.js project root |
| `tailwind.config.ts` | Full token system |
| `src/app/globals.css` | Global styles + prose-report utility |
| `src/app/layout.tsx` | Root layout with font + metadata |
| `src/components/providers/Providers.tsx` | Combined providers |
| `src/components/providers/QueryProvider.tsx` | TanStack Query setup |
| `src/store/auth-store.ts` | Zustand auth store |
| `src/lib/api.ts` | Typed API client |
| `src/lib/utils.ts` | cn(), date, score utilities |
| `src/lib/constants.ts` | Metrics, interview lengths, enums |
| `src/types/api.ts` | All API response/request types |
| `middleware.ts` | Route protection |
| `.env.local` | Environment variables |
