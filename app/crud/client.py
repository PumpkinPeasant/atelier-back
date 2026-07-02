from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


async def get(session: AsyncSession, client_id: int) -> Client | None:
    return await session.get(Client, client_id)


async def list_(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Client]:
    result = await session.execute(select(Client).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create(session: AsyncSession, data: ClientCreate) -> Client:
    client = Client(**data.model_dump())
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client


async def update(
    session: AsyncSession, client: Client, data: ClientUpdate
) -> Client:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    await session.commit()
    await session.refresh(client)
    return client


async def delete(session: AsyncSession, client: Client) -> None:
    await session.delete(client)
    await session.commit()
