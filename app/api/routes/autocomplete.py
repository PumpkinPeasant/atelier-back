"""Автокомплит для селектов при выборе айтемов.

Категория и Тип берутся из enum'ов, Цвет и Размер — из справочников в БД.
Все ручки возвращают единый формат {value, label} и поддерживают поиск ?q=.
"""

from enum import Enum

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.crud import category_group as category_group_crud
from app.crud import color as color_crud
from app.crud import size as size_crud
from app.models.product import Fit, ProductCategory
from app.schemas.category import CategoryGroupTree
from app.schemas.lookup import AutocompleteOption

router = APIRouter(prefix="/lookups", tags=["lookups"])

# Человекочитаемые подписи для enum-значений.
CATEGORY_LABELS: dict[ProductCategory, str] = {
    ProductCategory.TSHIRT: "Футболка",
    ProductCategory.SHORTS: "Шорты",
    ProductCategory.SWEATSHIRT: "Свитшот",
}
FIT_LABELS: dict[Fit, str] = {
    Fit.SLIM: "Slim",
    Fit.REGULAR: "Regular",
    Fit.OVERSIZE: "Oversize",
}


def _enum_options(
    labels: dict[Enum, str], q: str | None, limit: int
) -> list[AutocompleteOption]:
    options = [
        AutocompleteOption(value=member.value, label=label)
        for member, label in labels.items()
    ]
    if q:
        ql = q.lower()
        options = [
            o for o in options if ql in o.label.lower() or ql in o.value.lower()
        ]
    return options[:limit]


@router.get("/categories", response_model=list[AutocompleteOption])
async def categories(q: str | None = None, limit: int = 20):
    return _enum_options(CATEGORY_LABELS, q, limit)


@router.get("/types", response_model=list[AutocompleteOption])
async def types(q: str | None = None, limit: int = 20):
    return _enum_options(FIT_LABELS, q, limit)


@router.get("/colors", response_model=list[AutocompleteOption])
async def colors(session: SessionDep, q: str | None = None, limit: int = 20):
    items = await color_crud.search(session, q, limit)
    return [AutocompleteOption(value=str(c.id), label=c.name) for c in items]


@router.get("/sizes", response_model=list[AutocompleteOption])
async def sizes(session: SessionDep, q: str | None = None, limit: int = 20):
    items = await size_crud.search(session, q, limit)
    return [AutocompleteOption(value=str(s.id), label=s.name) for s in items]


@router.get("/category-groups", response_model=list[CategoryGroupTree])
async def category_groups(session: SessionDep):
    """Справочник категорий, сгруппированный: группы с вложенными категориями."""
    return await category_group_crud.list_(session)
