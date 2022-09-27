import uuid

from pydantic import BaseModel


class UserUpdatePayload(BaseModel):
    username: str | None
    email: str | None
    password: str | None


class UserCreatePayload(BaseModel):
    username: str
    email: str
    password: str


class UserLoginPayload(BaseModel):
    email: str
    password: str
    user_agent: str


class UserID(BaseModel):
    user_id: uuid.UUID


class ChangePasswordPayload(UserID):
    old_password: str
    new_password: str


class RefreshTokensPayload(UserID):
    user_agent: str
    refresh: str


class LogoutPayload(UserID):
    user_agent: str
    from_all: bool = False


class UserDevicePayload(UserID):
    user_agent: str


class SessionPayload(UserID):
    device_id: uuid.UUID


class OAuthUser(BaseModel):
    user_agent: str
    social_id: str
    username: str
    email: str


class SocialAccountPayload(UserID):
    social_id: str
    social_name: str
