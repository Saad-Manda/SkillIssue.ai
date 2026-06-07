"use client";
import { useState, Suspense } from "react";
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

function LoginPageContent() {
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
        username_or_email: data.email,
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

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="text-center py-4 text-text-muted text-sm font-sans">Loading...</div>}>
      <LoginPageContent />
    </Suspense>
  );
}
