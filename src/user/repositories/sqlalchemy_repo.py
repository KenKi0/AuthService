import uuid
from dataclasses import asdict

import user.layer_models as layer_models
import user.repositories.protocol as protocol
from db import session_scope
from models import AllowedDevice, Session, User


class UserRepository(protocol.UserRepositoryProtocol):
    def get_by_id(self, user_id: uuid.UUID) -> layer_models.User:
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise protocol.NotFoundError
        return layer_models.User.parse_obj(user)

    def get_by_email(self, email: str) -> layer_models.User:
        user = User.query.filter(User.email == email).first()
        if user is None:
            raise protocol.NotFoundError
        return layer_models.User.parse_obj(user)

    def get_multi(self, filters: protocol.UserFilter | None = None) -> list[layer_models.User]:
        users = User.query
        if filters:
            for filter_name, filter_value in asdict(filters).items():
                model_attribute = getattr(User, filter_name, None)
                if model_attribute is not None:
                    users = users.filter(model_attribute == filter_value)

        return [layer_models.User.parse_obj(user) for user in users.all()]

    def update(self, user_id: uuid.UUID, new_user: layer_models.UserUpdate) -> layer_models.User | None:
        with session_scope():
            user = User.query.filter(User.id == user_id)
            if user.count() != 1:
                raise protocol.NotFoundError
            user.update(**new_user.dict(exclude_none=True))
        return layer_models.User.parse_obj(user)

    def delete(self, user_id: uuid.UUID) -> layer_models.User | None:
        with session_scope():
            user = User.query.filter(User.id == user_id)
            if user.count() != 1:
                raise protocol.NotFoundError
            user.delete()
        return layer_models.User.parse_obj(user)

    def get_history(self, user_id: uuid.UUID) -> list[layer_models.UserHistory]:
        user_histories = Session.query.filter(Session.user_id == user_id).all()
        return [layer_models.UserHistory.parse_obj(user_history) for user_history in user_histories]

    def create(self, user: layer_models.UserCreate) -> layer_models.User:
        new_user = User(**user.dict())
        with session_scope() as db_session:
            db_session.add(new_user)
        return layer_models.User.parse_obj(new_user)

    def get_allowed_device(self, device: layer_models.UserDevice) -> layer_models.UserDevice:
        device = AllowedDevice.query.filter(
            AllowedDevice.user_id == device.user_id,
            AllowedDevice.user_agent == device.user_agent,
        ).first()
        return layer_models.UserDevice.parse_obj(device)

    def get_allowed_devices(self, user_id: uuid.UUID) -> list[layer_models.UserDevice]:
        devices = AllowedDevice.query.filter(AllowedDevice.user_id == user_id).all()
        return [layer_models.UserDevice.parse_obj(device) for device in devices]

    def set_new_session(self, session: layer_models.Session) -> None:
        new_session = Session(**session.dict())
        with session_scope() as db_session:
            db_session.add(new_session)

    def add_allowed_device(self, device: layer_models.UserDevice) -> layer_models.UserDevice:
        new_device = AllowedDevice(**device.dict())
        with session_scope() as db_session:
            db_session.add(new_device)
            db_session.flush()
            return layer_models.UserDevice.parse_obj(new_device)
