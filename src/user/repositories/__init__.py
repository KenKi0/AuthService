from protocol import (
    EmailAlreadyExist,
    NotFoundError,
    UserFilter,
    UserRepositoryProtocol,
    UserTmStorageRepositoryProtocol,
)
from redis_repo import UserTmStorageRepository
from sqlalchemy_repo import UserRepository


def get_user_db_repo() -> UserRepositoryProtocol:
    return UserRepository()


def get_user_tms_repo() -> UserTmStorageRepositoryProtocol:
    return UserTmStorageRepository


__all__ = [
    'EmailAlreadyExist',
    'NotFoundError',
    'UserFilter',
    'UserRepositoryProtocol',
    'UserRepository',
    'UserTmStorageRepositoryProtocol',
]
