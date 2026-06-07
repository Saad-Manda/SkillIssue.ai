# Feature Plan: phase-3-auth-layout-plan

> [!NOTE]
> This plan has been generated through parallel codebase analysis and is optimized for one-pass execution success.

## Feature Overview & Business Value
This phase builds the application nav/auth layout shells and pages (Login, Signup, Navbar, Redirects). It establishes the core navigation shell, layouts structure (separating auth-centric layouts from main app layout grids), and validates candidate credentials using React Hook Form + Zod with proper JWT persistence signals, ensuring a smooth transition from signup to profile creation.

## Architectural Design & Scope
- **Feature Type**: New Capability / Refactor
- **Complexity**: Medium
- **Systems Affected**: Client-side routing, navigation shell layout, authentication flows
- **Dependencies**: `lucide-react`, `react-hook-form`, `@hookform/resolvers`, `zod`, `next`

---

## Context References

### Mandatory Codebase Files to Read
- [src/types/api.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/types/api.ts) - TS interfaces for payloads and responses
- [src/lib/api.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/lib/api.ts) - API requests mapping
- [src/components/primitives/AppButton.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/AppButton.tsx) - Button primitive used in forms
- [src/components/primitives/AppInput.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/AppInput.tsx) - Input primitive used in forms
- [src/components/primitives/InitialsAvatar.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/primitives/InitialsAvatar.tsx) - Avatar primitive used in navbar

### New Files to Create / Modify
- [frontend-v2/src/app/page.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/app/page.tsx)
- [frontend-v2/src/app/(app)/layout.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/app/(app)/layout.tsx)
- [frontend-v2/src/app/(auth)/layout.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/app/(auth)/layout.tsx)
- [frontend-v2/src/app/(auth)/login/page.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/app/(auth)/login/page.tsx)
- [frontend-v2/src/app/(auth)/signup/page.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/app/(auth)/signup/page.tsx)
- [frontend-v2/src/components/layout/Navbar.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/components/layout/Navbar.tsx)
- [frontend-v2/src/hooks/use-auth.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/hooks/use-auth.ts)
- [frontend-v2/src/lib/validation.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/lib/validation.ts)

---

## Step-by-Step Tasks

### Phase 1: Foundation & Shared Schemas

#### Task 1.1: CREATE `frontend-v2/src/lib/validation.ts`
- **IMPLEMENT**: Centralized Zod verification schemas for auth, profile updates, and JD setups to maintain type-safe validation parameters.
- **CODE**:
```typescript
import { z } from "zod";

// ── Auth ──────────────────────────────────────────────────────────────
export const loginSchema = z.object({
  email:    z.string().email("Valid email required"),
  password: z.string().min(1, "Password required"),
});

export const signupSchema = z
  .object({
    username: z.string().min(3, "Username must be at least 3 characters").max(30),
    email:    z.string().email("Valid email required"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirm:  z.string(),
  })
  .refine((d) => d.password === d.confirm, {
    message: "Passwords do not match",
    path: ["confirm"],
  });

// ── Profile — Basic Info ──────────────────────────────────────────────
export const basicsSchema = z.object({
  name:         z.string().min(1, "Full name is required"),
  mobile:       z.string().optional(),
  github_url:   z.string().url("Must be a valid URL").optional().or(z.literal("")),
  linkedin_url: z.string().url("Must be a valid URL").optional().or(z.literal("")),
  skills:       z.array(z.string()).min(1, "Add at least one skill"),
});

// ── JD Setup ─────────────────────────────────────────────────────────
export const setupInterviewSchema = z.object({
  job_title:              z.string().min(2, "Job title is required"),
  job_type:               z.enum(["full_time", "part_time"]),
  min_experience:         z.coerce.number().min(0).max(50),
  required_qualification: z.string().min(1, "Required"),
  required_skills:        z.array(z.string()).min(1, "Add at least one skill"),
  responsibilities:       z.string().optional(),
  description:            z.string().optional(),
  interview_length:       z.enum(["short", "medium", "long"]),
});

export type SetupInterviewForm = z.infer<typeof setupInterviewSchema>;
```
- **VALIDATION**: Compile check in `frontend-v2`.

#### Task 1.2: CREATE `frontend-v2/src/hooks/use-auth.ts`
- **IMPLEMENT**: Convenience wrapper exposing Zustand auth store properties.
- **CODE**:
```typescript
import { useAuthStore } from "@/store/auth-store";

export function useAuth() {
  return useAuthStore();
}
```
- **VALIDATION**: Compile check.

---

### Phase 2: Page Shell layouts & Redirects

#### Task 2.1: UPDATE `frontend-v2/src/app/page.tsx`
- **IMPLEMENT**: Overwrite Next.js default root page.tsx to perform a server-side redirect to `/dashboard`.
- **CODE**:
```tsx
import { redirect } from "next/navigation";
export default function Home() {
  redirect("/dashboard");
}
```
- **VALIDATION**: Compile check.

