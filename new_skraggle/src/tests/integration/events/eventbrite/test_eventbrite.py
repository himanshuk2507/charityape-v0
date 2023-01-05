from flask import Response
from itsdangerous import json
from src.tests.integration.admin.fixtures import authorization_header
from src.tests.integration.events.eventbrite.fixtures import EventBriteKeyFixture, EventbriteEventsFixtures
from src.tests.integration.utils.assert_is_ok import assert_is_ok



def test_create_eventbrite_key(test_client):
     """
     GIVEN a request to the POST /eventbrite/eventbrite-settings endpoint
     WHEN the request body contains event attributes
     THEN a new event object is created
     """
     data = EventBriteKeyFixture.default_obj()
     response: Response = test_client.post('/eventbrite/eventbrite-settings', json=data, headers=authorization_header())
     assert_is_ok(response)
     
     


def test_eventbrite_key_set(test_client):
     """
     GIVEN a request to the GET /eventbrite/eventbrite-settings endpoint
     WHEN there exist event entities in database
     THEN the endpoint returns if eventbrite key is set
     """
     response: Response = test_client.get('/eventbrite/eventbrite-settings', headers=authorization_header())
     assert_is_ok(response)
     

def test_create_eventbrite(test_client):
     """
     GIVEN a request to the POST /eventbrite endpoint
     WHEN the request body contains event attributes
     THEN a new event object is created
     """
     data = EventbriteEventsFixtures.default_obj()
     response: Response = test_client.post('/eventbrite', json=data, headers=authorization_header())
     assert_is_ok(response)
     
     

def test_list__eventbrite(test_client):
     """
     GIVEN a request to the GET /eventbrite endpoint
     WHEN there exist event entities in database
     THEN the endpoint returns events as list of dicts
     """
     response: Response = test_client.get('/eventbrite', headers=authorization_header())
     assert_is_ok(response)
     

def test_get_eventbrite_by_id(test_client):
     """
     GIVEN a request to the GET /eventbrite/info/<uuid> endpoint
     WHEN the uri contains an existing event id
     THEN the endpoint returns corresponding event object
     """
     data = EventbriteEventsFixtures()
     response: Response = test_client.get(f'/eventbrite/info/{data.id}', headers=authorization_header())
     assert_is_ok(response)
     

def test_update_eventbrite(test_client):
     """
     GIVEN a request to the PATCH /eventbrite/<uuid> endpoint
     WHEN the request carries attributes of event to update
     THEN the event's attributes are updated
     """
     event = EventbriteEventsFixtures()
     data = dict(capacity=100)
     response: Response = test_client.patch(f'/eventbrite/{event.id}', json=data, headers=authorization_header())
     assert_is_ok(response)
     

def test_clone_eventbrite(test_client):
     """
     GIVEN a request to the GET /eventbrite/clone/<uuid> endpoint
     WHEN the uri contains an existing event id
     THEN the endpoint returns corresponding event object
     """
     data = EventbriteEventsFixtures()
     response: Response = test_client.get(f'/eventbrite/clone/{data.id}', headers=authorization_header())
     assert_is_ok(response)
     

def test_delete_eventbrite(test_client):
     """
     GIVEN a request to the DELETE /eventbrite endpoint
     WHEN the uri contains an existing event id
     THEN the endpoint delete corresponding event object
     """
     event = EventbriteEventsFixtures()
     data = {
          "ids": [event.id]
          }
     
     response: Response = test_client.delete(f'/eventbrite', json=data, headers=authorization_header())
     assert_is_ok(response)