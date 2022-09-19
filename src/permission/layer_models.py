import uuid

from pydantic import BaseModel


class DefaultModel(BaseModel):
    id: uuid.UUID  # noqa: VNE003

    class Config:
        orm_mode = True


class Permission(DefaultModel):
    name: str
    code: int
    description: str
