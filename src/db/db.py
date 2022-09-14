from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from core.config import settings

db = SQLAlchemy()


def init_db(app: Flask, config: str = settings.postgres.uri) -> None:
    """
    Подключение к БД.
    :param app: Flask
    :param config: settings
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = config
    db.init_app(app)
    app.app_context().push()
    db.create_all()
