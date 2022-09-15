from flask_security import RoleMixin
from sqlalchemy.dialects.postgresql import UUID

from db.db import db
from models.utils import BaseModel


class Role(BaseModel, RoleMixin):
    __tablename__ = 'roles'
    name = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    description = db.Column(db.String(length=150), nullable=False)

    def __repr__(self) -> str:
        return f'Role: {self.name} {self.id}'


class RoleUser(BaseModel):
    __tablename__ = 'users_roles'
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id'), {'schema': 'auth'})
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.roles.id'), nullable=False)
