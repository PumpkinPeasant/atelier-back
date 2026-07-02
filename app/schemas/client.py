from pydantic import BaseModel, ConfigDict, EmailStr


class ClientBase(BaseModel):
    full_name: str
    phone: str
    email: EmailStr | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


class ClientRead(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
