import json
from pathlib import Path

import click
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, send_from_directory
from flask.cli import with_appcontext
from flask_jwt_extended import JWTManager
from flask_security import Security
from flask_swagger_ui import get_swaggerui_blueprint

from api.v1.components.perm_schemas import Permission
from api.v1.components.role_schemas import Role
from api.v1.components.user_schemas import ChangePassword, Login, Logout, RefreshToken, Register
from api.v1.permission import permissions_blueprint
from api.v1.role import role_blueprint
from api.v1.user import auth_blueprint, user_blueprint
from core.config import settings
from db.db import db, init_db
from models.permissions import create_permission
from models.role import create_role
from models.user import User

jwt = JWTManager()

security = Security()
swagger_ui = get_swaggerui_blueprint(
    settings.swagger.SWAGGER_URL,
    settings.swagger.API_URL,
    config={'app_name': 'My App'},
)


def init_blueprint(app: Flask):
    app.register_blueprint(swagger_ui, url_prefix=settings.swagger.SWAGGER_URL)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(role_blueprint)
    app.register_blueprint(permissions_blueprint)


def init_jwt(app: Flask, config: object = settings.jwt) -> None:
    app.config.from_object(config)
    jwt.init_app(app)


def init_security(app: Flask, config: object = settings.security) -> None:
    app.config.from_object(config)
    security.init_app(app)


def init_spec(app: Flask) -> None:
    spec = APISpec(
        title='Auth service',
        version='1.0.0',
        openapi_version='3.0.2',
        info={'description': 'Auth service'},
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
    )
    security_scheme_bearer = {
        'type': 'http',
        'description': 'Enter JWT Bearer token',
        'scheme': 'bearer',
        'bearerFormat': 'JWT',
    }
    # security
    spec.components.security_scheme('BearerAuth', security_scheme_bearer)
    # Auth
    spec.components.schema('Register', schema=Register)
    spec.components.schema('Login', schema=Login)
    spec.components.schema('ChangePassword', schema=ChangePassword)
    spec.components.schema('RefreshToken', schema=RefreshToken)
    spec.components.schema('Logout', schema=Logout)
    # Role
    spec.components.schema('Role', schema=Role)
    # Permission
    spec.components.schema('Permission', schema=Permission)

    for tag in settings.swagger.SPEC_TAGS:
        spec.tag(tag)

    for fn_name in app.view_functions:
        view_fn = app.view_functions[fn_name]
        spec.path(view=view_fn)
    swagger_path = Path(Path(__file__).parent, 'static/swagger.json')
    with open(swagger_path, 'w') as file:
        json.dump(spec.to_dict(), file, indent=4)

    @app.route('/static/<path:path>')
    def swagger(path):
        return send_from_directory('static', path)


def init_cli(app: Flask):
    @with_appcontext
    @app.cli.command('create_sudo')
    @click.argument('name')
    @click.argument('mail')
    @click.argument('password')
    def create_sudo(name: str, mail: str, password: str):
        _admin = {
            'username': name,
            'password': mail,
            'email': password,
            'is_super': True,
        }
        admin = User.query.filter_by(email=_admin['email']).first()
        if admin:
            return
        admin = User(**_admin)
        db.session.add(admin)
        db.session.commit()


def create_app():

    app = Flask(__name__)

    init_blueprint(app)
    init_db(app)
    init_jwt(app)
    init_security(app)
    init_spec(app)
    init_cli(app)

    return app


def main(app: Flask):
    create_permission()
    create_role()
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main(create_app())
