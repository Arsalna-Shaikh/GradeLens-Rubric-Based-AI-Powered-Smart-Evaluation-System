import logging
from typing import Any, Annotated
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
from app.db import get_db
from app.models.user import User
from app.services.auth_service import decode_token

logger = logging.getLogger(__name__)


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    x_auth_token: Annotated[str | None, Header()] = None,
    db: Annotated[Session, Depends(get_db)] = None,
) -> User:
    raw = authorization or x_auth_token
    logger.info("auth header received: authorization=%s x_auth_token=%s", bool(authorization), bool(x_auth_token))
    if not raw:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = raw[7:] if raw.lower().startswith("bearer ") else raw
    try:
        payload = decode_token(token)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("scope") != "access":
        raise HTTPException(status_code=401, detail="Invalid token scope")
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(role: str):
    def checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role != role:
            raise HTTPException(status_code=403, detail=f"This resource requires the '{role}' role")
        return current_user
    return checker
