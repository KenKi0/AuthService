from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_security.utils import hash_password

from user.payload_models import (
    ChangePasswordPayload,
    LogoutPayload,
    RefreshTokensPayload,
    UserCreatePayload,
    UserID,
    UserLoginPayload,
)
from user.services.user_auth import UserService
from utils.exceptions import EmailAlreadyExist, InvalidPassword, NoAccessError, NotFoundError

from .components.user_schemas import Session as SessionSchem
from .utils import check_permission

auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
user_blueprint = Blueprint('user', __name__, url_prefix='/api/v1/user')


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
         description: New user was registered
       '409':
         description: Email is already in use
     tags:
       - Auth
    """
    _request = {
        'username': request.json.get('username'),
        'email': request.json.get('email'),
        'password': hash_password(request.json.get('password')),
    }
    try:
        UserService().register(UserCreatePayload(**_request))
    except EmailAlreadyExist:
        return jsonify(message='Email is already in use'), HTTPStatus.CONFLICT
    return jsonify(message='New user was registered'), HTTPStatus.OK


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
         description: Login successful
       '400':
         description: Wrong password
       '401':
         description: User is not exist
     tags:
       - Auth
    """
    _request = {
        'email': request.json.get('email'),
        'password': hash_password(request.json.get('password')),
        'user_agent': request.headers.get('User-Agent'),
    }
    try:
        access_token, refresh_token = UserService().login(UserLoginPayload(**_request))
    except NotFoundError:
        return jsonify(message='User is not exist'), HTTPStatus.UNAUTHORIZED
    except InvalidPassword:
        return jsonify(message='Wrong password'), HTTPStatus.BAD_REQUEST

    response = jsonify()
    response.set_cookie('access_token', access_token)
    response.set_cookie('refresh_token', refresh_token)
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


@auth_blueprint.route('/change-password/<uuid:user_id>', methods=('PATCH',))
@jwt_required()
# @check_permission(permission=0)
def change_password(user_id):
    """
    Смена пароля.
    ---
    patch:
     security:
      - BearerAuth: []
     summary: Смена пароля
     parameters:
      - name: user_id
        in: path
        type: string
        required: true
     requestBody:
       content:
        application/json:
         schema: ChangePassword
     responses:
       '200':
         description: Password changed successful
       '400':
         description: Wrong password
       '401':
         description: User is not exist
       '403':
         description: Permission denied
     tags:
       - Auth
    """

    _request = {
        'user_id': user_id,
        'old_password': hash_password(request.json.get('old_password')),
        'new_password': hash_password(request.json.get('new_password')),
    }
    try:
        UserService().change_password(ChangePasswordPayload(**_request))
    except NoAccessError:
        return jsonify(message='Not user'), HTTPStatus.BAD_REQUEST
    except NotFoundError:
        return jsonify(message='User is not exist'), HTTPStatus.UNAUTHORIZED
    except InvalidPassword:
        return jsonify(message='Wrong password'), HTTPStatus.BAD_REQUEST
    return jsonify(message='Password changed successful'), HTTPStatus.OK


@auth_blueprint.route('/refresh-token', methods=('POST',))
@jwt_required(refresh=True)
def refresh_token():
    """
    Обновление токенов.
    ---
    post:
     security:
      - BearerAuth: []
     summary: Обновление токенов
     responses:
       '200':
         description: Refresh successful
       '400':
         description: Not user
     tags:
       - Auth
    """

    _request = {
        'user_id': get_jwt_identity(),
        'user_agent': request.headers.get('User-Agent'),
        'refresh': request.headers.get('Authorization'),
    }
    try:
        access_token, refresh_token = UserService().refresh_tokens(RefreshTokensPayload(**_request))
    except NoAccessError:
        return jsonify(message='Not user'), HTTPStatus.BAD_REQUEST
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
@jwt_required()
def logout():
    """
    Выход пользователя из аккаунта.
    ---
    post:
     security:
      - BearerAuth: []
     summary: Выход пользователя из аккаунта
     requestBody:
       content:
        application/json:
         schema: Logout
     responses:
       '200':
         description: User logged out
       '400':
         description: Not user
     tags:
       - Auth
    """
    _request = {
        'user_id': get_jwt_identity(),
        'user_agent': request.headers.get('User-Agent'),
        'from_all': request.json.get('from_all'),
    }
    try:
        UserService().logout(LogoutPayload(**_request))
    except NoAccessError:
        return jsonify(message='Not user'), HTTPStatus.BAD_REQUEST
    return jsonify(message='User logged out'), HTTPStatus.OK


@user_blueprint.route('/login-history/<uuid:user_id>', methods=('GET',))
@check_permission(permission=0)
def login_history(user_id):
    """
    Получить историю посещений.
    ---
    get:
     security:
      - BearerAuth: []
     summary: Получить историю посещений
     parameters:
      - name: user_id
        in: path
        type: string
        required: true
     responses:
       '200':
         description: User logged out
       '400':
         description: Not user
       '403':
         description: Permission denied
     tags:
       - User
    """

    _request = {
        'user_id': user_id,
    }
    try:
        user_histories = UserService().get_history(UserID(**_request))
    except NoAccessError:
        return jsonify(message='Not user'), HTTPStatus.BAD_REQUEST
    return (
        jsonify(message='Refresh successful', history=[SessionSchem().dumps(histori) for histori in user_histories]),
        HTTPStatus.OK,
    )