#### Task 2.2: UPDATE `frontend-v2/src/app/(app)/layout.tsx`
- **IMPLEMENT**: Overwrite layout to import and mount navigation bars wrapping sub-pages.
- **CODE**:
```tsx
import { Navbar } from "@/components/layout/Navbar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-warm-bg flex flex-col">
      <Navbar />
      <main className="flex-1 w-full">{children}</main>
    </div>
  );
}
```
- **VALIDATION**: Compile check.

#### Task 2.3: UPDATE `frontend-v2/src/app/(auth)/layout.tsx`
- **IMPLEMENT**: Two-column layout featuring a Left brand panel with overlay grid texture and responsiveness that collapses columns below 1024px width.
- **CODE**:
```tsx
import type { Metadata } from "next";
import { BrainCircuit } from "lucide-react";

export const metadata: Metadata = {
  title: "Sign In — SkillIssue.ai",
};

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
      {/* Left — Brand Hero Panel */}
      <div className="hidden lg:flex flex-col justify-between bg-stone-950 p-12 text-white relative overflow-hidden">
        {/* Subtle grid texture */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: "radial-gradient(circle at 1px 1px, white 1px, transparent 0)",
            backgroundSize: "32px 32px",
          }}
        />

        {/* Logo */}
        <div className="relative z-10 flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
            <BrainCircuit size={18} className="text-white" />
          </div>
          <span className="text-lg font-semibold tracking-tight">SkillIssue.ai</span>
        </div>

        {/* Value props */}
        <div className="relative z-10 space-y-8">
          <blockquote className="space-y-4">
            <p className="text-2xl font-light leading-relaxed text-stone-100 font-serif italic">
              "Context-aware AI interviews that prepare you for the real conversation — not a generic script."
            </p>
          </blockquote>

          <div className="grid grid-cols-1 gap-4">
            {[
              { metric: "8 Metrics", label: "Evaluated per answer" },
              { metric: "Adaptive", label: "Questions based on your profile" },
              { metric: "Instant", label: "Readiness Report on completion" },
            ].map(({ metric, label }) => (
              <div key={metric} className="flex items-center gap-3">
                <div className="h-1.5 w-1.5 rounded-full bg-brand-400" />
                <span className="font-semibold text-white">{metric}</span>
                <span className="text-stone-400 text-sm">{label}</span>
              </div>
            ))}
          </div>
        </div>

        <p className="relative z-10 text-xs text-stone-500">
          © 2026 SkillIssue.ai — AI-Powered Interview Preparation
        </p>
      </div>

      {/* Right — Auth Form Panel */}
      <div className="flex items-center justify-center p-8 lg:p-12 bg-warm-bg">
        <div className="w-full max-w-md">
          {/* Mobile logo only */}
          <div className="flex lg:hidden items-center gap-2 mb-8">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-brand-600">
              <BrainCircuit size={16} className="text-white" />
            </div>
            <span className="font-semibold text-text-main">SkillIssue.ai</span>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
```
- **VALIDATION**: Compile check.

---

### Phase 3: Login & Signup Pages Implementation

#### Task 3.1: UPDATE `frontend-v2/src/app/(auth)/login/page.tsx`
- **IMPLEMENT**: Labeled fields, show/hide password toggle, React Hook Form registration, Zod schema validation errors, and cookie presence trigger on submission.
- **CODE**:
```tsx
"use client";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { Eye, EyeOff, Mail, Lock } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppInput } from "@/components/primitives/AppInput";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "@/lib/api";
import { loginSchema } from "@/lib/validation";
import type { z } from "zod";

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirectTo") ?? "/dashboard";
  const { setAuth } = useAuthStore();

  const [showPassword, setShowPassword] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (data: LoginForm) => {
    setApiError(null);
    try {
      const res = await authApi.login({
        username: data.email,
        email: data.email,
        password: data.password,
      });

      document.cookie = "skillissue-authed=1; path=/; max-age=86400; SameSite=Lax";

      setAuth(res.access_token, {
        id: res.user_id,
        email: data.email,
        username: data.email.split("@")[0],
      });

      router.push(redirectTo);
    } catch (err: unknown) {
      const error = err as { message?: string };
      setApiError(
        error.message === "Request failed"
          ? "Incorrect email or password. Please try again."
          : (error.message ?? "Something went wrong. Please try again.")
      );
    }
  };

  return (
    <div className="animate-slide-up space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-text-main tracking-tight">
          Welcome back
        </h1>
        <p className="text-sm text-text-secondary mt-1.5">
          Sign in to continue your interview prep.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {apiError && (
          <div className="rounded-lg bg-error/8 border border-error/20 px-4 py-3">
            <p className="text-sm text-error">{apiError}</p>
          </div>
        )}

        <AppInput
          label="Email address"
          type="email"
          placeholder="you@example.com"
          autoComplete="email"
          prefixIcon={<Mail size={16} />}
          error={errors.email?.message}
          {...register("email")}
        />

        <AppInput
          label="Password"
          type={showPassword ? "text" : "password"}
          placeholder="Your password"
          autoComplete="current-password"
          prefixIcon={<Lock size={16} />}
          suffixIcon={
            <button
              type="button"
              tabIndex={-1}
              onClick={() => setShowPassword((p) => !p)}
              className="text-text-muted hover:text-text-secondary transition-colors"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          }
          error={errors.password?.message}
          {...register("password")}
        />

        <div className="flex items-center justify-end">
          <Link
            href="#"
            className="text-sm text-brand-600 hover:text-brand-700 font-medium transition-colors"
          >
            Forgot password?
          </Link>
        </div>

        <AppButton
          type="submit"
          variant="brand"
          size="lg"
          fullWidth
          isLoading={isSubmitting}
        >
          Sign in
        </AppButton>
      </form>

      <p className="text-center text-sm text-text-secondary">
        Don&apos;t have an account?{" "}
        <Link
          href="/signup"
          className="font-medium text-brand-600 hover:text-brand-700 transition-colors"
        >
          Create one
        </Link>
      </p>
    </div>
  );
}
```
- **VALIDATION**: Compile check.

