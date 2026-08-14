import type { GraphNode, PulseTrigger } from "@/hooks/useSessionEvents";
import { cn } from "@/lib/utils";

const NODE_POS: Record<GraphNode, { x: number; y: number; label: string }> = {
  user_summarizer:    { x: 120, y: 20,  label: "US" },
  planner:            { x: 120, y: 80,  label: "PL" },
  router:             { x: 120, y: 150, label: "RT" },
  question_generator: { x: 60,  y: 230, label: "QG" },
  metric_calculator:  { x: 180, y: 230, label: "MC" },
  phase_summarizer:   { x: 120, y: 290, label: "PS" },
  report_generator:   { x: 120, y: 350, label: "RG" },
};

const EDGE_PATHS: { from: GraphNode; to: GraphNode; d: string }[] = [
  { from: "user_summarizer",    to: "planner",            d: "M120,20 L120,80" },
  { from: "planner",            to: "router",             d: "M120,80 L120,150" },
  { from: "router",             to: "question_generator", d: "M120,150 L60,230" },
  { from: "router",             to: "report_generator",   d: "M120,150 Q210,250 120,350" },
  { from: "question_generator", to: "phase_summarizer",   d: "M60,230 L120,290" },
  { from: "question_generator", to: "metric_calculator",  d: "M60,230 L180,230" },
  { from: "phase_summarizer",   to: "metric_calculator",  d: "M120,290 L180,230" },
  { from: "metric_calculator",  to: "router",             d: "M180,230 Q230,190 120,150" },
  { from: "metric_calculator",  to: "report_generator",   d: "M180,230 L120,350" },
];

function edgeKey(from: string, to: string) {
  return `${from}->${to}`;
}

export function InterviewGraphPanel({
  visitedNodes,
  visitedEdges,
  activeNode,
  pulseTrigger,
}: {
  visitedNodes: Set<GraphNode>;
  visitedEdges: Set<string>;
  activeNode: GraphNode | null;
  pulseTrigger: PulseTrigger | null;
}) {
  const activePulse = pulseTrigger
    ? EDGE_PATHS.find((e) => e.from === pulseTrigger.from && e.to === pulseTrigger.to)
    : null;

  if (visitedNodes.size === 0) {
    return (
      <p className="text-xs text-text-muted italic">Agent graph will appear as the interview runs…</p>
    );
  }

  return (
    <svg viewBox="0 0 240 380" className="w-full h-auto">
      {EDGE_PATHS.filter((e) => visitedEdges.has(edgeKey(e.from, e.to))).map((e) => (
        <path
          key={edgeKey(e.from, e.to)}
          d={e.d}
          fill="none"
          strokeWidth={1.5}
          className="stroke-brand-300 animate-fade-in"
        />
      ))}

      {activePulse && (
        <circle
          key={pulseTrigger!.key}
          r={4}
          className="fill-brand-600 animate-data-pulse"
          style={{ offsetPath: `path('${activePulse.d}')` } as React.CSSProperties}
        />
      )}

      {Object.entries(NODE_POS)
        .filter(([id]) => visitedNodes.has(id as GraphNode))
        .map(([id, pos]) => (
          <g
            key={id}
            transform={`translate(${pos.x},${pos.y})`}
            className="animate-fade-in"
          >
            <title>{id}</title>
            <circle
              r={16}
              className={cn(
                "fill-brand-100 stroke-brand-600",
                activeNode === id && "animate-pulse-brand"
              )}
              strokeWidth={2}
            />
            <text
              textAnchor="middle"
              dominantBaseline="central"
              className="fill-brand-700 text-[9px] font-semibold select-none"
            >
              {pos.label}
            </text>
          </g>
        ))}
    </svg>
  );
}
