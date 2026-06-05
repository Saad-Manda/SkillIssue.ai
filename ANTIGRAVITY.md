# ANTIGRAVITY.md

This file provides guidance to the Antigravity agent when working with code in this repository.

## Project Overview

SkillIssue.ai is an AI-powered mock interviewer platform. It conducts adaptive, context-aware interview sessions by synthesizing a candidate's structured profile (Resume — Experience, Education, Projects, Leadership) against a specific Job Description. The backend is a FastAPI application that drives a 7-node LangGraph multi-agent orchestration graph. The graph dynamically plans, executes, evaluates, and reports on the interview using Google Gemini as the LLM. The frontend is a React + Vite SPA. Session state is split between LangGraph's `MemorySaver` (lightweight in-graph state) and Redis (heavy chat history and phase summaries). PostgreSQL handles all persistent relational data; MongoDB is used for agent event logs.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Backend runtime |
| **FastAPI 0.128.2** | REST API framework — all routes under `/api/v1/` |
| **LangGraph 1.0.4** | Multi-agent graph orchestration with human-in-the-loop interrupt |
| **LangChain + Google Gemini** | LLM integration (`langchain-google-genai`) |
| **SQLAlchemy (async)** | ORM for PostgreSQL — Users, JDs, Sessions, Profiles, Tokens |
| **Alembic** | Database migration management |
| **Redis** | Session state store — `chat_history` and `phasewise_summary` |
| **MongoDB (Motor)** | Async agent event logging |
| **Argon2 + JWT** | Password hashing and Bearer token auth |
| **React + Vite** | Frontend SPA — served on port 5173 in dev |
| **react-router-dom** | Client-side routing |
| **react-markdown** | Renders the AI-generated Interview Readiness Report |
| **Gradio** | Alternative dev/demo UI — served on port 7860 |
| **Uvicorn** | ASGI server for FastAPI — port 8000 |
| **Pydantic v2** | Data validation, settings management, and state models |

---

## Commands

```bash
# ── Backend ──────────────────────────────────────────────────

# Start FastAPI dev server (hot reload)
uvicorn src.main:app --reload
# API: http://localhost:8000
# Swagger UI: http://localhost:8000/docs

# Start Gradio UI (alternative interface)
python -m src.gradio
# UI: http://localhost:7860

# Run database migrations
alembic upgrade head

# Generate a new migration after model changes
alembic revision --autogenerate -m "description_of_change"

# Run backend tests
pytest src/tests/ -v --cov=src --cov-report=term-missing

# ── Frontend ─────────────────────────────────────────────────

# Install dependencies (first time)
cd frontend && npm install

# Start Vite dev server
cd frontend && npm run dev
# UI: http://localhost:5173

# Build production bundle
cd frontend && npm run build

# Run frontend unit tests
cd frontend && npm run test

# Lint frontend
cd frontend && npm run lint
```

---

## Project Structure

