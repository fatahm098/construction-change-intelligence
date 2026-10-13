"""Router modul Auth: registrasi, login, dan profil pengguna.

Endpoint:
  - POST /api/auth/register — buat akun baru
  - POST /api/auth/login    — tukar kredensial dengan token JWT
  - GET  /api/auth/me       — profil user dari token

Catatan keamanan: user pertama yang mendaftar otomatis menjadi ADMIN (bootstrap);
pendaftar berikutnya selalu ENGINEER (field `role` pada payload diabaikan) agar
tidak ada eskalasi hak akses lewat registrasi publik.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...kernel.auth.dependencies import get_current_user
from ...kernel.auth.security import create_access_token, hash_password, verify_password
from ...models import User, UserRole
from ...schemas import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])
# Diekspor dalam bentuk list agar cocok dengan registry modul (`routers`).
routers = [router]

MIN_PASSWORD_LENGTH = 8


@router.post("/register", response_model=UserResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Daftarkan akun baru. 409 bila email sudah dipakai."""
    email = payload.email.strip().lower()
    if len(payload.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password minimal {MIN_PASSWORD_LENGTH} karakter.",
        )
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email sudah terdaftar.",
        )

    # User pertama menjadi admin agar sistem bisa dikelola.
    role = UserRole.ADMIN if db.query(User).count() == 0 else UserRole.ENGINEER

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=role,
        is_active=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Verifikasi kredensial dan kembalikan access token + data user."""
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun tidak aktif.",
        )

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    """Kembalikan profil user yang sedang login."""
    return current_user
