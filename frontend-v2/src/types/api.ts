// Auth
export interface User {
  id: string;
  email: string;
  username: string;
}

// Profile
export interface Experience {
  experience_id?: string;
  role: string;
  company: string;
  emp_type: "full_time" | "part_time";
  start_date: string;
  end_date?: string;
  loc_type: "onsite" | "remote" | "hybrid";
  location?: string;
  description?: string;
  skills_used: string[];
}

export interface Education {
  education_id?: string;
  institute_name: string;
  degree: string;
  grade: number;
  courses: string[];
  start_date: string;
  end_date?: string;
}

export interface Project {
  project_id?: string;
  title: string;
  description: string;
  skills_used: string[];
  github_url?: string;
  deployed_url?: string;
}

export interface Leadership {
  leadership_id?: string;
  committee_name: string;
  position: string;
  skills_used: string[];
  description?: string;
  start_date: string;
  end_date?: string;
}

export interface UserProfile {
  user_id: string;
  name: string;
  email: string;
  username?: string;
  mobile?: string;
  github_url?: string;
  linkedin_url?: string;
  skills: string[];
  experiences: Experience[];
  educations: Education[];
  projects: Project[];
  leaderships: Leadership[];
}

export type CreateProfilePayload = Omit<UserProfile, "user_id"> & {
  user_id?: string;
  hashed_password?: string;
  is_active?: boolean;
};

// JD
export interface CreateJDPayload {
  job_title: string;
  job_type: "full_time" | "part_time";
  min_experience: number;
  required_skills: string[];
  responsibilities: string[];
  required_qualification: string;
  description?: string;
}

export interface JDResponse extends CreateJDPayload {
  jd_id: string;
}

// Session
export interface SessionStartResponse {
  session_id: string;
  current_question: string;
  current_phase_name: string;
  current_topic_name?: string;
  current_topic_id?: string;
}

export interface AnswerResponse {
  current_question?: string;
  current_phase_name?: string;
  current_topic_name?: string;
  current_topic_id?: string;
  is_complete?: boolean;
}

// Interview History
export interface Interview {
  _id: string;
  session_id: string;
  jd_id: string;
  user_id: string;
  conducted_on: string;
  report?: string;
}

export interface ChatTurn {
  chat_id?: string;
  question: string;
  response: string;
  phase_name?: string;
  topic_id?: string;
  metrics?: {
    relevance_score?: number;
    clarity_score?: number;
    completeness_score?: number;
    technical_depth_score?: number;
    answer_confidence_score?: number;
    star_score?: number;
    feedback?: string;
  };
}

export interface InterviewDetail extends Interview {
  chat_history: ChatTurn[];
}
