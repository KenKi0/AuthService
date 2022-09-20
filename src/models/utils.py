import uuid
from datetime import datetime

from flask_sqlalchemy import BaseQuery
from psycopg2.errors import UniqueViolation
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from db import db


class QueryWithSoftDelete(BaseQuery):
    def __new__(cls, *args, **kwargs):
        obj = super(QueryWithSoftDelete, cls).__new__(cls)
        with_deleted = kwargs.pop('_with_deleted', False)
        if len(args) > 0:
            super(QueryWithSoftDelete, obj).__init__(*args, **kwargs)
            return obj.filter_by(is_deleted=False) if not with_deleted else obj
        return obj

    def __init__(self, *args, **kwargs):
        pass

    def with_deleted(self):
        return self.__class__(db.class_mapper(self._mapper_zero().class_), session=db.session(), _with_deleted=True)


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
    query_class = QueryWithSoftDelete

    def set(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except (PendingRollbackError, UniqueViolation, IntegrityError):
            raise

    def cond_delete(self):
        self.is_deleted = True
