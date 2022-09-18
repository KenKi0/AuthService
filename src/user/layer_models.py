import datetime
import uuid

from pydantic import BaseModel


class DefaultModel(BaseModel):
    id: uuid.UUID  # noqa: VNE003

    class Config:
        orm_mode = True


class User(DefaultModel):
    username: str
    email: str
    password: str
    is_super: bool


class Session(DefaultModel):
    device_id: uuid.UUID
    user_id: uuid.UUID
    auth_date: datetime.datetime


class UserDevice(DefaultModel):
    user_id: uuid.UUID
    user_agent: str


class Permission(DefaultModel):
    name: str
    code: int
    description: str
