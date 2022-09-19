import typing
import uuid

import role.layer_models as layer_models
import role.payload_models as payload_models


class RoleRepositoryProtocol(typing.Protocol):
    def get_multi(self) -> list[layer_models.Role]:
        ...

    def get_by_id(self, role_id: uuid.UUID) -> layer_models.Role:
        ...

    def get_by_name(self, name: str) -> layer_models.Role:
        ...

    def update(self, role_id: uuid.UUID, updated_role: payload_models.RoleUpdate) -> layer_models.Role:
        ...

    def create(self, new_role: payload_models.RoleCreate) -> layer_models.Role:
        ...

    def delete(self, role_id: uuid.UUID) -> None:
        ...

    def add_permission_for_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        ...

    def delete_permission_from_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        ...
