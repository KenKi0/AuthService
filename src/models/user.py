from datetime import datetime

from flask_security import UserMixin
from psycopg2.errors import UniqueViolation
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from db.db import db
from models.utils import BaseModel


class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    username = db.Column(db.String(length=150), nullable=False, index=True)
    password = db.Column(db.String(length=150), nullable=False)
    email = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    is_super = db.Column(db.Boolean(), default=False)

    def __repr__(self) -> str:
        return f'User: {self.username} {self.id}'


class UserInfo(BaseModel):
    __tablename__ = 'user_info'
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    full_name = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    birthday = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)

    def __repr__(self) -> str:
        return f'Login: {self.id} {self.date}'


# TODO ЗАГЛУШКА! (пока не реализован метод добавления через терминал)
def create_super():
    _super = {
        'username': 'Admin',
        'password': 'admin',
        'email': 'admin@admin.com',
        'is_super': True,
    }
    try:
        User(**_super).set()
    except (PendingRollbackError, UniqueViolation, IntegrityError):
        return
