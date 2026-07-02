from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.crud import category_group as crud
from app.schemas.category import (
    CategoryGroupCreate,
    CategoryGroupRead,
    CategoryGroupTree,
    CategoryGroupUpdate,
)

router = APIRouter(prefix="/category-groups", tags=["category-groups"])


@router.get("", response_model=list[CategoryGroupTree])
async def list_groups(session: SessionDep):
    return await crud.list_(session)


@router.post("", response_model=CategoryGroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(payload: CategoryGroupCreate, session: SessionDep):
    return await crud.create(session, payload)


@router.get("/{group_id}", response_model=CategoryGroupTree)
async def get_group(group_id: int, session: SessionDep):
    group = await crud.get(session, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category group not found")
    return group


@router.patch("/{group_id}", response_model=CategoryGroupRead)
async def update_group(
    group_id: int, payload: CategoryGroupUpdate, session: SessionDep
):
    group = await crud.get(session, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category group not found")
    return await crud.update(session, group, payload)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: int, session: SessionDep):
    group = await crud.get(session, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category group not found")
    await crud.delete(session, group)
