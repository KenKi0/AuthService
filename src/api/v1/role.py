from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from db.db import db
from models.permissions import Permission, RolePermission
from models.role import Role

from .components.perm_schemas import Permission as PermissionSchem
from .components.role_schemas import Role as RoleSchem
from .utils import check_permission

role_blueprint = Blueprint('role', __name__, url_prefix='/api/v1/')


@role_blueprint.route('/roles', methods=('GET',))
@jwt_required()
@check_permission(permission=3)
def roles():
    """
    Получение всех ролей из БД.
    ---
    get:
     security:
      - BearerAuth: []
     summary: Получение списка всех ролей из базы
     responses:
       '200':
         description: Ok
       '204':
         description: Role list is empty
       '400':
         description: Bad request
       '403':
         description: Permission denied
     tags:
       - Role
    """
    roles = Role.query.all()
    if not roles:
        return jsonify(message='Role list is empty'), HTTPStatus.NO_CONTENT
    return (
        jsonify(roles=[RoleSchem().dumps(role) for role in roles]),
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
     security:
      - BearerAuth: []
     summary: Добавление новой роли
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
    Role(**_request).set()
    return jsonify(message='New role was created'), HTTPStatus.OK


@role_blueprint.route(
    '/role/<uuid:role_id>',
    methods=(
        'GET',
        'PATCH',
        'DELETE',
    ),
)
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
         description: Ok
       '204':
         description: Permissions list is empty
       '403':
         description: Permission denied
       '404':
         description: Not found
     tags:
       - Role
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
     tags:
       - Role
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
         description: Ok
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
            return jsonify(message='Role list is empty'), HTTPStatus.NO_CONTENT
        return (
            jsonify(
                role=RoleSchem().dumps(role),
                permissions=[PermissionSchem().dumps(perm) for perm in permissions],
            ),
            HTTPStatus.OK,
        )

    if request.method == 'PATCH':
        _request = {
            'id': role_id,
            'name': request.json.get('name'),
            'description': request.json.get('description'),
        }
        role = Role.query.filter_by(id=_request['id']).first()
        if not role:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        for key in _request:
            setattr(role, key, _request[key])
        db.session.add(role)
        db.session.commit()
        return jsonify(message='Role was changed sucessfully'), HTTPStatus.OK

    if request.method == 'DELETE':
        _request = {
            'role_id': role_id,
        }
        role = Role.query.filter_by(id=_request['role_id']).first()
        if not role:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        db.session.delete(role)
        db.session.commit()
        return jsonify(message='Role was deleted sucessfully'), HTTPStatus.OK
