from contextlib import contextmanager

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

from core.config import settings

db = SQLAlchemy()
migrate = Migrate()


def init_db(app: Flask, config: str = settings.postgres.uri) -> None:
    """
    Подключение к БД.
    :param app: Flask
    :param config: settings
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = config
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.app_context().push()
    migrate.init_app(app, db)


@contextmanager
def session_scope() -> Session:
    """Контекстный менеджер для работы внутри транзакции"""

    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    finally:
        db.session.remove()
