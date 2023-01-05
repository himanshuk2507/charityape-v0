from flask import Response

from src.tests.integration.donations.fixtures import PledgeFixture
from src.tests.integration.admin.fixtures import AdminFixture, authorization_header
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_fetch_pledges_route(test_client):
    """
    GIVEN a request to the GET /donations/pledges endpoint
    WHEN there exist pledge entities in database
    THEN the endpoint returns pledges as list of dicts
    """
    response: Response = test_client.get('/donations/pledges', headers=authorization_header())
    assert_is_ok(response)


def test_create_pledges_route(test_client):
    """
    GIVEN a request to the POST /donations/pledges endpoint
    WHEN the request body contains pledge attributes
    THEN a new pledge object is created
    """
    data = PledgeFixture.default_obj()
    response: Response = test_client.post('/donations/pledges', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_fetch_pledge_by_id_route(test_client):
    """
    GIVEN a request to the GET /donations/pledges/<uuid> endpoint
    WHEN there exist pledge entities in database
    THEN the endpoint returns pledges as list of dicts
    """
    pledge_id = PledgeFixture().id
    response: Response = test_client.get(f'/donations/pledges/{pledge_id}', headers=authorization_header())
    assert_is_ok(response)


def test_update_pledge_by_id_route(test_client):
    """
    GIVEN a request to the PATCH /donations/pledges/{pledge_id} endpoint
    WHEN the request carries attributes of pledge to update
    THEN the pledge's attributes are updated
    """
    pledge_id = PledgeFixture().id
    data = {
        "name": "Postman",
        "start_date": "2022-07-02T11:55:23.560Z"
    }
    response: Response = test_client.patch(f'/donations/pledges/{pledge_id}', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_delete_pledges_by_id_route(test_client):
    """
    GIVEN a request to the DELETE /donations/pledges endpoint
    WHEN the request carries list of pledge ids to delete
    THEN the corresponding pledges are deleted
    """
    pledge_id = PledgeFixture().id
    data = {"ids": [pledge_id]}
    response: Response = test_client.delete('/donations/pledges', json=data, headers=authorization_header())
    assert_is_ok(response)