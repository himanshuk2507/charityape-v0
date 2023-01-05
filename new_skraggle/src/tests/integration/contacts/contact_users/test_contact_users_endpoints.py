from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.contacts.fixtures import ContactUsersFixture, ContactTagsFixture

from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_contact_user_route(test_client):
    """
    GIVEN a request to POST /contacts/users endpoint
    WHEN the request body contains dict of contact_user data
    THEN the route creates new contact_user entry
    """
    access_token = AdminFixture().access_token
    contact_user = ContactUsersFixture.default_obj()
    contact_user["primary_email"] = "fastsseah@cutest.com"
    response: Response = test_client.post('/contacts/users', json=contact_user,
                                          headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_all_contact_users_route(test_client):
    """
    GIVEN a request to GET /contacts/users endpoint
    WHEN there exist contact_user entities
    THEN the route returns list of dict of contact_user entities
    """
    access_token = AdminFixture().access_token
    response: Response = test_client.get('/contacts/users',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_contact_user_by_id_route(test_client):
    """
    GIVEN a request to GET /contacts/users/<uuid> endpoint
    WHEN there exist contact_user entity with given uuid
    THEN the route returns dict of corresponding contact_user
    """
    access_token = AdminFixture().access_token
    contact_user_id = ContactUsersFixture().id
    response: Response = test_client.get(f'/contacts/users/{contact_user_id}',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_update_contact_user_by_id_route(test_client):
    """
    GIVEN a request to PATCH /contacts/users/<uuid> endpoint
    WHEN there exist contact_user entity with given uuid
    THEN the route updates passed fields for the corresponding contact_user
    """
    access_token = AdminFixture().access_token
    contact_user_id = ContactUsersFixture().id
    contact_tag_id = ContactTagsFixture().id
    data = {
        "first_name": "Jane",
        "tags": [contact_tag_id]
    }
    response: Response = test_client.patch(f'/contacts/users/{contact_user_id}', json=data,
                                           headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_delete_contact_user_by_id_route(test_client):
    """
    GIVEN a request to DELETE /contacts/users endpoint
    WHEN there exist contact_user entity with given uuid
    THEN the route deletes contact_user with given id
    """
    access_token = AdminFixture().access_token
    contact_user_id = ContactUsersFixture().id
    response: Response = test_client.delete('/contacts/users', json={"contacts": [contact_user_id]},
                                            headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_list_interactions_route(test_client):
    """
    GIVEN a request to GET /contacts/users/<uuid>/interactions endpoint
    WHEN there exist contact_user entity with given uuid
    THEN the route returns interactions entries for the given contact_user
    """
    access_token = AdminFixture().access_token
    contact_user_id = ContactUsersFixture().id
    response: Response = test_client.get(f'/contacts/users/{contact_user_id}/interactions',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_list_todos_route(test_client):
    """
    GIVEN a request to GET /contacts/users/<uuid>/todos endpoint
    WHEN there exist contact_user entity with given uuid
    THEN the route returns todos entries for the given contact_user
    """
    access_token = AdminFixture().access_token
    contact_user_id = ContactUsersFixture().id
    response: Response = test_client.get(f'/contacts/users/{contact_user_id}/todos',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_list_volunteer_activity_route(test_client):
    """
    GIVEN a request to GET /contacts/users/<uuid>/volunteer-activity endpoint
    WHEN there exist contact_user entity with given uuid
    THEN the route returns volunteer-activity entries for the given contact_user
    """
    access_token = AdminFixture().access_token
    contact_user_id = ContactUsersFixture().id
    response: Response = test_client.get(f'/contacts/users/{contact_user_id}/volunteer-activity',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)
