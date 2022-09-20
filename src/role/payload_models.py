from pydantic import BaseModel


class RoleUpdate(BaseModel):
    name: str | None
    description: str | None


class RoleCreate(BaseModel):
    name: str
    description: str
