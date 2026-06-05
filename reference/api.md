# API Reference Specifications: SkillIssue.ai

This document details the interface contracts, REST endpoints, payload schemas, and response formats for the SkillIssue.ai FastAPI backend.

---

## 1. Global API Standards

### A. Base URL
- **Development**: `http://localhost:8000`
- **Interactive Docs (Swagger UI)**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### B. HTTP Headers

| Header | Required | Value |
|---|---|---|
| `Content-Type` | Yes (on POST/PUT) | `application/json` |
| `Authorization` | Yes (authenticated routes) | `Bearer <jwt_token>` |

### C. Response Conventions
Responses are direct Pydantic model serializations (FastAPI default). There is no global envelope wrapper — each endpoint returns its own schema directly.

#### Auth Error (HTTP 401)
```json
{ "detail": "Invalid authorization header" }
```

#### Server Error (HTTP 500)
```json
{ "detail": "Internal server error: <exception message>" }
```

---

## 2. Authentication API (`/api/v1/auth`)

### `POST /api/v1/auth/signup`
Registers a new user account.

**Request Payload** (`SignupRequest`):
```json
{
  "email": "user@example.com",
  "username": "saad_manda",
  "password": "securePassword123"
}
```

**Response** (`SignupResponse`, HTTP 201):
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "username": "saad_manda"
}
```

**Error**: HTTP 500 on duplicate email or DB failure.

---

### `POST /api/v1/auth/login`
Authenticates user credentials and returns a JWT access token.

**Request Payload** (`LoginRequest`):
```json
{
  "email": "user@example.com",
  "username": "saad_manda",
  "password": "securePassword123"
}
```

**Response** (`LoginResponse`, HTTP 200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error**: HTTP 401 on invalid credentials, HTTP 500 on server failure.

---

### `POST /api/v1/auth/logout`
Revokes the current JWT by adding it to the token blacklist.

**Headers**: `Authorization: Bearer <token>` (passed as request header, not body)

**Response** (HTTP 200):
```json
{ "message": "Logged out successfully" }
```

**Error**: HTTP 401 if `Authorization` header is missing or malformed.

---

## 3. User Profile API (`/api/v1/users`)

### `GET /api/v1/users/{user_id}`
Fetches the full profile for a user, including nested experience, education, projects, and leadership.

**Path Parameters**: `user_id` (string, UUID)

**Response** (HTTP 200): Full `User` object with nested arrays.
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "username": "saad_manda",
  "name": "Saad Manda",
  "mobile": "+923001234567",
  "github": "https://github.com/saad",
  "linkedin": "https://linkedin.com/in/saad",
  "top_skills": ["Python", "FastAPI", "LangGraph"],
  "experiences": [
    {
      "company": "Tech Corp",
      "role": "Backend Engineer",
      "start_date": "2023-01",
      "end_date": "2024-06",
      "description": "Built microservices..."
    }
  ],
  "educations": [...],
  "projects": [...],
  "leaderships": [...]
}
```

---

### `PUT /api/v1/users/{user_id}`
Updates the user's profile. Handles nested array replacement.

**Path Parameters**: `user_id` (string, UUID)

**Request Payload**: Same schema as GET response (full profile object).

**Response** (HTTP 200): Updated `User` object.

---

## 4. Job Description API (`/api/v1/jd`)

### `POST /api/v1/jd`
Creates a new Job Description record linked to a user.

**Request Payload**:
```json
{
  "user_id": "user-uuid",
  "title": "Senior Python Developer",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Redis"],
  "responsibilities": "Design and maintain backend microservices..."
}
```

**Response** (HTTP 201):
```json
{
  "id": "jd-uuid",
  "user_id": "user-uuid",
  "title": "Senior Python Developer",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Redis"],
  "responsibilities": "Design and maintain backend microservices..."
}
```

---

### `GET /api/v1/jd/user/{user_id}`
Lists all Job Descriptions created by a specific user.

**Path Parameters**: `user_id` (string, UUID)

**Response** (HTTP 200): Array of `JobDescription` objects.

---

### `GET /api/v1/jd/{jd_id}`
Fetches a single Job Description by its ID.

**Path Parameters**: `jd_id` (string, UUID)

**Response** (HTTP 200): Single `JobDescription` object.

