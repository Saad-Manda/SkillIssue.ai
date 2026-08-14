# Phase 6 — Staging & Deployment Plan

> **Status: PAUSED — awaiting a new feature to be designed into this plan before execution.**
> Nothing in this plan has been executed yet (no branches merged/deleted, no
> Dockerfile/CI/env files created, no accounts provisioned). Resume by filling
> in the "New Feature (pending design)" section below, then re-confirm the
> plan before starting Execution Order.

## New Feature (pending design)

TBD — the user flagged a new feature to design into this plan before
execution starts, but has not yet described it. Ask what it is at the start
of the next session before doing anything else in this doc.

## Context

This repo has zero deployment infrastructure today: no Dockerfile, no CI/CD, no
`.env.example`, no staging/prod branch mapping, and no deployment documentation
(confirmed by full audit of `src/`, `frontend/`, `frontend-v2/`, and all root docs).
The backend (FastAPI + LangGraph multi-agent) and the active frontend
(`frontend-v2`, Next.js 14) are both feature-complete enough to need a real staging
environment for QA before the eventual production launch described in `PRD.md`.
This plan stands up that staging environment, wires up the deploy path to
production, and adds the documentation scaffold so the process is repeatable
and discoverable (matching the existing `reference/*.md` pattern).

User decisions already made:
- **Backend host:** Render, free tier (accepted cold-starts/90-day Postgres
  expiry tradeoff — see note below on why Postgres itself won't live on Render).
- **Frontend host:** Vercel (native fit for Next.js, not asked — no viable
  alternative given the stack).
- **Datastores:** separate staging instances, isolated from dev data.
- **Branching:** staging deploys from `main` only. Feature branches merge into
  `dev`, `dev` merges into `main`, stale branches get deleted (see Branch
  Consolidation below).

## Audit Summary

**Backend (`src/`)** — FastAPI app (`src/main.py`), started via
`uvicorn src.main:app`. Three datastores: Postgres (SQLAlchemy async/`asyncpg`),
MongoDB Atlas (`motor`), Redis (session state). LLMs: Gemini + Groq via
LangChain/LangGraph. Auth: argon2/passlib/authlib, JWT via `SECRET_KEY`.
Gaps found:
- `alembic` is pinned in `requirements.txt` and documented in `ANTIGRAVITY.md`
  but **never initialized** — no `alembic/` dir. Schema is created by
  `init_db.py`'s one-shot `Base.metadata.create_all()`, which has no migration
  path for schema changes after first deploy.
- CORS origins are **hardcoded** to `localhost:5173`/`3000` in `src/main.py`
  (flagged in `ANTIGRAVITY.md` itself as needing a fix before prod).
- No `.env.example` — 13 required env vars only exist implicitly in
  `src/config.py`'s `Settings` class.
- `pytest` is not in `requirements.txt` despite 6 existing test files in
  `src/tests/`.
- `logs/interviews/*.log` writes unrotated, multi-MB files to local disk —
  fine for Render's ephemeral filesystem short-term, not a long-term store.
- `init_db.py`'s URL-normalization logic (stripping `sslmode`/`channel_binding`)
  is a Neon/Supabase-specific pattern — confirms Postgres is meant to be a
  managed serverless provider, not self-hosted.

**Frontend** — `frontend-v2` (Next.js 14 App Router, TS, Tailwind+shadcn,
zustand, react-query) is the active app, mid-build through "Phase 5 interview
flow," last commit later than legacy `frontend/`. `frontend/` (Vite+React, JS)
has had no commits since `frontend-v2` overtook it — dead weight, not part of
this deploy plan. No `.env.example` in either; `frontend-v2` reads
`NEXT_PUBLIC_API_URL` with a localhost fallback in `src/lib/api.ts`. No CI, no
Vercel config (none needed — Vercel auto-detects Next.js).

**Docs** — `README.md`, `PRD.md`, `ProblemStatement.md`, `ANTIGRAVITY.md`, and
`reference/{architecture,api,database,testing}.md` exist; none cover
deployment.

**Branch audit** (`git fetch --prune` + `git log dev..<branch>` for every
local/remote branch) — most of the ~15 feature/bug branches from `git branch
-a` are already fully merged into `dev` and already deleted on the remote
(GitHub auto-deletes on PR merge); they're just stale local refs. Three
branches carry real unmerged work:
- `origin/groq` — 1 commit, `feat(llm): implement multi-key distribution and
  fallback for Groq/Gemini`.
- `origin/fix/interview-end-condition` — 3 commits, including the same groq
  commit as an ancestor, plus `fix(backend): stop repeating last question and
  expose completion signal` and `feat(frontend): add non-dismissable
  completion modal and auto-navigation to report`. This branch is a strict
  superset of `groq`.
- `frontend` (local) — 1 unique commit, `Deleted DS_Store` — trivial, no real
  work, safe to drop without merging.

Local `main` is also 2 commits behind `origin/main` (needs a fast-forward
pull before anything merges into it). `dev` is 213 commits ahead of `main` —
`main` hasn't been updated since early in the project.

## Environment Topology

| | Local dev | Staging | Production |
|---|---|---|---|
| Branch | any feature branch | `main` | `main` (promotion mechanism TBD — see below) |
| Backend | `uvicorn --reload` on laptop | Render (free web service) | Render (paid, once launched) |
| Frontend | `next dev --turbo` on laptop | Vercel (production branch `main`) | Vercel (same project; promotion TBD) |
| Postgres | existing dev Neon/Supabase DB (current `.env`) | **new** free Neon project `skillissue-staging` | new Neon project, paid tier later |
| MongoDB | existing dev Atlas cluster | **new** free M0 Atlas cluster, db `skillissue_staging` | new Atlas cluster/db |
| Redis | local/existing dev Redis | **new** free Upstash Redis (Render has no free Redis tier) | Upstash paid or Render Key-Value |
| CORS origins | `localhost:5173`/`3000` | staging Vercel URL | prod domain |

Render's own Postgres/Redis add-ons are skipped even on the free plan — Render
free Postgres auto-*expires after 90 days*, and Render has no free Redis at
all. Neon (Postgres) and Upstash (Redis) both have real, non-expiring free
tiers and are the lazier/cheaper fit here.

**Going forward**, feature branches merge into `dev` (integration/code
review), then `dev` merges into `main` (release). Render and Vercel watch
`main` only — that's the single deploy trigger for staging right now.
Production is intentionally left as a separate, later decision: once ready to
actually launch, promote via either a second Render/Vercel environment on a
`release`/tag, or a manual "promote to production" click in each platform's
dashboard — not solved here since it wasn't asked for yet.

## Branch Consolidation

One-time cleanup, done before wiring up Render/Vercel so the first deploy
comes from a clean `main`:

1. `git fetch origin --prune` (already run — remote already auto-deleted
   most merged branch refs; local refs to those are now stale).
2. Fast-forward local `main` to `origin/main` (2 commits behind).
3. Create local tracking branches for the two remote branches with real
   unmerged work and merge each into `dev`:
   - `git checkout -b fix/interview-end-condition origin/fix/interview-end-condition`
     → merge into `dev` (this branch's history already contains the `groq`
     commit, so merging it covers both).
   - `origin/groq` itself becomes redundant once the above merge lands —
     confirm with `git log dev..origin/groq` (should show nothing left), then
     skip merging it separately.
4. Merge `dev` into `main`.
5. Delete stale branches — safe because each is either fully merged into
   `dev`/`main` or (for `frontend`) reviewed and confirmed to carry only a
   trivial, droppable commit:
   - Local: `auth`, `dark`, `diagnosis`, `fastapi`, `fine-tuning`,
     `frontend`, `frontend-v2`, `mongodb`, `planner_done_good`, `refactor`,
     `report_1_bug_2`, `report_2_bug_5`, `report_3_bug_13`, `ui`, `groq`
     (after step 3 confirms it's subsumed).
   - Remote: `origin/groq`, `origin/fix/interview-end-condition` (`git push
     origin --delete <branch>`), plus any other stale `origin/*` refs still
     listed in `git branch -r` beyond `dev`/`main`.
6. Leave `dev` alive as the ongoing integration branch — only the now-merged
   *feature* branches get deleted, not `dev` itself.

## Deliverables

**Backend infra**
- `Dockerfile` (repo root) — `python:3.11-slim`, install `requirements.txt`,
  `CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "$PORT"]`
  (Render sets `$PORT`). `.dockerignore` alongside it.
- `.env.example` (repo root) — every var from `src/config.py`'s `Settings`
  class (`DATABASE_URL`, `REDIS_URL`, `ATLAS_DB_URI`, `MONGO_DB`,
  `COLLECTION_NAME`, `GOOGLE_API_KEY`, `GROQ_API_KEY`, `MODEL`, `SECRET_KEY`,
  `ALGORITHM`, `ACCESS_TOKEN_EXPIRY_MINUTES`, `JWT_API_KEY`, `DEBUG`) plus new
  `ALLOWED_ORIGINS`, with placeholder values and comments.
- `src/main.py` — CORS `origins` list read from `ALLOWED_ORIGINS` env var
  (comma-separated, default to the existing localhost list for backward
  compat in dev) instead of the hardcoded array.
- `requirements-dev.txt` — `pytest`, `pytest-asyncio` (kept separate from
  `requirements.txt` so prod images stay lean; no new dependency manager).
- **Alembic**: `alembic init alembic`, point `alembic/env.py` at
  `Settings.DATABASE_URL` and `Base.metadata` from `src/schemas/base.py`,
  generate one baseline migration via `--autogenerate` against the current
  schema. `init_db.py` stays as-is for local dev bootstrap; staging/prod use
  `alembic upgrade head` as the actual deploy-time schema step.

**Frontend infra**
- `frontend-v2/.env.example` — `NEXT_PUBLIC_API_URL`.
- No Dockerfile/`output: 'standalone'` needed — Vercel builds Next.js
  natively, so skip containerizing the frontend entirely.

**CI** (`.github/workflows/ci.yml`) — runs on PRs into `dev`/`main`:
- Backend job: `pip install -r requirements.txt -r requirements-dev.txt`,
  `pytest src/tests`.
- Frontend job: `npm ci`, `npm run lint`, `npm run build` — scoped to
  `frontend-v2` only (`frontend/` is dead, not built in CI).

No custom **CD** workflow is needed: Render and Vercel both deploy natively
off a connected GitHub branch — both watch `main`. Building a GitHub Actions
deploy job would just duplicate what the platforms already do for free.

**Documentation scaffold**
- New `reference/deployment.md`, matching the existing
  `reference/{architecture,api,database,testing}.md` pattern: environment
  topology table (above), provisioning steps for Neon/Atlas/Upstash/Render/
  Vercel, the env var reference table, the alembic migration workflow, and
  rollback notes (Render/Vercel both support one-click redeploy of a previous
  build).
- `ANTIGRAVITY.md` — add a row to the "On-Demand Context" table pointing to
  `reference/deployment.md`; update the CORS note now that it's fixed.
- `README.md` — short new "Deployment" section linking to
  `reference/deployment.md` (detail lives in the reference doc, matching how
  README already defers to `reference/` for architecture/API/DB).

**Explicitly not doing** (flagged, not actioned, to avoid scope creep beyond
"staging and deployment"):
- Not deleting/archiving legacy `frontend/` or the untracked
  `frontend/src/lib/utils.js` — dead weight but a separate cleanup decision.
- Not fixing the non-HttpOnly `skillissue-authed` cookie auth mirror in
  `frontend-v2/src/middleware.ts` — real security gap before a public prod
  launch with real user data, but orthogonal to standing up staging. Will
  note it prominently in `reference/deployment.md` as a pre-launch blocker.
- Not touching stale `implementation_log.md` beyond one note that it's
  superseded by git log / `.antigravity/plans/` — full rewrite out of scope.

## Execution Order

1. Branch consolidation (above) — merge feature branches → `dev` → `main`,
   delete stale branches, local and remote.
2. `.env.example` (root + `frontend-v2`), `Dockerfile`, `.dockerignore`,
   `requirements-dev.txt`.
3. `src/main.py` CORS env-var fix.
4. Alembic init + baseline migration.
5. `.github/workflows/ci.yml`.
6. `reference/deployment.md` + `ANTIGRAVITY.md`/`README.md` updates.
7. Manual provisioning (done by the user via web consoles — third-party
   accounts can't be created by the agent): Neon staging project, Atlas
   M0 staging cluster, Upstash staging Redis, Render web service watching
   `main`, Vercel project watching the repo with root dir `frontend-v2`,
   production branch `main`.
8. Set staging env vars in Render/Vercel dashboards (secrets — never
   committed), run `alembic upgrade head` once against the fresh staging DB.
9. First staging deploy + smoke test.

## Verification

- `docker build .` succeeds locally; `docker run -p 8000:8000 --env-file .env <image>`
  boots and responds on the existing health-check route
  (`src/routes/routes_health_check.py`).
- `pytest src/tests` passes locally with `requirements-dev.txt` installed.
- `alembic upgrade head` runs clean against a throwaway empty Postgres DB.
- `cd frontend-v2 && npm run build` succeeds.
- End-to-end on the deployed staging URL: sign up, fill profile, start an
  interview session, confirm one Q&A turn round-trips through the LangGraph
  pipeline and hits staging Postgres/Mongo/Redis (not dev).
