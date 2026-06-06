import { cn } from "@/lib/utils";
import { CheckCircle2, AlertTriangle, Clock } from "lucide-react";

type InterviewStatus = "completed" | "abandoned" | "in_progress" | "unknown";

interface StatusBadgeProps {
  status: InterviewStatus;
  className?: string;
}

const STATUS_CONFIG = {
  completed:   { label: "Completed",   icon: CheckCircle2,  class: "bg-success/10 text-success  border-success/20"  },
  abandoned:   { label: "Abandoned",   icon: AlertTriangle, class: "bg-warning/10 text-warning  border-warning/20"  },
  in_progress: { label: "In Progress", icon: Clock,         class: "bg-info/10    text-info     border-info/20"     },
  unknown:     { label: "Unknown",     icon: Clock,         class: "bg-warm-muted text-text-muted border-warm-border"},
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.unknown;
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 text-xs font-medium",
        "px-2.5 py-1 rounded-full border",
        config.class,
        className
      )}
    >
      <Icon size={12} />
      {config.label}
    </span>
  );
}
