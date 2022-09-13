from datetime import timedelta
from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class BaseConfig(BaseSettings):
    class Config:
        env_file = Path(Path(__file__).parent.parent.parent, '.env')
        env_file_encoding = 'utf-8'


class RedisSettings(BaseConfig):
    HOST: str = '127.0.0.1'
    PORT: int = 6379

    class Config:
        env_prefix = 'REDIS_'

    @property
    def url(self):
        return f'redis://{self.HOST}:{self.PORT}'


class PostgresSettings(BaseConfig):
    USER: str
    PASSWORD: str
    DB: str
    HOST: str = '127.0.0.1'
    PORT: int = 5432

    @property
    def uri(self):
        return f'postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}'

    class Config:
        env_prefix = 'PG_'


class FlaskSettings(BaseConfig):
    HOST: str = '127.0.0.1'
    PORT: int = 5000

    class Config:
        env_prefix = 'FLASK_'


class JWTSettings(BaseConfig):
    SECRET: str = '245585dbb5cbe2f151742298d61d364880575bff0bdcbf4ae383f0180e7e47dd'
    REFRESH_TOKEN_EXP: timedelta = timedelta(days=10)
    ACCESS_TOKEN_EXP: timedelta = timedelta(minutes=20)

    class Config:
        env_prefix = 'JWT_'


class ProjectSettings(BaseConfig):
    PASSWORD_SALT: str = 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a'
    SWAGGER_CONFIG = {
        'headers': [],
        'openapi': '3.0.2',
        'specs': [
            {
                'endpoint': 'apispec_1',
                'route': '/apispec_1.json',
                'rule_filter': lambda rule: True,
                'model_filter': lambda tag: True,
            },
        ],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': '/openapi/',
    }
    redis: RedisSettings = RedisSettings()
    postgres: PostgresSettings = PostgresSettings()
    flask: FlaskSettings = FlaskSettings()
    jwt: JWTSettings = JWTSettings()


settings = ProjectSettings()
