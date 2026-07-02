from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import ACCESS_TOKEN, decode_token
from app.db.session import get_session
from app.models.admin import Admin

SessionDep = Annotated[AsyncSession, Depends(get_session)]

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"

_credentials_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
)


async def get_current_admin(request: Request, session: SessionDep) -> Admin:
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        raise _credentials_error
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise _credentials_error
    if payload.get("type") != ACCESS_TOKEN:
        raise _credentials_error
    admin = await session.get(Admin, int(payload["sub"]))
    if admin is None or not admin.is_active:
        raise _credentials_error
    return admin


CurrentAdmin = Annotated[Admin, Depends(get_current_admin)]
