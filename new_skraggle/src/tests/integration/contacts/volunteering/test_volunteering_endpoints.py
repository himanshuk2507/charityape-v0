from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.contacts.fixtures import VolunteerActivityFixture

from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_list_volunteer_activity_route(test_client):
    """
    GIVEN a request to GET /contacts/volunteer-activity endpoint
    WHEN there exist volunteer activity entries
    THEN the route returns dict of those entities
    """
    access_token = AdminFixture().access_token
    VolunteerActivityFixture()
    response: Response = test_client.get("/contacts/volunteer-activity",
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_create_volunteer_activity_route(test_client):
    """
    GIVEN a request to POST /contacts/volunteer-activity endpoint
    WHEN the request body contains volunteer activity data
    THEN the route creates new contact volunteer activity
    """
    access_token = AdminFixture().access_token
    volunteer_activity = VolunteerActivityFixture.default_obj()
    response: Response = test_client.post("/contacts/volunteer-activity", json=volunteer_activity,
                                          headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)
