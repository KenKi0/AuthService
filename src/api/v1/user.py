from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_security.utils import hash_password

from db.db import db  # noqa: F401
from models.session import AllowedDevice, Session  # noqa: F401
from models.user import User, user_datastore

from .utils import check_permission, get_tokens

auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth_blueprint.route('/register', methods=('POST',))
def register():
    """
    Регистрация нового пользователя.
    ---
    openapi: 3.0.2
    info:
        title: Auth service
        version: v1
    paths:
    /auth/register:
            post:
                description: Регистрация нового пользователя
                parameters:
                    name: username
                    in: query
                    required: true
                    schema:
                        type: string
                    name: email
                    in: query
                    required: true
                    schema:
                        type: string
                    name: password
                    in: query
                    required: true
                    schema:
                        type: string
                requestBody:
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    username:
                                        type: string
                                        writeOnly: true
                                    email:
                                        type: string
                                        writeOnly: true
                                    password:
                                        type: string
                                        writeOnly: true
                                required:
                                    - username
                                    - email
                                    - password
                            example:
                                username: test
                                email: test@test.com
                                password: test_12345
                responses:
                    '200':
                        description: Successfull registration
                        content:
                            application/json:
                                schema:
                                    type: object
                                    properties:
                                        message:
                                            type: string
                                            title: response message
                                example:
                                    message: New user was registered
                    '400':
                        description: Registration failed
                        content:
                            application/json:
                                schema:
                                    type: object
                                    properties:
                                        message:
                                            type: string
                                            title: response message
                                example:
                                    message: Email is already in use
    """
    _request = {
        'username': request.json.get('username'),
        'email': request.json.get('email'),
        'is_super': False,
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
    user_datastore.create_user(**_request)
    db.session.commit()
    return jsonify(message='New user was registered'), HTTPStatus.OK


@auth_blueprint.route('/login', methods=('POST',))
@jwt_required()
def login():
    """
    Вход пользователя в аккаунт.
    ---
    openapi: 3.0.2
    info:
        title: 'Auth service'
        version: 'v1'
    paths:
        /auth/login:
            post:
            description: Вход пользователя в аккаунт
            requestBody:
                content:
                application/json:
                    schema:
                    type: object
                    properties:
                        email:
                            type: string
                            writeOnly: true
                        password:
                            type: string
                            writeOnly: true
                    required:
                        - email
                        - password
                    example:
                        email: test@test.com
                        password: test_12345
            responses:
                '200':
                description: Получение Токенов
                content:
                    application/json:
                    schema:
                        type: object
                        properties:
                            msg:
                                type: string
                                title: response message
                            tokens:
                                type: object
                                properties:
                                    access_token:
                                        type: string
                                        title: access token
                                    refresh_token:
                                        type: string
                                        title: refresh token
                    example:
                        message: Login successful
                        tokens:
                            access_token: eyJLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiZi0zNWRhLTQ0NjYwYmQifQ.-xN_h82PHVTCMA9v
                            refresh_token: eyJ0eXAiOiJIUzI1NiJ9.eyJpZ9uZSIsImlhdCI6MTU5cm9sZSI6InVzZXIifQ.Zvk7_x3_9ryms
                '401':
                description: Unauthorized access
                content:
                    application/json:
                    schema:
                        type: object
                        properties:
                        msg:
                            type: string
                            title: response message
                    example:
                        message: User is not exist
    """
    _request = {
        'email': request.json.get('email'),
        'password': hash_password(request.json.get('password')),
        'user_agent': request.json.get('User-Agent'),
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
@check_permission('User')
def change_password(user_id):
    """
    Смена пароля.
    ---
    openapi: 3.0.2
    info:
        title: 'Auth service'
        version: 'v1'
    paths:
        /auth/change-password:
            patch:
            description: Смена пароля
            requestBody:
                content:
                application/json:
                    schema:
                    type: object
                    properties:
                        old_password:
                            type: string
                            writeOnly: true
                        new_password:
                            type: string
                            writeOnly: true
                    required:
                        - old_password
                        - new_password
                    example:
                    old_password: test_12345
                    new_password: test_67890
            responses:
                '200':
                description: Password changed successful
                content:
                    application/json:
                    schema:
                        type: object
                        properties:
                        msg:
                            type: string
                            title: response message
                    example:
                        message: Password changed successful
                '401':
                description: Unauthorized access
                content:
                    application/json:
                    schema:
                        type: object
                        properties:
                        msg:
                            type: string
                            title: response message
                    example:
                        message: Email or password are not correct
                '403':
                description: Access is not allowed
                content:
                    application/json:
                    schema:
                        type: object
                        properties:
                        msg:
                            type: string
                            title: response message
                    example:
                        message: Permission denied
                '404':
                description: Not found
                content:
                    application/json:
                    schema:
                        type: object
                        properties:
                        msg:
                            type: string
                            title: response message
                    example:
                        message: Not found
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
@jwt_required(refresh=True)
def refresh_token():
    """
    Обновление токенов.
    ---
    openapi: 3.0.2
    info:
        title: 'Auth service'
        version: 'v1'
    paths:
        /auth/refresh-token:
            post:
            description: Обновления токенов
            responses:
                '200':
                description: Refresh successful
                content:
                    application/json:
                    schema:
                        type: object
                        properties:
                        msg:
                            type: string
                            title: response message
                        tokens:
                            type: object
                            properties:
                            access_token:
                                type: string
                                title: access token
                            refresh_token:
                                type: string
                                title: refresh token
                    example:
                        message: Refresh successful
                        tokens:
                        access_token: eyJLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiZi0zNWRhLTQ0NjYwYmQifQ.-xN_h82PHVTCMA9vdoH
                        refresh_token: eyJ0eXAiOiJIUzI1NiJ9.eyJpZ9uZSIsImlhdCI6MTU5cm9sZSI6InVzZXIifQ.Zvk7_x3_9rymsDAx
                '401':
                description: Unauthorized access
                content:
                    application/json:
                    schema:
                        type: object
                        properties:
                        msg:
                            type: string
                            title: response message
                    example:
                        message: User is not exist
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
