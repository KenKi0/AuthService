import datetime
import typing
from contextlib import contextmanager

from db.redis import redis
from user.repositories.protocol import TMStorageTransaction, UserTmStorageRepositoryProtocol


class UserTmStorageRepository(UserTmStorageRepositoryProtocol):
    @staticmethod
    def get(key: str | bytes) -> typing.Any:
        return redis.get(key)

    @staticmethod
    def set(key: str | bytes, value: bytes, ex: int | datetime.timedelta | None = None) -> None:
        redis.set(key, value, ex=ex)

    @staticmethod
    def delete(*keys: str | bytes) -> None:
        redis.delete(*keys)

    @staticmethod
    @contextmanager
    def transaction() -> TMStorageTransaction:
        pipeline = redis.pipeline()
        try:
            yield pipeline
            pipeline.execute()
        except Exception:
            # TODO логировать ошибку
            pipeline.transaction.rollback()
            raise
