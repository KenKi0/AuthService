import json
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required  # noqa: F401
from flask_pydantic_spec import Response
from flask_security.utils import hash_password  # noqa: F401

from api.v1.components.role_schemas import Role as role_body
from db.db import db  # noqa: F401
from models.role import Role
from models.session import AllowedDevice, Session  # noqa: F401

from .utils import api, check_permission, get_tokens  # noqa: F401

role_blueprint = Blueprint('role', __name__, url_prefix='/api/v1/role')


@role_blueprint.route('/', methods=('GET', 'POST'))
@api.validate(body=role_body, resp=Response('HTTP_409', 'HTTP_204', 'HTTP_200'), tags=['role'])
def role():
    """Получение всех ролей | Добавление новой роли."""
    # Получить все роли
    if request.method == 'GET':
        # get_roles():
        _roles = Role.query.all()
        if not _roles:
            return jsonify(message='Role list is empty'), HTTPStatus.NO_CONTENT

        return (jsonify(roles=[json.dumps(role) for role in _roles]), HTTPStatus.OK)

    # Добавить новую роль
    if request.method == 'POST':
        # create_role():
        _request = {
            'name': request.json.get('name'),
            'description': request.json.get('description'),
        }
        role = Role.query.filter_by(name=_request['name']).first()
        if role:
            return jsonify(message='Role is already in use'), HTTPStatus.CONFLICT

        role = Role(**_request)
        role.set()
        return jsonify(message='New role was created'), HTTPStatus.OK


@role_blueprint.route('/<uuid:user_id>', methods=('GET', 'PATCH', 'DELETE'))
@api.validate(body=role_body, resp=Response('HTTP_409', 'HTTP_204', 'HTTP_200'), tags=['role'])
def role_by_id(role_id):
    ...
