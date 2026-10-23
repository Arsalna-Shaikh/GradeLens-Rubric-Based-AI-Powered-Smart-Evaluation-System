# AI Disclosure

This project uses AI-assisted coding tools (GitHub Copilot / ChatGPT) to generate boilerplate, scaffold code, and documentation. Human review is applied to all security-critical code, schema design, and dependency choices.

| Date | Tool | Task | Human review |
|------|------|------|--------------|
| 2025-06-10 | Copilot / ChatGPT | Phase 2 scaffold: FastAPI app, SQLAlchemy models, Alembic migration, auth router, deps, tests, Next.js pages, auth context, docs | Security flow, schema constraints, JWT scope handling, role guards reviewed |
| 2025-06-10 | Copilot / ChatGPT | Phase 4 platform migration: db/migrations SQL, Alembic sync, bcrypt 4.0.1 pin, JWT_SECRET/SESSION_SECRET fallback, docs/README updates | Migration safety, dependency ordering, secret fallback logic reviewed; live register/login remains unverified |
| 2025-06-10 | Coding agent | Project status documentation and migration syntax review | Workspace files and live schema inspected; no secrets read |

## Verification

Phase 11 review covered startup router loading, JWT scope and fallback extraction, role/ownership boundaries, deadline enforcement, release-only student/report access, and the demo seed script. Groq remains optional and is only used when configured; no model output is released without teacher approval.

- Backend tests cover registration, duplicate email, wrong password, full pyotp 2FA flow, role guard 403, and `scope=2fa` token rejection.
- Frontend manually verified by running `npm run dev` and exercising `/register`, `/login`, `/security`, `/teacher`, and `/student`.
- No secrets committed; only `.env.example` files contain placeholder keys.

## Phase 11 hardening verification

The hardening pass reviewed router registration, authentication fallback transport, ownership/role dependencies, submission deadlines, release gating, and the student-facing submission/report boundaries. AI-assisted changes were limited to verification and cleanup; Groq remains an optional integration configured by environment variables and is not a production secret in this repository.

Demo seed credentials are explicitly development-only and must not be used for real users. Hardening verification also checked that students receive only released data, teachers are ownership-scoped, failed password attempts are rate-limited in-process, and uploaded PDFs are validated and stored with random filenames. These controls still require a production deployment review (TLS, external rate limiting, backups, and monitoring). No student-facing response model includes AI draft columns; the hardening pass specifically reviewed `/submissions/mine`, submission status, release, and report paths for accidental leakage.

## Verified production guardrails

The final review explicitly checked wildcard-CORS credential handling, optional router startup isolation, release-only analytics/report access, status response minimization, deadline and duplicate-submission checks, and the demo seed's non-production credentials. These are code-level checks; run the documented pytest and deployment checklist against the target environment.

## Phase 11 production-readiness review

The final review added response-boundary checks, security response headers, request correlation IDs, defensive startup router loading, and documentation of the pending-versus-released student status contract. No new grading behavior was added. Human review remains required for deployment configuration, migrations, and any AI-generated draft.

## Phase 11 production-readiness review

The final review added response-boundary checks, security response headers, request correlation IDs, defensive startup router loading, and documentation of the pending-versus-released student status contract. No new grading behavior was added. Human review remains required for deployment configuration, migrations, and any AI-generated draft.

## Phase 11 hardening verification note

This pass added focused regression coverage for proxy token fallbacks and authentication boundaries, and corrected browser form upload headers plus login limiter bucketing. Human review should still validate deployment CORS, TLS, database migrations, and private storage configuration.

## Final hardening note
The final pass was limited to security verification and deployment readiness: startup failures are logged while optional routers remain isolated, release-only response boundaries were reviewed, and the PDF dependency/documentation were aligned with the approved workflow. AI-generated suggestions remain drafts until teacher approval.

## Login fix chunks (commits 1–4)

| Date | Tool | Task | Human review |
|------|------|------|--------------|
| 2025-06-10 | Coding agent | Generated the four small login-fix changes: disambiguated SQLAlchemy submission relationships, restored the assignments router dependency wiring, and improved actionable frontend login errors | A human reproduced the login failure and reviewed each change; no schema or dependency changes were made |

The changes are intended to be applied as four separate commits in the requested order. Commit 5 records this combined disclosure entry.

## Assignment UI chunks (commits 1–7)

| Date | Tool | Task | Human review |
|------|------|------|--------------|
| 2025-06-10 | Coding agent | feat(routes): root `app/teacher/{assignments,review,grading,analytics}` re-export pages | Confirmed routes resolve instead of 404 |
| 2025-06-10 | Coding agent | feat(teacher): dashboard links to Create assignment, Review, Grading, Analytics | Visual check of link row |
| 2025-06-10 | Coding agent | fix(teacher): ProtectedRoute + RoleGuard on assignment page, optional ISO deadline, Back to dashboard link | Role guard and deadline payload reviewed |
| 2025-06-10 | Coding agent | feat(teacher): MCQ options/correct answer, client validation matching backend rules, backend error display, total marks | Payload compared against `AssignmentCreate` validator |
| 2025-06-10 | Coding agent | feat(student): `/student/assignments` list grouped by class with submitted status | Endpoints `/classes/enrolled`, `/assignments/class/{id}`, `/submissions/mine` reused unchanged |
| 2025-06-10 | Coding agent | feat(student): text/PDF submission form (FormData, client .pdf + 10 MB check, server errors shown) | Server remains source of truth for deadline, duplicate, enrollment and PDF checks |
| 2025-06-10 | Coding agent | feat(student): dashboard "View assignments" link and assignment titles in My submissions | No API changes |

No backend code, migrations or dependencies were changed for these chunks.
