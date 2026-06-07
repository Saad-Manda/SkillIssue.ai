"use client";
import { useId, useState } from "react";
import { TagInput as EmblorTagInput, Tag } from "emblor";
import { cn } from "@/lib/utils";

interface TagInputProps {
  label?: string;
  hint?: string;
  error?: string;
  tags: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  maxTags?: number;
  className?: string;
}

export function TagInput({
  label,
  hint,
  error,
  tags,
  onChange,
  placeholder = "Type and press Enter…",
  maxTags = 20,
  className,
}: TagInputProps) {
  const id = useId();
  const [activeTagIndex, setActiveTagIndex] = useState<number | null>(null);
  const tagObjects: Tag[] = tags.map((t, i) => ({ id: String(i), text: t }));

  return (
    <div className={cn("flex flex-col gap-1.5 w-full", className)}>
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-text-main">
          {label}
        </label>
      )}

      <EmblorTagInput
        id={id}
        tags={tagObjects}
        setTags={(newTags) => {
          const arr = (typeof newTags === "function" ? newTags(tagObjects) : newTags);
          onChange(arr.map((t) => t.text));
        }}
        activeTagIndex={activeTagIndex}
        setActiveTagIndex={setActiveTagIndex}
        placeholder={placeholder}
        maxTags={maxTags}
        styleClasses={{
          input: cn(
            "min-w-[120px] bg-transparent text-sm text-text-main placeholder:text-text-muted",
            "focus:outline-none"
          ),
          tag: {
            body: "inline-flex items-center gap-1 px-2.5 py-1 bg-brand-100 text-brand-800 text-xs font-medium rounded-full border border-brand-200",
            closeButton: "text-brand-600 hover:text-brand-800 ml-1",
          },
          inlineTagsContainer: cn(
            "flex flex-wrap gap-1.5 w-full min-h-[42px] px-3 py-2",
            "rounded-lg border border-warm-border bg-white",
            "focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-600/20",
            "transition-colors duration-150",
            error && "border-error focus-within:ring-error/20"
          ),
        }}
        inputFieldPosition="bottom"
      />

      {error && <p className="text-xs text-error">{error}</p>}
      {hint && !error && (
        <p className="text-xs text-text-muted">{hint}</p>
      )}
    </div>
  );
}
