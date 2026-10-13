"""Router modul Settings: pengaturan LLM + API key.

Endpoint (kontrak beku v1):
  - GET  /api/settings/llm       → LLMSettingsResponse (tanpa API key mentah)
  - PUT  /api/settings/llm       → LLMSettingsResponse (api_key write-only)
  - POST /api/settings/llm/test  → LLMSettingsTestResponse

Catatan: saat `auth_enabled=true`, hanya role ADMIN yang boleh membaca/mengubah
pengaturan. Saat `auth_enabled=false` (default dev) endpoint terbuka, konsisten
dengan endpoint lain di aplikasi.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...kernel import settings_store
from ...kernel.auth.dependencies import get_current_user_optional
from ...kernel.config import settings
from ...models import User, UserRole
from ...schemas import (
    LLMSettingsResponse,
    LLMSettingsTestResponse,
    LLMSettingsUpdateRequest,
)
from .service import test_connection

router = APIRouter(prefix="/api/settings", tags=["Pengaturan"])
routers = [router]


def require_admin_when_auth_enabled(
    current_user: User | None = Depends(get_current_user_optional),
) -> None:
    """No-op saat auth mati; bila auth aktif, wajib admin."""
    if not settings.auth_enabled:
        return
    if current_user is None or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses pengaturan.",
        )


@router.get("/llm", response_model=LLMSettingsResponse)
def get_llm_settings(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin_when_auth_enabled),
):
    return settings_store.effective_settings(db)


@router.put("/llm", response_model=LLMSettingsResponse)
def update_llm_settings(
    payload: LLMSettingsUpdateRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin_when_auth_enabled),
):
    return settings_store.update_settings(
        db,
        provider=payload.provider,
        model=payload.model,
        base_url=payload.base_url,
        embedding_model=payload.embedding_model,
        api_key=payload.api_key,
    )


@router.post("/llm/test", response_model=LLMSettingsTestResponse)
def test_llm_settings(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin_when_auth_enabled),
):
    return test_connection(db)
