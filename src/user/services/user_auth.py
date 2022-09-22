import uuid

from flask_jwt_extended import create_access_token, create_refresh_token
from flask_security.utils import hash_password, verify_password

import user.layer_models as layer_models
import user.payload_models as payload_models
import user.repositories as repo
import utils.exceptions as exc
import utils.types as types
from api.v1.utils import Pagination
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)

db_repo = repo.get_user_db_repo()
tms_repo = repo.get_user_tms_repo()


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
        user = self.db_repo.get_by_email(user_payload.email)
        if not user:
            raise exc.NotFoundError
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

    def change_password(self, passwords: payload_models.ChangePasswordPayload) -> None:
        """
        Меняет пароль указанного пользователя.

        :param passwords: данные для смены пароля пользователя
        :raises NotFoundError: если указанный пользователь не был найден в базе
        :raises InvalidPassword: если был указан не правильный текущий пароль
        """
        try:
            user = self.db_repo.get_by_id(passwords.user_id)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке изменить пароль пользователя: \n %s', str(ex))
            raise
        if not verify_password(passwords.old_password, user.password):
            raise exc.InvalidPassword
        self.db_repo.update(
            passwords.user_id,
            payload_models.UserUpdatePayload(password=hash_password(passwords.new_password)),
        )

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

    def get_history(self, user: payload_models.UserID, paginate: Pagination) -> list[layer_models.Session]:
        """
        Отдает историю посещений пользователя на аккаунт
        :param paginate: данные пагинации
        :param user: данные пользователя
        :return: список из историй
        """
        return self.db_repo.get_history(user.user_id, paginate)

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

    def get_roles(self, user_id: uuid.UUID) -> list[layer_models.Role]:
        """
        Получить все роли пользователя.

        :param user_id: id пользователя
        :return: список с ролями
        :raises NotFoundError: если пользователя с таким id несущетвует
        """
        try:
            self.db_repo.get_by_id(user_id)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке получить роли пользователя: \n %s', str(ex))
            raise
        return self.db_repo.get_user_roles(user_id)

    def add_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        """
        Выдать роль пользователю.

        :param user_id: id пользователя
        :param role_id: id роли
        :raises NotFoundError: если пользователь или роль с указанными id несущетвуют
        :raises UniqueConstraintError: если указанная связь между ролью и пользователем уже сущетсвует
        """
        try:
            return self.db_repo.add_role_for_user(user_id, role_id)
        except (exc.NotFoundError, exc.UniqueConstraintError) as ex:
            logger.info('Ошибка при попытке присвоить роль пользователю: \n %s', str(ex))
            raise

    def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        """
        Отобрать роль у пользователя.

        :param user_id: id пользователя
        :param role_id: id роли
        :raises NotFoundError: если связи между указанными пользователем и ролью несущетвует
        """
        try:
            return self.db_repo.delete_role_from_user(user_id, role_id)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке отобрать роль у пользователя: \n %s', str(ex))
            raise
