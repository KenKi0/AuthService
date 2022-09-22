from http import HTTPStatus

from tests.functional.settings import test_settings

# /api/v1/permissions GET

# /api/v1/permission/<uuid:permission_id> GET
# /api/v1/permission/<uuid:permission_id> PATCH
# /api/v1/permission/<uuid:permission_id> DELETE

# /api/v1//permission POST


# /api/v1/permissions GET
def test_permissions_user_get(client, user_headers_access):
    response = client.get(
        f'{test_settings.service_url}/api/v1/permissions',
        headers=user_headers_access,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_permissions_moderator_get(client, moderator_headers):
    response = client.get(
        f'{test_settings.service_url}/api/v1/permissions',
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json['permissions']) == 3


def test_permissions_admin_get(client, admin_headers):
    response = client.get(
        f'{test_settings.service_url}/api/v1/permissions',
        headers=admin_headers,
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json['roles']) == 3


# /api/v1//permission POST
def test_permission_user_post(client, user_headers_access):
    response = client.post(
        f'{test_settings.service_url}/api/v1/permission',
        json={
            'name': 'User_new',
            'description': 'FORBIDDEN',
            'code': 4,
        },
        headers=user_headers_access,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_permission_moderator_post(client, moderator_headers):
    response = client.post(
        f'{test_settings.service_url}/api/v1/permission',
        json={
            'name': 'Moderator_new',
            'description': 'mod',
            'code': 4,
        },
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.OK


def test_permission_moderator_post_conflict(client, moderator_headers):
    response = client.post(
        f'{test_settings.service_url}/api/v1/permission',
        json={
            'name': 'Moderator_new',
            'description': 'mod',
            'code': 4,
        },
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.CONFLICT


def test_permission_admin_post(client, admin_headers):
    response = client.post(
        f'{test_settings.service_url}/api/v1/permission',
        json={
            'name': 'Admin_new',
            'description': 'admin',
            'code': 5,
        },
        headers=admin_headers,
    )
    assert response.status_code == HTTPStatus.OK


# /api/v1/permission/<uuid:permission_id> GET
def test_permission_by_id_user_get(
    client,
    user_headers_access,
    get_prmission_id,
):
    permission_id = get_prmission_id('Default_user_test')
    response = client.get(
        f'{test_settings.service_url}/api/v1/permission/{permission_id}',
        headers=user_headers_access,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_permission_by_id_moderator_get(
    client,
    moderator_headers,
    get_prmission_id,
):
    permission_id = get_prmission_id('Moderator_test')
    response = client.get(
        f'{test_settings.service_url}/api/v1/permission/{permission_id}',
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.OK


def test_permission_by_id_moderator_get_not_found(
    client,
    moderator_headers,
):
    response = client.get(
        f'{test_settings.service_url}/api/v1/permission/1234',
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_permission_by_id_admin_get(
    client,
    admin_headers,
    get_prmission_id,
):
    permission_id = get_prmission_id('Moderator_test')
    response = client.get(
        f'{test_settings.service_url}/api/v1/permission/{permission_id}',
        headers=admin_headers,
    )
    assert response.status_code == HTTPStatus.OK


# /api/v1/permission/<uuid:permission_id> PATCH
def test_permision_by_id_moderator_patch(  # noqa: F811
    client,
    moderator_headers,
    get_prmission_id,
):
    prmission_id = get_prmission_id('Moderator_new')
    response = client.patch(
        f'{test_settings.service_url}/api/v1/permission/{prmission_id}',
        json={
            'name': 'Moderator_new_new',
            'description': 'user',
            'code': 10,
        },
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.OK


def test_permision_by_id_moderator_patch(client, moderator_headers, get_prmission_id):  # noqa: F811
    prmission_id = get_prmission_id('Moderator_permission_new_new')
    response = client.patch(
        f'{test_settings.service_url}/api/v1/permission/{prmission_id}',
        json={
            'name': 'Test',
            'description': 'user',
            'code': 2,
        },
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.CONFLICT


# /api/v1/permission/<uuid:permission_id> DELETE
def test_permision_by_id_moderator_delete(
    client,
    moderator_headers,
    get_prmission_id,
):
    prmission_id = get_prmission_id('Moderator_permission_new_new')
    response = client.delete(
        f'{test_settings.service_url}/api/v1/permission/{prmission_id}',
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.OK


def test_permision_by_id_moderator_delete(  # noqa: F811
    client,
    moderator_headers,
    get_prmission_id,
):
    prmission_id = get_prmission_id('Default user')
    response = client.delete(
        f'{test_settings.service_url}/api/v1/permission/{prmission_id}',
        headers=moderator_headers,
    )
    assert response.status_code == HTTPStatus.CONFLICT
