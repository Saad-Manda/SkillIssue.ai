import {
  UserProfile,
  CreateProfilePayload,
  CreateJDPayload,
  JDResponse,
  SessionStartResponse,
  AnswerResponse,
  Interview,
  InterviewDetail,
} from "../types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options?: RequestInit,
  token?: string | null
): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options?.headers,
  };

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new ApiError(res.status, err.detail ?? "Request failed");
  }

  // Handle 204 No Content
  if (res.status === 204) return {} as T;
  return res.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────────────
export const authApi = {
  signup: (data: { username: string; email: string; password: string }) =>
    request<{ signup_token: string }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (data: { username_or_email: string; password: string }) =>
    request<{ access_token: string; user_id: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  logout: (token: string) =>
    request<void>("/auth/logout", { method: "POST" }, token),
};

// ── Users / Profile ───────────────────────────────────────────────────
export const usersApi = {
  getProfile: (userId: string, token: string) =>
    request<UserProfile>(`/users/${userId}`, {}, token),

  createProfile: (data: CreateProfilePayload, signupToken: string) =>
    request<UserProfile>(`/users/?signup_token=${signupToken}`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateProfile: (userId: string, data: Partial<CreateProfilePayload>, token: string) =>
    request<UserProfile>(`/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }, token),
};

// ── Job Descriptions ──────────────────────────────────────────────────
export const jdApi = {
  create: (data: CreateJDPayload) =>
    request<{ jd_id: string }>("/jd/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  get: (jdId: string) =>
    request<JDResponse>(`/jd/${jdId}`),
};

// ── Sessions / Interview ──────────────────────────────────────────────
export const sessionApi = {
  start: (userId: string, jdId: string, length: "short" | "medium" | "long") =>
    request<SessionStartResponse>(
      `/session/user/${userId}/jd/${jdId}/length/${length}`
    ),

  submitAnswer: (sessionId: string, answer: string) =>
    request<AnswerResponse>(`/session/${sessionId}/answer`, {
      method: "POST",
      body: JSON.stringify({ answer }),
    }),

  getReport: (sessionId: string) =>
    request<{ report: string }>(`/session/${sessionId}/report`),
};

// ── Interview History ─────────────────────────────────────────────────
export const interviewApi = {
  getAll: (userId: string) =>
    request<Interview[]>(`/interview/${userId}`),

  getDetails: (userId: string, interviewId: string) =>
    request<InterviewDetail>(`/interview/${userId}/${interviewId}`),

  delete: (interviewId: string) =>
    request<void>(`/interview/${interviewId}`, { method: "DELETE" }),
};
