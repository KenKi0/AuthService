import uuid

from pydantic import BaseModel


class DefaultModel(BaseModel):
    id: uuid.UUID  # noqa: VNE003

    class Config:
        orm_mode = True


class Role(DefaultModel):
    name: str
    description: str


class Permission(DefaultModel):
    name: str
    code: int
