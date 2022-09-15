import json

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_security import Security
from flask_swagger_ui import get_swaggerui_blueprint

from api.v1.components.user_schemas import ChangePassword, Login, RefreshToken, Register
from api.v1.user import auth_blueprint
from core.config import settings
from db.db import init_db

jwt = JWTManager()
app = Flask(__name__)
security = Security()
swagger_ui = get_swaggerui_blueprint(
    settings.swagger.SWAGGER_URL,
    settings.swagger.API_URL,
    config={'app_name': 'Auth'},
)

app.register_blueprint(swagger_ui, url_prefix=settings.swagger.SWAGGER_URL)
app.register_blueprint(auth_blueprint)


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
    spec.components.schema('Register', schema=Register)
    spec.components.schema('Login', schema=Login)
    spec.components.schema('ChangePassword', schema=ChangePassword)
    spec.components.schema('RefreshToken', schema=RefreshToken)

    for tag in settings.swagger.SPEC_TAGS:
        spec.tag(tag)

    for fn_name in app.view_functions:
        view_fn = app.view_functions[fn_name]
        spec.path(view=view_fn)

    with open('src/static/swagger.json', 'w') as file:
        json.dump(spec.to_dict(), file, indent=4)

    @app.route('/static/<path:path>')
    def swagger(path):
        return send_from_directory('static', path)


def main():
    init_db(app)
    init_jwt(app)
    init_security(app)
    init_spec(app)
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
