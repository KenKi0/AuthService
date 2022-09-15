from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_security.utils import hash_password

from .utils import check_permission

auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth_blueprint.route('/register', methods=('POST',))
def register():
    """
    Регистрация нового пользователя.
    ---
    post:
     summary: Регистрация нового пользователя
     requestBody:
       content:
        application/json:
         schema: Register
     responses:
       '200':
         description: Результат возведения в степень
       '409':
         description: Не передан обязательный параметр
     tags:
       - Auth
    """
    _request = {  # noqa: F841
        'username': request.json.get('username'),
        'email': request.json.get('email'),
        'password': hash_password(request.json.get('password')),
    }
    ...


@auth_blueprint.route('/login', methods=('POST',))
def login():
    """
    Вход пользователя в аккаунт.
    ---
    post:
     summary: Вход пользователя в аккаунт
     requestBody:
       content:
        application/json:
         schema: Login
     responses:
       '200':
         description: ///
       '401':
         description: ///
     tags:
       - Auth
    """
    _request = {  # noqa: F841
        'email': request.json.get('email'),
        'password': hash_password(request.json.get('password')),
        'user_agent': request.headers.get('User-Agent'),
    }
    ...


# TODO определиться что передавать в @check_permission (int | str)
@auth_blueprint.route('/change-password/<uuid:user_id>', methods=('PATCH',))
@check_permission('User')
def change_password(user_id):
    """
    Смена пароля.
    ---
    patch:
     summary: Смена пароля
     parameters:
      - name: user_id
        in: query
        type: string
        required: true
     requestBody:
       content:
        application/json:
         schema: ChangePassword
     responses:
       '200':
         description: ///
       '401':
         description: ///
       '404':
         description: ///
     tags:
       - Auth
    """
    _request = {  # noqa: F841
        'old_password': hash_password(request.json.get('old_password')),
        'new_password': hash_password(request.json.get('new_password')),
    }
    ...


@auth_blueprint.route('/refresh-token', methods=('POST',))
@jwt_required(refresh=True)
def refresh_token():
    """
    Обновление токенов.
    ---
    post:
     summary: Обновление токенов
     requestBody:
       content:
        application/json:
         schema: Register
     responses:
       '200':
         description: ///
       '401':
         description: ///
     tags:
       - Auth
    """
    ...


@auth_blueprint.route('/logout', methods=('POST',))
def logout():
    """Выход пользователя из аккаунта."""
    ...


# TODO определиться что передавать в @check_permission (int | str)
@auth_blueprint.route('/login-history/<uuid:user_id>', methods=('GET',))
@check_permission('User')
def login_history(user_id):
    """Получить историю посещений."""
    ...
