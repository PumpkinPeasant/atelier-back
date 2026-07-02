from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.crud import color as crud
from app.schemas.lookup import ColorCreate, ColorRead, ColorUpdate

router = APIRouter(prefix="/colors", tags=["colors"])


@router.get("", response_model=list[ColorRead])
async def list_colors(session: SessionDep, skip: int = 0, limit: int = 100):
    return await crud.list_(session, skip=skip, limit=limit)


@router.post("", response_model=ColorRead, status_code=status.HTTP_201_CREATED)
async def create_color(payload: ColorCreate, session: SessionDep):
    return await crud.create(session, payload)


@router.get("/{color_id}", response_model=ColorRead)
async def get_color(color_id: int, session: SessionDep):
    color = await crud.get(session, color_id)
    if color is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Color not found")
    return color


@router.patch("/{color_id}", response_model=ColorRead)
async def update_color(color_id: int, payload: ColorUpdate, session: SessionDep):
    color = await crud.get(session, color_id)
    if color is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Color not found")
    return await crud.update(session, color, payload)


@router.delete("/{color_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_color(color_id: int, session: SessionDep):
    color = await crud.get(session, color_id)
    if color is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Color not found")
    await crud.delete(session, color)
