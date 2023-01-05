from flask import Response

from src.tests.integration.admin.fixtures import authorization_header
from src.tests.integration.events.fixtures import PromoCodeFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_code(test_client):
    """
    GIVEN a request to the POST /promocode/create endpoint
    WHEN the request body contains promocode attributes
    THEN a new promocode object is created
    """
    data = PromoCodeFixture.default_obj()
    response: Response = test_client.post('/promocode/create', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_list_promocode(test_client):
    """
    GIVEN a request to the GET /promocode endpoint
    WHEN there exist promocode entities in database
    THEN the endpoint returns promocodes as list of dicts
    """
    response: Response = test_client.get('/promocode', headers=authorization_header())
    assert_is_ok(response)


def test_update_promocode(test_client):
    """
    GIVEN a request to the PATCH /promocode/{promocode.id} endpoint
    WHEN the request carries attributes of promocode to update
    THEN the promocode's attributes are updated
    """
    promocode_id = PromoCodeFixture().id
    data = {
        "code": "SAVE8888",
        "description": "2nd Save Testing",
        "discount": "200",
        "max_user": "4",
    }
    response: Response = test_client.patch(f'/promocode/{promocode_id}', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_promocode_info_by_id(test_client):
    """
    GIVEN a request to the GET /promocode/info/{promocode.id} endpoint
    WHEN the uri contains an existing promocode id
    THEN the endpoint returns corresponding promocode object
    """
    promocode_id = PromoCodeFixture().id
    response: Response = test_client.get(f'/promocode/info/{promocode_id}', headers=authorization_header())
    assert_is_ok(response)


def test_delete_promocode(test_client):
    """
    GIVEN a request to the DELETE /promocode endpoint
    WHEN the request carries list of promocode ids to delete
    THEN the corresponding promocode are deleted
    """
    promocode_id = PromoCodeFixture().id
    data = {"promocodes": [promocode_id]}
    response: Response = test_client.delete('/promocode', json=data, headers=authorization_header())
    assert_is_ok(response)
