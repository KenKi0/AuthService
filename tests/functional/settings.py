from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class TestSettings(BaseSettings):
    pg_db: str = Field('test', env='PG_DB')
    pg_host: str = Field('127.0.0.1:5432', env='PG_HOST')
    pg_port: str = Field(5432, env='PG_PORT')
    pg_user: str = Field('test_user', env='PG_USER')
    pg_password: str = Field('test', env='PG_PASSWORD')

    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    service_url: str = Field('http://127.0.0.1:8000', env='SERVICE_URL')


test_settings = TestSettings()
