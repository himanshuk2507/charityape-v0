from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.contacts.fixtures import HouseHoldsFixture

from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_household_route(test_client):
    """
    GIVEN a request to POST /contacts/households endpoint
    WHEN the request contains household data
    THEN the route creates new household entry
    """
    access_token = AdminFixture().access_token
    household = HouseHoldsFixture.default_obj()
    household["name"] = "Updated Household name"
    response: Response = test_client.post('/contacts/households', json=household,
                                          headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_all_households_route(test_client):
    """
    GIVEN a request to GET /contacts/households endpoint
    WHEN there exist households entities
    THEN the route returns dict of those entities
    """
    access_token = AdminFixture().access_token
    response: Response = test_client.get('/contacts/households',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_delete_households_route(test_client):
    """
    GIVEN a request to DELETE /contacts/households endpoint
    WHEN there exist household entities with given uuids
    THEN the route deletes those entities
    """
    access_token = AdminFixture().access_token
    household_id = HouseHoldsFixture().id
    response: Response = test_client.delete('/contacts/households', json={"households": [household_id]},
                                            headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_household_by_id_route(test_client):
    """
    GIVEN a request to GET /contacts/households/<uuid> endpoint
    WHEN there exist household entity with given uuid
    THEN the route fetches dict of corresponding household uuid
    """
    access_token = AdminFixture().access_token
    household_id = HouseHoldsFixture().id
    response: Response = test_client.get(f'/contacts/households/{household_id}',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_update_household_by_id_route(test_client):
    """
    GIVEN a request to PATCH /contacts/households/<uuid> endpoint
    WHEN there exist household entity with given uuid
    THEN the route updates passed fields for household data
    """
    access_token = AdminFixture().access_token
    household_id = HouseHoldsFixture().id
    response: Response = test_client.patch(f'/contacts/households/{household_id}', json={"name": "Update again"},
                                           headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_household_members_route(test_client):
    """
    GIVEN a request to GET /contacts/households/<uuid>/members endpoint
    WHEN there exist household entity with given uuid
    THEN the route fetches member entities for corresponding household
    """
    access_token = AdminFixture().access_token
    household_id = HouseHoldsFixture().id
    response: Response = test_client.get(f'/contacts/households/{household_id}/members',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)
