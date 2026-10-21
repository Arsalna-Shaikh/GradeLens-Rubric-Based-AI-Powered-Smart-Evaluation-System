from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app import models  # noqa: F401 - registers all ORM tables
from app.routers import auth

app = FastAPI(title="GradeLens API", version="0.1.0")


def _get_cors_origins() -> list[str]:
    # Preview / unknown-origin mode: allow any origin. In normal shared-origin
    # proxy mode this is not needed, but it keeps direct backend access working
    # when the frontend origin cannot be known ahead of time (e.g. preview URLs).
    if settings.FRONTEND_URL == "*" or settings.PREVIEW_MODE:
        return ["*"]
    origins = {settings.FRONTEND_URL, "http://localhost:3000"}
    return list(origins)


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        db_status = f"error: {exc}"

    return {"status": "ok", "db": db_status}
