from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from core.config import settings

db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """
    Подключение к БД.
    :param app: Flask
    """
    app.config['SECRET_KEY'] = settings.SECRET
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.postgres.uri()
    app.config['SECRET_PASSWORD_SALT'] = settings.PASSWORD_SALT
    db.init_app(app)
