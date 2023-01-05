from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.contacts.fixtures import ContactCompaniesFixture, ContactUsersFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_company_route(test_client):
    """
    GIVEN a request to POST /contacts/companies endpoint
    WHEN the request body contains company parameters
    THEN the route creates new company entry
    """
    access_token = AdminFixture().access_token
    data = ContactCompaniesFixture.default_obj()
    response: Response = test_client.post('/contacts/companies',
                                          json=data,
                                          headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_list_companies_route(test_client):
    """
    GIVEN a request to GET /contacts/companies endpoint
    WHEN there exist company entities
    THEN the route returns list of dicts of companies
    """
    access_token = AdminFixture().access_token
    response: Response = test_client.get('/contacts/companies',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_company_by_id_route(test_client):
    """
    GIVEN a request to GET /contacts/companies/<uuid> endpoint
    WHEN there exists a company entity with the given uuid
    THEN the route returns dict of the corresponding uuid company
    """
    access_token = AdminFixture().access_token
    company_id = ContactCompaniesFixture().id
    response: Response = test_client.get(f'/contacts/companies/{company_id}',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_update_company_by_id_route(test_client):
    """
    GIVEN a request to PATCH /contacts/companies/<uuid> endpoint
    WHEN there exists a company with the given UUID
    THEN the route updates the passed field values for the company entity corresponding to the uuid
    """
    access_token = AdminFixture().access_token
    company_id = ContactCompaniesFixture().id
    contact_user_id = ContactUsersFixture().id
    data = {
        "name": "Facebook",
        "primary_contact": contact_user_id
    }
    response: Response = test_client.patch(f'/contacts/companies/{company_id}', json=data,
                                           headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_delete_companies_route(test_client):
    """
    GIVEN a request to DELETE /contacts/companies endpoint
    WHEN the request body contains list of company ids to delete
    THEN the route deletes the corresponding company entries
    """
    access_token = AdminFixture().access_token
    company_id = ContactCompaniesFixture().id
    response: Response = test_client.delete('/contacts/companies', json={"companies": [company_id]},
                                            headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_associated_contacts_route(test_client):
    """
    GIVEN a request to GET /contacts/companies/<uuid>/contacts endpoint
    WHEN there exist contacts associated to company with given id
    THEN the route returns list of dicts of those contacts
    """
    access_token = AdminFixture().access_token
    company_id = ContactCompaniesFixture().id
    response: Response = test_client.get(f'/contacts/companies/{company_id}/contacts',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_add_associated_contacts_route(test_client):
    """
    GIVEN a request to POST /contacts/companies/<uuid>/contacts endpoint
    WHEN there exist company with given uuid and request body contains list of contacts
    THEN the route adds associated contacts for given company
    """
    access_token = AdminFixture().access_token
    company_id = ContactCompaniesFixture().id
    contact_user_id = ContactUsersFixture().id

    data = {
        "contacts": [
            {
                "contact_id": contact_user_id,
                "position": "CEO"
            }
        ]
    }

    response: Response = test_client.post(f'/contacts/companies/{company_id}/contacts', json=data,
                                          headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_delete_associated_contacts(test_client):
    """
    GIVEN a request to DELETE /contacts/companies/<uuid>/contacts endpoint
    WHEN there exist company with given uuid
    THEN the route deletes associated contacts entries for company
    """
    access_token = AdminFixture().access_token
    company_id = ContactCompaniesFixture().id
    contact_user_id = ContactUsersFixture().id
    data = {
        "contacts": [contact_user_id]
    }
    response: Response = test_client.delete(f'/contacts/companies/{company_id}/contacts', json=data,
                                            headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_list_interactions_route(test_client):
    """
    GIVEN a request to GET /contacts/companies/<uuid>/interactions endpoint
    WHEN there exist company with given uuid
    THEN the route returns list of dicts of interactions for the company
    """
    access_token = AdminFixture().access_token
    company_id = ContactCompaniesFixture().id
    response: Response = test_client.get(f'/contacts/companies/{company_id}/interactions',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_list_todos_route(test_client):
    """
    GIVEN a request to GET /contacts/companies/<uuid>/interactions endpoint
    WHEN there exist company with given uuid
    THEN the route returns list of dicts of todos for the company
    """
    access_token = AdminFixture().access_token
    company_id = ContactCompaniesFixture().id
    response: Response = test_client.get(f'/contacts/companies/{company_id}/todos',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)