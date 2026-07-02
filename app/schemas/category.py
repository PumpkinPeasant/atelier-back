from pydantic import BaseModel, ConfigDict


# --- Category ---
class CategoryBase(BaseModel):
    name: str
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    group_id: int


class CategoryUpdate(BaseModel):
    name: str | None = None
    sort_order: int | None = None
    group_id: int | None = None


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int


# --- CategoryGroup ---
class CategoryGroupBase(BaseModel):
    name: str
    sort_order: int = 0


class CategoryGroupCreate(CategoryGroupBase):
    pass


class CategoryGroupUpdate(BaseModel):
    name: str | None = None
    sort_order: int | None = None


class CategoryGroupRead(CategoryGroupBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CategoryGroupTree(CategoryGroupRead):
    """Группа вместе с вложенными категориями (для сгруппированного вывода)."""

    categories: list[CategoryRead] = []
