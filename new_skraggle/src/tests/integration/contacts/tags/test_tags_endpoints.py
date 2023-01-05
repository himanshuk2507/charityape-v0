from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.contacts.fixtures import ContactTagsFixture

from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_tag_route(test_client):
    """
    GIVEN a request to POST /contacts/tags endpoint
    WHEN the request contains tags data
    THEN the route creates new tag entry
    """
    access_token = AdminFixture().access_token
    contact_tags = ContactTagsFixture.default_obj()
    contact_tags["name"] = "New Tag Name"
    response: Response = test_client.post("/contacts/tags", json=contact_tags,
                                          headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_all_tags_route(test_client):
    """
    GIVEN a request to GET /contacts/tags endpoint
    WHEN there exist tags entries
    THEN the route returns list of dict of those entities
    """
    access_token = AdminFixture().access_token
    ContactTagsFixture().default_obj()
    response: Response = test_client.get("/contacts/tags",
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_delete_tags_route(test_client):
    """
    GIVEN a request to DELETE /contacts/tags endpoint
    WHEN the request carries tag ids to delete
    THEN the route deletes tags corresponding to those ids
    """
    access_token = AdminFixture().access_token
    contact_tag_id = ContactTagsFixture().id
    response: Response = test_client.delete("/contacts/tags", json={"tags": [contact_tag_id]},
                                            headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_tag_by_id_route(test_client):
    """
    GIVEN a request to GET /contacts/tags/<uuid> endpoint
    WHEN there exist tag entity with the given id
    THEN the route deletes corresponding tag entity
    """
    access_token = AdminFixture().access_token
    contact_tag_id = ContactTagsFixture().id
    response: Response = test_client.get(f"/contacts/tags/{contact_tag_id}",
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_tagged_contacts_route(test_client):
    """
    GIVEN a request to GET /contacts/tags/<uuid>/contacts endpoint
    WHEN there exist contacts against the given tag id
    THEN the route returns contacts added for the tag
    """
    access_token = AdminFixture().access_token
    contact_tag_id = ContactTagsFixture().id
    response: Response = test_client.get(f"/contacts/tags/{contact_tag_id}/contacts",
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_update_tag_by_id_route(test_client):
    """
    GIVEN a request to PATCH /contacts/tags/<uuid> endpoint
    WHEN there exist tag with the given tag id
    THEN the route updates the tag fields data passed in request
    """
    access_token = AdminFixture().access_token
    contact_tag_id = ContactTagsFixture().id
    data = {
        "name": "Folks in Australia"
    }
    response: Response = test_client.patch(f"/contacts/tags/{contact_tag_id}", json=data,
                                           headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)
