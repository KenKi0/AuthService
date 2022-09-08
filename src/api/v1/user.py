from flask import Blueprint

from db.db import db  # noqa: F401
from models.session import LoginInfo, Session  # noqa: F401
from models.user import User  # noqa: F401

blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@blueprint.route('/register', methods=('POST',))
def register():
    """Регистрация нового пользователя."""
    ...


@blueprint.route('/login', methods=('POST',))
def login():
    """Вход пользователя."""
    ...


@blueprint.route('/refresh-token', methods=('POST',))
def refresh_token():
    """Обновление токена."""
    ...


@blueprint.route('/logout', methods=('POST',))
def logout():
    """Выход пользователя."""
    ...


# TODO сделать проверку прав у пользователя
@blueprint.route('/change-password/<uuid:user_id>', methods=('PATCH',))
def change_password(user_id):
    """Смена пароля."""
    ...


# TODO сделать проверку прав у пользователя
@blueprint.route('/login-history/<uuid:user_id>', methods=('GET',))
def get_login_history(user_id):
    """Получить историю посещений."""
    ...
