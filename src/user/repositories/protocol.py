import dataclasses
import datetime
import typing
import uuid
from contextlib import contextmanager

import user.layer_models as layer_models


class NotFoundError(Exception):
    ...


class EmailAlreadyExist(Exception):
    ...


@dataclasses.dataclass
class UserFilter:
    username: str | None = None


class UserRepositoryProtocol(typing.Protocol):
    def get_by_id(self, user_id: uuid.UUID) -> layer_models.User:
        ...

    def get_by_email(self, email: str) -> layer_models.User:
        ...

    def get_multi(self, filters: UserFilter | None) -> list[layer_models.User]:
        ...

    def update(self, user_id: uuid.UUID, user: layer_models.UserUpdate) -> layer_models.User:
        ...

    def delete(self, user_id: uuid.UUID) -> layer_models.User:
        ...

    def get_history(self, user_id: uuid.UUID) -> list[layer_models.UserHistory]:
        ...

    def create(self, user: layer_models.UserCreate) -> layer_models.User:
        ...

    def get_allowed_device(self, device: layer_models.UserDevice) -> layer_models.UserDevice:
        ...

    def get_allowed_devices(self, user: uuid.UUID) -> list[layer_models.UserDevice]:
        ...

    def set_new_session(self, session: layer_models.Session) -> None:
        ...

    def add_allowed_device(self, device: layer_models.UserDevice) -> layer_models.UserDevice:
        ...


class TMStorageTransaction(typing.Protocol):
    def set(self, key: str | bytes, value: bytes, ex: int | datetime.timedelta | None = None) -> None:
        ...

    def delete(self, key: str | bytes) -> None:
        ...


class UserTmStorageRepositoryProtocol(typing.Protocol):
    def get(self, key: str | bytes) -> typing.Any:
        ...

    def set(self, key: str | bytes, value: bytes, ex: int | datetime.timedelta | None = None) -> None:
        ...

    def delete(self, *keys: str | bytes) -> None:
        ...

    @contextmanager
    def transaction(self) -> typing.ContextManager[TMStorageTransaction]:
        ...
