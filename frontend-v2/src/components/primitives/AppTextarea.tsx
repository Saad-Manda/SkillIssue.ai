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
