from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from db.db import db
from models.permissions import Permission, RolePermission
from models.role import Role
from permission.payload_models import PermissionCreate, PermissionUpdate
from permission.services.permission import PermissionService
from utils.exceptions import NotFoundError, UniqueConstraintError

from .components.perm_schemas import Permission as PermissionSchem
from .components.role_schemas import Role as RoleSchem
from .utils import check_permission

permissions_blueprint = Blueprint('permission', __name__, url_prefix='/api/v1/')

service = PermissionService()


@permissions_blueprint.route('/permissions', methods=('GET',))
@jwt_required()
@check_permission(permission=3)
def permissions():
    """
    Получение всех уровней доступа из БД.
    ---
    get:
     security:
      - BearerAuth: []
     summary: Получение списка всех уровней доступа из базы
     responses:
       '200':
         description: Ok
       '204':
         description: Permissions list is empty
       '403':
         description: Permission denied
     tags:
       - Permission
    """
    try:
        permissions = service.get_all()
    except NotFoundError:
        return jsonify(message='Permissions list is empty'), HTTPStatus.NO_CONTENT
    if not permissions:
        return jsonify(message='Permissions list is empty'), HTTPStatus.NO_CONTENT
    return (
        jsonify(permissions=[PermissionSchem().dumps(permission) for permission in permissions]),
        HTTPStatus.OK,
    )

    # permissions = Permission.query.all()
    # if not permissions:
    #     return jsonify(message='Permissions list is empty'), HTTPStatus.NO_CONTENT

    # return (
    #     jsonify(permissions=[PermissionSchem().dumps(permission) for permission in permissions]),
    #     HTTPStatus.OK,
    # )


@permissions_blueprint.route(
    '/permission/<uuid:permission_id>',
    methods=(
        'GET',
        'PATCH',
        'DELETE',
    ),
)
@jwt_required()
@check_permission(permission=3)
def permission_by_id(permission_id):  # noqa: C901
    """
    Просмотр | Изменение | Удаление уровня доступа по id.
    ---
    get:
     security:
      - BearerAuth: []
     summary: Просмотр уровня доступа по id
     parameters:
      - name: permission_id
        in: path
        type: string
        required: true
     responses:
       '200':
         description: Ok
       '204':
         description: Role list is empty
       '403':
         description: Permission denied
       '404':
         description: Not found
     tags:
       - Permission
    patch:
     security:
      - BearerAuth: []
     summary: Измение уровня доступа по id
     parameters:
      - name: permission_id
        in: path
        type: string
        required: true
     requestBody:
       content:
        application/json:
         schema: Permission
     responses:
       '200':
         description: Permission was changed sucessfully
       '403':
         description: Permission denied
       '404':
         description: Not found
     tags:
       - Permission
    delete:
     security:
      - BearerAuth: []
     summary: Удаление уровня доступа по id
     parameters:
      - name: permission_id
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
       - Permission
    """

    if request.method == 'GET':
        _request = {
            'perm_id': permission_id,
        }
        try:
            service.get(**_request)
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND

        # TODO не приходят списки ролей

        # permission = Permission.query.filter_by(id=_request['permission_id']).first()
        # if not permission:
        #     return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        # roles = (
        #     db.session.query(Role)
        #     .join(RolePermission)
        #     .filter(RolePermission.perm_id == _request['permission_id'])
        #     .all()
        # )
        # if not permissions:
        #     return jsonify(message='Permissions list is empty'), HTTPStatus.NO_CONTENT
        # return (
        #     jsonify(
        #         permission=PermissionSchem().dumps(permission),
        #         roles=[RoleSchem().dumps(role) for role in roles],
        #     ),
        #     HTTPStatus.OK,
        # )

    if request.method == 'PATCH':
        _request = {
            'name': request.json.get('name'),
            'code': request.json.get('code'),
            'description': request.json.get('description'),
        }
        try:
            service.update(
                perm_id=permission_id,
                update_perm=PermissionUpdate(**_request),
            )
        except UniqueConstraintError:
            return jsonify(message='Permission is already in use'), HTTPStatus.CONFLICT
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        return jsonify(message='Permission was changed sucessfully'), HTTPStatus.OK

        # permission = Permission.query.filter_by(id=_request['id']).first()
        # if not permission:
        #     return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        # for key in _request:
        #     setattr(permission, key, _request[key])
        # db.session.add(permission)
        # db.session.commit()
        # return jsonify(message='Permission was changed sucessfully'), HTTPStatus.OK

    if request.method == 'DELETE':
        _request = {
            'perm_id': permission_id,
        }

        try:
            service.delete(**_request)
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        return jsonify(message='Permission was deleted sucessfully'), HTTPStatus.OK

        # permission = Permission.query.filter_by(id=_request['perm_id']).first()
        # if not permission:
        #     return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        # db.session.delete(permission)
        # db.session.commit()
        # return jsonify(message='Permission was deleted sucessfully'), HTTPStatus.OK


