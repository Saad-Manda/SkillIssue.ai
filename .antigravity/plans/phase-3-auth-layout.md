# Phase 3 — Auth Pages & Layout Shell

> **Goal:** Build the application shell — Navbar, layout wrappers (auth & app), and both auth pages (Login/Signup) with full UX completeness: active link states, user dropdown, client-side validation, password toggle, and animated card entrance.  
> **Prerequisite:** Phase 1 + Phase 2 complete.  
> **Output:** A fully navigable app shell. Users can sign up, log in, and be redirected to the (empty) dashboard.

---

## 3.1 Root Redirect Page

**File: `src/app/page.tsx`**

```tsx
import { redirect } from "next/navigation";
export default function Home() {
  redirect("/dashboard");
}
```

---

## 3.2 App Layout (Authenticated Pages)

**File: `src/app/(app)/layout.tsx`**

This wraps all authenticated routes: `/dashboard`, `/profile`, `/interview`, `/report`, `/history`.

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

---

## 3.3 Auth Layout (Login / Signup)

**File: `src/app/(auth)/layout.tsx`**

Two-column layout: left = branding hero, right = form. Collapses to single column on mobile.

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

---

## 3.4 Login Page

**File: `src/app/(auth)/login/page.tsx`**

Fixes: removes `username` field (email + password only for login), adds password toggle, adds client-side validation with Zod + React Hook Form, adds loading spinner on button, proper error messages.

```tsx
"use client";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { Eye, EyeOff, Mail, Lock } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppInput } from "@/components/primitives/AppInput";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "@/lib/api";

const loginSchema = z.object({
  email:    z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

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
      // Backend still requires username — we send email as username for MVP
      const res = await authApi.login({
        username: data.email,
        email: data.email,
        password: data.password,
      });

      // Set auth cookie signal for middleware
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
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-text-main tracking-tight">
          Welcome back
        </h1>
        <p className="text-sm text-text-secondary mt-1.5">
          Sign in to continue your interview prep.
        </p>
      </div>

      {/* Form */}
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

      {/* Footer */}
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

---

## 3.5 Signup Page

**File: `src/app/(auth)/signup/page.tsx`**

Fixes: adds Zod validation (email format, password match, min length), password strength indicator, password visibility toggle.

```tsx
"use client";
import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { Eye, EyeOff, Mail, Lock, User } from "lucide-react";
import { AppButton } from "@/components/primitives/AppButton";
import { AppInput } from "@/components/primitives/AppInput";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "@/lib/api";
import { cn } from "@/lib/utils";

const signupSchema = z
  .object({
    username: z.string().min(3, "Username must be at least 3 characters").max(30),
    email:    z.string().email("Please enter a valid email address"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirm:  z.string(),
  })
  .refine((d) => d.password === d.confirm, {
    message: "Passwords do not match",
    path: ["confirm"],
  });

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

---

## 3.6 Navbar

**File: `src/components/layout/Navbar.tsx`**

Fixes from audit: active link indicator, user avatar dropdown (not raw email), global theme toggle placeholder, mobile menu.

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
    // Remove auth middleware cookie
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
              {/* User info */}
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

---

## 3.7 useAuth Hook (convenience wrapper)

**File: `src/hooks/use-auth.ts`**

```typescript
import { useAuthStore } from "@/store/auth-store";

// Convenience hook that mirrors the old useAuth() context interface
export function useAuth() {
  return useAuthStore();
}
```

---

## 3.8 Form Validation Schemas (Shared)

**File: `src/lib/validation.ts`**

Centralizes Zod schemas for all forms — avoids duplication across pages.

```typescript
import { z } from "zod";

// ── Auth ──────────────────────────────────────────────────────────────
export const loginSchema = z.object({
  email:    z.string().email("Valid email required"),
  password: z.string().min(1, "Password required"),
});

export const signupSchema = z
  .object({
    username: z.string().min(3).max(30),
    email:    z.string().email(),
    password: z.string().min(8, "At least 8 characters"),
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

---

## Phase 3 Verification Checklist

- [ ] `/login` renders two-panel layout (hero left, form right) on desktop
- [ ] `/login` collapses to single column with mobile logo on < 1024px  
- [ ] Login form shows inline Zod errors on invalid submit (email, password)
- [ ] Password visibility toggle works on both login and signup
- [ ] Signup password strength bar updates in real time
- [ ] Signup password mismatch shows error on `confirm` field
- [ ] Successful login stores token in Zustand + sets `skillissue-authed` cookie
- [ ] Successful login redirects to `/dashboard` (or `redirectTo` param)
- [ ] Navbar shows user initials avatar (not raw email)
- [ ] Navbar active link has amber background pill indicator
- [ ] User dropdown shows username + email, Edit Profile link, Sign Out
- [ ] Sign Out clears Zustand state + removes auth cookie + redirects to `/login`
- [ ] "New Interview" button in navbar navigates to `/interview/setup`
- [ ] Navigating to `/dashboard` without auth cookie redirects to `/login`

---

## Files Created in Phase 3

| File | Description |
|---|---|
| `src/app/page.tsx` | Root redirect |
| `src/app/(app)/layout.tsx` | Authenticated app layout |
| `src/app/(auth)/layout.tsx` | Auth two-panel layout |
| `src/app/(auth)/login/page.tsx` | Login form with validation |
| `src/app/(auth)/signup/page.tsx` | Signup form with strength meter |
| `src/components/layout/Navbar.tsx` | Navbar with active links + user dropdown |
| `src/hooks/use-auth.ts` | Auth convenience hook |
| `src/lib/validation.ts` | Centralized Zod schemas |
