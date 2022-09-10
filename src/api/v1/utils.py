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
from db.db import db
from models.permissions import Permission, RolePermission
from models.role import RoleUser
from models.user import User


def get_user_permissions(user_id) -> list[int]:
    """
    Получение всех прав пользователя.
    :param user_id: id пользователя.
    :return permissions: Список прав.
    """
    permissions = (
        db.session.query(Permission)
        .join(RolePermission)
        .join(RoleUser, RoleUser.role_id == RolePermission.role_id)
        .filter(RoleUser.user_id == user_id)
        .all()
    )
    return [permission.code for permission in permissions]


def get_tokens(user_id, token: dict = None):
    """
    Получение | Обновление пользователем access_token и refresh_token.
    :param user_id: id пользователя.
    :param token: Токен.
    :return access_token, refresh_token: Токены.
    """
    if token:
        permissions = token.get('permissions', [])
        is_super = token.get('is_super', False)
    else:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise ValueError('[-] Пользователя не существует.')
        permissions = get_user_permissions(user_id)
        is_super = user.is_super

    additional_claims = {
        'permissions': permissions,
        'is_super': is_super,
    }
    access_token = create_access_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=settings.ACCESS_TOKEN_EXP_DELTA,
    )
    refresh_token = create_refresh_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=settings.REFRESH_TOKEN_EXP_DELTA,
    )
    return access_token, refresh_token


def check_permission(permission: str):
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
            permissions = claims.get('permissions')

            if is_owner or is_super or (permission in permissions):
                return func(*args, **kwargs)
            else:
                return jsonify(msg='Permission denied'), HTTPStatus.FORBIDDEN

        return inner

    return func_wrapper
