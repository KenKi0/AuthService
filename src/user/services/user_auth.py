from flask_jwt_extended import create_access_token, create_refresh_token
from flask_security.utils import hash_password, verify_password

import user.payload_models as payload_models
import user.repositories as repo
import utils.exceptions as exc
import utils.types as types
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)

db_repo = repo.get_user_db_repo()
tms_repo = repo.get_user_tms_repo()


class UserAuthService:
    def __init__(
        self,
        db_repository: repo.UserRepositoryProtocol = db_repo,
        tm_storage_repository: repo.UserTmStorageRepositoryProtocol = tms_repo,
    ):
        self.db_repo = db_repository
        self.tms_repo = tm_storage_repository

    def register(self, new_user: payload_models.UserCreatePayload) -> None:
        """
        Создает пользователя если не существует пользователя с указанным email.

        :param new_user: данные нового пользователя
        :raises EmailAlreadyExist:
        """
        try:
            new_user.password = hash_password(new_user.password)
            self.db_repo.create(new_user)
        except exc.UniqueConstraintError as ex:
            logger.info('Ошибка при попытке зарегестрировать нового пользователя: \n %s', str(ex))
            raise exc.EmailAlreadyExist from ex

    def login(self, user_payload: payload_models.UserLoginPayload) -> tuple[types.AccessToken, types.RefreshToken]:
        """
        При верных указанных данных возвращает access и refresh токены пользователя.

        :param user_payload: данные пользователя для входа
        :return: кортеж из access и refresh токенов
        :raises NotFoundError: если не получилось идентефицировать пользователя
        :raises InvalidPassword: если не получлось аутентифицировать пользователя
        """
        try:
            user = self.db_repo.get_by_email(user_payload.email)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке получить пользователя: \n %s', str(ex))
            raise
        if not verify_password(user_payload.password, user.password):
            raise exc.InvalidPassword
        device = payload_models.UserDevicePayload(user_id=user.id, user_agent=user_payload.user_agent)
        try:
            user_device = self.db_repo.get_allowed_device(device)
        except exc.NotFoundError:
            # TODO подтвердить вход с нового устройства через email
            user_device = self.db_repo.add_allowed_device(device)
        self.db_repo.add_new_session(payload_models.SessionPayload(user_id=user.id, device_id=user_device.id))
        user_permissions = self.db_repo.get_user_permissions(user.id)
        additional_claims = {
            'permissions': [permission.code for permission in user_permissions],
            'is_super': user.is_super,
        }
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims,
            expires_delta=settings.jwt.ACCESS_TOKEN_EXP,
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=settings.jwt.REFRESH_TOKEN_EXP,
        )
        self.tms_repo.set(
            user_payload.user_agent + str(user.id),
            refresh_token,
            ex=settings.jwt.REFRESH_TOKEN_EXP,
        )
        return access_token, refresh_token

    def refresh_tokens(
        self,
        token: payload_models.RefreshTokensPayload,
    ) -> tuple[types.AccessToken, types.RefreshToken]:
        """
        Выдает новые access и refresh токены для указанного пользователя.

        :param token: данные для обнволения токенов
        :return: кортеж из access и refresh токенов
        :raises NotFoundError: если указанный пользователь не был найден в базе
        :raises NoAccessError: если укзанный рефреш токен не совпадает с активным
        """
        try:
            user = self.db_repo.get_by_id(token.user_id)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке обновить токены пользователя: \n %s', str(ex))
            raise
        tms_key = token.user_agent + str(token.user_id)
        current_token = self.tms_repo.get(tms_key)
        if current_token != token.refresh:
            raise exc.NoAccessError
        user_permissions = self.db_repo.get_user_permissions(user.id)
        additional_claims = {
            'permissions': [permission.code for permission in user_permissions],
            'is_super': user.is_super,
        }
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims,
            expires_delta=settings.jwt.ACCESS_TOKEN_EXP,
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=settings.jwt.REFRESH_TOKEN_EXP,
        )
        self.tms_repo.set(tms_key, refresh_token, ex=settings.jwt.REFRESH_TOKEN_EXP)
        return access_token, refresh_token

    def logout(self, logout: payload_models.LogoutPayload) -> None:
        """
        Завершает текущюю или все активные сессис аккаунта
        :param logout: данные пользователя
        :raises NotFoundError: если не было найдено устройства в разрешенных устройствах пользователя
        """
        if logout.from_all:
            devices = self.db_repo.get_allowed_devices(logout.user_id)
            if not devices:
                raise exc.NotFoundError
        else:
            try:
                devices = [
                    self.db_repo.get_allowed_device(
                        payload_models.UserDevicePayload(user_id=logout.user_id, user_agent=logout.user_agent),
                    ),
                ]
            except exc.NotFoundError as ex:
                logger.info('Ошибка при попытке ыйти из аккаунта: \n %s', str(ex))
                raise
        tms_keys = [device.user_agent + str(logout.user_id) for device in devices]
        self.tms_repo.delete(*tms_keys)
