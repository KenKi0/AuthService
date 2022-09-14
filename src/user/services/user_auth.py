from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from flask_security.utils import hash_password, verify_password

import user.layer_models as layer_models
import user.repositories as repo
from core.config import settings

db_repo = repo.get_user_db_repo()
tms_repo = repo.get_user_tms_repo()


class InvalidPassword(Exception):
    ...


class NoAccessError(Exception):
    ...


class UserService:
    def __init__(
        self,
        db_repository: repo.UserRepositoryProtocol = db_repo,
        tm_storage_repository: repo.UserTmStorageRepositoryProtocol = tms_repo,
    ):
        self.db_repo = db_repository
        self.tms_repo = tm_storage_repository

    def register(self, new_user: layer_models.UserCreate) -> layer_models.User:
        if self.db_repo.get_by_email(new_user.email):
            raise repo.EmailAlreadyExist
        new_user.password = hash_password(new_user.password)
        return self.db_repo.create(new_user)

    def login(self, user_payload: layer_models.UserLogin):
        user = self.db_repo.get_by_email(user_payload.email)
        if not user:
            raise repo.NotFoundError
        if not verify_password(user_payload.password, user.password):
            raise InvalidPassword
        device = layer_models.UserDevice(user_id=user.id, user_agent=user_payload.user_agent)
        try:
            user_device = self.db_repo.get_allowed_device(device)
        except repo.NotFoundError:
            # TODO подтвердить вход с нового устройства через email
            user_device = self.db_repo.add_allowed_device(device)
        session = layer_models.Session(user_id=user.id, device_id=user_device.id)
        self.db_repo.set_new_session(session)
        access_token = create_access_token(
            identity=user.id,
            expires_delta=settings.ACCESS_TOKEN_EXP_DELTA,
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=settings.REFRESH_TOKEN_EXP_DELTA,
        )
        tms_key = user_payload.user_agent + str(user.id)
        self.tms_repo.set(tms_key, refresh_token)
        return access_token, refresh_token

    def change_password(self, passwords: layer_models.ChangePassword):
        token_user = get_jwt_identity()
        if passwords.user_id != token_user:
            raise NoAccessError
        try:
            user = self.db_repo.get_by_id(passwords.user_id)
        except repo.NotFoundError:
            # TODO логировать ошибку
            raise
        if not verify_password(passwords.old_password, user.password):
            raise InvalidPassword
        self.db_repo.update(passwords.user_id, layer_models.UserUpdate(password=passwords.new_password))

    def refresh_tokens(self, token: layer_models.RefreshTokens):
        token_user = get_jwt_identity()
        if token.user_id != token_user:
            raise NoAccessError
        tms_key = token.user_agent + str(token.user_id)
        current_token = self.tms_repo.get(tms_key)
        if current_token != token.refresh:
            raise NoAccessError
        access_token = create_access_token(
            identity=token_user,
            expires_delta=settings.ACCESS_TOKEN_EXP_DELTA,
        )
        refresh_token = create_refresh_token(
            identity=token_user,
            expires_delta=settings.REFRESH_TOKEN_EXP_DELTA,
        )
        self.tms_repo.set(tms_key, refresh_token)
        return access_token, refresh_token

    def get_history(self, user: layer_models.UserID) -> list[layer_models.UserHistory]:
        token_user = get_jwt_identity()
        if user.user_id != token_user:
            raise NoAccessError
        return self.db_repo.get_history(user.user_id)

    def logout(self, logout: layer_models.Logout):
        token_user = get_jwt_identity()
        if logout.user_id != token_user:
            raise NoAccessError
        if logout.from_all:
            devices = self.db_repo.get_allowed_devices(logout.user_id)
        else:
            devices = [
                self.db_repo.get_allowed_device(
                    layer_models.UserDevice(user_id=logout.user_id, user_agent=logout.user_agent),
                ),
            ]
        tms_keys = [device.user_agent + str(token_user) for device in devices]
        self.tms_repo.delete(*tms_keys)
        with self.tms_repo.transaction() as tr:
            for device in devices:
                tr.delete(device.user_agent + str(logout.user_id))
