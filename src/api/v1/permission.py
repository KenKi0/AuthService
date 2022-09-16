import json
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required  # noqa: F401
from flask_pydantic_spec import Response
from flask_security.utils import hash_password  # noqa: F401

from api.v1.components.role_schemas import Role as role_body
from db.db import db  # noqa: F401
from models.role import Role
from models.permissions import Permission, RolePermission
from models.session import AllowedDevice, Session  # noqa: F401

from .utils import api, check_permission, get_tokens  # noqa: F401

# role_blueprint = Blueprint('role', __name__, url_prefix='/api/v1/role')
permissions_blueprint = Blueprint('role', __name__, url_prefix='/api/v1/')


@permissions_blueprint.route('/permissions', methods=('GET',))
@jwt_required()
@check_permission(permission=3)
# @api.validate(body=role_body, resp=Response('HTTP_409', 'HTTP_204', 'HTTP_200'), tags=['role'])
def roles():
    """
    Получение всех ролей.
    ---
    get:
     security:
      - BearerAuth: []
     summary: Получение списка всех ролей из базы
     responses:
       '200':
         description: ...
       '204':
         description: Role list is empty
       '400':
         description: ...
       '403':
         description: Permission denied
     tags:
       - Role
    """

    roles = Role.query.all()
    if not roles:
        return jsonify(message='Role list is empty'), HTTPStatus.NO_CONTENT

    return (jsonify(
        _roles=[json.dumps(role) for role in roles]
    ),
        HTTPStatus.OK,
    )


@role_blueprint.route('/role', methods=('POST',))
@jwt_required()
@check_permission(permission=3)
def role():
    """
    Добавление новой роли в базу.
    ---
    post:
     summary: обавление новой роли
     requestBody:
       content:
        application/json:
         schema: Role
     responses:
       '200':
         description: New role was created
       '409':
         description: Role is already in use
       '403':
         description: Permission denied
     tags:
       - Role
    """

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


@role_blueprint.route('/role/<uuid:role_id>', methods=('GET', 'PATCH', 'DELETE',))
@jwt_required()
@check_permission(permission=3)
def role_by_id(role_id):
    """
    Просмотр | Изменение | Удаление роли по id.
    ---
    get:
     security:
      - BearerAuth: []
     summary: Просмотр роли по id
     parameters:
      - name: role_id
        in: path
        type: string
        required: true
     responses:
       '200':
         description: ///
       '403':
         description: Permission denied
       '404':
         description: Not found
    patch:
     security:
      - BearerAuth: []
     summary: Изменить роль по id
     parameters:
      - name: role_id
        in: path
        type: string
        required: true
     requestBody:
       content:
        application/json:
         schema: Role
     responses:
       '200':
         description: Role was changed sucessfully
       '403':
         description: Permission denied
       '404':
         description: Not found
    delete:
     security:
      - BearerAuth: []
     summary: Удаление роли по id
     parameters:
      - name: role_id
        in: path
        type: string
        required: true
     responses:
       '200':
         description: Role was deleted sucessfully
       '403':
         description: Permission denied
       '404':
         description: Not found
     tags:
       - Role
    """

    if request.method == 'GET':
        _request = {
            'role_id': role_id,
        }
        role = Role.query.filter_by(id=_request['role_id']).first()
        if not role:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        permissions = (
            db.session.query(Permission)
            .join(RolePermission)
            .filter(RolePermission.role_id == _request['role_id'])
            .all()
        )
        if not permissions:
            permissions = []
        return (jsonify(
            role=role,
            permissions=[perm.name for perm in permissions],
        ),
            HTTPStatus.OK
        )

    if request.method == 'PATCH':
        _request = {
            'role_id': role_id,
            'name': request.json.get('name'),
            'description': request.json.get('description'),
        }
        role = Role.query.filter_by(id=_request['role_id']).first()
        if not role:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        role.update(**_request)
        db.session.commit()
        return jsonify(message='Role was changed sucessfully'), HTTPStatus.OK

    if request.method == 'DELETE':
        _request = {
            'role_id': role_id,
        }
        role = Role.query.filter_by(id=_request['role_id']).first()
        if not role:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        role.delete()
        db.session.commit()
        return jsonify(message='Role was deleted sucessfully'), HTTPStatus.OK






# @role_blueprint.route('/<uuid:user_id>', methods=('GET', 'PATCH', 'DELETE'))
# @api.validate(body=role_body, resp=Response('HTTP_409', 'HTTP_204', 'HTTP_200'), tags=['role'])
# def role_by_id(role_id):
#     ...


# @role_blueprint.route('/', methods=('GET', 'POST'))
# @api.validate(body=role_body, resp=Response('HTTP_409', 'HTTP_204', 'HTTP_200'), tags=['role'])
# def role():
#     """Получение всех ролей | Добавление новой роли."""
#     # Получить все роли
#     if request.method == 'GET':
#         # get_roles():
#         _roles = Role.query.all()
#         if not _roles:
#             return jsonify(message='Role list is empty'), HTTPStatus.NO_CONTENT

#         return (jsonify(roles=[json.dumps(role) for role in _roles]), HTTPStatus.OK)

#     # Добавить новую роль
#     if request.method == 'POST':
#         # create_role():
#         _request = {
#             'name': request.json.get('name'),
#             'description': request.json.get('description'),
#         }
#         role = Role.query.filter_by(name=_request['name']).first()
#         if role:
#             return jsonify(message='Role is already in use'), HTTPStatus.CONFLICT

#         role = Role(**_request)
#         role.set()
#         return jsonify(message='New role was created'), HTTPStatus.OK
