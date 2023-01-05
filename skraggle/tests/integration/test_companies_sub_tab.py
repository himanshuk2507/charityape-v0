from datetime import timedelta
from skraggle.profile.models import Admin
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.contact_users import ContactUsersFixture
from skraggle.tests.integration.test_admin_auth import credentials
from flask_jwt_extended import create_access_token

from skraggle.contact.models import CompanyUsers


def test_add_company(test_client):
    '''
    GIVEN a request to the company/add route
    WHEN the request carries json of a new company details
    THEN the endpoint creates new company and returns success message
    '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()

    response = test_client.post(f'/company/add',
                                headers={"Authorization": f"Bearer {access_token}"},
                                json={
                                    "company_name": "something",
                                    "primary_phone": "1234567890",
                                    "tag": "testing@mail.com",
                                    "tags": ["tag1", "tag2", "tag3"]
                                }
                                )

    assert response.status_code == 200
    assert b'Company - something created successfully' in response.data


def test_update_company_info(test_client):
    '''
        GIVEN a request to the company/update route
        WHEN the request carries json of company details
        THEN the endpoint updates company with company_id as query param and returns success message
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()

    cu = CompanyUsers.query.first()

    response = test_client.patch(f'/company/update?id={cu.company_id}',
                                 headers={"Authorization": f"Bearer {access_token}"},
                                 json={
                                     "company_name": "something",
                                     "primary_phone": "1234567890",
                                     "tag": "testing@mail.com",
                                     "tags": ["tag1", "tag2", "tag3"]
                                 }
                                 )

    assert response.status_code == 200
    response_string = 'company with id {company_id} Updated'.format(company_id=cu.company_id)
    assert bytes(response_string, 'utf-8') in response.data


def test_get_info(test_client):
    '''
        GIVEN a request to the company/all/page route
        WHEN the request carries page number as query parameter
        THEN the endpoint returns list of companies based on indexing and that page
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()

    response = test_client.get(f'/company/all/1', headers={"Authorization": f"Bearer {access_token}"}, )

    assert response.status_code == 200
    assert b'"success": true' in response.data


def test_get_information(test_client):
    '''
        GIVEN a request to the company/{comapny_id} route
        WHEN the request carries company_id as last part of URL
        THEN the endpoint returns details of that company
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()

    cu = CompanyUsers.query.first()

    response = test_client.get(f'/company/{cu.company_id}', headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    response_string = '"company_id": "{company_id}"'.format(company_id=cu.company_id)
    assert bytes(response_string, 'utf-8') in response.data


def test_search(test_client):
    '''
        GIVEN a request to the company/search route
        WHEN the request carries search_string and page_number as query_paramenters
        THEN the endpoint returns paginated list of companies where search_string is found in any of the fields
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()
    search_string = 'something'
    response = test_client.get(f'/company/search?search_string={search_string}&page=1',
                               headers={"Authorization": f"Bearer {access_token}"}
                               )
    assert response.status_code == 200
    cu = CompanyUsers.query.first()
    response_string = '"company_id": "{company_id}"'.format(company_id=cu.company_id)
    assert bytes(response_string, 'utf-8') in response.data
    assert b'"success": true' in response.data

    search_string = 'notsomething'
    response = test_client.get(f'/company/search?search_string={search_string}&page=1',
                               headers={"Authorization": f"Bearer {access_token}"}
                               )
    assert response.status_code == 200
    assert b'"message": []' in response.data
    assert b'"success": true' in response.data


def test_delete_company(test_client):
    '''
        GIVEN a request to the company/delete route
        WHEN the request carries list of company_ids and json object
        THEN the endpoint deletes companies with those ids
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()
    cu = CompanyUsers.query.all()
    cu_count = len(cu)

    response = test_client.delete(f'/company/delete',
                                  headers={"Authorization": f"Bearer {access_token}"},
                                  json={
                                      "companies": [cu[0].company_id]
                                  }
                                  )

    assert response.status_code == 200
    assert b'Deleted Successfully' in response.data

    cu = CompanyUsers.query.all()
    assert cu_count - 1 == len(cu)