```
SkillIssue.ai/
├── src/                          # Python FastAPI backend
│   ├── main.py                   # App entry point — CORS, router registration
│   ├── gradio.py                 # Gradio alternative UI
│   ├── config.py                 # Pydantic Settings — reads .env
│   ├── database.py               # SQLAlchemy async engine + Motor MongoDB client
│   ├── agents/                   # LangGraph agent nodes
│   │   ├── orchestrator.py       # Graph builder (nodes, edges, conditional routing)
│   │   ├── llm.py                # Gemini LLM client singleton
│   │   ├── session_logging.py    # MongoDB agent event logger
│   │   ├── user_summarizer/      # Agent: summarize candidate profile
│   │   ├── planner/              # Agent: generate phase/topic interview plan
│   │   ├── router/               # Agent: 3-case routing (PROBE / INDEPENDENT / TOPIC_CHANGE)
│   │   ├── question_generator/   # Agent: craft contextual questions
│   │   ├── phase_summarizer/     # Agent: rolling phase summaries
│   │   ├── metric_calculator/    # Agent: score 8 metrics per turn
│   │   └── report_generator/     # Agent: compile final Markdown report
│   ├── controllers/              # Business logic per domain (auth, session, user, jd)
│   ├── routes/                   # FastAPI routers
│   │   ├── routes_auth.py        # /api/v1/auth/*
│   │   ├── routes_user.py        # /api/v1/users/*
│   │   ├── routes_jd.py          # /api/v1/jd/*
│   │   ├── routes_session.py     # /api/v1/session/*
│   │   ├── routes_interview.py   # /api/v1/interview/*
│   │   └── routes_health_check.py
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── user_model.py
│   │   ├── jd_model.py
│   │   ├── interview_model.py
│   │   ├── plan_model.py
│   │   ├── experience_model.py / education_model.py / project_model.py / leadership_model.py
│   │   ├── token_model.py        # JWT blacklist table
│   │   └── states/               # In-session state models (SystemState, SessionState, Turn, Metrics)
│   └── schemas/                  # Pydantic request/response schemas
├── frontend/                     # React + Vite SPA
│   └── src/
│       ├── App.jsx               # Root router + AppLayout wrapper
│       ├── index.css             # Global design tokens (Jost font, Minimalist White theme)
│       ├── pages/                # auth/, dashboard/, profile/, interview/
│       ├── components/           # layout/ (Navbar), ui/ (Input, Button, Card)
│       ├── context/              # AuthContext.jsx — global token/user state
│       └── services/             # api.js — all calls to FastAPI backend
├── reference/                    # Architecture, API, DB, and Testing reference docs
├── PRD.md                        # Product Requirements Document (source of truth)
├── requirements.txt              # Python dependencies
└── .env                          # Environment variables (never commit)
```

---

## Architecture

The system uses a **layered + multi-agent** architecture:

1. **API Layer** (FastAPI routes) → **Controller Layer** (business logic) → **Agent Layer** (LangGraph graph) → **Storage Layer** (PostgreSQL + Redis + MongoDB).

2. **LangGraph Graph** (`src/agents/orchestrator.py`): A `StateGraph` of 7 nodes compiled once at startup. The graph uses `interrupt_before=[phase_summarizer]` — it pauses after generating a question, returns it to the frontend, then resumes when the user submits an answer. This is the core human-in-the-loop (HITL) mechanism.

3. **Dual-State Architecture**: Session state is deliberately split:
   - `SystemState` (Pydantic) — lightweight, propagated through every graph node, stored in `MemorySaver` keyed by `thread_id = session_id`.
   - `SessionState` (Redis) — heavy, append-only `chat_history` and `phasewise_summary` lists, stored in Redis under `session:{session_id}`.

4. **Graph Flow**:
   ```
   user_summarizer → planner → router → question_generator
       ↑                                      ↓ [INTERRUPT]
       └── router ← metric_calculator ← phase_summarizer
                          ↓ (when complete)
                    report_generator → END
   ```

---

## Code Patterns

### Naming Conventions
- **Python files**: `snake_case` (e.g., `routes_session.py`, `user_model.py`)
- **Agent directories**: named after their role (e.g., `planner/`, `router/`, `metric_calculator/`)
- **Each agent directory** contains an `agent.py` file with the node function (e.g., `planner_node`, `router_node`)
- **Routes**: prefixed with `routes_` (e.g., `routes_auth.py`)
- **Frontend components**: `PascalCase.jsx` (e.g., `InterviewSession.jsx`)
- **Frontend services**: `camelCase.js` (e.g., `api.js`)
- **React pages**: grouped in subdirectories by feature (e.g., `pages/interview/`, `pages/auth/`)

### File Organization
- Each agent is a self-contained directory with its own `agent.py` — never mix agent logic into the orchestrator.
- Controllers are separated from routes — routes only parse HTTP, controllers hold business logic.
- All Pydantic state models live in `src/models/states/` — do not define state inline in agent files.
- Frontend API calls are centralized in `services/api.js` — components never call `fetch` directly.

### Error Handling
- Route handlers wrap controller calls in `try/except` and raise `HTTPException` with appropriate status codes.
- Log all exceptions with `logger.exception(...)` before re-raising.
- Agent nodes should not silently swallow errors — let them propagate to the orchestrator.
- Never expose raw exception messages to the frontend in production.

### State Mutation
- `SystemState` is immutable per-node — nodes return a new partial state dict, LangGraph merges it.
- Redis session state is mutated via `session_store.update(session_id, {...})` — always fetch first with `session_store.get()`.

---

## Testing

