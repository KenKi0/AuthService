import uuid

from flask_security.utils import hash_password, verify_password

import user.layer_models as layer_models
import user.payload_models as payload_models
import user.repositories as repo
import utils.exceptions as exc
from api.v1.utils import Pagination
from core.logger import get_logger

logger = get_logger(__name__)

db_repo = repo.get_user_db_repo()
tms_repo = repo.get_user_tms_repo()


class UserService:
    def __init__(
        self,
        db_repository: repo.UserRepositoryProtocol = db_repo,
    ):
        self.db_repo = db_repository

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

    def get_history(self, user: payload_models.UserID, paginate: Pagination) -> list[layer_models.Session]:
        """
        Отдает историю посещений пользователя на аккаунт
        :param paginate: данные пагинации
        :param user: данные пользователя
        :return: список из историй
        """
        return self.db_repo.get_history(user.user_id, paginate)

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
