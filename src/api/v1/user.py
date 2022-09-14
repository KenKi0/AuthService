from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_pydantic_spec import FlaskPydanticSpec, Response
from flask_security.utils import hash_password

from api.v1.components.user_schemas import ChangePassword, Login, RefreshToken, Register
from db.db import db  # noqa: F401
from models.session import AllowedDevice, Session  # noqa: F401
from models.user import User

from .utils import check_permission, get_tokens

auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
api = FlaskPydanticSpec('flask')


@auth_blueprint.route('/register', methods=('POST',))
# @api.validate(body=Register, resp=Response('HTTP_409', 'HTTP_200'), tags=['auth'])
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
    _request = {
        'username': request.json.get('username'),
        'email': request.json.get('email'),
        'password': hash_password(request.json.get('password')),
    }

    # TODO проверка наличтя всех данных в request (+валиность)

    # Проверка email (есть или нет в базе)
    user = User.query.filter_by(email=_request['email']).first()
    if user:
        return jsonify(message='Email is already in use'), HTTPStatus.CONFLICT

    if _request['username'] == 'admin' and _request['email'] == 'admin@test.com':
        _request['is_super'] = True

    # Запись пользователя в базу
    user = User(**_request)
    user.set()
    return jsonify(message='New user was registered'), HTTPStatus.OK


@auth_blueprint.route('/login', methods=('POST',))
# @api.validate(body=Login, resp=Response('HTTP_401', 'HTTP_200'), tags=['auth'])
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
    _request = {
        'email': request.json.get('email'),
        'password': hash_password(request.json.get('password')),
        'user_agent': request.headers.get('User-Agent'),
    }

    # TODO проверка наличтя всех данных в request (+валиность)

    user = User.query.filter_by(email=_request['email']).first()
    if not user:
        return jsonify(message='User is not exist'), HTTPStatus.UNAUTHORIZED

    # TODO проверить пароль

    # Запись данных о девайсе и сессии юзера
    device = AllowedDevice.query.filter_by(user_id=user.id, user_agent=_request['user_agent']).first()
    if not device:
        device = AllowedDevice(user_id=user.id, user_agent=_request['user_agent'])
        device.set()
    session = Session(user_id=user.id, device_id=device.id)
    session.set()

    #  Получение JWT токенов
    access_token, refresh_token = get_tokens(user.id)

    return (
        jsonify(
            message='Login successful',
            tokens={
                'access_token': access_token,
                'refresh_token': refresh_token,
            },
        ),
        HTTPStatus.OK,
    )


# TODO определиться что передавать в @check_permission (int | str)
@auth_blueprint.route('/change-password/<uuid:user_id>', methods=('PATCH',))
# @api.validate(body=ChangePassword, resp=Response('HTTP_404', 'HTTP_401', 'HTTP_200'), tags=['auth'])
# @check_permission('User')
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
    _request = {
        'old_password': hash_password(request.json.get('old_password')),
        'new_password': hash_password(request.json.get('new_password')),
    }

    # TODO проверка наличтя всех данных в request (+валиность)

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify(message='Not found'), HTTPStatus.NOT_FOUND

    # TODO Проверка пароля (old_password)

    user.password = _request['new_password']
    user.set()
    return jsonify(message='Password changed successful'), HTTPStatus.OK


@auth_blueprint.route('/refresh-token', methods=('POST',))
# @api.validate(body=RefreshToken, resp=Response('HTTP_401', 'HTTP_200'), tags=['auth'])
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
    user_id = get_jwt_identity()  # TODO посмотреть что возвращает get_jwt_identity() (использовать try/except)
    token = get_jwt()

    if not user_id:
        return jsonify(message='User is not exist'), HTTPStatus.UNAUTHORIZED

    access_token, refresh_token = get_tokens(user_id, token)
    return (
        jsonify(
            message='Refresh successful',
            tokens={
                'access_token': access_token,
                'refresh_token': refresh_token,
            },
        ),
        HTTPStatus.OK,
    )


@auth_blueprint.route('/logout', methods=('POST',))
def logout():
    """
    Выход пользователя из аккаунта.
    ---
    openapi: 3.0.2
    info:
        title: 'Auth service'
        version: 'v1'
    paths:
        /auth/logout:
            post:
                ...
    """
    ...


# TODO определиться что передавать в @check_permission (int | str)
@auth_blueprint.route('/login-history/<uuid:user_id>', methods=('GET',))
@check_permission('User')
def login_history(user_id):
    """
    Получить историю посещений.
    ---
    openapi: 3.0.2
    info:
        title: 'Auth service'
        version: 'v1'
    paths:
        /login-history/<uuid:user_id>:
            get:
                ...
    """
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify(message='Not found'), HTTPStatus.NOT_FOUND

    #  Находим историю пользователя
    sessions = Session.query.filter_by(user_id=user.id).order_by(Session.auth_date.asc()).all()  # noqa: F841

    # TODO придумать как отдавать историю (посмотреть flask_marshmallow)