@permissions_blueprint.route('/permission', methods=('POST',))
@jwt_required()
@check_permission(permission=3)
def permission():
    """
    Добавление нового уровня доступа в БД.
    ---
    post:
     security:
      - BearerAuth: []
     summary: Добавление нового уровня доступа
     requestBody:
       content:
        application/json:
         schema: Permission
     responses:
       '200':
         description: New permission was created
       '409':
         description: Permission is already in use
       '403':
         description: Permission denied
     tags:
       - Permission
    """

    _request = {
        'name': request.json.get('name'),
        'code': request.json.get('code'),
        'description': request.json.get('description'),
    }
    try:
        service.create(PermissionCreate(**_request))
    except UniqueConstraintError:
        return jsonify(message='Permission is already in use'), HTTPStatus.CONFLICT
    return jsonify(message='New permission was created'), HTTPStatus.OK

    # permission = Permission.query.filter_by(name=_request['name']).first()
    # if permission:
    #     return jsonify(message='Permission is already in use'), HTTPStatus.CONFLICT
    # Permission(**_request).set()
    # return jsonify(message='New permission was created'), HTTPStatus.OK


@permissions_blueprint.route(
    '/permissions/<uuid:role_id>',
    methods=(
        'GET',
        'POST',
        'DELETE',
    ),
)
@jwt_required()
@check_permission(permission=3)
def role_permissions(role_id):
    """
    Получение | Добавление | Удаление уровня доступа роли.
    ---
    get:
     security:
      - BearerAuth: []
     summary: Получение списка всех уровней доступа роли
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
     tags:
       - Permission
    post:
     security:
      - BearerAuth: []
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
       '204':
         description: Permissions list is empty
       '403':
         description: Permission denied
       '409':
         description: Permission is already in use
     tags:
       - Permission
    delete:
     security:
      - BearerAuth: []
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
       '204':
         description: Permissions list is empty
       '403':
         description: Permission denied
       '409':
         description: Permission is already deleted
     tags:
       - Permission
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
            return jsonify(message='Permissions list is empty'), HTTPStatus.NO_CONTENT
        return (
            jsonify(roles=[PermissionSchem().dumps(permission) for permission in permissions]),
            HTTPStatus.OK,
        )

    if request.method == 'POST':
        _request = {
            'perm_id': request.args.get('permission_id'),
            'role_id': role_id,
        }
        role = Role.query.filter_by(id=_request['role_id']).first()
        if not role:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        role_permissions = RolePermission.query.filter_by(
            role_id=_request['role_id'],
            perm_id=_request['perm_id'],
        ).first()
        if role_permissions:
            return jsonify(message='Permissions is already in use'), HTTPStatus.CONFLICT
        RolePermission(**_request).set()
        return jsonify(message='Permissions assigned to role'), HTTPStatus.OK

    if request.method == 'DELETE':
        _request = {
            'perm_id': request.args.get('permission_id'),
            'role_id': role_id,
        }
        role = Role.query.filter_by(id=_request['role_id']).first()
        if not role:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        role_permission = RolePermission.query.filter_by(
            role_id=_request['role_id'],
            perm_id=_request['perm_id'],
        ).first()
        if not role_permission:
            return jsonify(message='Permission is already deleted'), HTTPStatus.CONFLICT
        db.session.delete(role_permission)
        db.session.commit()
        return jsonify(message='Permission was deleted sucessfully'), HTTPStatus.OK
