from flask import Response

from src.tests.integration.admin.fixtures import authorization_header
from src.tests.integration.events.fixtures import FieldsFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_fields(test_client):
    """
    GIVEN a request to the POST /field/create endpoint
    WHEN the request body contains field attributes
    THEN a new field object is created
    """
    data = FieldsFixture.default_obj()
    response: Response = test_client.post('/field/create', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_list_fields(test_client):
    """
    GIVEN a request to the GET /field endpoint
    WHEN there exist field entities in database
    THEN the endpoint returns fields as list of dicts
    """
    response: Response = test_client.get('/field', headers=authorization_header())
    assert_is_ok(response)


def test_update_fields(test_client):
    """
    GIVEN a request to the PATCH /field/{field.id} endpoint
    WHEN the request carries attributes of field to update
    THEN the field's attributes are updated
    """
    field_id = FieldsFixture().id
    data = {
        "field_label": "Doe Test",
        "reporting_label": "Testing update",
        "field_type": "Checkbox",
    }

    response: Response = test_client.patch(f'/field/{field_id}', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_field_info_by_id(test_client):
    """
    GIVEN a request to the GET /field/info/{field.id} endpoint
    WHEN the uri contains an existing field id
    THEN the endpoint returns corresponding field object
    """
    field_id = FieldsFixture().id
    response: Response = test_client.get(f'/field/info/{field_id}', headers=authorization_header())
    assert_is_ok(response)


def test_delete_field(test_client):
    """
    GIVEN a request to the DELETE /fieldendpoint
    WHEN the request carries list of field ids to delete
    THEN the corresponding fields are deleted
    """
    field_id = FieldsFixture().id
    data = {"ids": [field_id]}
    response: Response = test_client.delete(f'/field', json=data, headers=authorization_header())
    assert_is_ok(response)
