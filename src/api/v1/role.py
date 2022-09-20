from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from role.payload_models import RoleCreate, RoleUpdate
from role.services.role import RoleService
from utils.exceptions import AttemptDeleteProtectedObjectError, NotFoundError, UniqueConstraintError

from .components.perm_schemas import Permission as PermissionSchem
from .components.role_schemas import Role as RoleSchem
from .utils import check_permission

role_blueprint = Blueprint('role', __name__, url_prefix='/api/v1/')

service = RoleService()


@role_blueprint.route('/roles', methods=('GET',))
@jwt_required()
@check_permission(permission=3)
def roles():
    """
    Получение всех ролей из БД.
    ---
    get:
     security:
      - AccessAuth: []
     summary: Получение списка всех ролей из базы
     responses:
       '200':
         description: Ok
       '403':
         description: Permission denied
     tags:
       - Role
    """

    return (
        jsonify(roles=[RoleSchem().dumps(role) for role in service.get_all()]),
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
      - AccessAuth: []
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

    try:
        service.create(RoleCreate(**_request))
    except UniqueConstraintError:
        return jsonify(message='Role is already in use'), HTTPStatus.CONFLICT
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
def role_by_id(role_id):  # noqa: C901
    """
    Просмотр | Изменение | Удаление роли по id.
    ---
    get:
     security:
      - AccessAuth: []
     summary: Просмотр роли по id
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
    patch:
     security:
      - AccessAuth: []
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
       '409':
         description: Role is already in use
     tags:
       - Role
    delete:
     security:
      - AccessAuth: []
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
       '409':
         description: Protected Role
     tags:
       - Role
    """
    if request.method == 'GET':
        _request = {
            'role_id': role_id,
        }

        try:
            role, permissions = service.get(**_request)
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        return (
            jsonify(
                role=RoleSchem().dumps(role),
                permissions=[PermissionSchem().dumps(perm) for perm in permissions],
            ),
            HTTPStatus.OK,
        )

    if request.method == 'PATCH':
        _request = {
            'name': request.json.get('name'),
            'description': request.json.get('description'),
        }

        try:
            service.update(role_id=role_id, update_role=RoleUpdate(**_request))
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        except UniqueConstraintError:
            return jsonify(message='Role is already in use'), HTTPStatus.CONFLICT
        return jsonify(message='Role was changed sucessfully'), HTTPStatus.OK

    if request.method == 'DELETE':
        _request = {
            'role_id': role_id,
        }

        try:
            service.delete(**_request)
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        except AttemptDeleteProtectedObjectError:
            return jsonify(message='Protected Role'), HTTPStatus.CONFLICT
        return jsonify(message='Role was deleted sucessfully'), HTTPStatus.OK


@role_blueprint.route(
    '/permissions/<uuid:role_id>',
    methods=(
        'POST',
        'DELETE',
    ),
)
@jwt_required()
@check_permission(permission=3)
def role_permissions(role_id):
    """
    Добавление | Удаление пермишина у роли.
    ---
    post:
     security:
      - AccessAuth: []
     summary: Добавление уровня доступа к роли
     parameters:
      - name: role_id
        in: path
        type: string
        required: true
      - name: permission_id
        in: query
        type: string
        required: true
     responses:
       '200':
         description: Permission assigned to role
       '403':
         description: Permission denied
       '404':
         description: Not found
       '409':
         description: Permission is already in use
     tags:
       - Permission
    delete:
     security:
      - AccessAuth: []
     summary: Удаление уровня доступа у роли
     parameters:
      - name: role_id
        in: path
        type: string
        required: true
      - name: permission_id
        in: query
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

    if request.method == 'POST':
        _request = {
            'permission_id': request.args.get('permission_id'),
            'role_id': role_id,
        }

        try:
            service.add_permission(**_request)
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        except UniqueConstraintError:
            return jsonify(message='Permissions is already in use'), HTTPStatus.CONFLICT
        return jsonify(message='Permissions assigned to role'), HTTPStatus.OK

    if request.method == 'DELETE':
        _request = {
            'permission_id': request.args.get('permission_id'),
            'role_id': role_id,
        }

        try:
            service.remove_permission(**_request)
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        return jsonify(message='Permission was deleted sucessfully'), HTTPStatus.OK
