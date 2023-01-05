from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture, authorization_header
from src.tests.integration.elements.fixtures import ElementFixture
from src.elements.models import Element
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_element_route(test_client):
    """
    GIVEN a request to the POST /elements endpoint
    WHEN the request body contains element attributes
    THEN a new element object is created
    """
    data = ElementFixture.default_obj()
    response: Response = test_client.post('/elements', json=data, headers={**authorization_header()})
    assert_is_ok(response)


def test_fetch_elements_route(test_client):
    """
    GIVEN a request to the GET /elements endpoint
    WHEN there exist element entities in database
    THEN the endpoint returns elements as list of dicts
    """
    response: Response = test_client.get('/elements', headers={**authorization_header()})
    assert_is_ok(response)


def test_fetch_element_by_id_route(test_client):
    """
    GIVEN a request to the GET /elements/{element.id} endpoint
    WHEN the uri contains an existing element id
    THEN the endpoint returns corresponding element object
    """
    element_id = ElementFixture().id
    response: Response = test_client.get(f'/elements/{element_id}', headers={**authorization_header()})
    assert_is_ok(response)


def test_update_element_by_id_route(test_client):
    """
    GIVEN a request to the PATCH /elements/{element.id} endpoint
    WHEN the request carries attributes of element to update
    THEN the element's attributes are updated
    """
    element_id = ElementFixture().id
    data = {
        "name": "My special button"
    }
    response: Response = test_client.patch(f'/elements/{element_id}', json=data, headers={**authorization_header()})
    assert_is_ok(response)


def test_delete_elements_by_id_route(test_client):
    """
    GIVEN a request to the DELETE /elements endpoint
    WHEN the request carries list of element ids to delete
    THEN the corresponding elements are deleted
    """
    element_id = ElementFixture().id
    data = {"elements": [element_id]}
    response: Response = test_client.delete('/elements', json=data, headers={**authorization_header()})
    assert_is_ok(response)
