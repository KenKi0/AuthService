from .protocol import RoleRepositoryProtocol
from .sqlalchemy_repo import RoleSqlalchemyRepository


def get_role_db_repo() -> RoleRepositoryProtocol:
    return RoleSqlalchemyRepository()


__all__ = [
    'get_role_db_repo',
    'RoleSqlalchemyRepository',
    'RoleRepositoryProtocol',
]
