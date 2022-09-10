from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from db.db import db
from models.utils import BaseModel


class Session(BaseModel):
    __tablename__ = 'sessions'
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    device_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.allowed_device.id'), nullable=False)
    auth_date = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)

    def __repr__(self) -> str:
        return f'Session: {self.id} {self.auth_date}'


class AllowedDevice(BaseModel):
    __tablename__ = 'allowed_device'
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    user_agent = db.Column(db.String, nullable=False)

    def __repr__(self) -> str:
        return f'Device: {self.id}'
