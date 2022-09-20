import typing
import uuid

import permission.layer_models as layer_models
import permission.payload_models as payload_models


class PermissionRepositoryProtocol(typing.Protocol):
    def get_by_id(self, perm_id: uuid.UUID) -> layer_models.Permission:
        """
        :raises NotFoundError:
        """
        ...

    def get_by_code(self, code: int) -> layer_models.Permission:
        """
        :raises NotFoundError:
        """
        ...

    def get_multi(self) -> list[layer_models.Permission]:
        ...

    def create(self, new_perm: payload_models.PermissionCreate) -> layer_models.Permission:
        """
        :raises UniqueConstraintError: конфликт уникальных значений
        """
        ...

    def update(self, perm_id: uuid.UUID, update_perm: payload_models.PermissionUpdate) -> layer_models.Permission:
        """
        :raises NotFoundError: пермишана с указаным id несуществует
        :raises UniqueConstraintError: конфликт уникальных значений
        """
        ...

    def delete(self, perm_id: uuid.UUID) -> None:
        """
        :raises NotFoundError: пермишана с указаным id несуществует
        """
        ...
