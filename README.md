# GradeLens

Rubric-based AI-powered evaluation platform for universities. Teachers create classes, assignments and rubrics; students submit PDFs; MCQs are auto-graded; written answers are evaluated by a Groq LLM; teachers review and approve before releasing feedback.

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL |
| Auth | JWT, bcrypt, pyotp TOTP 2FA |
| Frontend | Next.js App Router, React, Tailwind CSS |
| AI (later) | LangChain ChatGroq via Groq API |

## Project structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── deps.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── routers/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   └── src/app/
├── docs/
│   └── ARCHITECTURE.md
└── .agents/skills/
```

## Windows setup

1. Install Python 3.11+ and Node.js 18+.
2. Install PostgreSQL locally (or use the provided `DATABASE_URL`).
3. Create `backend/.env` and `.env.local` (at repo root) from the `.env.example` files.

## Quick start

From the repository root:

```powershell
# 1. Install dependencies
npm install

# 2. Configure environment
copy backend\.env.example backend\.env
copy .env.example .env.local
# Edit backend\.env and .env.local with your values.
# For the shared-origin proxy, leave NEXT_PUBLIC_API_URL empty.

# 3. Start both backend and frontend
npm run dev
```

- Frontend: http://localhost:3000 (or the `PORT` provided by the preview)
- Backend:  http://localhost:8000
- API calls from the browser go to `/api/*` and are rewritten to the backend by Next.js.
- The dev/start command runs `alembic upgrade head` before uvicorn starts, so tables are created automatically.
- For platform previews, the schema is also managed by `db/migrations/0001_initial_core_tables.sql`, which creates the same tables and seeds `alembic_version` to revision `000000000001` so the backend Alembic runner stays in sync.

### Manual backend (for development)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment variables

### Backend (`backend/.env`)

- `DATABASE_URL` — PostgreSQL connection string
- `JWT_SECRET` — at least 32 characters; falls back to `SESSION_SECRET` when unset or too short
- `SESSION_SECRET` — used as a fallback for JWT signing in preview environments
- `FRONTEND_URL` — frontend origin for CORS (use `*` for unknown/preview origins)
- `PREVIEW_MODE` — set to `true` to allow any CORS origin dynamically
- `GROQ_API_KEY` / `GROQ_MODEL` — used in later phases
- `OCR_ENABLED` — optional OCR fallback flag

### Frontend (`.env.local` at repo root)

- `NEXT_PUBLIC_API_URL` — backend base URL (e.g. `http://localhost:8000`). Leave empty or unset to use the shared-origin `/api` proxy.

### Preview deployment

- Leave `NEXT_PUBLIC_API_URL` empty so the frontend calls `/api/*` and Next.js rewrites them to the local backend on port 8000.
- Set `FRONTEND_URL` to the preview URL, or set it to `*` / `PREVIEW_MODE=true` to allow any CORS origin.
- `npm run dev` automatically reads the `PORT` environment variable for the frontend and runs `alembic upgrade head` before starting the backend.

## Project status

See [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for the current implementation inventory and open verification items.

## Testing

```powershell
cd backend
pytest -q
```

## Verifying register/login end-to-end

With both services running:

```powershell
# Register a test user
curl -X POST http://localhost:8000/auth/register `
  -H "Content-Type: application/json" `
  -d '{"name":"Test User","email":"test@example.com","password":"password123","role":"student"}'

# Confirm the row exists in the database
psql $env:DATABASE_URL -c "SELECT id, email, role FROM users WHERE email = 'test@example.com';"

# Log in
curl -X POST http://localhost:8000/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com","password":"password123"}'
```

Or use the frontend at `/register` and `/login`.

### Runtime fixes in this phase

- `bcrypt==4.0.1` is pinned before `passlib[bcrypt]` to avoid the passlib 1.7.4 / bcrypt 4.1+ `__about__` incompatibility.
- `JWT_SECRET` falls back to `SESSION_SECRET` when missing or shorter than 32 characters; the app raises a clear error if neither secret is usable.
