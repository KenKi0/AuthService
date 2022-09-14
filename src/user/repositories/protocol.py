import dataclasses
import typing
import uuid

from user import layer_models


class NotFoundError(Exception):
    ...


class EmailAlreadyExist(Exception):
    ...


@dataclasses.dataclass
class UserFilter:
    username: str | None = None
    email: str | None = None


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
