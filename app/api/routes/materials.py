from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.crud import material as crud
from app.schemas.material import MaterialCreate, MaterialRead, MaterialUpdate

router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("", response_model=list[MaterialRead])
async def list_materials(session: SessionDep, skip: int = 0, limit: int = 100):
    return await crud.list_(session, skip=skip, limit=limit)


@router.post("", response_model=MaterialRead, status_code=status.HTTP_201_CREATED)
async def create_material(payload: MaterialCreate, session: SessionDep):
    return await crud.create(session, payload)


@router.get("/{material_id}", response_model=MaterialRead)
async def get_material(material_id: int, session: SessionDep):
    material = await crud.get(session, material_id)
    if material is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Material not found")
    return material


@router.patch("/{material_id}", response_model=MaterialRead)
async def update_material(
    material_id: int, payload: MaterialUpdate, session: SessionDep
):
    material = await crud.get(session, material_id)
    if material is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Material not found")
    return await crud.update(session, material, payload)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(material_id: int, session: SessionDep):
    material = await crud.get(session, material_id)
    if material is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Material not found")
    await crud.delete(session, material)
