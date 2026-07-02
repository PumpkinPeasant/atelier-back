from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.crud import size as crud
from app.schemas.lookup import SizeCreate, SizeRead, SizeUpdate

router = APIRouter(prefix="/sizes", tags=["sizes"])


@router.get("", response_model=list[SizeRead])
async def list_sizes(session: SessionDep, skip: int = 0, limit: int = 100):
    return await crud.list_(session, skip=skip, limit=limit)


@router.post("", response_model=SizeRead, status_code=status.HTTP_201_CREATED)
async def create_size(payload: SizeCreate, session: SessionDep):
    return await crud.create(session, payload)


@router.get("/{size_id}", response_model=SizeRead)
async def get_size(size_id: int, session: SessionDep):
    size = await crud.get(session, size_id)
    if size is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Size not found")
    return size


@router.patch("/{size_id}", response_model=SizeRead)
async def update_size(size_id: int, payload: SizeUpdate, session: SessionDep):
    size = await crud.get(session, size_id)
    if size is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Size not found")
    return await crud.update(session, size, payload)


@router.delete("/{size_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_size(size_id: int, session: SessionDep):
    size = await crud.get(session, size_id)
    if size is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Size not found")
    await crud.delete(session, size)
