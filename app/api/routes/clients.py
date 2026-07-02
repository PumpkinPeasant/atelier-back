from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.crud import client as crud
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=list[ClientRead])
async def list_clients(session: SessionDep, skip: int = 0, limit: int = 100):
    return await crud.list_(session, skip=skip, limit=limit)


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(payload: ClientCreate, session: SessionDep):
    return await crud.create(session, payload)


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(client_id: int, session: SessionDep):
    client = await crud.get(session, client_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client not found")
    return client


@router.patch("/{client_id}", response_model=ClientRead)
async def update_client(client_id: int, payload: ClientUpdate, session: SessionDep):
    client = await crud.get(session, client_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client not found")
    return await crud.update(session, client, payload)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int, session: SessionDep):
    client = await crud.get(session, client_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client not found")
    await crud.delete(session, client)
