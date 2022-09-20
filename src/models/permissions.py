from psycopg2.errors import UniqueViolation
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from db.db import db
from models.utils import BaseModel


class Permission(BaseModel):
    __tablename__ = 'permissions'
    name = db.Column(db.String(length=150), unique=True, nullable=False)
    code = db.Column(db.INTEGER, unique=True, nullable=False, index=True)
    description = db.Column(db.String(length=150), nullable=False)

    def __repr__(self) -> str:
        return f'Permission: {self.name} {self.id}'


class RolePermission(BaseModel):
    __tablename__ = 'roles_permissions'
    __table_args__ = (db.UniqueConstraint('perm_id', 'role_id'), {'schema': 'auth'})
    perm_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.permissions.id'), nullable=False)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.roles.id'), nullable=False)


def create_permission():
    default_permission = [
        {
            'name': 'Default user',
            'code': 0,
            'description': 'Может просматривать свой контент',
        },
        {
            'name': 'Subscriber',
            'code': 1,
            'description': 'Может смотреть бесплатный контент',
        },
        {
            'name': 'Vip subscriber',
            'code': 2,
            'description': 'Может смотреть платный контент',
        },
        {
            'name': 'Moderator',
            'code': 3,
            'description': 'Может работать с role',
        },
    ]

    for perm in default_permission:
        try:
            Permission(**perm).set()
        except (PendingRollbackError, UniqueViolation, IntegrityError):
            continue
