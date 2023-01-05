from datetime import timedelta
from flask_jwt_extended import create_access_token

from skraggle.profile.models import Admin
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.utils.bytes_to_dict_converter import byte_to_dict

email_verification_sent_confirmation_message = "An OTP to confirm your email has been sent to your email address."

'''
test-user credentials for registration/authentication
'''
credentials = dict(first_name="test", last_name="test", email="test@test.com", password="12345")


def test_create_form(test_client):
    '''
    GIVEN a request to a create form route
    WHEN the request body carries valid fields
    THEN the form is successfully created
    '''
    data = {
        "form_name": "testform732",
        "form_type": "donation",
        "desc": "linking form to a compaign",
        "status": "closed",
        "followers": ["folower1", "follower2", "follower3"],
        "is_default_donation": True,
        "is_default_currency": True,
        "tags": "",
        "is_minimum_amount": True,
        "is_processing_fee": True,
        "is_tribute": True
    }
    access_token = TestAuthCredentials().access_token
    response = test_client.post('/forms/create', json=data, headers={"Authorization": f"Bearer {access_token}"})

    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] == True
    assert "created successfully" in as_dict['message']


def test_view_forms(test_client):
    '''
        GIVEN a request to a get forms list route
        WHEN the url contains page number for records
        THEN the paginated list of forms is returned
        '''

    access_token = TestAuthCredentials().access_token
    response = test_client.get('/forms/all/1', headers={"Authorization": f"Bearer {access_token}"})

    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] is True
    assert len(as_dict['message']) > 0

