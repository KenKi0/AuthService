import dataclasses
import datetime
import typing
import uuid
from contextlib import contextmanager

import user.layer_models as layer_models
import user.payload_models as payload_models
from api.v1.utils import Pagination


@dataclasses.dataclass
class UserFilter:
    username: str | None = None


class UserRepositoryProtocol(typing.Protocol):
    def get_by_id(self, user_id: uuid.UUID) -> layer_models.User:
        """
        :raises NotFoundError:
        """
        ...

    def get_by_email(self, email: str) -> layer_models.User:
        """
        :raises NotFoundError:
        """
        ...

    def get_multi(self, filters: UserFilter | None) -> list[layer_models.User]:
        ...

    def create(self, user: payload_models.UserCreatePayload) -> layer_models.User:
        """
        :raises UniqueConstraintError: если пользователь с указанным email уже существует
        """
        ...

    def update(self, user_id: uuid.UUID, user: payload_models.UserUpdatePayload) -> layer_models.User:
        """
        :raises NotFoundError: если не была найдена запись для обновления в базе
        :raises UniqueConstraintError: если пользователь с указанным email уже существует
        """
        ...

    def delete(self, user_id: uuid.UUID) -> layer_models.User:
        """
        :raises NotFoundError: если не была найдена запись для удаления в базе
        """
        ...

    def add_allowed_device(self, device: payload_models.UserDevicePayload) -> layer_models.UserDevice:
        """
        :raises UniqueConstraintError: если устройство с указанным user_agent для указанного пользователя
         уже существует
        """
        ...

    def get_allowed_device(self, device: payload_models.UserDevicePayload) -> layer_models.UserDevice:
        ...

    def get_allowed_devices(self, user: uuid.UUID) -> list[layer_models.UserDevice]:
        ...

    def add_new_session(self, session: payload_models.SessionPayload) -> layer_models.Session:
        ...

    def get_user_permissions(self, user_id: uuid.UUID) -> list[layer_models.Permission]:
        ...

    def get_history(self, user_id: uuid.UUID, paginate: Pagination) -> list[layer_models.Session]:
        ...

    def get_user_roles(self, user_id: uuid.UUID) -> list[layer_models.Role]:
        ...

    def add_role_for_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        """
        :raises NotFoundError: если роль с указанным id несуществует
        :raises UniqueConstraintError: если указанная связь между ролью и пользователем уже сущетсвует
        """
        ...

    def delete_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        """
        :raises NotFoundError: если связи RoleUser с указанными id user и role несуществует
        """
        ...


class TMStorageTransaction(typing.Protocol):
    def set(self, key: str | bytes, value: bytes, ex: int | datetime.timedelta | None = None) -> None:
        ...

    def delete(self, key: str | bytes) -> None:
        ...


class UserTmStorageRepositoryProtocol(typing.Protocol):
    @staticmethod
    def get(key: str | bytes) -> typing.Any:
        ...

    @staticmethod
    def set(key: str | bytes, value: bytes, ex: int | datetime.timedelta | None = None) -> None:
        ...

    @staticmethod
    def delete(*keys: str | bytes) -> None:
        ...

    @staticmethod
    @contextmanager
    def transaction() -> typing.ContextManager[TMStorageTransaction]:
        ...
