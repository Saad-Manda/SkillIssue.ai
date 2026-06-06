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
