from flask import Response

from src.tests.integration.admin.fixtures import authorization_header
from src.tests.integration.impact_area.fixtures import ImpactAreaFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_fetch_all_impact_areas_route(test_client):
    """
    GIVEN a request to the GET /impact-area endpoint
    WHEN there exist impact-area entities in database
    THEN the endpoint returns impact-areas as list of dicts
    """
    response: Response = test_client.get('/impact-area', headers=authorization_header())
    assert_is_ok(response)


def test_create_impact_area_route(test_client):
    """
    GIVEN a request to the POST /impact-area endpoint
    WHEN the request body contains impact-area attributes
    THEN a new impact-area object is created
    """
    data = ImpactAreaFixture.default_obj()
    response: Response = test_client.post('/impact-area', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_update_impact_area_route(test_client):
    """
    GIVEN a request to the PATCH /impact-area/{impact_area_id} endpoint
    WHEN the request carries attributes of impact-area to update
    THEN the impact-area's attributes are updated
    """
    impact_area_id = ImpactAreaFixture().id
    data = {"name": "Updated Impact", "description": "Updated Desc"}
    response: Response = test_client.patch(f'/impact-area/{impact_area_id}', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_fetch_impact_area_by_id_route(test_client):
    """
    GIVEN a request to the GET /impact-area/{impact_area_id} endpoint
    WHEN the uri contains an existing impact-area id
    THEN the endpoint returns corresponding impact-area object
    """
    impact_area_id = ImpactAreaFixture().id
    response: Response = test_client.get(f'/impact-area/{impact_area_id}', headers=authorization_header())
    assert_is_ok(response)


def test_delete_impact_area_by_id_route(test_client):
    """
    GIVEN a request to the DELETE /impact-area endpoint
    WHEN the request carries list of impact-area ids to delete
    THEN the corresponding impact-areas are deleted
    """
    impact_area_id = ImpactAreaFixture().id
    data = {"ids": [impact_area_id]}
    response: Response = test_client.delete('/impact-area', json=data, headers=authorization_header())
    assert_is_ok(response)
