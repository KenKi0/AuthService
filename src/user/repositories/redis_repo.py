import datetime
import typing
from contextlib import contextmanager

from db.redis import redis
from user.repositories.protocol import TMStorageTransaction, UserTmStorageRepositoryProtocol


class UserTmStorageRepository(UserTmStorageRepositoryProtocol):
    def get(self, key: str | bytes) -> typing.Any:
        return redis.get(key)

    def set(self, key: str | bytes, value: bytes, ex: int | datetime.timedelta | None = None) -> None:
        redis.set(key, value, ex=ex)

    def delete(self, *keys: str | bytes) -> None:
        redis.delete(*keys)

    @contextmanager
    def transaction(self) -> TMStorageTransaction:
        pipeline = redis.pipeline()
        try:
            yield pipeline
            pipeline.execute()
        except Exception:
            # TODO логировать ошибку
            pipeline.transaction.rollback()
            raise
