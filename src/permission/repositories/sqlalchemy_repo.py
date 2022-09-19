import uuid

import sqlalchemy.exc as sqlalch_exc

import permission.layer_models as layer_models
import permission.payload_models as payload_models
import permission.repositories.protocol as protocol
import utils.exceptions as exc
from db import session_scope
from models.permissions import Permission


class PermissionSqlalchemyRepository(protocol.PermissionRepositoryProtocol):
    def get_by_id(self, perm_id: uuid.UUID) -> layer_models.Permission:
        perm = Permission.query.filter(Permission.id == perm_id)
        if perm.count() != 1:
            raise exc.NotFoundError
        return layer_models.Permission.from_orm(perm.first())

    def get_by_code(self, code: int) -> layer_models.Permission:
        perm = Permission.query.filter(Permission.code == code)
        if perm.count() != 1:
            raise exc.NotFoundError
        return layer_models.Permission.from_orm(perm.first())

    def get_multi(self) -> list[layer_models.Permission]:
        perms = Permission.query.all()
        return [layer_models.Permission.from_orm(perm) for perm in perms]

    def create(self, new_perm: payload_models.PermissionCreate) -> layer_models.Permission:
        new_perm = Permission(**new_perm.dict())
        try:
            with session_scope() as session:
                session.add(new_perm)
                session.flush()
                return layer_models.Permission.from_orm(new_perm)
        except exc.UniqueConstraintError as ex:
            raise exc.UniqueConstraintError from ex

    def update(self, perm_id: uuid.UUID, update_perm: payload_models.PermissionUpdate) -> layer_models.Permission:
        try:
            with session_scope():
                perm = Permission.query.filter(Permission.id == perm_id)
                if perm.count() != 1:
                    raise exc.NotFoundError
                perm.update(update_perm.dict(exclude_none=True))
        except sqlalch_exc.IntegrityError as ex:
            raise exc.UniqueConstraintError from ex
        return layer_models.Permission.from_orm(perm.first())

    def delete(self, perm_id: uuid.UUID) -> None:
        with session_scope():
            perm = Permission.query.filter(Permission.id == perm_id)
            if perm.count() != 1:
                raise exc.NotFoundError
            perm.update({'is_deleted': True})
