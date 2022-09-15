from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from flask_security.utils import hash_password, verify_password

import user.layer_models as layer_models
import user.payload_models as payload_models
import user.repositories as repo
from core.config import settings

db_repo = repo.get_user_db_repo()
tms_repo = repo.get_user_tms_repo()


class InvalidPassword(Exception):
    ...


class NoAccessError(Exception):
    ...


class EmailAlreadyExist(Exception):
    ...


class UserService:
    def __init__(
        self,
        db_repository: repo.UserRepositoryProtocol = db_repo,
        tm_storage_repository: repo.UserTmStorageRepositoryProtocol = tms_repo,
    ):
        self.db_repo = db_repository
        self.tms_repo = tm_storage_repository

    def register(self, new_user: payload_models.UserCreatePayload) -> None:
        """
        Создает пользователя если не существует пользователя с указанным email
        :param new_user: данные нового пользователя
        :raises : EmailAlreadyExist
        """
        try:
            self.db_repo.get_by_email(new_user.email)
        except repo.NotFoundError:
            new_user.password = hash_password(new_user.password)
            self.db_repo.create(new_user)
        raise EmailAlreadyExist

    def login(self, user_payload: payload_models.UserLoginPayload) -> tuple[str, str]:
        """
        При верных указанных данных возвращает access и refresh токены пользователя
        :param user_payload: данные пользователя для входа
        :return: кортеж из access и refresh токенов
        :raises :
            NotFoundError : если не получилось идентефицировать пользователя
            InvalidPassword : если не получлось аутентифицировать пользователя
        """
        user = self.db_repo.get_by_email(user_payload.email)
        if not user:
            raise repo.NotFoundError
        if not verify_password(user_payload.password, user.password):
            raise InvalidPassword
        device = payload_models.UserDevicePayload(user_id=user.id, user_agent=user_payload.user_agent)
        try:
            user_device = self.db_repo.get_allowed_device(device)
        except repo.NotFoundError:
            # TODO подтвердить вход с нового устройства через email
            user_device = self.db_repo.add_allowed_device(device)
        self.db_repo.set_new_session(payload_models.SessionPayload(user_id=user.id, device_id=user_device.id))
        user_permissions = self.db_repo.get_user_permissions(user.id)
        additional_claims = {
            'permissions': [permission.code for permission in user_permissions],
            'is_super': user.is_super,
        }
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims,
            expires_delta=settings.ACCESS_TOKEN_EXP_DELTA,
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=settings.REFRESH_TOKEN_EXP_DELTA,
        )
        tms_key = user_payload.user_agent + str(user.id)
        self.tms_repo.set(tms_key, refresh_token)
        return access_token, refresh_token

    def change_password(self, passwords: payload_models.ChangePasswordPayload) -> None:
        """
        Меняет пароль указанного пользователя
        :param passwords: данные для смены пароля пользователя
        :raises :
            NoAccessError : если была попытка изменить пароль другого пользователя
            NotFoundError : если указанный пользователь не был найден в базе
            InvalidPassword : если был указан не правильный текущий пароль
        """
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
        self.db_repo.update(passwords.user_id, payload_models.UserUpdatePayload(password=passwords.new_password))

    def refresh_tokens(self, token: payload_models.RefreshTokensPayload) -> tuple[str, str]:
        """
        Выдает новые access и refresh токены для указанного пользователя
        :param token: данные для обнволения токенов
        :return: кортеж из access и refresh токенов
        :raises :
            NoAccessError : если была попытка получить токены другого пользователя
            NotFoundError : если указанный пользователь не был найден в базе
            InvalidPassword : если был указан не правильный текущий пароль
        """
        try:
            user = self.db_repo.get_by_id(token.user_id)
        except repo.NotFoundError:
            # TODO логировать ошибку
            raise
        token_user = get_jwt_identity()
        if user.id != token_user:
            raise NoAccessError
        tms_key = token.user_agent + str(token.user_id)
        current_token = self.tms_repo.get(tms_key)
        if current_token != token.refresh:
            raise NoAccessError
        user_permissions = self.db_repo.get_user_permissions(token_user)
        additional_claims = {
            'permissions': [permission.code for permission in user_permissions],
            'is_super': user.is_super,
        }
        access_token = create_access_token(
            identity=token_user,
            additional_claims=additional_claims,
            expires_delta=settings.ACCESS_TOKEN_EXP_DELTA,
        )
        refresh_token = create_refresh_token(
            identity=token_user,
            expires_delta=settings.REFRESH_TOKEN_EXP_DELTA,
        )
        self.tms_repo.set(tms_key, refresh_token)
        return access_token, refresh_token

    def get_history(self, user: payload_models.UserID) -> list[layer_models.Session]:
        """
        Отдает историю посещений пользователя на аккаунт
        :param user: данные пользователя
        :return: список из историй
        :raises :
            NoAccessError : если была попатка получить истории другого пользователя
        """
        token_user = get_jwt_identity()
        if user.user_id != token_user:
            raise NoAccessError
        return self.db_repo.get_history(user.user_id)

    def logout(self, logout: payload_models.LogoutPayload):
        """
        Заверщает текущюю или все активные сессис аккаунта
        :param logout: данные пользователя
        :raises :
            NoAccessError : если была попытка выйти из чужого аккаунта
        """
        token_user = get_jwt_identity()
        if logout.user_id != token_user:
            raise NoAccessError
        if logout.from_all:
            devices = self.db_repo.get_allowed_devices(logout.user_id)
        else:
            devices = [
                self.db_repo.get_allowed_device(
                    payload_models.UserDevicePayload(user_id=logout.user_id, user_agent=logout.user_agent),
                ),
            ]
        tms_keys = [device.user_agent + str(token_user) for device in devices]
        self.tms_repo.delete(*tms_keys)
