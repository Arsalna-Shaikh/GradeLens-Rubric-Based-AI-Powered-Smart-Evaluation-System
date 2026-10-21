import base64
import io
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter(prefix="/auth", tags=["auth"])


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
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.totp_enabled:
        temp_token = create_temp_token(user.id)
        return LoginResponse(requires_2fa=True, temp_token=temp_token)

    access_token = create_access_token(user.id, user.role)
    return LoginResponse(access_token=access_token)


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


@router.post("/2fa/login", response_model=TokenResponse)
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

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(payload.code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid TOTP code")

    access_token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserOut)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return _user_to_out(current_user)
