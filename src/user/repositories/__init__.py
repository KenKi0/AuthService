from protocol import EmailAlreadyExist, NotFoundError, UserFilter, UserRepositoryProtocol
from sqlalchemy_repo import UserRepository


def get_user_repo():
    return UserRepository()


__all__ = [
    'EmailAlreadyExist',
    'NotFoundError',
    'UserFilter',
    'UserRepositoryProtocol',
    'UserRepository',
]
