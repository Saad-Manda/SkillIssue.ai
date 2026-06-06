import { cn } from "@/lib/utils";

interface ScoreBarProps {
  score: number;
  maxScore?: number;
  height?: "sm" | "md";
  className?: string;
}

export function ScoreBar({ score, maxScore = 10, height = "sm", className }: ScoreBarProps) {
  const pct = Math.min(Math.max((score / maxScore) * 100, 0), 100);

  const barColor =
    score >= 8 ? "bg-success" :
    score >= 6 ? "bg-warning" :
    score >= 4 ? "bg-orange-500" :
    "bg-error";

  return (
    <div
      className={cn(
        "w-full rounded-full bg-black/5 overflow-hidden",
        height === "sm" ? "h-1.5" : "h-2.5",
        className
      )}
    >
      <div
        className={cn("h-full rounded-full transition-all duration-500 ease-out", barColor)}
        style={{ width: `${pct}%` }}
        role="progressbar"
        aria-valuenow={score}
        aria-valuemin={0}
        aria-valuemax={maxScore}
      />
    </div>
  );
}
