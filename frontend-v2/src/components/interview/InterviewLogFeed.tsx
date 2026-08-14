import { useEffect, useRef } from "react";
import type { SessionEvent } from "@/types/api";

export function InterviewLogFeed({ events }: { events: SessionEvent[] }) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "nearest" });
  }, [events]);

  if (events.length === 0) return null;

  return (
    <div className="max-h-48 overflow-y-auto rounded-lg bg-warm-muted px-2 py-1.5 font-mono text-micro text-text-secondary space-y-0.5">
      {events.slice(-50).map((e, i) => (
        <div key={i} className="whitespace-nowrap">
          <span className="text-text-muted">{new Date(e.timestamp).toLocaleTimeString()}</span>{" "}
          <span className="text-brand-700">{e.agent}</span> {e.event}
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
