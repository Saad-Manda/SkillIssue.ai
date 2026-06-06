import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow } from "date-fns";

// ── Tailwind class merger ───────────────────────────────────────────
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ── Date formatting ────────────────────────────────────────────────
export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "Present";
  try {
    return format(new Date(dateStr), "MMM yyyy");
  } catch {
    return dateStr;
  }
}

export function formatDateFull(dateStr?: string | null): string {
  if (!dateStr) return "";
  try {
    return format(new Date(dateStr), "d MMM yyyy, h:mm a");
  } catch {
    return dateStr;
  }
}

export function timeAgo(dateStr?: string | null): string {
  if (!dateStr) return "";
  try {
    return formatDistanceToNow(new Date(dateStr), { addSuffix: true });
  } catch {
    return dateStr;
  }
}

// ── Score helpers ──────────────────────────────────────────────────
export function getScoreColor(score: number): string {
  if (score >= 8)  return "text-success";
  if (score >= 6)  return "text-warning";
  if (score >= 4)  return "text-orange-500";
  return "text-error";
}

export function getScoreBg(score: number): string {
  if (score >= 8)  return "bg-success/10 border-success/20";
  if (score >= 6)  return "bg-warning/10 border-warning/20";
  if (score >= 4)  return "bg-orange-50   border-orange-200";
  return "bg-error/10 border-error/20";
}

export function getScoreLabel(score: number): string {
  if (score >= 8)  return "Excellent";
  if (score >= 6)  return "Good";
  if (score >= 4)  return "Average";
  return "Needs Work";
}

// ── String helpers ─────────────────────────────────────────────────
export function getInitials(name?: string | null): string {
  if (!name) return "?";
  return name
    .split(" ")
    .slice(0, 2)
    .map((n) => n[0]?.toUpperCase() ?? "")
    .join("");
}

export function truncate(str: string, maxLen: number): string {
  return str.length > maxLen ? `${str.slice(0, maxLen)}…` : str;
}

// ── Local date input helper ────────────────────────────────────────
export function toDateInput(value?: string | null): string {
  return typeof value === "string" ? value.split("T")[0] : "";
}
