from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.crud import category as crud
from app.crud import category_group as group_crud
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(session: SessionDep, group_id: int | None = None):
    return await crud.list_(session, group_id=group_id)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, session: SessionDep):
    if await group_crud.get(session, payload.group_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category group not found")
    return await crud.create(session, payload)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, session: SessionDep):
    category = await crud.get(session, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int, payload: CategoryUpdate, session: SessionDep
):
    category = await crud.get(session, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    if payload.group_id is not None and (
        await group_crud.get(session, payload.group_id) is None
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category group not found")
    return await crud.update(session, category, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, session: SessionDep):
    category = await crud.get(session, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    await crud.delete(session, category)
