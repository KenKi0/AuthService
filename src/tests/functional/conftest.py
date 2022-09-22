import json
from http import HTTPStatus

import pytest
from flask import Flask
from flask_jwt_extended import create_access_token, create_refresh_token

from db.db import db
from db.redis import redis
from main import create_app
from models.permissions import Permission
from models.role import Role
from models.user import User

from .settings import test_settings


@pytest.fixture(scope='session')
def app():
    return create_app()


@pytest.fixture(scope='session')
def client(app: Flask):
    return app.test_client()


@pytest.fixture
def db_session():
    yield db.session
    db.session.remove()


@pytest.fixture
def redis_session():
    session = redis
    yield session
    session.flushall()


@pytest.fixture
def login(client):
    def _inner(email, password):
        request_body = json.dumps({'email': email, 'password': password})
        response = client.post(
            f'{test_settings.service_url}/api/v1/auth/login',
            data=request_body,
            content_type='application/json',
        )
        if response.status_code == HTTPStatus.OK:
            return response.json['tokens']
        else:
            raise Exception(f'Bad request: {response.status_code}')

    return _inner


@pytest.fixture
def admin_headers(client, login):
    tokens = login(email='admin_test@test.com', password='Test_12345')
    access_token = tokens['access_token']
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def moderator_headers(client, login):
    tokens = login(email='moderator_test@test.com', password='Test_12345')
    access_token = tokens['access_token']
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def user_headers_access(client, login):
    tokens = login(email='user_test@test.com', password='Test_12345')
    access_token = tokens['access_token']
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def user_headers_refresh(client, login):
    tokens = login(email='user_test@test.com', password='Test_12345')
    refresh_token = tokens['refresh_token']
    return {'Authorization': f'Bearer {refresh_token}'}


@pytest.fixture
def get_role_id(client):
    def _inner(name):
        role = Role.query.filter_by(name=name).first()
        return str(role.id)

    return _inner


@pytest.fixture
def get_prmission_id(client):
    def _inner(name):
        permission = Permission.query.filter_by(name=name).first()
        return str(permission.id)

    return _inner


@pytest.fixture
def get_user_id(client):
    def _inner(email):
        user = User.query.filter_by(email=email).first()
        return str(user.id)

    return _inner


@pytest.fixture
def create_tokens(client):
    def _inner(user_id: str, permissions: list[int]):
        additional_claims = {
            'permissions': permissions,
            'is_super': False,
        }
        access_token = create_access_token(
            identity=user_id,
            additional_claims=additional_claims,
            expires_delta=test_settings.jwt.ACCESS_TOKEN_EXP,
        )
        refresh_token = create_refresh_token(
            identity=user_id,
            expires_delta=test_settings.jwt.REFRESH_TOKEN_EXP,
        )
        return access_token, refresh_token

    return _inner
