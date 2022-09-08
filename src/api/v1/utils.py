from functools import wraps
from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    verify_jwt_in_request,
)

from core.config import settings
from models.user import User

access_token_exp = settings.ACCESS_TOKEN_EXP_DELTA
refresh_token_exp = settings.REFRESH_TOKEN_EXP_DELTA


def get_tokens(user_id, token=None):
    """
    Получение | Обновление пользователем access_token и refresh_token.
    :param user_id: id пользователя.
    :param token: Токен.
    :return access_token, refresh_token: Токены.
    """
    if token:
        roles = token.get('roles', [])
        is_super = token.get('is_super', False)
    else:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise ValueError('[-] Пользователя не существует.')
        roles = user.roles
        is_super = user.is_super

    additional_claims = {
        'roles': roles,
        'is_super': is_super,
    }
    access_token = create_access_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=access_token_exp,
    )
    refresh_token = create_refresh_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=refresh_token_exp,
    )
    return access_token, refresh_token


def check_permission(role: str):
    """
    Проверка наличия прав для доступа.
    :param role: Необходимая роль для доступа.
    :return func_wrapper: Результат выполнения функции.
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            current_user = get_jwt_identity()
            user = kwargs.get('user_id')
            is_owner = current_user == user
            is_super = claims.get('is_super', False)
            roles = claims.get('roles')

            if is_owner or is_super or (role in roles):
                return func(*args, **kwargs)
            else:
                return jsonify(msg='Permission denied'), HTTPStatus.FORBIDDEN

        return inner

    return func_wrapper