- **Run backend tests**: `pytest src/tests/ -v`
- **Run frontend tests**: `cd frontend && npm run test`
- **Test location (backend)**: `src/tests/`
- **Pattern**: PyTest for backend (unit + async integration via `httpx.AsyncClient`), Vitest + React Testing Library for frontend components, Playwright for E2E flows.
- Mock all LLM calls in unit tests — never make real Gemini API calls in the test suite.

---

## Validation

```bash
# Before committing — run all of these and ensure they pass:

# 1. Backend tests with coverage
pytest src/tests/ -v --cov=src --cov-fail-under=70

# 2. Frontend unit tests
cd frontend && npm run test -- --run

# 3. Frontend lint
cd frontend && npm run lint

# 4. Verify the LangGraph graph compiles (catches import/config errors)
python -c "from src.agents.orchestrator import _build_graph; _build_graph(); print('Graph OK')"
```

---

## Key Files

| File | Purpose |
|---|---|
| `src/main.py` | FastAPI app entry — CORS config, all router registrations |
| `src/config.py` | All env vars via Pydantic Settings — touch this to add new config |
| `src/database.py` | SQLAlchemy async engine + MongoDB Motor client setup |
| `src/agents/orchestrator.py` | LangGraph graph definition — nodes, edges, interrupt config |
| `src/agents/llm.py` | Gemini LLM client singleton — shared by all agent nodes |
| `src/models/states/states.py` | `SystemState` and `SessionState` model definitions |
| `src/models/states/redis_session.py` | `RedisSessionStore` — get/set/update session state |
| `src/models/states/state_init.py` | Factory for initialising `SystemState` at session start |
| `src/routes/routes_session.py` | The 3 core interview interaction endpoints (start, answer, report) |
| `src/agents/session_logging.py` | MongoDB logger — call `log_agent_event()` from any agent node |
| `frontend/src/services/api.js` | All frontend↔backend API calls — add new endpoints here |
| `frontend/src/context/AuthContext.jsx` | Global auth state (token, user) — used by all pages |
| `frontend/src/App.jsx` | React Router config — add new routes here |
| `frontend/src/index.css` | Design tokens (Jost font, Minimalist White palette, shadows) |
| `.env` | Environment variables — see `src/config.py` for all required keys |
| `requirements.txt` | Python dependencies — pin versions when adding new packages |

---

## On-Demand Context

| Topic | File |
|---|---|
| Full product requirements & phased roadmap | `PRD.md` |
| System architecture, data flow diagrams, LangGraph graph | `reference/architecture.md` |
| All API endpoints, payloads, and response schemas | `reference/api.md` |
| Database models, ERD, Redis/MongoDB schemas, indexes | `reference/database.md` |
| Testing strategy, test targets, pre-commit gate | `reference/testing.md` |
| Original problem statement & phase definitions | `ProblemStatement.md` |
| Chronological build log | `implementation_log.md` |

---

## Notes

- **Never commit `.env`** — it contains live API keys (Gemini, Groq, MongoDB Atlas, JWT secret).
- **Graph is compiled once at startup** in `orchestrator.py`. If `_build_graph()` fails (import error, config missing), the entire backend is dead. Always validate after agent changes.
- **`thread_id = session_id`** is the LangGraph checkpoint key. Every `graph.invoke()` and `graph.get_state()` call must pass `config={"configurable": {"thread_id": session_id}}`.
- **Interview length** (`short` / `medium` / `long`) controls `min_topics` and `max_topics` in `SystemState`, which the planner uses to size the interview. Map these values in `state_init.py`.
- **`should_generate_report`** is the signal that terminates the interview loop. It is set by `metric_calculator` when all phases are exhausted. Do not set it anywhere else.
- **Redis keys** follow the pattern `session:{session_id}`. If you need to debug a live session, you can inspect it with `redis-cli GET session:<id>`.
- **CORS** is currently restricted to `http://localhost:5173` only. Update `origins` in `src/main.py` when deploying to production.
- **Alembic migrations** must be run before starting the backend if models have changed: `alembic upgrade head`.
- **Frontend design system**: All styling uses the "Minimalist White" theme defined in `frontend/src/index.css` using `Jost` typography. Do not introduce inline styles or ad-hoc Tailwind classes — extend the design tokens in `index.css`.
