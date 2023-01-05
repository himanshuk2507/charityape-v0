from flask import Response

from src.tests.integration.admin.fixtures import authorization_header
from src.tests.integration.events.fixtures import EventsInformationFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_event(test_client):
    """
    GIVEN a request to the POST /event/create endpoint
    WHEN the request body contains event attributes
    THEN a new event object is created
    """
    data = EventsInformationFixture.default_obj()
    response: Response = test_client.post('/event/create', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_list_events(test_client):
    """
    GIVEN a request to the GET /event endpoint
    WHEN there exist event entities in database
    THEN the endpoint returns events as list of dicts
    """
    response: Response = test_client.get('/event', headers=authorization_header())
    assert_is_ok(response)


def test_update_event(test_client):
    """
    GIVEN a request to the PATCH /event/{event.id} endpoint
    WHEN the request carries attributes of event to update
    THEN the event's attributes are updated
    """
    event_id = EventsInformationFixture().id
    data = {
        "name": "Test Event Update",
        "description": "This is Test",
        "event_image": "www.image.com",
        "event_sold_out_message": "This is Test",
        "venue": "Test",
        "address": "test",
        "city": "test",
        "state": "test",
        "zip_country": "12345",
        "enable_map": False,
        "display_option": "mobile",
        "max_no_of_total_participant": "5",
        "enable_one_time_event_donation": True,
        "event_start_date_time": "2022-05-30:12:00",
        "event_stop_date_time": "2022-05-30:12:00",
        "event_has_reg_cutoff_date": False
    }
    response: Response = test_client.patch(f'/event/{event_id}', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_event_info_by_id(test_client):
    """
    GIVEN a request to the GET /event/info/{event.id} endpoint
    WHEN the uri contains an existing event id
    THEN the endpoint returns corresponding event object
    """
    event_id = EventsInformationFixture().id
    response: Response = test_client.get(f'/event/info/{event_id}', headers=authorization_header())
    assert_is_ok(response)


def test_delete_event(test_client):
    """
    GIVEN a request to the DELETE /event/{event.id} endpoint
    WHEN the request carries list of event ids to delete
    THEN the corresponding events are deleted
    """
    event_id = EventsInformationFixture().id
    data = {"ids": [event_id]}
    response: Response = test_client.delete(f'/event', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_clone_event(test_client):
    """
    GIVEN a request to the DELETE /event/clone endpoint
    WHEN the request carries list of event ids to clone
    THEN the corresponding events are cloned
    """
    event_id = EventsInformationFixture().id
    data = {"events": [event_id]}
    response: Response = test_client.post('/event/clone', json=data, headers=authorization_header())
    assert_is_ok(response)


# def test_archive_event(test_client):
# To be added after endpoint fixed
