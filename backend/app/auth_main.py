# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""Standalone FastAPI app for authentication and identity endpoints."""

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User as UserModel
from app.routers.auth import router as auth_router
from app.schemas.users import User as UserResponse
from app.security.auth import ensure_schema_current, get_current_user

app = FastAPI(title="Sentinel Auth")
app.include_router(auth_router)


@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["auth"])
async def me(current_user: UserModel = Depends(get_current_user)):
    return current_user


@app.get("/api/v1/auth/health", tags=["health"])
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await ensure_schema_current(db)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Auth database is unavailable or schema is outdated") from exc
    return {"status": "ok"}
