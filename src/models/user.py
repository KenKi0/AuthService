from datetime import datetime

from flask_security import UserMixin

from db.db import db
from models.utils import BaseModel


class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    username = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(length=150), nullable=False)
    email = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    user_agent = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean(), nullable=False)
    roles = db.Column(db.ARRAY(db.String), nullable=False)
    create_at = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now(), onupdate=datetime.now(), nullable=False)

    def __repr__(self) -> str:
        return f'User: {self.username} {self.id}'
