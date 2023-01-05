from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_whoami_route(test_client):
    '''
    GIVEN a request to the GET /admin endpoint
    WHEN the Admin account is registered
    THEN the Admin account with jwt token is returned
    '''
    access_token = AdminFixture().access_token
    response: Response = test_client.get('/admin', headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_update_admin_profile_route(test_client):
    '''
    GIVEN a request to the PATCH /admin endpoint
    WHEN the request carries field(s) to update
    THEN User field(s) is updated to new value(s).
    '''
    access_token = AdminFixture().access_token
    response: Response = test_client.patch('/admin', json={"first_name": "Hippo"}, headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_revoke_access_token_route(test_client):
    '''
    GIVEN a request to the DELETE /admin/access-token endpoint
    WHEN the client has access token
    THEN the client's access token is revoked
    '''
    access_token = AdminFixture().access_token
    response: Response = test_client.delete('/admin/access-token', headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_reset_password_route(test_client):
    '''
    GIVEN a request to the POST /admin/password endpoint
    WHEN the request carries email of the user account
    THEN the password reset request is made
    '''
    access_token = AdminFixture().access_token
    response: Response = test_client.post('/admin/password', json={"email": "test@test.com"},
                                          headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_change_password_route(test_client):
    '''
    GIVEN a request to the PATCH /admin/password endpoint
    WHEN the request carries old and new passwords
    THEN the user password is changed
    '''
    access_token = AdminFixture().access_token
    data = {
        "old": "12345",
        "new": "123457"
    }
    response: Response = test_client.patch('/admin/password', json=data,
                                           headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_confirm_password_reset_route(test_client):
    '''
    GIVEN a request to the POST /admin/password/confirm endpoint
    WHEN the request carries email and last generated token
    THEN the user password reset is confirmed
    '''
    admin_fixture = AdminFixture()
    access_token = admin_fixture.access_token
    token = admin_fixture.admin.last_generated_token
    data = {
        "email": "test@test.com",
        "token": token
    }
    response: Response = test_client.post('/admin/password/confirm', json=data,
                                          headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)