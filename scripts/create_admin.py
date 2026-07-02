"""Создание администратора.

Использование:
    python -m scripts.create_admin <email> <password>
"""

import asyncio
import sys

from app.crud import admin as crud
from app.db.session import async_session_maker, engine


async def main(email: str, password: str) -> None:
    async with async_session_maker() as session:
        existing = await crud.get_by_email(session, email)
        if existing is not None:
            print(f"Admin already exists: {email} (id={existing.id})")
            return
        admin = await crud.create(session, email, password)
        print(f"Created admin id={admin.id} email={admin.email}")
    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.create_admin <email> <password>")
        raise SystemExit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
