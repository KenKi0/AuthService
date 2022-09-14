from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from flask_security.utils import hash_password, verify_password

import user.layer_models as layer_models
import user.repositories as repo
from core.config import settings

default_repo = repo.get_user_repo()


class InvalidPassword(Exception):
    ...


class NoAccessError(Exception):
    ...


class UserService:
    def __init__(self, repository: repo.UserRepositoryProtocol = default_repo):
        self.repo = repository

    def register(self, new_user: layer_models.UserCreate) -> layer_models.User:
        if self.repo.get_by_email(new_user.email):
            raise repo.EmailAlreadyExist
        new_user.password = hash_password(new_user.password)
        return self.repo.create(new_user)

    def login(self, user_payload: layer_models.UserLogin):
        user = self.repo.get_by_email(user_payload.email)
        if not user:
            raise repo.NotFoundError
        if not verify_password(user_payload.password, user.password):
            raise InvalidPassword
        device = layer_models.UserDevice(user_id=user.id, user_agent=user_payload.user_agent)
        try:
            user_device = self.repo.get_allowed_device(device)
        except repo.NotFoundError:
            # TODO подтвердить вход с нового устройства через email
            user_device = self.repo.add_allowed_device(device)
        session = layer_models.Session(user_id=user.id, device_id=user_device.id)
        self.repo.set_new_session(session)
        access_token = create_access_token(
            identity=user.id,
            expires_delta=settings.ACCESS_TOKEN_EXP_DELTA,
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=settings.REFRESH_TOKEN_EXP_DELTA,
        )
        # TODO обновить refresh_token в редисе
        return access_token, refresh_token

    def change_password(self, passwords: layer_models.ChangePassword):
        token_user = get_jwt_identity()
        if passwords.user_id != token_user:
            raise NoAccessError
        try:
            user = self.repo.get_by_id(passwords.user_id)
        except repo.NotFoundError:
            # TODO логировать ошибку
            raise
        if not verify_password(passwords.old_password, user.password):
            raise InvalidPassword
        self.repo.update(passwords.user_id, layer_models.UserUpdate(password=passwords.new_password))

    def refresh_tokens(self, token: layer_models.RefreshTokens):
        token_user = get_jwt_identity()
        if token.user_id != token_user:
            raise NoAccessError
        # TODO сделать запрос в редис и получить токен и сравнить с текущим
        access_token = create_access_token(
            identity=token_user,
            expires_delta=settings.ACCESS_TOKEN_EXP_DELTA,
        )
        refresh_token = create_refresh_token(
            identity=token_user,
            expires_delta=settings.REFRESH_TOKEN_EXP_DELTA,
        )
        # TODO обновить refresh_token в редисе
        return access_token, refresh_token

    def get_history(self, user: layer_models.UserID) -> list[layer_models.UserHistory]:
        token_user = get_jwt_identity()
        if user.user_id != token_user:
            raise NoAccessError
        return self.repo.get_history(user.user_id)

    def logout(self, logout: layer_models.Logout):
        token_user = get_jwt_identity()
        if logout.user_id != token_user:
            raise NoAccessError
        if logout.from_all:
            devices = self.repo.get_allowed_devices(logout.user_id)
        else:
            devices = [
                self.repo.get_allowed_device(
                    layer_models.UserDevice(user_id=logout.user_id, user_agent=logout.user_agent),
                ),
            ]
        for _ in devices:
            ...
            # TODO удалить рефреш токены всех этих устройств из редиса
