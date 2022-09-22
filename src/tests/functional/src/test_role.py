import json
from http import HTTPStatus

from tests.functional.settings import test_settings

# /api/v1/roles GET

# /api/v1/role POST

# /api/v1/role/<uuid:role_id> GET
# /api/v1/role/<uuid:role_id> PATCH
# /api/v1/role/<uuid:role_id> DELETE

# /api/v1/permissions/<uuid:role_id> POST
# /api/v1/permissions/<uuid:role_id> DELETE


# /api/v1/roles GET
def test_roles_user_get(client, user_headers_access):
    response = client.get(f'{test_settings.service_url}/api/v1/roles', headers=user_headers_access)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_roles_moderator_get(client, moderator_headers):
    response = client.get(f'{test_settings.service_url}/api/v1/roles', headers=moderator_headers)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json['roles']) == 3


def test_roles_admin_get(client, admin_headers):
    response = client.get(f'{test_settings.service_url}/api/v1/roles', headers=admin_headers)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json['roles']) == 3


# /api/v1/role POST
def test_role_user_post(client, user_headers_access):
    response = client.post(
        f'{test_settings.service_url}/api/v1/role',
        json={
            'name': 'User_role',
            'description': 'user',
        },
        headers=user_headers_access,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_role_moderator_post(client, moderator_headers):
    response = client.post(
        f'{test_settings.service_url}/api/v1/role',
        json={
            'name': 'Moderator_role',
            'description': 'mod',
        },
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.OK


def test_role_moderator_post_conflict(client, moderator_headers):
    response = client.post(
        f'{test_settings.service_url}/api/v1/role',
        json={
            'name': 'Moderator_test',
            'description': 'mod',
        },
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.CONFLICT


def test_role_admin_post(client, admin_headers):
    response = client.post(
        f'{test_settings.service_url}/api/v1/role',
        json={
            'name': 'Admin_role',
            'description': 'admin',
        },
        headers=admin_headers,
    )
    assert response.status_code == HTTPStatus.OK


# /api/v1/role/<uuid:role_id> GET
def test_role_by_id_user_get(client, user_headers_access, get_role_id):
    role_id = get_role_id('User')
    response = client.get(f'{test_settings.service_url}/api/v1/role/{role_id}', headers=user_headers_access)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_role_by_id_moderator_get(client, moderator_headers, get_role_id):
    role_id = get_role_id('Moderator_test')
    response = client.get(f'{test_settings.service_url}/api/v1/role/{role_id}', headers=moderator_headers)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json['permissions']) == 2


def test_role_by_id_moderator_get_not_found(client, moderator_headers):
    response = client.get(f'{test_settings.service_url}/api/v1/role/1234', headers=moderator_headers)
    assert response.status_code == HTTPStatus.NOT_FOUND


# падает
def test_role_by_id_admin_get(client, admin_headers, get_role_id):
    role_id = get_role_id('User')
    response = client.get(f'{test_settings.service_url}/api/v1/role/{role_id}', headers=admin_headers)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json['permissions']) == 1


# /api/v1/role/<uuid:role_id> PATCH
def test_role_by_id_moderator_patch(client, moderator_headers, get_role_id):
    role_id = get_role_id('Moderator_role')
    response = client.patch(
        f'{test_settings.service_url}/api/v1/role/{role_id}',
        json={
            'name': 'Moderator_role_new',
            'description': 'user',
        },
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.OK


def test_role_by_id_moderator_patch_conflict(client, moderator_headers, get_role_id):
    role_id = get_role_id('Moderator_role_new')
    response = client.patch(
        f'{test_settings.service_url}/api/v1/role/{role_id}',
        json={
            'name': 'User',
            'description': 'user',
        },
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.CONFLICT


# /api/v1/role/<uuid:role_id> DELETE
def test_role_by_id_moderator_delete(client, moderator_headers, get_role_id):
    role_id = get_role_id('Moderator_role_new')
    response = client.delete(f'{test_settings.service_url}/api/v1/role/{role_id}', headers=moderator_headers)
    assert response.status_code == HTTPStatus.OK

    response = client.get(f'{test_settings.service_url}/api/v1/role/{role_id}', headers=moderator_headers)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_role_by_id_moderator_delete_conflict(client, moderator_headers, get_role_id):
    role_id = get_role_id('User')
    response = client.delete(f'{test_settings.service_url}/api/v1/role/{role_id}', headers=moderator_headers)
    assert response.status_code == HTTPStatus.CONFLICT


# # /api/v1/permissions/<uuid:role_id> POST
def test_role_permission_user_post(client, user_headers_access, get_role_id, get_prmission_id):
    role_id = get_role_id('Moderator_test')
    permission_id = get_prmission_id('Test')
    response = client.post(
        f'{test_settings.service_url}/api/v1/permissions/{role_id}',
        json={'permission_id': permission_id},
        headers=user_headers_access,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


# -
def test_role_permission_moderator_post(client, moderator_headers, get_role_id, get_prmission_id):
    role_id = get_role_id('Moderator_test')
    permission_id = get_prmission_id('Test')

    response = client.post(
        f'{test_settings.service_url}/api/v1/permissions/{role_id}',
        json=json.dumps({'permission_id': permission_id}),
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.OK


# /api/v1/permissions/<uuid:role_id> DELETE
def test_role_permission_user_delete(client, user_headers_access, get_role_id, get_prmission_id):
    role_id = get_role_id('Moderator_test')
    permission_id = get_prmission_id('Test')
    response = client.delete(
        f'{test_settings.service_url}/api/v1/permissions/{role_id}',
        json={'permission_id': permission_id},
        headers=user_headers_access,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


#
def test_role_permission_moderator_delete(client, moderator_headers, get_role_id, get_prmission_id):
    role_id = get_role_id('Moderator_test')
    permission_id = get_prmission_id('Test')
    response = client.delete(
        f'{test_settings.service_url}/api/v1/permissions/{role_id}',
        json=json.dumps({'permission_id': permission_id}),
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.OK


def test_role_permission_moderator_delete_conflict(client, moderator_headers, get_role_id, get_prmission_id):
    role_id = get_role_id('Moderator_test')
    permission_id = get_prmission_id('Default_user_test')
    response = client.delete(
        f'{test_settings.service_url}/api/v1/permissions/{role_id}',
        json=json.dumps({'permission_id': permission_id}),
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.CONFLICT
