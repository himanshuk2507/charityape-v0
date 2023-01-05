from flask import Response

from src.tests.integration.donations.fixtures import DonationSourceFixture
from src.tests.integration.admin.fixtures import authorization_header
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_fetch_sources_route(test_client):
    """
    GIVEN a request to the GET /donations/sources endpoint
    WHEN there exist source entities in database
    THEN the endpoint returns sources as list of dicts
    """
    response: Response = test_client.get('/donations/sources', headers=authorization_header())
    assert_is_ok(response)


def test_create_source_route(test_client):
    """
    GIVEN a request to the POST /donations/sources endpoint
    WHEN the request body contains source attributes
    THEN a new source object is created
    """
    data = DonationSourceFixture.default_obj()
    data['name'] = 'abcde'
    response: Response = test_client.post('/donations/sources', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_fetch_source_by_id_route(test_client):
    """
    GIVEN a request to the GET /donations/sources/<uuid> endpoint
    WHEN there exist source entities in database
    THEN the endpoint returns sources as list of dicts
    """
    source_id = DonationSourceFixture().id
    response: Response = test_client.get(f'/donations/sources/{source_id}', headers=authorization_header())
    assert_is_ok(response)


def test_update_source_by_id_route(test_client):
    """
    GIVEN a request to the PATCH /donations/sources/{source_id} endpoint
    WHEN the request carries attributes of source to update
    THEN the source's attributes are updated
    """
    source_id = DonationSourceFixture().id
    data = {"name": "Toothpick"}
    response: Response = test_client.patch(f'/donations/sources/{source_id}', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_delete_sources_by_id_route(test_client):
    """
    GIVEN a request to the DELETE /donations/sources endpoint
    WHEN the request carries list of source ids to delete
    THEN the corresponding sources are deleted
    """
    source_id = DonationSourceFixture().id
    data = {"ids": [source_id]}
    response: Response = test_client.delete(f'/donations/sources', json=data, headers=authorization_header())
    assert_is_ok(response)
