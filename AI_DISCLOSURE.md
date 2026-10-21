# AI Disclosure

This project uses AI-assisted coding tools (GitHub Copilot / ChatGPT) to generate boilerplate, scaffold code, and documentation. Human review is applied to all security-critical code, schema design, and dependency choices.

| Date | Tool | Task | Human review |
|------|------|------|--------------|
| 2025-06-10 | Copilot / ChatGPT | Phase 2 scaffold: FastAPI app, SQLAlchemy models, Alembic migration, auth router, deps, tests, Next.js pages, auth context, docs | Security flow, schema constraints, JWT scope handling, role guards reviewed |
| 2025-06-10 | Copilot / ChatGPT | Phase 4 platform migration: db/migrations SQL, Alembic sync, bcrypt 4.0.1 pin, JWT_SECRET/SESSION_SECRET fallback, docs/README updates | Migration safety, dependency ordering, secret fallback logic reviewed; live register/login remains unverified |
| 2025-06-10 | Coding agent | Project status documentation and migration syntax review | Workspace files and live schema inspected; no secrets read |

## Verification

- Backend tests cover registration, duplicate email, wrong password, full pyotp 2FA flow, role guard 403, and `scope=2fa` token rejection.
- Frontend manually verified by running `npm run dev` and exercising `/register`, `/login`, `/security`, `/teacher`, and `/student`.
- No secrets committed; only `.env.example` files contain placeholder keys.
