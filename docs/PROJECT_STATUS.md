# GradeLens Project Status

## 1. Project overview

GradeLens is intended to help university teachers evaluate rubric-based student work. The repository currently contains the authentication and core data foundation; grading, OCR, reports, and analytics are not implemented. The stack is FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Next.js 14, React 18, Tailwind, JWT, bcrypt/passlib, and pyotp. Groq and PDF tooling are configuration placeholders for later phases.

## 2. Current status

| Phase | Status | Missing |
|---|---|---|
| 0 Skeleton | Done | None known |
| 1 DB + auth + 2FA | Done | Live preview verification unverified |
| 2 Classes | Not started | Class API/UI |
| 3 Assignments | Not started | Assignment/rubric API/UI |
| 4 Submissions | Not started | Upload and submission flow |
| 5 AI grading | Not started | Groq evaluation |
| 6 Review/approval | Not started | Teacher review workflow |
| 7 PDF report | Not started | Report generation |
| 8 Analytics | Not started | Analytics views |
| 9 OCR | Not started | OCR pipeline |
| 10 Hardening | Not started | Production hardening |

## 3. What has been built

### Backend

`GET /health` runs `SELECT 1`. Auth routes are defined in `backend/app/routers/auth.py`: registration and login, 2FA setup/verify/login, and `GET /auth/me`. Registration/login are public; setup, verify, and me require an access JWT. Role guards are implemented in `deps.py`, though no class/business routes currently use them.

### Frontend

The root Next app has landing, login, register, security, student, and teacher routes. The parallel `frontend/src/app` tree contains the same auth/dashboard pages and shared auth components. The browser API wrapper uses `/api` when `NEXT_PUBLIC_API_URL` is empty and sends both Authorization and X-Auth-Token.

### Database

The live schema inspection showed `users`, `classes`, `enrollments`, `assignments`, `questions`, `submissions`, `answers`, `feedback_reports`, and `alembic_version`. Users include TOTP fields; email and class join code are unique, enrollment is unique per student/class, and feedback reports are unique per submission. Platform SQL migrations are in `db/migrations/`; the canonical initial migration seeds Alembic revision `000000000001`. The backend equivalent is `backend/alembic/versions/20250610_initial_core_tables.py`.

### Auth and tests

JWTs use HS256, include `sub`, role, and scope, and reject non-access scopes for normal routes. Passwords use passlib bcrypt with `bcrypt==4.0.1`. TOTP uses pyotp and QR code generation. Tests are under `backend/tests` and run with `cd backend; pytest -q`.

## 4. Architecture and preview

The root scripts run FastAPI on port 8000 and Next.js on the preview-selected port. Next rewrites `/api/*` to FastAPI. Backend startup runs `alembic upgrade head`; the platform migration creates the tables first and seeds the matching revision, avoiding duplicate creation.

## 5. Environment variables

| Variable | Purpose | Required | Set in |
|---|---|---|---|
| DATABASE_URL | PostgreSQL connection | Yes | Secrets / backend env |
| JWT_SECRET | JWT signing, with SESSION_SECRET fallback | One of JWT_SECRET/SESSION_SECRET | Secrets |
| SESSION_SECRET | JWT fallback | See above | Secrets |
| FRONTEND_URL | CORS origin | No | backend env |
| PREVIEW_MODE | Dynamic CORS | No | backend env |
| GROQ_API_KEY, GROQ_MODEL | Future AI | No currently | Secrets/env |
| OCR_ENABLED | Future OCR flag | No | backend env |
| NEXT_PUBLIC_API_URL | Optional API base; empty uses proxy | No | frontend env |

## 6. Known problems and open issues

Live register/login and a fresh preview traceback are **unverified** in this workspace. The database schema is present according to inspection. The earlier auth transport issue is addressed by forwarding Authorization and X-Auth-Token and accepting either header. The root app includes teacher/student routes; whether a deployed URL returns 404 is unverified. No current `NEXT_PUBLIC_API_URL` warning was reproduced. The previously mentioned Alembic sync migration exists; its deployed application status is unverified.

## 7. How to run and verify

Set secrets, run `npm install`, then `npm run dev`. Run backend tests with `cd backend; pytest -q`. Register through `/register`, sign in through `/login`, configure TOTP through `/security`, test role redirection, refresh, and sign out. Confirm persistence with `SELECT id,email,role FROM users` using the configured database client.

## 8. Repo guide

`AGENTS.md` contains working rules; `docs/SPEC.md` is the product specification; `.agents/skills` contains endpoint and Groq guidance; `backend` contains FastAPI, models, migrations, and tests; `frontend` contains the secondary Next app tree; `db/migrations` contains platform-managed SQL.

## 9. Hackathon checklist

| Requirement | Status |
|---|---|
| Live AI main journey | Not started |
| Persistent real database | Partly done; schema exists, live restart verification unverified |
| Sign-up/sign-in/2FA/per-account data | Partly done; live verification unverified |
| One complete journey | Not started |
| README/spec/AI disclosure | Done |
| Commits spread over event | Unverified |
| Two published code gigs | Not started |
| AGENTS.md and skills | Done |

## 10. Next steps

1. Run preview register/login and inspect `/auth/me` if it fails.
2. Build classes, then assignments, submissions, grading, review, reports, analytics, OCR, and hardening.
3. Split work: person A owns backend/domain migrations, person B owns frontend routes, person C owns grading/report/testing; coordinate shared schema changes first.

Live external verification and commit history were not available to this documentation pass.
