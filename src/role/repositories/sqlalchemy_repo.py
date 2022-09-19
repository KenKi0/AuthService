import uuid

import role.layer_models as layer_models
import role.payload_models as payload_models
import role.repositories.protocol as protocol
import utils.exceptions as exc
from db import session_scope
from models.permissions import Permission, RolePermission
from models.role import Role


class RoleSqlalchemyRepository(protocol.RoleRepositoryProtocol):
    def get_multi(self) -> list[layer_models.Role]:
        roles = Role.query.all()
        return [layer_models.Role.from_orm(role) for role in roles]

    def get_by_id(self, role_id: uuid.UUID) -> layer_models.Role:
        role = Role.query.filter(Role.id == role_id)
        if role.count() == 0:
            raise exc.NotFoundError
        return layer_models.Role.from_orm(role.first())

    def get_by_name(self, name: str) -> layer_models.Role:
        role = Role.query.filter(Role.name == name)
        if role.count() == 0:
            raise exc.NotFoundError
        return layer_models.Role.from_orm(role.first())

    def update(self, role_id: uuid.UUID, updated_role: payload_models.RoleUpdate) -> layer_models.Role:
        with session_scope():
            role = Role.query.filter(Role.id == role_id)
            if role.count() != 1:
                raise exc.NotFoundError
            role.update(updated_role.dict(exclude_none=True))
        return layer_models.Role.from_orm(role.first())

    def create(self, new_role: payload_models.RoleCreate) -> layer_models.Role:
        new_role = Role(**new_role.dict())
        with session_scope() as db_session:
            db_session.add(new_role)
            db_session.flush()
            return layer_models.Role.from_orm(new_role)

    def delete(self, role_id: uuid.UUID) -> None:
        with session_scope():
            role = Role.query.filter(Role.id == role_id)
            if role.count() != 1:
                raise exc.NotFoundError
            role.update({'is_deleted': True})

    def add_permission_for_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        perm = Permission.query.filter(Permission.id == permission_id)
        if perm.count() != 1:
            raise exc.NotFoundError
        new_link = RolePermission(role_id=role_id, permission_id=permission_id)
        with session_scope() as db_session:
            db_session.add(new_link)

    def delete_permission_from_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        with session_scope():
            role_permission = RolePermission.query.filter(
                RolePermission.role_id == role_id,
                RolePermission.perm_id == permission_id,
            )
            if role_permission.count() != 1:
                raise exc.NotFoundError
            role_permission.update({'is_deleted': True})
