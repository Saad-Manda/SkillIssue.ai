"use client";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";
import type { METRICS } from "@/lib/constants";

type MetricEntry = {
  metric: string; // short label
  score: number;
  fullMark: number;
};

interface ScoreRadarChartProps {
  scores: Record<string, number | undefined>;
  metrics: typeof METRICS;
}

export function ScoreRadarChart({ scores, metrics }: ScoreRadarChartProps) {
  const data: MetricEntry[] = metrics.map((m) => ({
    metric: m.label,
    score: scores[m.key] ?? 0,
    fullMark: m.maxScore,
  }));

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} margin={{ top: 16, right: 24, bottom: 16, left: 24 }}>
          <PolarGrid stroke="#E8E5DF" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: "#78716C", fontSize: 12, fontWeight: 500 }}
          />
          <Radar
            dataKey="score"
            stroke="#D97706"
            fill="#D97706"
            fillOpacity={0.18}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
