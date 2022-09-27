from datetime import datetime

from flask_security import UserMixin
from sqlalchemy.dialects.postgresql import UUID

from db import db
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


class SocialAccount(BaseModel):
    __tablename__ = 'social_account'
    __table_args__ = (db.UniqueConstraint('social_id', 'social_name', name='social_pk'), {'schema': 'auth'})

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
