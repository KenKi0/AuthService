import datetime
import uuid

from pydantic import BaseModel


class User(BaseModel):
    id: uuid.UUID  # noqa: VNE003
    username: str
    email: str
    password: str
    is_super: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    username: str | None
    email: str | None
    password: str | None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str
    user_agent: str


class UserHistory(BaseModel):
    id: uuid.UUID  # noqa: VNE003
    device_id: str
    auth_date: datetime.datetime


class UserID(BaseModel):
    user_id: uuid.UUID


class Session(UserID):
    device_id: str


class UserDevice(UserID):
    id: uuid.UUID | None  # noqa: VNE003
    user_agent: str

    class Config:
        orm_mode = True


class ChangePassword(UserID):
    old_password: str
    new_password: str


class RefreshTokens(UserID):
    user_agent: str
    refresh: str


class Logout(UserID):
    user_agent: str
    from_all: bool = False


class Permission(BaseModel):
    name: str
    code: int
    description: str

    class Config:
        orm_mode = True
