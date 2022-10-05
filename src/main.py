import json
from pathlib import Path

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, request, send_from_directory
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
from db.db import init_db
from db.redis import redis
from utils.command import init_cli
from utils.tracing import configure_tracer
from utils.middlewares import RateLimitMiddleware

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
    security_scheme_access = {
        'type': 'http',
        'description': 'Enter JWT Bearer token',
        'scheme': 'bearer',
        'bearerFormat': 'JWT',
        'name': 'access_token',
    }
    security_scheme_refresh = {
        'type': 'http',
        'description': 'Enter JWT Bearer token',
        'scheme': 'bearer',
        'bearerFormat': 'JWT',
        'name': 'refresh_token',
    }
    # security
    spec.components.security_scheme('AccessAuth', security_scheme_access)
    spec.components.security_scheme('RefreshAuth', security_scheme_refresh)
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


def is_have_request_id():
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('request id is required')


def create_app():

    app = Flask(__name__)
    app.before_request(is_have_request_id)
    app.wsgi_app = RateLimitMiddleware(app.wsgi_app, app, redis)

    init_blueprint(app)
    init_db(app)
    init_jwt(app)
    init_security(app)
    init_spec(app)
    init_cli(app)
    configure_tracer(app)

    return app


def main(app: Flask):
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main(create_app())
