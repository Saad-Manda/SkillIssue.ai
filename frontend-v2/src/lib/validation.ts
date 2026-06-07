import { z } from "zod";

// ── Auth ──────────────────────────────────────────────────────────────
export const loginSchema = z.object({
  email:    z.string().email("Valid email required"),
  password: z.string().min(1, "Password required"),
});

export const signupSchema = z
  .object({
    username: z.string().min(3, "Username must be at least 3 characters").max(30),
    email:    z.string().email("Valid email required"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirm:  z.string(),
  })
  .refine((d) => d.password === d.confirm, {
    message: "Passwords do not match",
    path: ["confirm"],
  });

// ── Profile — Basic Info ──────────────────────────────────────────────
export const basicsSchema = z.object({
  name:         z.string().min(1, "Full name is required"),
  mobile:       z.string().optional(),
  github_url:   z.string().url("Must be a valid URL").optional().or(z.literal("")),
  linkedin_url: z.string().url("Must be a valid URL").optional().or(z.literal("")),
  skills:       z.array(z.string()).min(1, "Add at least one skill"),
});

// ── JD Setup ─────────────────────────────────────────────────────────
export const setupInterviewSchema = z.object({
  job_title:              z.string().min(2, "Job title is required"),
  job_type:               z.enum(["full_time", "part_time"]),
  min_experience:         z.coerce.number().min(0).max(50),
  required_qualification: z.string().min(1, "Required"),
  required_skills:        z.array(z.string()).min(1, "Add at least one skill"),
  responsibilities:       z.string().optional(),
  description:            z.string().optional(),
  interview_length:       z.enum(["short", "medium", "long"]),
});

export type SetupInterviewForm = z.infer<typeof setupInterviewSchema>;
