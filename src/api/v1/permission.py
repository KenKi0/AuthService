from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from core.config import settings
from permission.payload_models import PermissionCreate, PermissionUpdate
from permission.services.permission import PermissionService
from utils.exceptions import AttemptDeleteProtectedObjectError, NotFoundError, UniqueConstraintError

from .components.perm_schemas import Permission as PermissionSchem
from .utils import check_permission

permissions_blueprint = Blueprint('permission', __name__, url_prefix='/api/v1/')

service = PermissionService()


@permissions_blueprint.route('/permissions', methods=('GET',))
@jwt_required()
@check_permission(permission=settings.permission.Moderator)
def permissions():
    """
    Получение всех уровней доступа из БД.
    ---
    get:
     security:
      - AccessAuth: []
     summary: Получение списка всех уровней доступа из базы
     responses:
       '200':
         description: Ok
       '403':
         description: Permission denied
     tags:
       - Permission
    """
    return (
        jsonify(permissions=[PermissionSchem().dumps(permission) for permission in service.get_all()]),
        HTTPStatus.OK,
    )


@permissions_blueprint.route(
    '/permission/<uuid:permission_id>',
    methods=(
        'GET',
        'PATCH',
        'DELETE',
    ),
)
@jwt_required()
@check_permission(permission=settings.permission.Moderator)
def permission_by_id(permission_id):  # noqa: C901
    """
    Просмотр | Изменение | Удаление уровня доступа по id.
    ---
    get:
     security:
      - AccessAuth: []
     summary: Просмотр уровня доступа по id
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
    patch:
     security:
      - AccessAuth: []
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
       '409':
         description: Permission is already in use
     tags:
       - Permission
    delete:
     security:
      - AccessAuth: []
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
       '409':
         description: Protected Permission
     tags:
       - Permission
    """

    if request.method == 'GET':
        _request = {
            'perm_id': permission_id,
        }
        try:
            permission = service.get(**_request)
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        return (
            jsonify(PermissionSchem().dumps(permission)),
            HTTPStatus.OK,
        )

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

    if request.method == 'DELETE':
        _request = {
            'perm_id': permission_id,
        }

        try:
            service.delete(**_request)
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        except AttemptDeleteProtectedObjectError:
            return jsonify(message='Protected Permission'), HTTPStatus.CONFLICT
        return jsonify(message='Permission was deleted sucessfully'), HTTPStatus.OK


@permissions_blueprint.route('/permission', methods=('POST',))
@jwt_required()
@check_permission(permission=settings.permission.Moderator)
def permission():
    """
    Добавление нового уровня доступа в БД.
    ---
    post:
     security:
      - AccessAuth: []
     summary: Добавление нового уровня доступа
     requestBody:
       content:
        application/json:
         schema: Permission
     responses:
       '200':
         description: New permission was created
       '403':
         description: Permission denied
       '409':
         description: Permission is already in use
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