#### Task 3.2: UPDATE `frontend-v2/src/app/(auth)/signup/page.tsx`
- **IMPLEMENT**: Signup flow including password strength meters, confirmation fields, API validation endpoints calling, and redirect rules.
- **CODE**:
```tsx
"use client";
import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { Eye, EyeOff, Mail, Lock, User } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppInput } from "@/components/primitives/AppInput";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import { signupSchema } from "@/lib/validation";
import type { z } from "zod";

type SignupForm = z.infer<typeof signupSchema>;

function PasswordStrength({ password }: { password: string }) {
  const strength = useMemo(() => {
    let score = 0;
    if (password.length >= 8)  score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score;
  }, [password]);

  if (!password) return null;

  const labels = ["Weak", "Fair", "Good", "Strong"];
  const colors = ["bg-error", "bg-warning", "bg-brand-500", "bg-success"];

  return (
    <div className="mt-1.5 space-y-1.5">
      <div className="flex gap-1">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className={cn(
              "h-1 flex-1 rounded-full transition-all duration-300",
              i < strength ? colors[strength - 1] : "bg-warm-border"
            )}
          />
        ))}
      </div>
      <p className={cn("text-xs", strength <= 1 ? "text-error" : strength <= 2 ? "text-warning" : "text-success")}>
        {labels[strength - 1] ?? "Too short"}
      </p>
    </div>
  );
}

export default function SignupPage() {
  const router = useRouter();
  const { setSignupToken } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<SignupForm>({ resolver: zodResolver(signupSchema) });

  const password = watch("password", "");

  const onSubmit = async (data: SignupForm) => {
    setApiError(null);
    try {
      const res = await authApi.signup({
        username: data.username,
        email: data.email,
        password: data.password,
      });
      setSignupToken(res.signup_token);
      router.push("/profile/new");
    } catch (err: unknown) {
      const error = err as { message?: string };
      setApiError(error.message ?? "Signup failed. Please try again.");
    }
  };

  return (
    <div className="animate-slide-up space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-text-main tracking-tight">
          Create your account
        </h1>
        <p className="text-sm text-text-secondary mt-1.5">
          Build your profile and start practicing today.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {apiError && (
          <div className="rounded-lg bg-error/8 border border-error/20 px-4 py-3">
            <p className="text-sm text-error">{apiError}</p>
          </div>
        )}

        <AppInput
          label="Username"
          type="text"
          placeholder="johndoe"
          autoComplete="username"
          prefixIcon={<User size={16} />}
          hint="3–30 characters, used to identify you"
          error={errors.username?.message}
          {...register("username")}
        />

        <AppInput
          label="Email address"
          type="email"
          placeholder="you@example.com"
          autoComplete="email"
          prefixIcon={<Mail size={16} />}
          error={errors.email?.message}
          {...register("email")}
        />

        <div>
          <AppInput
            label="Password"
            type={showPassword ? "text" : "password"}
            placeholder="At least 8 characters"
            autoComplete="new-password"
            prefixIcon={<Lock size={16} />}
            suffixIcon={
              <button
                type="button"
                tabIndex={-1}
                onClick={() => setShowPassword((p) => !p)}
                className="text-text-muted hover:text-text-secondary transition-colors"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            }
            error={errors.password?.message}
            {...register("password")}
          />
          <PasswordStrength password={password} />
        </div>

        <AppInput
          label="Confirm password"
          type={showPassword ? "text" : "password"}
          placeholder="Repeat your password"
          autoComplete="new-password"
          prefixIcon={<Lock size={16} />}
          error={errors.confirm?.message}
          {...register("confirm")}
        />

        <AppButton
          type="submit"
          variant="brand"
          size="lg"
          fullWidth
          isLoading={isSubmitting}
        >
          Create account
        </AppButton>
      </form>

      <p className="text-center text-sm text-text-secondary">
        Already have an account?{" "}
        <Link
          href="/login"
          className="font-medium text-brand-600 hover:text-brand-700 transition-colors"
        >
          Sign in
        </Link>
      </p>
    </div>
  );
}
```
- **VALIDATION**: Compile check.