---

## 5. Session API (`/api/v1/session`)

The Session API drives the live interview interaction. It wraps the LangGraph orchestrator.

### `GET /api/v1/session/user/{user_id}/jd/{jd_id}/length/{interview_length}`
Initializes a new interview session. This triggers the `user_summarizer` → `planner` → `router` → `question_generator` pipeline and returns the opening question.

**Path Parameters**:
- `user_id` (string, UUID)
- `jd_id` (string, UUID)
- `interview_length` (string): `"short"` | `"medium"` | `"long"`

**Response** (HTTP 200):
```json
{
  "session_id": "session-uuid",
  "current_question": "Walk me through your experience designing REST APIs with FastAPI...",
  "current_phase_name": "Technical",
  "current_topic_id": "topic-uuid-001",
  "current_topic_name": "API Design & FastAPI",
  "chat": []
}
```

---

### `POST /api/v1/session/{session_id}/answer`
Submits the candidate's answer for the current question. Resumes the LangGraph from `phase_summarizer`, runs `metric_calculator`, routes to the next question.

**Path Parameters**: `session_id` (string, UUID)

**Request Payload**:
```json
{
  "answer": "I have designed REST APIs using FastAPI for 2 years. I particularly focus on..."
}
```

**Response** (HTTP 200):
```json
{
  "session_id": "session-uuid",
  "current_question": "You mentioned using dependency injection — can you walk me through a specific case where it saved you from a bug?",
  "current_phase_name": "Technical",
  "current_topic_id": "topic-uuid-001",
  "current_topic_name": "API Design & FastAPI",
  "turn_count": 3,
  "store_count": 3,
  "chat": [
    {
      "question": "Walk me through your experience...",
      "answer": "I have designed REST APIs...",
      "metrics": {
        "QAR": 0.85,
        "TDS": 0.72,
        "ACS": 0.80,
        "SS": 0.68,
        "CCS": 0.75,
        "FARQ": 0.90,
        "RFD": 0.0,
        "STAR": 0.60
      }
    }
  ]
}
```

> [!NOTE]
> When the interview is complete (`should_generate_report = true`), the `current_question` field will be empty and the `report_generator` node will have been triggered automatically. Fetch the report via the endpoint below.

---

### `GET /api/v1/session/{session_id}/report`
Fetches the final Interview Readiness Report for a completed session.

**Path Parameters**: `session_id` (string, UUID)

**Response** (HTTP 200):
```json
{
  "report": "# Interview Readiness Report\n\n## Executive Summary\n...\n\n## Metric Breakdown\n...\n\n## Key Strengths\n...\n\n## Areas for Improvement\n...\n\n## Hiring Recommendation\n**Conditional Yes** — Strong technical foundation but needs to improve specificity in behavioral answers."
}
```

---

## 6. Interview API (`/api/v1/interview`)

### `GET /api/v1/interview/{session_id}`
Fetches metadata and status for a completed or in-progress interview session.

**Path Parameters**: `session_id` (string, UUID)

**Response** (HTTP 200): Interview metadata including session status, turn count, and phase progression.

---

## 7. Health Check API

### `GET /api/v1/health`
Returns the server health status and DB connectivity check.

**Response** (HTTP 200):
```json
{ "status": "ok", "db_connected": true }
```

---

## 8. Metrics Reference

Each turn in the `chat` array includes a `metrics` object with the following 8 dimensions, all scored 0.0–1.0:

| Key | Full Name | Description |
|---|---|---|
| `QAR` | Question Answer Relevance | Semantic relevance of the answer to the specific question. |
| `TDS` | Topical Depth Score | Causal reasoning, concrete examples, quantified details. |
| `ACS` | Answer Completeness Score | On-topic consistency and sufficient response length. |
| `SS` | Specificity Score | Usage of concrete technologies, tools, numeric data. |
| `CCS` | Confidence Clarity Score | Direct, action-oriented language; penalizes hedging. |
| `FARQ` | Factual Accuracy & Reasoning | LLM-judged technical correctness and logical soundness. |
| `RFD` | Red Flag Detector | Blame-shifting, contradictions, or question avoidance (higher = more red flags). |
| `STAR` | STAR Method Tracking | Adherence to Situation-Task-Action-Result structure. |
