from flask import Flask
from flask_jwt_extended import JWTManager
from flask_security import Security

from api.v1.role import role_blueprint
from api.v1.user import auth_blueprint
from api.v1.utils import api
from core.config import settings
from db.db import init_db

jwt = JWTManager()
app = Flask(__name__)
security = Security()

app.register_blueprint(auth_blueprint)
app.register_blueprint(role_blueprint)


def init_jwt(app: Flask, config: object = settings.jwt) -> None:
    app.config.from_object(config)
    jwt.init_app(app)


def init_api(app: Flask) -> None:
    api.register(app)


def init_security(app: Flask, config: object = settings.security) -> None:
    app.config.from_object(config)
    security.init_app(app)


def main():
    init_db(app)
    init_jwt(app)
    init_api(app)
    init_security(app)
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
