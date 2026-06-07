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
              &ldquo;Context-aware AI interviews that prepare you for the real conversation — not a generic script.&rdquo;
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
