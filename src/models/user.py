from flask_security import SQLAlchemyUserDatastore, UserMixin
from sqlalchemy import String

from db.db import db
from models.role import Role
from models.utils import BaseModel


class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    username = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(length=150), nullable=False)
    email = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    user_agent = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean(), nullable=False)
    roles = db.Column(db.ARRAY(String), nullable=False)
    is_super = db.Column(db.Boolean(), default=False)

    def __repr__(self) -> str:
        return f'User: {self.username} {self.id}'


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
