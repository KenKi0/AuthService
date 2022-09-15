from flask import Blueprint
from flask_pydantic_spec import Response

from .utils import api

role_blueprint = Blueprint('role', __name__, url_prefix='/api/v1/role')

# Временная заглушка (role_body импортируется из api.v1.components.role_schemas)
role_body = ''


@role_blueprint.route('/', methods=('GET', 'POST'))
@api.validate(body=role_body, resp=Response('HTTP_409', 'HTTP_204', 'HTTP_200'), tags=['role'])
def role():
    """Получение всех ролей | Добавление новой роли."""
    ...


@role_blueprint.route('/<uuid:user_id>', methods=('GET', 'PATCH', 'DELETE'))
@api.validate(body=role_body, resp=Response('HTTP_409', 'HTTP_204', 'HTTP_200'), tags=['role'])
def role_by_id(role_id):
    ...
