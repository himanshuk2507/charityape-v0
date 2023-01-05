from flask import Response

from src.p2p.models import P2P, P2PEmail
from src.tests.integration.admin.fixtures import AdminFixture, authorization_header
from src.tests.integration.p2p.fixtures import P2PFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_p2p_route(test_client):
    """
    GIVEN a request to the POST /p2p endpoint
    WHEN the request body carries p2p attributes
    THEN a new p2p object is created
    """
    p2p = P2PFixture.default_obj()
    response: Response = test_client.post('/p2p', json=p2p, headers={**authorization_header()})
    assert_is_ok(response)


def test_list_p2ps_route(test_client):
    """
    GIVEN a request to the GET /p2p endpoint
    WHEN there exist p2p entities in database
    THEN the endpoint returns p2ps as list of dicts
    """
    response: Response = test_client.get('/p2p', headers={**authorization_header()})
    assert_is_ok(response)


def test_fetch_p2p_by_id_route(test_client):
    """
    GIVEN a request to the GET /p2p/{p2p.id} endpoint
    WHEN the uri contains an existing p2p id
    THEN the endpoint returns corresponding p2p object
    """
    p2p_id = P2PFixture().id
    response: Response = test_client.get(f'/p2p/{p2p_id}', headers={**authorization_header()})
    assert_is_ok(response)


def test_update_p2p_by_id_route(test_client):
    """
    GIVEN a request to the PATCH /p2p/{p2p.id} endpoint
    WHEN the request carries attributes of p2p to update
    THEN the p2p's attributes are updated
    """
    p2p_id = P2PFixture().id
    data = {
        "archived": True
    }
    response: Response = test_client.patch(f'/p2p/{p2p_id}', json=data, headers={**authorization_header()})
    assert_is_ok(response)


def test_delete_p2p_by_id_route(test_client):
    """
    GIVEN a request to the DELETE /p2p endpoint
    WHEN the request carries list of p2p ids to delete
    THEN the corresponding p2ps are deleted
    """
    p2p_id = P2PFixture().id
    data = {"ids": [p2p_id]}
    response: Response = test_client.delete('/p2p', json=data, headers={**authorization_header()})
    assert_is_ok(response)
