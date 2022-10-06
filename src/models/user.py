from datetime import datetime

from flask_security import UserMixin
from sqlalchemy import UniqueConstraint
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


def create_user_region_partition(target, connection, **kw) -> None:
    """creating partition by user_sign_in"""
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_info_cis" PARTITION OF "user_info"
        FOR VALUES IN ('Russia', 'Ukraine', 'Belarus', 'Kazakhstan')""",
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_info_eu" PARTITION OF "user_info"
        FOR VALUES IN ('UK', 'France', 'Germany', 'Netherlands')""",
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_info_na" PARTITION OF "user_info"
        FOR VALUES IN ('USA', 'Canada')""",
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_info_as" PARTITION OF "user_info"
        FOR VALUES IN ('China', 'Japan', 'South Korea')""",
    )


class UserInfo(BaseModel):
    __tablename__ = 'user_info'
    __table_args__ = (
        UniqueConstraint('id', 'country'),
        {
            'postgresql_partition_by': 'LIST (country)',
            'listeners': [('after_create', create_user_region_partition)],
        },
    )
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
