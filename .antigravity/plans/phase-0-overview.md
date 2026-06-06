# SkillIssue.ai — Frontend Migration Master Plan

> **Migration:** Vite + React + Vanilla CSS → **Next.js 14 (App Router) + Tailwind CSS v3 + shadcn/ui**  
> **Design Direction:** Minimal · Light-first · Warm neutrals · Inter + serif accent · Lucide icons  
> **Audit Source:** Full frontend audit report (2026-06-06)

---

## Why This Migration?

| Current State | Target State |
|---|---|
| Vite + React SPA | Next.js 14 App Router (CSR pages only — no SSR needed yet) |
| Vanilla CSS with inline styles everywhere | Tailwind CSS v3 + CSS variables |
| Ad-hoc component primitives | shadcn/ui component system |
| Dark mode only, no light theme | Light-first, with optional dark mode toggle |
| No design token system | Complete token system via `tailwind.config.ts` |
| Fragmented theme state (per-page toggles) | Global `ThemeProvider` context |
| No routing protection (middleware) | Next.js Middleware for route protection |
| No TypeScript | TypeScript throughout |
| Inline `window.confirm()`, `window.print()` | Custom modals, proper PDF export |

---

## Design System Decisions

### Color Palette — Warm Minimal Light Theme

```
Background:     #FAFAF8   (warm off-white, not pure white)
Surface:        #FFFFFF   (card surfaces)
Border:         #E8E5DF   (warm stone border)
Text Primary:   #1C1917   (warm near-black)
Text Secondary: #78716C   (warm stone 500)
Text Muted:     #A8A29E   (warm stone 400)

Brand Accent:   #D97706   (amber-600 — warm, authoritative, memorable)
Accent Hover:   #B45309   (amber-700)
Accent Subtle:  #FEF3C7   (amber-50 — for backgrounds)
Accent Border:  #FCD34D   (amber-300)

Success:        #059669   (emerald-600)
Warning:        #D97706   (amber-600)
Error:          #DC2626   (red-600)
Info:           #2563EB   (blue-600)
```

**Why amber?** Amber is warm, intellectually credible, and rarely used in this space (green/blue dominate competitors). It pairs perfectly with the warm neutral backgrounds and Inter typography.

### Typography Stack

```
Primary:   Inter (variable font) — all UI text, labels, body
Headings:  Cal Sans / Instrument Serif — large display headings only
Mono:      JetBrains Mono — code blocks in reports
```

**Font sizes (Tailwind scale):**
- `text-xs`  (12px) — metadata, timestamps
- `text-sm`  (14px) — labels, secondary text
- `text-base`(16px) — body text
- `text-lg`  (18px) — card titles, section headers
- `text-xl`  (20px) — page sub-headings
- `text-2xl` (24px) — page headings
- `text-4xl` (36px) — hero/report scorecard numbers

### Spacing Philosophy
All spacing via Tailwind's 4px scale. Component-specific padding defined via `cn()` utility variants, not inline styles.

### Icon System
All icons: **Lucide React** (already in use). No custom SVG icons. Size conventions:
- Inline text: `size={14}` 
- Nav / labels: `size={16}`
- Feature icons: `size={20}`
- Empty states: `size={40}`

---

## Tech Stack

| Layer | Choice | Version | Rationale |
|---|---|---|---|
| Framework | Next.js | 14.x (App Router) | File-based routing, middleware, future SSR/ISR readiness |
| Language | TypeScript | 5.x | Type safety across all components and API layer |
| Styling | Tailwind CSS | 3.4.x | Utility-first, pairs with shadcn/ui |
| Component Library | shadcn/ui | latest | Copy-paste, Radix primitives, customizable |
| Charts | Recharts (via shadcn) | 2.x | Radar chart for score metrics |
| State Management | Zustand | 4.x | Minimal global store for auth + theme |
| Data Fetching | TanStack Query (React Query) | 5.x | Caching, loading/error states, refetch |
| Forms | React Hook Form + Zod | 7.x / 3.x | Validation, wizard steps |
| Markdown | react-markdown + remark-gfm | 10.x | Report rendering |
| PDF Export | html2pdf.js or @react-pdf/renderer | latest | Proper PDF export (replace window.print) |
| Animations | Framer Motion (light use) | 10.x | Page transitions, modal animations |
| Tag Input | emblor | latest | Skill chip inputs |
| Date Formatting | date-fns | 3.x | Format ISO dates to readable format |

---

## Phase Overview

