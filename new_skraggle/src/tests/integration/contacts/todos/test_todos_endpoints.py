from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.contacts.fixtures import ContactTodoFixture

from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_fetch_all_contact_todos_route(test_client):
    """
    GIVEN a request to GET /contacts/todos endpoint
    WHEN there exist contact todos entities
    THEN the route returns list of dicts of contact todos
    """
    access_token = AdminFixture().access_token
    ContactTodoFixture()
    response: Response = test_client.get("/contacts/todos",
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_add_contact_todos_route(test_client):
    """
    GIVEN a request to POST /contacts/todos endpoint
    WHEN the request contains contact todos data
    THEN the route returns dict of entities
    """
    access_token = AdminFixture().access_token
    todo = ContactTodoFixture.default_obj()
    response: Response = test_client.post("/contacts/todos", json=todo,
                                          headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_contact_todo_by_id_route(test_client):
    """
    GIVEN a request to GET /contacts/todos/{contact_todo.id} endpoint
    WHEN there exist contact entity with the given id
    THEN the route returns dict of to-dos for that entity
    """
    access_token = AdminFixture().access_token
    contact_todo_id = ContactTodoFixture().id
    response: Response = test_client.get(f"/contacts/todos/{contact_todo_id}",
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_update_contact_todo_by_id_route(test_client):
    """
    GIVEN a request to PATCH /contacts/todos/{contact_todo.id} endpoint
    WHEN there exist contact entity with the given id
    THEN the route updates contact to-do as passed fields
    """
    access_token = AdminFixture().access_token
    contact_todo_id = ContactTodoFixture().id
    data = {
        "completed": True,
        "details": "New details"
    }
    response: Response = test_client.patch(f"/contacts/todos/{contact_todo_id}", json=data,
                                           headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)
