from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.admin import Admin


async def get_by_email(session: AsyncSession, email: str) -> Admin | None:
    result = await session.execute(select(Admin).where(Admin.email == email))
    return result.scalar_one_or_none()


async def authenticate(
    session: AsyncSession, email: str, password: str
) -> Admin | None:
    admin = await get_by_email(session, email)
    if admin is None or not admin.is_active:
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    return admin


async def create(session: AsyncSession, email: str, password: str) -> Admin:
    admin = Admin(email=email, hashed_password=hash_password(password))
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin
