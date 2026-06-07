import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

// Interview history card skeleton
export function InterviewCardSkeleton() {
  return (
    <div className="flex items-center justify-between p-4 rounded-xl border border-warm-border bg-white">
      <div className="flex flex-col gap-2 flex-1">
        <Skeleton className="h-4 w-32 bg-warm-muted" />
        <Skeleton className="h-3 w-48 bg-warm-muted" />
      </div>
      <Skeleton className="h-7 w-20 rounded-full bg-warm-muted" />
    </div>
  );
}

// Profile section skeleton
export function ProfileSectionSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-5 w-48 bg-warm-muted" />
      <Skeleton className="h-4 w-full bg-warm-muted" />
      <Skeleton className="h-4 w-3/4 bg-warm-muted" />
    </div>
  );
}

// Metric card skeleton (for report loading)
export function MetricCardSkeleton() {
  return (
    <div className="rounded-xl border border-warm-border p-4 space-y-3">
      <div className="flex justify-between">
        <Skeleton className="h-3 w-10 bg-warm-muted" />
        <Skeleton className="h-3 w-3 rounded-full bg-warm-muted" />
      </div>
      <Skeleton className="h-4 w-3/4 bg-warm-muted" />
      <Skeleton className="h-8 w-16 bg-warm-muted" />
      <Skeleton className="h-1.5 w-full rounded-full bg-warm-muted" />
    </div>
  );
}

// Full report loading skeleton
export function ReportSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <MetricCardSkeleton key={i} />
        ))}
      </div>
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className={cn("h-4 bg-warm-muted", i % 2 === 0 ? "w-full" : "w-4/5")} />
        ))}
      </div>
    </div>
  );
}
