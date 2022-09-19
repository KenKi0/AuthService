import uuid
from datetime import datetime

from psycopg2.errors import UniqueViolation
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from db import db


class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {'schema': 'auth'}
    id = db.Column(  # noqa: VNE003
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    create_at = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now(), onupdate=datetime.now(), nullable=False)
    is_deleted = db.Column(db.Boolean(), nullable=False, default=False)

    def set(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except (PendingRollbackError, UniqueViolation, IntegrityError):
            raise

    def cond_delete(self):
        self.is_deleted = True
