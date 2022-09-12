from datetime import datetime

from flask_security import SQLAlchemyUserDatastore, UserMixin
from sqlalchemy.dialects.postgresql import UUID

from db.db import db
from models.role import Role
from models.utils import BaseModel


class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    username = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(length=150), nullable=False)
    email = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    active = db.Column(db.Boolean(), nullable=False)
    is_super = db.Column(db.Boolean(), default=False)

    def __repr__(self) -> str:
        return f'User: {self.username} {self.id}'


user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class UserInfo(BaseModel):
    __tablename__ = 'user_info'
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    full_name = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    birthday = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)

    def __repr__(self) -> str:
        return f'Login: {self.id} {self.date}'
