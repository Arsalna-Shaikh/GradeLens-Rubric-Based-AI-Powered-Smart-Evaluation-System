import base64
import io
import time
from collections import defaultdict
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from jose import JWTError
import pyotp
import qrcode

from app.db import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TwoFaLoginRequest,
    LoginResponse,
    TokenResponse,
)
from app.schemas.user import UserOut
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_temp_token,
    decode_token,
)
from app.deps import get_current_user


def request_key(value: str) -> str:
    """Use a non-secret stable bucket key without logging or persisting the token."""
    import hashlib
    return hashlib.sha256(value.encode()).hexdigest()[:24]

router = APIRouter(prefix="/auth", tags=["auth"])
_FAILED_LOGINS: defaultdict[str, list[float]] = defaultdict(list)
_FAILED_2FA: defaultdict[str, list[float]] = defaultdict(list)
_MAX_FAILURES = 8
_WINDOW_SECONDS = 300


def _check_limited(bucket: defaultdict[str, list[float]], key: str) -> None:
    now = time.monotonic()
    attempts = [stamp for stamp in bucket[key] if now - stamp < _WINDOW_SECONDS]
    bucket[key] = attempts
    if len(attempts) >= _MAX_FAILURES:
        raise HTTPException(status_code=429, detail="Too many failed attempts; try again later")


def _record_failure(bucket: defaultdict[str, list[float]], key: str) -> None:
    bucket[key].append(time.monotonic())

def _check_login_rate(key: str) -> None:
    _check_limited(_FAILED_LOGINS, key)


def _record_login_failure(key: str) -> None:
    _record_failure(_FAILED_LOGINS, key)


def _user_to_out(user: User) -> UserOut:
    return UserOut.model_validate(user)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Annotated[Session, Depends(get_db)]):
    if payload.role not in ("teacher", "student"):
        raise HTTPException(status_code=400, detail="role must be 'teacher' or 'student'")

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_to_out(user)


@router.post("/login", response_model=LoginResponse)
def login(request: Request, payload: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    # Combine email and client address so one noisy client cannot exhaust every
    # account bucket. The address is used only as an in-process limiter key.
    limiter_key = f"{payload.email.lower()}:{request.client.host if request.client else 'unknown'}"
    _check_login_rate(limiter_key)
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        _record_login_failure(limiter_key)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    _FAILED_LOGINS.pop(limiter_key, None)

    if user.totp_enabled:
        temp_token = create_temp_token(user.id)
        return LoginResponse(requires_2fa=True, temp_token=temp_token, user=_user_to_out(user))

    access_token = create_access_token(user.id, user.role)
    return LoginResponse(access_token=access_token, user=_user_to_out(user))


@router.post("/2fa/setup")
def setup_2fa(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    secret = pyotp.random_base32()
    current_user.totp_secret = secret
    current_user.totp_enabled = False
    db.commit()

    otpauth_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email, issuer_name="GradeLens"
    )
    qr = qrcode.make(otpauth_uri)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    qr_code = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    return {"secret": secret, "otpauth_uri": otpauth_uri, "qr_code": qr_code}


@router.post("/2fa/verify")
def verify_2fa(
    code: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA setup not started")

    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(code.get("code", ""), valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid TOTP code")

    current_user.totp_enabled = True
    db.commit()
    return {"message": "2FA enabled successfully"}


@router.post("/2fa/login", response_model=LoginResponse)
def login_2fa(payload: TwoFaLoginRequest, db: Annotated[Session, Depends(get_db)]):
    try:
        token_payload = decode_token(payload.temp_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired temp token")

    if token_payload.get("scope") != "2fa":
        raise HTTPException(status_code=401, detail="Invalid token scope")

    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.totp_enabled or not user.totp_secret:
        raise HTTPException(status_code=401, detail="2FA not configured")

    # Temporary tokens are deliberately rate-limited separately from passwords.
    # This limiter is process-local; production should use a shared store.
    limiter_key = f"{user.id}:{request_key(payload.temp_token)}"
    _check_limited(_FAILED_2FA, limiter_key)
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(payload.code, valid_window=1):
        _record_failure(_FAILED_2FA, limiter_key)
        raise HTTPException(status_code=401, detail="Invalid TOTP code")
    _FAILED_2FA.pop(limiter_key, None)

    access_token = create_access_token(user.id, user.role)
    return LoginResponse(access_token=access_token, user=_user_to_out(user))


@router.get("/me", response_model=UserOut)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return _user_to_out(current_user)
