from sqlalchemy.dialects.postgresql import UUID

from db.db import db
from models.utils import BaseModel


class Permission(BaseModel):
    __tablename__ = 'permissions'
    name = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    description = db.Column(db.String(length=150), nullable=False)

    def __repr__(self) -> str:
        return f'Role: {self.name} {self.id}'


class RolePermission(BaseModel):
    __tablename__ = 'roles_permissions'
    perm_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.permissions.id'), nullable=False)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.roles.id'), nullable=False)
