from flasgger import Swagger
from flask import Flask
from flask_jwt_extended import JWTManager

from api.v1.user import auth_blueprint
from core.config import settings
from db.db import init_db

jwt = JWTManager()
app = Flask(__name__)

app.config['SECRET_PASSWORD_SALT'] = settings.PASSWORD_SALT

swagger = Swagger(app, config=settings.swagger_config)
app.register_blueprint(auth_blueprint)


def init_jwt(app: Flask, config: object = settings.jwt) -> None:
    app.config.from_object(config)
    jwt.init_app(app)


def main():
    init_db(app)
    init_jwt(app)
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
