from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint

from db.db import db
from models.utils import BaseModel


class AllowedDevice(BaseModel):
    __tablename__ = 'allowed_device'
    __table_args__ = (db.UniqueConstraint('user_id', 'user_agent'), {'schema': 'auth'})
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    user_agent = db.Column(db.String, nullable=False)

    def __repr__(self) -> str:
        return f'Device: {self.id}'


def create_session_partition(target, connection, **kw) -> None:
    """ creating partition by sessions """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "sessions_old" PARTITION OF "sessions" FOR VALUES FROM ('2000-01-01') TO ('2021-12-31');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "sessions_2022" PARTITION OF "sessions" FOR VALUES FROM ('2022-01-01') TO ('2023-12-31');"""
    )


class Session(BaseModel):
    __tablename__ = 'sessions'
    __table_args__ = (
        {
            'postgresql_partition_by': 'RANGE (auth_date)',
            'listeners': [('after_create', create_session_partition)],
        }
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    device_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.allowed_device.id'), nullable=False)
    auth_date = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)

    def __repr__(self) -> str:
        return f'Session: {self.id} {self.auth_date}'
