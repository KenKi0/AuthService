from pydantic import BaseModel


class PermissionCreate(BaseModel):
    name: str
    code: int
    description: str


class PermissionUpdate(BaseModel):
    name: str | None
    code: int | None
    description: str | None
