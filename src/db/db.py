from contextlib import contextmanager

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

from core.config import settings

db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """
    Подключение к БД.
    :param app: Flask
    """
    app.config['SQL_DB'] = settings.postgres.uri()
    db.init_app(app)


@contextmanager
def session_scope() -> Session:
    """Контекстный менеджер для работы внутри транзакции"""

    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
