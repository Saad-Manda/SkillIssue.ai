// Interview metrics — full name, abbreviation, description
export const METRICS = [
  {
    key: "relevance_score",
    label: "QAR",
    fullName: "Question-Answer Relevance",
    description: "How directly your answer addressed the question asked.",
    maxScore: 10,
  },
  {
    key: "technical_depth_score",
    label: "TDS",
    fullName: "Technical Depth Score",
    description: "Depth and accuracy of technical knowledge demonstrated.",
    maxScore: 10,
  },
  {
    key: "answer_confidence_score",
    label: "ACS",
    fullName: "Answer Confidence Score",
    description: "Confidence and certainty in your responses.",
    maxScore: 10,
  },
  {
    key: "structure_score",
    label: "SS",
    fullName: "Structure Score",
    description: "How well-organized and logical your answer was.",
    maxScore: 10,
  },
  {
    key: "clarity_score",
    label: "CCS",
    fullName: "Clarity & Communication Score",
    description: "Clarity and precision of language used.",
    maxScore: 10,
  },
  {
    key: "completeness_score",
    label: "FARQ",
    fullName: "Full Answer to Requirements Quality",
    description: "Whether your answer fully addressed all parts of the question.",
    maxScore: 10,
  },
  {
    key: "rfd_score",
    label: "RFD",
    fullName: "Resume-to-Fact Discrepancy",
    description: "Consistency between your resume claims and live answers.",
    maxScore: 10,
  },
  {
    key: "star_score",
    label: "STAR",
    fullName: "STAR Framework Adherence",
    description: "How well you used Situation-Task-Action-Result structure.",
    maxScore: 10,
  },
] as const;

export type MetricKey = typeof METRICS[number]["key"];

// Interview length options
export const INTERVIEW_LENGTHS = [
  {
    value: "short" as const,
    label: "Short",
    duration: "~15 min",
    questions: "8–10 questions",
    description: "Quick assessment — great for warm-up sessions.",
  },
  {
    value: "medium" as const,
    label: "Medium",
    duration: "~30 min",
    questions: "15–20 questions",
    description: "Standard depth — mimics a typical first round.",
  },
  {
    value: "long" as const,
    label: "Long",
    duration: "~45 min",
    questions: "25–30 questions",
    description: "Deep dive — full technical and behavioral coverage.",
  },
] as const;

export type InterviewLength = "short" | "medium" | "long";

// Employment types
export const EMP_TYPE_LABELS: Record<string, string> = {
  full_time: "Full-time",
  part_time: "Part-time",
};

// Location types
export const LOC_TYPE_LABELS: Record<string, string> = {
  onsite: "On-site",
  remote: "Remote",
  hybrid: "Hybrid",
};
