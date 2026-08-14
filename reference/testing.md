# Testing & Validation Framework Specification: SkillIssue.ai

This document details the test suites, configurations, testing commands, and verification protocols for the SkillIssue.ai platform.

---

## 1. Testing Stack Overview

| Layer | Tooling | Location |
|---|---|---|
| **Backend Unit Tests** | PyTest | `src/tests/` |
| **Backend API Integration** | PyTest + HTTPX `AsyncClient` | `src/tests/` |
| **Agent / LangGraph Tests** | PyTest + mock LLM responses | `src/tests/agents/` |
| **Frontend Unit Tests** | Vitest + React Testing Library | `frontend/src/__tests__/` |
| **Frontend E2E Tests** | Playwright | `frontend/e2e/` |

---

## 2. Backend Unit Tests (PyTest)

### Tooling
- **Framework**: `pytest` with `pytest-asyncio` for async test support.
- **Mocking**: `unittest.mock` / `pytest-mock` for LLM calls, Redis, and DB queries.
- **Coverage**: `pytest-cov` targeting ≥ 80% on `src/controllers/` and `src/agents/`.

### Running

```bash
# From project root, with .venv activated
pytest src/tests/ -v --cov=src --cov-report=term-missing
```

### Key Test Targets

#### Auth Controllers (`src/tests/test_auth.py`)
- `test_signup_success` — valid payload creates user, returns hashed password.
- `test_signup_duplicate_email` — duplicate email raises HTTP 409.
- `test_login_success` — valid credentials return JWT.
- `test_login_invalid_password` — wrong password returns HTTP 401.
- `test_logout_blacklists_token` — token inserted into `Token` table after logout.

#### Session Controllers (`src/tests/test_session.py`)
- `test_start_session_creates_interview_record` — DB row created with correct `user_id` and `jd_id`.
- `test_submit_answer_returns_next_question` — graph resumes and returns a non-empty `current_question`.
- `test_get_report_returns_markdown` — report endpoint returns string containing `#` markdown heading.

#### Agent Unit Tests (`src/tests/test_agents.py`)
- `test_router_probe_case` — mocked LLM returns probe signal → `current_turn_status = "PROBE"`.
- `test_router_topic_change` — after `max_topics` questions, status becomes `"TOPIC_CHANGE"`.
- `test_metric_calculator_scores_range` — all 8 metrics are floats between 0.0 and 1.0.
- `test_planner_generates_valid_plan` — plan contains at least `min_topics` per phase.

---

## 3. Backend Integration / API Tests

### Tooling
- **Client**: `httpx.AsyncClient` with ASGI transport (hits real FastAPI routes without network).
- **Database**: Separate test PostgreSQL database (or SQLite for speed) — configured via `TEST_DATABASE_URL` env var.
- **Redis**: `fakeredis` for in-memory Redis simulation.

### Running

```bash
pytest src/tests/integration/ -v --asyncio-mode=auto
```

### Key Test Targets

#### Full Auth Flow
```
POST /api/v1/auth/signup → 201
POST /api/v1/auth/login  → 200 (token)
POST /api/v1/auth/logout → 200 (token blacklisted)
POST /api/v1/auth/login  → re-login with same credentials → 200 (new token)
```

#### Full Interview Flow
```
POST /api/v1/auth/login                               → token
POST /api/v1/jd                                       → jd_id
GET  /api/v1/session/user/{uid}/jd/{jd_id}/length/short → session_id, opening_question
POST /api/v1/session/{session_id}/answer              → next_question
... (repeat N times)
GET  /api/v1/session/{session_id}/report              → markdown report string
```

---

## 4. Frontend Unit Tests (Vitest)

### Tooling
- **Framework**: `vitest` (bundled with Vite ecosystem).
- **Component Testing**: `@testing-library/react` + `@testing-library/user-event`.
- **Mocking**: `vi.mock` for `api.js` service calls.

### Running

```bash
cd frontend
npm run test
```

### Key Test Targets

#### Auth Pages
- `Login.test.jsx` — form renders, submits payload, redirects on success token.
- `Signup.test.jsx` — validation errors shown on empty fields.

#### Profile Page
- `Profile.test.jsx` — add/remove experience entries mutates form state correctly.
- `Profile.test.jsx` — pre-fill effect populates fields from mocked API response.

#### InterviewSession Page
- `InterviewSession.test.jsx` — question displays in chat canvas after start.
- `InterviewSession.test.jsx` — input is disabled while `isLoading=true`.
- `InterviewSession.test.jsx` — sidebar displays correct `current_phase_name`.

---

## 5. End-to-End (E2E) Tests (Playwright)

### Tooling
- **Framework**: Playwright (`@playwright/test`).
- **Target URL**: `http://localhost:5173` (Vite dev server) + `http://localhost:8000` (FastAPI).
- **Browsers**: Chromium (primary), Firefox (secondary).

### Running

```bash
cd frontend

# Install Playwright browsers (first time only)
npx playwright install

# Run E2E suite
npx playwright test
```

### Key User Flow Tests

#### `auth.spec.ts`
1. Navigate to `/signup` → fill form → submit → redirect to `/login`.
2. Navigate to `/login` → fill credentials → submit → redirect to `/dashboard`.
3. Click logout → redirect to `/login` → token is invalidated.

#### `interview.spec.ts`
1. Login → navigate to `/profile/new` → fill and save profile.
2. Navigate to interview setup → fill JD → click "Start Interview".
3. Verify opening question appears in chat canvas.
4. Type answer → submit → verify next question appears.
5. (After sufficient turns) Verify navigation to `/report/{session_id}`.
6. Verify report page renders markdown content with a heading.

#### `profile.spec.ts`
1. Add an experience entry → save → reload page → verify pre-fill.
2. Remove an experience entry → save → reload → verify entry is gone.

---

## 6. Agent Smoke Tests

Before deploying any change to the agent graph, run a quick smoke test to verify end-to-end graph execution:

```bash
# From project root, with .venv activated
python -m src.tests.smoke_test_graph
```

This script should:
1. Initialize a minimal `SystemState` with a mock user and JD.
2. Run the full graph from `user_summarizer` through to `question_generator`.
3. Assert `current_question` is a non-empty string.
4. Submit a mock answer and resume to `metric_calculator`.
5. Assert all 8 metric keys are present in the output state.

---

## 7. Pre-Commit Verification Gate

Before committing any code, all of the following must pass:

```bash
# 1. Backend: run all tests with coverage
pytest src/tests/ -v --cov=src --cov-fail-under=70

# 2. Frontend: unit tests
cd frontend && npm run test -- --run

# 3. Frontend: linting
cd frontend && npm run lint

# 4. Python: linting (if configured)
ruff check src/

# 5. Agent smoke test
python -m src.tests.smoke_test_graph
```

> [!WARNING]
> Never commit with failing tests or lint errors. The LangGraph graph compilation (`_build_graph()`) should also be validated — if it raises at import time, the entire backend is dead on startup.

---

## 8. Environment Setup for Testing

### Backend Test Environment Variables
Create a `.env.test` file (gitignored) with a test-specific DB and Redis:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/skillissue_test
REDIS_URL=redis://localhost:6379/1
ATLAS_DB_URI=mongodb://localhost:27017
MONGO_DB=skillissue_test
COLLECTION_NAME=agent_logs_test
GOOGLE_API_KEY=<test-key-or-mock>
MODEL=gemini-2.0-flash
SECRET_KEY=test-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRY_MINUTES=30
JWT_API_KEY=test-jwt-api-key
```

### Frontend Test Environment
```env
VITE_API_URL=http://localhost:8000
```
