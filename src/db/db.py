from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from core.config import settings

db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """
    Подключение к БД.
    :param app: Flask
    """
    app.config['SECRET_KEY'] = settings.postgres.uri()
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.postgres.uri()
    db.init_app(app)
