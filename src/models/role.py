from flask_security import RoleMixin
from psycopg2.errors import UniqueViolation
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from db.db import db
from models.utils import BaseModel


class Role(BaseModel, RoleMixin):
    __tablename__ = 'roles'
    protected = db.Column(db.Boolean(), nullable=False, default=False)
    name = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    description = db.Column(db.String(length=150), nullable=False)

    def __repr__(self) -> str:
        return f'Role: {self.name} {self.id}'


class RoleUser(BaseModel):
    __tablename__ = 'users_roles'
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id'), {'schema': 'auth'})
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.roles.id'), nullable=False)


def create_role():
    default_role = [
        {'name': 'User', 'description': 'new user', 'protected': True},
        {'name': 'Subscriber', 'description': 'subscriber'},
        {'name': 'Admin', 'description': 'admin'},
    ]
    for role in default_role:
        try:
            Role(**role).set()
        except (PendingRollbackError, UniqueViolation, IntegrityError):
            continue
