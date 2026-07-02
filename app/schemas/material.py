from pydantic import BaseModel, ConfigDict


class MaterialBase(BaseModel):
    name: str


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: str | None = None


class MaterialRead(MaterialBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
