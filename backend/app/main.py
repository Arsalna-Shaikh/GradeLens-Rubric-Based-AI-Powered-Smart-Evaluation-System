import logging
import time
import uuid
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app import models  # noqa: F401
from app.routers import auth

logger = logging.getLogger("gradelens.startup")
app = FastAPI(title="GradeLens API", version="0.1.0")

@app.middleware("http")
async def request_logging(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    logger.info("request method=%s path=%s status=%s duration_ms=%.1f request_id=%s",
                request.method, request.url.path, response.status_code,
                (time.perf_counter() - started) * 1000, getattr(request.state, "request_id", "-"))
    return response

def _get_cors_origins() -> list[str]:
    # Browsers reject wildcard origins when credentials are enabled. Preview mode
    # therefore uses reflected origins without allowing cookies cross-site.
    if settings.FRONTEND_URL == "*" or settings.PREVIEW_MODE:
        return ["*"]
    return list({settings.FRONTEND_URL, "http://localhost:3000"})

_wildcard_cors = settings.FRONTEND_URL == "*" or settings.PREVIEW_MODE
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=not _wildcard_cors,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Auth-Token", "X-Access-Token"],
)

@app.middleware("http")
async def security_headers(request, call_next):
    # Correlate server logs without exposing request data or credentials.
    request.state.request_id = uuid.uuid4().hex
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
    response.headers["X-Request-ID"] = request.state.request_id
    return response

app.include_router(auth.router)

# Feature routers are optional at import time, but available when their
# dependencies are installed. Auth and health never depend on them.
for _name in ("classes", "assignments", "submissions", "grading", "review", "reports", "analytics", "ocr"):
    try:
        _module = __import__(f"app.routers.{_name}", fromlist=["router"])
        app.include_router(_module.router)
    except Exception as exc:
        # Optional modules must never take down auth/health, but failures are
        # observable in deployment logs rather than silently swallowed.
        logger.warning("optional router unavailable: %s (%s)", _name, exc.__class__.__name__)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        # Do not expose driver, host, or SQL details through a public health check.
        db_status = "error"
    return {"status": "ok", "db": db_status}