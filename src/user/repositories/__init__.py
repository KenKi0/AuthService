from utils.exceptions import NotFoundError

from .protocol import UserFilter, UserRepositoryProtocol, UserTmStorageRepositoryProtocol
from .redis_repo import UserTmStorageRepository
from .sqlalchemy_repo import UserSqlalchemyRepository


def get_user_db_repo() -> UserRepositoryProtocol:
    return UserSqlalchemyRepository()


def get_user_tms_repo() -> UserTmStorageRepositoryProtocol:
    return UserTmStorageRepository


__all__ = [
    'NotFoundError',
    'UserFilter',
    'UserRepositoryProtocol',
    'UserSqlalchemyRepository',
    'UserTmStorageRepositoryProtocol',
]
