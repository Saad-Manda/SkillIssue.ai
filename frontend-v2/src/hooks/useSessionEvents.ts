import { useEffect, useRef, useState } from "react";
import { API_BASE } from "@/lib/api";
import type { SessionEvent } from "@/types/api";

export const GRAPH_NODES = [
  "user_summarizer",
  "planner",
  "router",
  "question_generator",
  "phase_summarizer",
  "metric_calculator",
  "report_generator",
] as const;
export type GraphNode = (typeof GRAPH_NODES)[number];

const EDGES: [GraphNode, GraphNode][] = [
  ["user_summarizer", "planner"],
  ["planner", "router"],
  ["router", "question_generator"],
  ["router", "report_generator"],
  ["question_generator", "phase_summarizer"],
  ["question_generator", "metric_calculator"],
  ["phase_summarizer", "metric_calculator"],
  ["metric_calculator", "router"],
  ["metric_calculator", "report_generator"],
];
const EDGE_KEYS = new Set(EDGES.map(([from, to]) => `${from}->${to}`));

function isGraphNode(agent: string): agent is GraphNode {
  return (GRAPH_NODES as readonly string[]).includes(agent);
}

export interface PulseTrigger {
  from: GraphNode;
  to: GraphNode;
  key: number;
}

export function useSessionEvents(sessionId: string | undefined) {
  const [events, setEvents] = useState<SessionEvent[]>([]);
  const [visitedNodes, setVisitedNodes] = useState<Set<GraphNode>>(new Set());
  const [visitedEdges, setVisitedEdges] = useState<Set<string>>(new Set());
  const [activeNode, setActiveNode] = useState<GraphNode | null>(null);
  const [pulseTrigger, setPulseTrigger] = useState<PulseTrigger | null>(null);

  const previousNode = useRef<GraphNode | null>(null);
  const pulseCounter = useRef(0);

  useEffect(() => {
    if (!sessionId) return;

    const source = new EventSource(`${API_BASE}/session/${sessionId}/events`);

    source.onmessage = (e) => {
      const evt = JSON.parse(e.data) as SessionEvent;
      setEvents((prev) => [...prev.slice(-199), evt]);

      // ponytail: keying off "start" only — no need to track per-node "done" naming consistency across 7 files
      if (evt.event !== "start" || !isGraphNode(evt.agent)) return;

      setVisitedNodes((prev) =>
        prev.has(evt.agent as GraphNode) ? prev : new Set(prev).add(evt.agent as GraphNode)
      );
      setActiveNode(evt.agent as GraphNode);

      const prevNode = previousNode.current;
      const edgeKey = prevNode ? `${prevNode}->${evt.agent}` : null;
      if (prevNode && edgeKey && EDGE_KEYS.has(edgeKey)) {
        setVisitedEdges((prev) => (prev.has(edgeKey) ? prev : new Set(prev).add(edgeKey)));
        pulseCounter.current += 1;
        setPulseTrigger({ from: prevNode, to: evt.agent as GraphNode, key: pulseCounter.current });
      }
      previousNode.current = evt.agent as GraphNode;
    };

    return () => source.close();
  }, [sessionId]);

  return { events, visitedNodes, visitedEdges, activeNode, pulseTrigger, EDGES };
}
