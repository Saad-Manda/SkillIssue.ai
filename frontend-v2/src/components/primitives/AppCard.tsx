import { cn } from "@/lib/utils";

interface AppCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "outlined" | "flat";
  hoverable?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
}

const variantStyles = {
  default:  "bg-white border border-warm-border shadow-warm-sm",
  outlined: "bg-transparent border-2 border-warm-border",
  flat:     "bg-warm-muted border-0",
};

const paddingStyles = {
  none: "",
  sm:   "p-4",
  md:   "p-6",
  lg:   "p-8",
};

export function AppCard({
  variant = "default",
  hoverable = false,
  padding = "md",
  className,
  children,
  ...props
}: AppCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl w-full",
        variantStyles[variant],
        paddingStyles[padding],
        hoverable && "cursor-pointer transition-shadow duration-200 hover:shadow-warm-md hover:border-warm-border/80",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
