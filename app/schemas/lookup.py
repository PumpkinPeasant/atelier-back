from pydantic import BaseModel, ConfigDict


class AutocompleteOption(BaseModel):
    """Опция для селекта/автокомплита на фронте."""

    value: str
    label: str


# --- Color ---
class ColorBase(BaseModel):
    name: str
    hex: str | None = None


class ColorCreate(ColorBase):
    pass


class ColorUpdate(BaseModel):
    name: str | None = None
    hex: str | None = None


class ColorRead(ColorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# --- Size ---
class SizeBase(BaseModel):
    name: str
    sort_order: int = 0


class SizeCreate(SizeBase):
    pass


class SizeUpdate(BaseModel):
    name: str | None = None
    sort_order: int | None = None


class SizeRead(SizeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
