# GradeLens

GradeLens is a FastAPI + Next.js rubric evaluation platform. Teachers author classes and assignments, students submit work, deterministic MCQs and optional Groq drafts are reviewed by teachers, and only released results are visible to students.

## Quickstart

Set `DATABASE_URL` and a 32+ character `JWT_SECRET` or `SESSION_SECRET` in the workspace Secrets panel. Then:

```powershell
npm install
npm run dev
```

Backend checks:

```powershell
cd backend
alembic upgrade head
pytest -q
```

The browser uses the shared `/api` proxy to `127.0.0.1:8000`. Start the API separately when using the frontend:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

Then start Next.js from `frontend` (`npm install; npm run dev`) or use the root scripts if configured. Feature routers are loaded defensively, while auth and `/health` remain available if an optional integration is unavailable.

## Demo data

Development only: `python scripts/seed.py` creates `teacher@gradelens.com` and `student@gradelens.com`, both using `DemoOnly-ChangeMe-123!` by default, plus class code `DEMO11` and a sample assignment. Set `DEMO_PASSWORD` for local demonstrations; never use demo credentials in production.

## Security and release policy

All protected endpoints require an access JWT and enforce role plus ownership. Students receive enrolled assignments and minimal submission status metadata while work is pending; result content, scores, feedback, and AI fields are excluded until teacher approval. Reports are released-only. Uploads are PDF magic-byte checked, limited to 10 MB, and stored with random names. Deadlines and one-submission-per-assignment are enforced server-side. JWT transport supports Authorization, X-Auth-Token, X-Access-Token, and a preview query fallback; production should replace localStorage with an httpOnly cookie session.

Groq is optional (`GROQ_API_KEY`, `GROQ_MODEL`). Written grading validates JSON, retries once, rate-limits briefly on 429, and flags invalid output for manual review. Teacher approval is required before release.

See `docs/PROJECT_STATUS.md`, `docs/ARCHITECTURE.md`, `docs/SPEC.md`, and `AI_DISCLOSURE.md` for verification notes.

## Phase 11 verification

The hardening pass keeps optional routers from blocking startup, validates access-token scopes, distinguishes missing/invalid users, adds safe response headers and request IDs, rate-limits password and 2FA failures, and checks role/ownership and release boundaries. Run the backend suite and manually verify the journey: register teacher/student, create class and assignment, enroll, submit before deadline, review, release, and download the report. Groq is opt-in and must never be exposed to the browser. The in-memory limiters are per-process and must be replaced with shared infrastructure for multi-instance deployments.

## Phase 11 sign-off

Hardening is verification-only: startup keeps auth and health available when an optional router fails, request IDs and safe headers aid incident tracing, and role/ownership plus release boundaries are enforced in backend dependencies and queries. Login and 2FA failures are limited in-process by email/IP or temporary-token buckets. This limiter is intentionally not distributed; deploy a shared limiter before scaling horizontally.

Run `npm run test:backend` after configuring PostgreSQL. The full journey should be exercised with a teacher and student: register, enable TOTP, create/join a class, create an assignment, submit before the deadline, review/release, then download the released report. Live Groq calls are opt-in and must be mocked in default tests.

## Deployment checklist

Before production, run `cd backend; alembic upgrade head; pytest -q`, use a strong unique JWT/SESSION secret, set an exact HTTPS `FRONTEND_URL` (do not use preview CORS), terminate TLS, and put uploads in private object storage. Configure external rate limiting, database backups, log aggregation, and alerting. Never enable demo credentials or expose `GROQ_API_KEY` to the browser. The health endpoint intentionally reports only `ok`/`error`, not database internals.

## Observability and production handoff
Startup logs identify unavailable optional routers without exposing exception details to clients. `/health` returns a deliberately minimal database status. Before deployment, run the migration and test commands, configure HTTPS and exact CORS, enable external rate limiting/log aggregation, and use private object storage for uploads.

The demo seed is intentionally not production data. The complete journey is verified by API boundaries (ownership, role, deadline, one submission, approval, and released-only reports); a live Groq run requires `GROQ_API_KEY` and is opt-in.