| Phase | Name | Scope | Files Created | Est. Effort |
|---|---|---|---|---|
| **0** | **Master Plan (this doc)** | Architecture, decisions, token system | 1 overview + 5 phase docs | Planning |
| **1** | **Foundation & Infrastructure** | Next.js init, Tailwind config, token system, global styles, providers, middleware | ~15 files | Large |
| **2** | **Shared Component Library** | Button, Input, Card, Modal, TagInput, Skeleton, Avatar, Badge, Metric card, Select | ~12 files | Large |
| **3** | **Auth & Layout Shell** | Navbar, Auth pages (Login/Signup), Layout wrapper, global providers | ~8 files | Medium |
| **4** | **Core Pages (Dashboard + Profile)** | Dashboard with stats, Profile wizard, ProfileView hero | ~10 files | Large |
| **5** | **Interview Flow** | Setup wizard, Interview session, Report scorecard, History detail | ~10 files | Large |

---

## Migration Strategy

### Approach: Parallel New Directory
Create a new `frontend-v2/` directory at the project root containing the Next.js app. The existing `frontend/` (Vite) remains running and unchanged. Once v2 is validated, swap.

### Routing Mapping

| Old Route (Vite) | New Route (Next.js App Router) |
|---|---|
| `/login` | `/app/(auth)/login/page.tsx` |
| `/signup` | `/app/(auth)/signup/page.tsx` |
| `/dashboard` | `/app/(app)/dashboard/page.tsx` |
| `/profile` | `/app/(app)/profile/page.tsx` |
| `/profile/new` | `/app/(app)/profile/new/page.tsx` |
| `/profile/update` | `/app/(app)/profile/edit/page.tsx` |
| `/interview/start` | `/app/(app)/interview/setup/page.tsx` |
| `/interview/:session_id` | `/app/(app)/interview/[session_id]/page.tsx` |
| `/report/:session_id` | `/app/(app)/report/[session_id]/page.tsx` |
| `/interview/details/:id` | `/app/(app)/history/[interview_id]/page.tsx` |

### API Layer
The FastAPI backend stays unchanged. Only the frontend API client (`/lib/api.ts`) is rewritten to be type-safe and use TanStack Query hooks.

### State: Auth Token
The existing `localStorage` token approach is preserved for compatibility (the FastAPI backend is not modified). However, we add a **Zustand store** to centralize state instead of prop-drilling through React Context. Note in a future security audit, migrating to HTTP-only cookies should be explored.

---

## Cross-Phase Conventions

### File Naming
- Pages: `page.tsx` (Next.js convention)
- Components: `PascalCase.tsx`
- Hooks: `use-camelCase.ts`
- Utils: `camelCase.ts`
- Types: `types.ts` per feature, global at `/types/index.ts`

### Component Pattern
All feature components follow this internal structure:
```tsx
// 1. 'use client' directive (if interactive)
// 2. imports (external → internal → types)
// 3. TypeScript interfaces
// 4. Default export function
// 5. Sub-components (if small and only used here)
```

### `cn()` Utility
All class composition uses the `cn()` utility from `@/lib/utils` (clsx + tailwind-merge).

### Error Handling Pattern
All API calls wrapped in TanStack Query. Errors surface via `<ErrorState />` component. No raw `try/catch` in components.

---

## Open Questions for User Review

> [!IMPORTANT]
> **Q1 — Next.js vs Vite + React:**  
> The plan recommends **Next.js App Router** (CSR pages, no actual server-rendering for now). If you prefer a simpler Vite + React migration without Next.js overhead, Phase 1 can be adapted to use Vite + React Router v6 + TypeScript instead. This skips Next.js entirely. **Please confirm: Next.js or Vite+React?**

> [!IMPORTANT]
> **Q2 — Interview Length Selector:**  
> Currently hardcoded to `'short'`. The API supports `short | medium | long`. Should Phase 5 implement the full 3-option selector as card UI (with time estimates), or is it acceptable to implement as a simple radio group for now?

> [!WARNING]
> **Q3 — Auth Security Note:**  
> The current frontend stores JWT in `localStorage`. This is preserved in the migration for backend compatibility. Research confirms this is a known XSS risk. Should we flag this for the backend team to add a cookie-setting endpoint, or accept the `localStorage` approach for now?

> [!NOTE]
> **Q4 — TypeScript Strictness:**  
> Do you want strict TypeScript (`"strict": true`)? This requires explicit types everywhere and catches the most bugs, but is more verbose. Recommended: yes. Confirm?

> [!NOTE]
> **Q5 — Framer Motion:**  
> Framer Motion adds ~31KB gzipped. For a "minimal" aesthetic with subtle animations (page fade-in, modal slide), it's the cleanest option. Alternatively, CSS transitions only. Preference?

---

## Phase Documents

| Phase | Document | 
|---|---|
| Phase 1 | [phase-1-foundation.md](./phase-1-foundation.md) |
| Phase 2 | [phase-2-components.md](./phase-2-components.md) |
| Phase 3 | [phase-3-auth-layout.md](./phase-3-auth-layout.md) |
| Phase 4 | [phase-4-dashboard-profile.md](./phase-4-dashboard-profile.md) |
| Phase 5 | [phase-5-interview-flow.md](./phase-5-interview-flow.md) |
