from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.contacts.fixtures import ContactInteractionFixture

from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_interaction_route(test_client):
    """
    GIVEN a request to POST /contacts/interactions endpoint
    WHEN the request contains interaction data
    THEN the route creates new contact interactions entry
    """
    access_token = AdminFixture().access_token
    data = ContactInteractionFixture.default_obj()
    response: Response = test_client.post("/contacts/interactions", json=data,
                                          headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_list_interaction_route(test_client):
    """
    GIVEN a request to GET /contacts/interactions endpoint
    WHEN there exist interaction entities
    THEN the route returns dict of those entities
    """
    access_token = AdminFixture().access_token
    response: Response = test_client.get("/contacts/interactions",
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)
