import uuid

import permission.layer_models as layer_models
import permission.payload_models as payload_models
import permission.repositories as repo
import utils.exceptions as exc
from core.logger import get_logger

logger = get_logger(__name__)

db_repo = repo.get_perm_db_repo()


class PermissionService:
    def __init__(self, repository: repo.PermissionRepositoryProtocol = db_repo):
        self.repo = repository

    def get(self, perm_id: uuid.UUID) -> layer_models.Permission:
        """
        Получить премишан по id.

        :param perm_id: id пермишана
        :return: пермишан
        :raises NotFoundError: пермишана с указанным id несуществует
        """
        try:
            return self.repo.get_by_id(perm_id)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке получить пермишан: \n %s', str(ex))
            raise

    def get_all(self) -> list[layer_models.Permission]:
        """
        Получить все пермишены.

        :return: список всех пермишанов
        """
        return self.repo.get_multi()

    def create(self, new_perm: payload_models.PermissionCreate) -> None:
        """
        Создать пермишан по указанным данным.

        :param new_perm: данные пермишана
        :raises UniqueConstraintError: если случился конфликтов уникальному значению code
        """
        try:
            self.repo.create(new_perm)
        except exc.UniqueConstraintError as ex:
            logger.info('Ошибка при попытке создать пермишан: \n %s', str(ex))
            raise

    def update(self, perm_id: uuid.UUID, update_perm: payload_models.PermissionUpdate) -> None:
        """
        Обновить данные пермишана.

        :param perm_id: id пермишана
        :param update_perm: новые данные пермишана
        :raises UniqueConstraintError: если случился конфликтов уникальному значению code
        :raises NotFoundError: если пермишана с указанным id несуществует
        """
        try:
            self.repo.update(perm_id, update_perm)
        except (exc.NotFoundError, exc.UniqueConstraintError) as ex:
            logger.info('Ошибка при попытке обновить данные пермишана: \n %s', str(ex))
            raise

    def delete(self, perm_id: uuid.UUID) -> None:
        """
        Удалить пермишан.

        :param perm_id: id пермишана
        :raises NotFoundError: если пермишана с указанным id несуществует
        """
        try:
            self.repo.delete(perm_id)
        except exc.NotFoundError as ex:
            logger.info('Ошибка при попытке удалить пермишан: \n %s', str(ex))
            raise
