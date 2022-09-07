from datetime import datetime

from db.db import db
from models.utils import BaseModel


class Session(BaseModel):
    __tablename__ = 'sessions'
    user_id = db.Column(db.String, db.ForeignKey('auth.users.id'), nullable=False)
    refresh_token = db.Column(db.String, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now(), onupdate=datetime.now(), nullable=False)

    def __repr__(self) -> str:
        return f'Session: {self.id}'


class LoginInfo(BaseModel):
    __tablename__ = 'login_info'
    user_id = db.Column(db.String, db.ForeignKey('auth.users.id'), nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)

    def __repr__(self) -> str:
        return f'Login: {self.id} {self.date}'
