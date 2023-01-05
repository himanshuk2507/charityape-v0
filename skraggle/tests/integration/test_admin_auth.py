from datetime import timedelta
from flask_jwt_extended import create_access_token

from skraggle.profile.models import Admin
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials

email_verification_sent_confirmation_message = "An OTP to confirm your email has been sent to your email address."

'''
test-user credentials for registration/authentication
'''
credentials = dict(first_name="test", last_name="test", email="test@test.com", password="12345")

def test_user_required_decorator(test_client):
    '''
    GIVEN a request to a protected route
    WHEN the client is unauthenticated 
    THEN the corresponding error message is returned
    '''
    response = test_client.get('/')
    assert b"You aint logged in, no page for u!" in response.data


def test_signup_route(test_client):
    '''
    GIVEN a request to the admin/sign-up route
    WHEN the request payload carries the credentials of a non-existing user 
    THEN a new user row is entered to the DB
    '''

    credentials['email'] = 'random@mail.com'
    response = test_client.post('/admin/signup', json=credentials, follow_redirects=True)

    assert response.status_code == 200
    assert bytes(email_verification_sent_confirmation_message, "utf-8") in response.data


def test_login_route(test_client):
    '''
    GIVEN a request to the /admin/login route
    WHEN the request payload carries the credentials of an existing user 
    THEN the user is recognised
    '''

    response = test_client.post('/admin/login', json=credentials, follow_redirects=True)
    # since this user account has not been activated
    assert response.status_code == 401
    assert b"Please Activate your account" in response.data


def test_logout_route(test_client):
    '''
    GIVEN a request to the /admin/logout route 
    WHEN the Authorization header carries a valid access token 
    THEN the access token is revoked
    '''

    # create an access token for the first user in the DB 
    admin = Admin.query.filter_by(email=credentials["email"]).first()
    access_token = create_access_token(
        identity=admin.admin_id,
        expires_delta=timedelta(days=1),
        additional_claims={
            "is_admin": True,
            "org": admin.organization_id,
            "activated": True,
            "email": credentials['email'],
        },
    )

    # call the /admin/revoke endpoint 
    response = test_client.delete('/admin/logout', headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert b"Logged out" in response.data



def test_send_verification_email_route(test_client):
    '''
    GIVEN a POST request to the /email/verification/send route 
    WHEN the request body has a valid email field
    THEN a verification email is sent to the email address
    '''
    
    admin = TestAuthCredentials(credentials).admin
    response = test_client.post('/email/verification/send', json={"email": admin.email})

    assert response.status_code == 200
    assert bytes(email_verification_sent_confirmation_message, "utf-8") in response.data