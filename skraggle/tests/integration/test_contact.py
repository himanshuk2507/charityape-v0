from datetime import timedelta
from skraggle.profile.models import Admin
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.contact_users import ContactUsersFixture
from skraggle.tests.integration.test_admin_auth import credentials
from flask_jwt_extended import create_access_token

from skraggle.contact.models import CompanyUsers, ContactUsers

def test_contact_profile(test_client):
    '''
    GIVEN a request to the contacts/profile/contact_profile/contact_id route
    WHEN the request carries the contact_id of an existing contact 
    THEN the endpoint return all information related to contact id
    '''
    
    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()
    
    # Get Contacts User ID
    instance = ContactUsersFixture().get()
    contact_id = instance.id
    
    response = test_client.get(f'/contacts/profile/contact_profile/{contact_id}', headers={"Authorization": f"Bearer {access_token}"})
    
    assert response.status_code == 200
    
    

def test_contact_search(test_client):
    '''
    GIVEN a request to the contacts/search route
    WHEN the request carries search_string and page_number as query_paramenters
    THEN the endpoint returns paginated list of contacts where search_string is found in any of the fields
    '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()
    search_string = 'something'
    response = test_client.get(f'/contacts/search?search_string={search_string}&page=1',
                               headers={"Authorization": f"Bearer {access_token}"}
                               )
    assert response.status_code == 200

    search_string = 'notsomething'
    response = test_client.get(f'/contacts/search?search_string={search_string}&page=1',
                               headers={"Authorization": f"Bearer {access_token}"}
                               )
    assert response.status_code == 200
    assert b'"message": []' in response.data
    assert b'"success": true' in response.data