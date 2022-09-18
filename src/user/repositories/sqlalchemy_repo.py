import uuid
from dataclasses import asdict

import user.layer_models as layer_models
import user.payload_models as payload_models
import user.repositories.protocol as protocol
import utils.exceptions as exc
from db import session_scope
from models import AllowedDevice, Permission, Role, RolePermission, RoleUser, Session, User

DEFAULT_USER_ROLE = 'User'


class UserSqlalchemyRepository(protocol.UserRepositoryProtocol):
    def get_by_id(self, user_id: uuid.UUID) -> layer_models.User:
        user = User.query.filter(User.id == user_id, User.is_deleted == False).first()  # noqa: E712
        if user is None:
            raise exc.NotFoundError
        return layer_models.User.from_orm(user)

    def get_by_email(self, email: str) -> layer_models.User:
        user = User.query.filter(User.email == email, User.is_deleted == False).first()  # noqa: E712
        if user is None:
            raise exc.NotFoundError
        return layer_models.User.from_orm(user)

    def get_multi(self, filters: protocol.UserFilter | None = None) -> list[layer_models.User]:
        users = User.query.filter(User.is_deleted == False)  # noqa: E712
        if filters:
            for filter_name, filter_value in asdict(filters).items():
                model_attribute = getattr(User, filter_name, None)
                if model_attribute is not None:
                    users = users.filter(model_attribute == filter_value)

        return [layer_models.User.from_orm(user) for user in users.all()]

    def create(self, user: payload_models.UserCreatePayload) -> layer_models.User:
        new_user = User(**user.dict())
        role = Role.query.filter(Role.name == DEFAULT_USER_ROLE).first()
        with session_scope() as db_session:
            db_session.add(new_user)
            db_session.flush()
            role_user = RoleUser(user_id=new_user.id, role_id=role.id)
            db_session.add(role_user)
            return layer_models.User.from_orm(new_user)

    def update(self, user_id: uuid.UUID, new_user: payload_models.UserUpdatePayload) -> layer_models.User:
        with session_scope():
            user = User.query.filter(User.id == user_id, User.is_deleted == False)  # noqa: E712
            if user.count() != 1:
                raise exc.NotFoundError
            user.update(**new_user.dict(exclude_none=True))
        return layer_models.User.from_orm(user)

    def delete(self, user_id: uuid.UUID) -> layer_models.User | None:
        with session_scope():
            user = User.query.filter(User.id == user_id, User.is_deleted == False)  # noqa: E712
            if user.count() != 1:
                raise exc.NotFoundError
            user.cond_delete()
        return layer_models.User.from_orm(user)

    def add_allowed_device(self, device: payload_models.UserDevicePayload) -> layer_models.UserDevice:
        new_device = AllowedDevice(**device.dict())
        with session_scope() as db_session:
            db_session.add(new_device)
            db_session.flush()
            return layer_models.UserDevice.from_orm(new_device)

    def get_allowed_device(self, device: payload_models.UserDevicePayload) -> layer_models.UserDevice:
        device = AllowedDevice.query.filter(
            AllowedDevice.user_id == device.user_id,
            AllowedDevice.user_agent == device.user_agent,
            AllowedDevice.is_deleted == False,  # noqa: E712
        )
        if device.count() == 0:
            raise exc.NotFoundError
        return layer_models.UserDevice.from_orm(device)

    def get_allowed_devices(self, user_id: uuid.UUID) -> list[layer_models.UserDevice]:
        devices = AllowedDevice.query.filter(
            AllowedDevice.user_id == user_id,
            AllowedDevice.is_deleted == False,  # noqa: E712
        ).all()
        return [layer_models.UserDevice.from_orm(device) for device in devices]

    def get_history(self, user_id: uuid.UUID) -> list[layer_models.Session]:
        user_histories = Session.query.filter(
            Session.user_id == user_id,
            Session.is_deleted == False,  # noqa: E712
        ).all()
        return [layer_models.Session.from_orm(user_history) for user_history in user_histories]

    def add_new_session(self, session: payload_models.SessionPayload) -> layer_models.Session:
        new_session = Session(**session.dict())
        with session_scope() as db_session:
            db_session.add(new_session)
            db_session.flush()
            return layer_models.Session.from_orm(new_session)

    def get_user_permissions(self, user_id: uuid.UUID) -> list[layer_models.Permission]:
        query = Permission.query
        query = query.join(RolePermission).join(RoleUser, RoleUser.role_id == RolePermission.role_id)
        permissions = query.filter(RoleUser.user_id == user_id, Permission.is_deleted == False).all()  # noqa: E712
        return [layer_models.Permission.from_orm(permission) for permission in permissions]
