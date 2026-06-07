import { cn, getScoreColor, getScoreBg, getScoreLabel } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { InfoIcon } from "lucide-react";
import { ScoreBar } from "./ScoreBar";

interface MetricCardProps {
  label: string;        // e.g. "QAR"
  fullName: string;     // e.g. "Question-Answer Relevance"
  description: string;  // Tooltip text
  score: number;        // 0–10
  maxScore?: number;
  className?: string;
}

export function MetricCard({
  label,
  fullName,
  description,
  score,
  maxScore = 10,
  className,
}: MetricCardProps) {
  const normalized = Math.min(Math.max(score, 0), maxScore);
  const displayScore = normalized.toFixed(1);

  return (
    <div
      className={cn(
        "rounded-xl border p-4 flex flex-col gap-3 transition-shadow hover:shadow-warm-md",
        getScoreBg(normalized),
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <span className="text-xs font-semibold uppercase tracking-widest text-text-muted">
            {label}
          </span>
          <p className="text-sm font-medium text-text-main mt-0.5 leading-tight">
            {fullName}
          </p>
        </div>

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="text-text-muted hover:text-text-secondary transition-colors mt-0.5">
                <InfoIcon size={14} />
              </button>
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-[220px] text-xs">
              {description}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      {/* Score */}
      <div className="flex items-end gap-2">
        <span className={cn("text-3xl font-bold tabular-nums", getScoreColor(normalized))}>
          {displayScore}
        </span>
        <span className="text-xs text-text-muted mb-1">/ {maxScore}</span>
        <span className={cn("ml-auto text-xs font-medium", getScoreColor(normalized))}>
          {getScoreLabel(normalized)}
        </span>
      </div>

      {/* Progress bar */}
      <ScoreBar score={normalized} maxScore={maxScore} />
    </div>
  );
}
