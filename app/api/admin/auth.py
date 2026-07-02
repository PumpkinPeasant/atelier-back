import jwt
from fastapi import APIRouter, HTTPException, Request, Response, status

from app.api.deps import ACCESS_COOKIE, REFRESH_COOKIE, CurrentAdmin, SessionDep
from app.core.config import settings
from app.core.security import (
    REFRESH_TOKEN,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.crud import admin as crud
from app.models.admin import Admin
from app.schemas.auth import AdminRead, LoginRequest

router = APIRouter(prefix="/auth", tags=["admin:auth"])


def _set_auth_cookies(response: Response, subject: int) -> None:
    response.set_cookie(
        ACCESS_COOKIE,
        create_access_token(subject),
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )
    response.set_cookie(
        REFRESH_COOKIE,
        create_refresh_token(subject),
        max_age=settings.refresh_token_expire_days * 86400,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )


@router.post("/login", response_model=AdminRead)
async def login(payload: LoginRequest, response: Response, session: SessionDep):
    admin = await crud.authenticate(session, payload.email, payload.password)
    if admin is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid email or password"
        )
    _set_auth_cookies(response, admin.id)
    return admin


@router.post("/refresh", response_model=AdminRead)
async def refresh(request: Request, response: Response, session: SessionDep):
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing refresh token")
    try:
        claims = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    if claims.get("type") != REFRESH_TOKEN:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

    admin = await session.get(Admin, int(claims["sub"]))
    if admin is None or not admin.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

    _set_auth_cookies(response, admin.id)
    return admin


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")


@router.get("/me", response_model=AdminRead)
async def me(admin: CurrentAdmin):
    return admin
