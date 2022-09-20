import uuid

import role.layer_models as layer_models
import role.payload_models as payload_models
import role.repositories as repo
import utils.exceptions as exc

db_repo = repo.get_role_db_repo()


class RoleService:
    def __init__(self, repository: repo.RoleRepositoryProtocol = db_repo):
        self.repo = repository

    def create(self, new_role: payload_models.RoleCreate) -> None:
        """
        Создать роль с указанными данными.

        :param new_role: данные роли
        :raises UniqueConstraintError: если роль с указанным именем уже сущетвует
        """
        try:
            self.repo.create(new_role)
        except exc.UniqueConstraintError:
            # TODO логировать ошибку
            raise

    def get(self, role_id: uuid.UUID) -> tuple[layer_models.Role, list[layer_models.Permission]]:
        """
        Получить роль по его id.

        :param role_id: id роли
        :return: указанную роль
        :raises NotFoundError: если нету роли с указанным id
        """
        try:
            return self.repo.get_by_id(role_id)
        except exc.NotFoundError:
            # TODO логировать ошибку
            raise

    def get_all(self) -> list[layer_models.Role]:
        """
        Получить все не удаленные роли.
        :return: список ролей
        """
        return self.repo.get_multi()

    def update(self, role_id: uuid.UUID, update_role: payload_models.RoleUpdate) -> layer_models.Role:
        """
        Обновить данные у указанной роли.

        :param role_id: id роли для изменения
        :param update_role: новые данные роли
        :return: обновленную роль
        :raises NotFoundError: если роль с указанным id несуществует
        :raises UniqueConstraintError: если роль с указанным именем уже существует
        """
        try:
            return self.repo.update(role_id, update_role)
        except (exc.NotFoundError, exc.UniqueConstraintError):
            # TODO логировать ошибку
            raise

    def delete(self, role_id) -> None:
        """
        Удалить указанную роль.

        :param role_id:
        :raises NotFoundError: если роль с указанным id несуществует
        """
        try:
            return self.repo.delete(role_id)
        except exc.NotFoundError:
            # TODO логировать ошибку
            raise

    def add_permission(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        """
        Добавить новый пермишан к роли.

        :param role_id: id роли к которому нужно добавить пермишан
        :param permission_id: id пермишана для добавления к роли
        :raises NotFoundError: если роль или пермишан с указанными id несуществуют
        :raises UniqueConstraintError: сли указанная связь между ролью и пермишаном уже существует
        """
        try:
            return self.repo.add_permission_for_role(role_id, permission_id)
        except (exc.NotFoundError, exc.UniqueConstraintError):
            # TODO логировать ошибку
            raise

    def remove_permission(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        """
        Убрать у роли пермишан.

        :param role_id: id роли
        :param permission_id: id пермишана
        :raises NotFoundError: если связи между укзанными ролем и пермишаном несуществуют
        """
        try:
            return self.repo.delete_permission_from_role(role_id, permission_id)
        except exc.NotFoundError:
            # TODO логировать ошибку
            raise