---

### Phase 4: App Navigation Shell

#### Task 4.1: CREATE `frontend-v2/src/components/layout/Navbar.tsx`
- **IMPLEMENT**: Accessible header navigation bar featuring responsive mobile links, brand triggers, new interview setup action shortcuts, and InitialsAvatar user dropdown.
- **CODE**:
```tsx
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BrainCircuit, LayoutDashboard, User, Plus, LogOut, Settings } from "lucide-react";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { InitialsAvatar } from "@/components/primitives/InitialsAvatar";
import { AppButton } from "@/components/primitives/AppButton";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "@/lib/api";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/profile",   label: "Profile",   icon: User           },
];

export function Navbar() {
  const pathname  = usePathname();
  const router    = useRouter();
  const { user, token, clearAuth } = useAuthStore();

  const handleLogout = async () => {
    try {
      if (token) await authApi.logout(token);
    } catch {
      // Ignore logout API errors — clear client state regardless
    }
    document.cookie = "skillissue-authed=; path=/; max-age=0";
    clearAuth();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-warm-border bg-white/80 backdrop-blur-sm">
      <nav
        className="flex h-14 items-center justify-between px-4 md:px-8 max-w-screen-xl mx-auto"
        aria-label="Main navigation"
      >
        {/* Left — Logo + Nav links */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-brand-600">
              <BrainCircuit size={16} className="text-white" />
            </div>
            <span className="font-semibold text-text-main text-sm tracking-tight hidden sm:block">
              SkillIssue.ai
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map(({ href, label, icon: Icon }) => {
              const isActive = pathname === href || pathname.startsWith(`${href}/`);
              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium",
                    "transition-colors duration-150",
                    isActive
                      ? "bg-brand-50 text-brand-700"
                      : "text-text-secondary hover:text-text-main hover:bg-warm-muted"
                  )}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon size={16} />
                  {label}
                </Link>
              );
            })}
          </div>
        </div>

        {/* Right — New Interview shortcut + User menu */}
        <div className="flex items-center gap-3">
          <AppButton
            variant="brand"
            size="sm"
            leftIcon={<Plus size={14} />}
            onClick={() => router.push("/interview/setup")}
            className="hidden sm:inline-flex"
          >
            New Interview
          </AppButton>

          {/* User Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 rounded-full"
                aria-label="Open user menu"
              >
                <InitialsAvatar name={user?.username ?? user?.email} size="sm" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-52 bg-white border-warm-border shadow-warm-lg">
              <div className="px-3 py-2 border-b border-warm-border">
                <p className="text-sm font-medium text-text-main truncate">
                  {user?.username ?? "User"}
                </p>
                <p className="text-xs text-text-muted truncate">{user?.email}</p>
              </div>

              <DropdownMenuItem asChild>
                <Link href="/profile" className="flex items-center gap-2 cursor-pointer">
                  <User size={14} /> My Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="#" className="flex items-center gap-2 cursor-pointer text-text-muted">
                  <Settings size={14} /> Settings
                </Link>
              </DropdownMenuItem>

              <DropdownMenuSeparator />

              <DropdownMenuItem
                onClick={handleLogout}
                className="flex items-center gap-2 text-error focus:text-error focus:bg-error/8 cursor-pointer"
              >
                <LogOut size={14} /> Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </nav>
    </header>
  );
}
```
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
1. Verify navigating to `/` redirects cleanly to `/dashboard` which triggers the auth check and redirects to `/login`.
2. Inspect the `/login` and `/signup` page responsiveness down to mobile resolutions.
3. Validate client-side Zod validation errors on both login and signup screens by clicking submit with invalid information.
4. Input complex values to ensure the password strength indicator changes colors.
5. Log in successfully and check if cookies and Zustand store persist details correctly.
6. Verify clicking navbar links activates state style changes.

### Acceptance Criteria Checklist
- [ ] Auth pages collapse to single columns under 1024px width.
- [ ] Error alert messages appear cleanly upon login/signup failure.
- [ ] Active link headers present proper background pills.
- [ ] Logging out clears the Zustand store and removes auth cookies.
