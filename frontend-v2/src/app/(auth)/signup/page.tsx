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
      <p className={cn("text-xs font-medium", strength <= 1 ? "text-error" : strength <= 2 ? "text-warning" : "text-success")}>
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
