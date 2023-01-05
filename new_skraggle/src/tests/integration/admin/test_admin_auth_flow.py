from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture


def test_admin_required_decorator(test_client):
    '''
    GIVEN a request to a protected route
    WHEN the client is unauthenticated
    THEN the route is inaccessible to the client
    '''
    response: Response = test_client.get('/admin')
    assert response.status_code in [401, 403, 308]


def test_signup_route(test_client):
    '''
    GIVEN a request to the POST /admin endpoint
    WHEN the request payload carries the credentials of a non-existing user
    THEN a new user is registered
    '''
    credentials = AdminFixture.default_obj()
    response: Response = test_client.post('/admin', json=credentials)

    assert response.status_code == 200


def test_request_verification_route(test_client):
    '''
    GIVEN a request to the POST /admin/request-verification endpoint
    WHEN the request payload carries the email of an existing user
    THEN a new OTP is sent via email

    WHEN the request payload carries the email of a non-existing user
    THEN the endpoint returns error
    '''
    credentials = AdminFixture.default_obj()
    response: Response = test_client.post('/admin/request-verification', json={"email": credentials.get('email')})
    assert response.status_code == 200

    response: Response = test_client.post('/admin/request-verification', json={"email": "abc@ymail.com"})
    assert response.status_code == 406


def test_verify_account_route(test_client):
    '''
    GIVEN a request to the POST /admin/verify-account endpoint
    WHEN the request payload carries the email of an existing user
    THEN a new OTP is sent via email

    WHEN the request payload carries the email of a non-existing user
    THEN the endpoint returns error
    '''
    admin = AdminFixture().admin
    response: Response = test_client.post('/admin/verify-account',
                                          json={"email": admin.email, "token": admin.last_generated_token}
                                          )
    assert response.status_code == 200

    response: Response = test_client.post('/admin/verify-account', json={"email": admin.email, "token": ""})
    assert response.status_code == 406


def test_login_route(test_client):
    credentials = AdminFixture.default_obj()
    data = {
        "email": credentials.get("email"),
        "password": credentials.get("password")
    }
    response: Response = test_client.post('/admin/login', json=data)

    assert response.status_code == 200


def test_logout_route(test_client):
    '''
    GIVEN a request to the DELETE /admin/access-token endpoint
    WHEN the client is authenticated
    THEN the client's authorisation is revoked
    '''
    # step 1: send request to DELETE /admin/access-token and assert the status code is 200
    access_token = AdminFixture().access_token
    response: Response = test_client.delete('/admin/access-token', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    
    # step 2: make another request to a protected endpoint and assert the status code is 308, 401 or 403
    response = test_client.get('/admin')
    assert response.status_code in [308, 401, 403]

