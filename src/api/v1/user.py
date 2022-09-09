from http import HTTPStatus

from flask import Blueprint, jsonify, request

from db.db import db  # noqa: F401
from models.session import LoginInfo, Session  # noqa: F401
from models.user import User, user_datastore

from .utils import check_permission  # noqa: F401

blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@blueprint.route('/register', methods=('POST',))
def register():
    """Регистрация нового пользователя."""
    _request = {
        'username': request.json.get('username'),
        'email': request.json.get('email'),
        'roles': ['user'],
        'is_super': False,
        'password': request.json.get('password'),
    }

    # TODO проверка наличтя всех данных в request (+валиность)

    # Проверка email (есть или нет в базе)
    user = User.query.filter_by(email=_request['email']).first()
    if user:
        return jsonify(msg='Email is already in use'), HTTPStatus.CONFLICT

    if _request['username'] == 'admin' and _request['email'] == 'admin@test.com':
        _request['is_super'] = True

    # Запись пользователя в базу
    user_datastore.create_user(**_request)
    db.session.commit()
    return jsonify(msg='New user was registered'), HTTPStatus.OK


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
@check_permission('user')
def change_password(user_id):
    """Смена пароля."""
    ...


# TODO сделать проверку прав у пользователя
@blueprint.route('/login-history/<uuid:user_id>', methods=('GET',))
def get_login_history(user_id):
    """Получить историю посещений."""
    ...
