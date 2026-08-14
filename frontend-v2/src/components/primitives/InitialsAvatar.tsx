import { cn, getInitials } from "@/lib/utils";

interface InitialsAvatarProps {
  name?: string | null;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

const sizeStyles = {
  sm:  "h-7  w-7  text-xs",
  md:  "h-9  w-9  text-sm",
  lg:  "h-11 w-11 text-base",
  xl:  "h-16 w-16 text-xl",
};

export function InitialsAvatar({ name, size = "md", className }: InitialsAvatarProps) {
  const initials = getInitials(name);

  return (
    <div
      className={cn(
        "rounded-full bg-brand-100 text-brand-800 font-semibold",
        "flex items-center justify-center flex-shrink-0 select-none",
        "border border-brand-200",
        sizeStyles[size],
        className
      )}
      aria-label={name ?? "User"}
    >
      {initials}
    </div>
  );
}
