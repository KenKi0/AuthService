from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_pydantic_spec import Response

from .utils import api, check_permission

auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# Временная заглушка (ChangePassword, Login, RefreshToken, Register импортируется из api.v1.components.user_schemas)
Register = ''
Login = ''
ChangePassword = ''
RefreshToken = ''


@auth_blueprint.route('/register', methods=('POST',))
@api.validate(body=Register, resp=Response('HTTP_409', 'HTTP_200'), tags=['auth'])
def register():
    """Регистрация нового пользователя."""
    ...


@auth_blueprint.route('/login', methods=('POST',))
@api.validate(body=Login, resp=Response('HTTP_401', 'HTTP_200'), tags=['auth'])
def login():
    """Вход пользователя в аккаунт."""
    ...


# TODO определиться что передавать в @check_permission (int | str)
@auth_blueprint.route('/change-password/<uuid:user_id>', methods=('PATCH',))
@api.validate(body=ChangePassword, resp=Response('HTTP_404', 'HTTP_401', 'HTTP_200'), tags=['auth'])
@check_permission('User')
def change_password(user_id):
    """Смена пароля."""
    ...


@auth_blueprint.route('/refresh-token', methods=('POST',))
@api.validate(body=RefreshToken, resp=Response('HTTP_401', 'HTTP_200'), tags=['auth'])
@jwt_required(refresh=True)
def refresh_token():
    """Обновление токенов."""
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
