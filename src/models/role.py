from db.db import db
from utils import BaseModel
from flask_security import RoleMixin


class Role(BaseModel, RoleMixin):
    __tablename__ = 'roles'
    name = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    description = db.Column(db.String(length=150), nullable=False)

    def __repr__(self) -> str:
        return f'Role: {self.name} {self.id}'


class RoleUser(BaseModel):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.String, db.ForeignKey('auth.users.id'), nullable=False)
    role_id = db.Column(db.String, db.ForeignKey('auth.roles.id'), nullable=False)
