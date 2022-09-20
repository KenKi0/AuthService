from .protocol import PermissionRepositoryProtocol
from .sqlalchemy_repo import PermissionSqlalchemyRepository


def get_perm_db_repo() -> PermissionRepositoryProtocol:
    return PermissionSqlalchemyRepository()


__all__ = [
    'get_perm_db_repo',
    'PermissionRepositoryProtocol',
    'PermissionSqlalchemyRepository',
]
