import uuid
from http import HTTPStatus

from tests.functional.settings import test_settings


def test_register_correct(client):
    response = client.post(
        f'{test_settings.service_url}/api/v1/auth/register',
        json={
            'username': 'test',
            'email': 'testauth@gmail.com',
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK


def test_register_with_existing_email(client):
    response = client.post(
        f'{test_settings.service_url}/api/v1/auth/register',
        json={
            'username': 'test',
            'email': 'testauth@gmail.com',
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT


def test_login_correct(client):
    response = client.post(
        f'{test_settings.service_url}/api/v1/auth/login',
        json={
            'email': 'testauth@gmail.com',
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK


def test_login_unexisting_user(client):
    response = client.post(
        f'{test_settings.service_url}/api/v1/auth/login',
        json={
            'email': 'testauth1@gmail.com',
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_login_with_incorrect_password(client):
    response = client.post(
        f'{test_settings.service_url}/api/v1/auth/login',
        json={
            'email': 'testauth@gmail.com',
            'password': 'testpassword1',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_change_password_correct(client, get_user_id, login):
    tokens = login('testauth@gmail.com', 'testpassword')
    response = client.patch(
        f'{test_settings.service_url}/api/v1/auth/change-password',
        json={
            'old_password': 'testpassword',
            'new_password': 'testpassword1',
        },
        headers={'Authorization': f'Bearer {tokens["access_token"]}'},
    )
    assert response.status_code == HTTPStatus.OK


def test_change_password_with_invalid_password(client, get_user_id, login):
    tokens = login('testauth@gmail.com', 'testpassword1')
    response = client.patch(
        f'{test_settings.service_url}/api/v1/auth/change-password',
        json={
            'old_password': 'testpassword',
            'new_password': 'testpassword12',
        },
        headers={'Authorization': f'Bearer {tokens["access_token"]}'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_change_password_for_unexisting_user(client, create_tokens):
    access, refresh = create_tokens(str(uuid.uuid4()), [0])
    response = client.patch(
        f'{test_settings.service_url}/api/v1/auth/change-password',
        json={
            'old_password': 'testpassword',
            'new_password': 'testpassword12',
        },
        headers={'Authorization': f'Bearer {access}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_token_correct(client, login):
    tokens = login('testauth@gmail.com', 'testpassword1')
    response = client.post(
        f'{test_settings.service_url}/api/v1/auth/refresh-token',
        headers={'Authorization': f'Bearer {tokens["refresh_token"]}'},
    )
    assert response.status_code == HTTPStatus.OK


def test_refresh_token_with_incorrect_token(client, create_tokens):
    access, refresh = create_tokens(str(uuid.uuid4()), [0])
    response = client.post(
        f'{test_settings.service_url}/api/v1/auth/refresh-token',
        headers={'Authorization': f'Bearer {refresh}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_logout_correct(client, login):
    tokens = login('testauth@gmail.com', 'testpassword1')
    response = client.post(
        f'{test_settings.service_url}/api/v1/auth/logout',
        json={'from_all': False},
        headers={'Authorization': f'Bearer {tokens["access_token"]}'},
    )
    assert response.status_code == HTTPStatus.OK


def test_logout_with_incorrect_token(client, create_tokens):
    access, refresh = create_tokens(str(uuid.uuid4()), [0])
    response = client.post(
        f'{test_settings.service_url}/api/v1/auth/logout',
        json={'from_all': False},
        headers={'Authorization': f'Bearer {access}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_login_history_correct(client, login, get_user_id):
    user_id = get_user_id('testauth@gmail.com')
    tokens = login('testauth@gmail.com', 'testpassword1')
    response = client.get(
        f'{test_settings.service_url}/api/v1/user/login-history/{user_id}',
        headers={'Authorization': f'Bearer {tokens["access_token"]}'},
    )
    assert response.status_code == HTTPStatus.OK


def test_get_user_roles_correct(client, get_user_id, moderator_headers):
    user_id = get_user_id('testauth@gmail.com')
    response = client.get(
        f'{test_settings.service_url}/api/v1/user/roles/{user_id}',
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.OK


def test_get_unexisting_user_roles(client, moderator_headers):
    user_id = str(uuid.uuid4())
    response = client.get(
        f'{test_settings.service_url}/api/v1/user/roles/{user_id}',
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_user_roles_without_permission(client, create_tokens):
    user_id = str(uuid.uuid4())
    access, refresh = create_tokens(user_id, [0])
    response = client.get(
        f'{test_settings.service_url}/api/v1/user/roles/{user_id}',
        headers={'Authorization': f'Bearer {access}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_add_role_to_user_correct(client, get_user_id, get_role_id, moderator_headers):
    user_id = get_user_id('testauth@gmail.com')
    role_id = get_role_id('Moderator_test')
    response = client.post(
        f'{test_settings.service_url}/api/v1/user/roles/{user_id}',
        headers=moderator_headers,
        query_string={'role_id': role_id},
    )
    assert response.status_code == HTTPStatus.OK


def test_add_unexisting_role_to_user(client, get_user_id, moderator_headers):
    user_id = get_user_id('testauth@gmail.com')
    response = client.post(
        f'{test_settings.service_url}/api/v1/user/roles/{user_id}',
        headers=moderator_headers,
        query_string={'role_id': str(uuid.uuid4())},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_add_already_linked_role_to_user(client, get_user_id, get_role_id, moderator_headers):
    user_id = get_user_id('testauth@gmail.com')
    role_id = get_role_id('Moderator_test')
    response = client.post(
        f'{test_settings.service_url}/api/v1/user/roles/{user_id}',
        headers=moderator_headers,
        query_string={'role_id': role_id},
    )
    assert response.status_code == HTTPStatus.CONFLICT


def test_delete_role_from_user_correct(client, get_user_id, get_role_id, moderator_headers):
    user_id = get_user_id('testauth@gmail.com')
    role_id = get_role_id('Moderator_test')
    response = client.delete(
        f'{test_settings.service_url}/api/v1/user/roles/{user_id}',
        headers=moderator_headers,
        query_string={'role_id': role_id},
    )
    assert response.status_code == HTTPStatus.OK


def test_delete_unlinked_role_from_user(client, get_user_id, get_role_id, moderator_headers):
    user_id = get_user_id('testauth@gmail.com')
    role_id = get_role_id('Moderator_test')
    response = client.delete(
        f'{test_settings.service_url}/api/v1/user/roles/{user_id}',
        headers=moderator_headers,
        query_string={'role_id': role_id},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
