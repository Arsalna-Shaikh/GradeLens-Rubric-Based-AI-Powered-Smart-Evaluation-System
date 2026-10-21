---
name: add-endpoint
description: Add a new FastAPI endpoint with model, schema, service logic, router wiring, and a pytest.
---

# add-endpoint

1. Define the SQLAlchemy model change in `backend/app/models/` and create an Alembic migration (`alembic revision --autogenerate -m "..."`).
2. Add Pydantic request/response schemas in `backend/app/schemas/`.
3. Implement business logic in `backend/app/services/` and keep the router thin in `backend/app/routers/`.
4. Protect the route with `get_current_user` and `require_role(...)` where appropriate; filter queries by the current user's id.
5. Add a pytest in `backend/tests/` covering the happy path and an auth/permission failure.
6. Run `pytest -q` and `alembic upgrade head` before committing.
