from flask import Response

from src.forms.models import Form
from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.forms.fixtures import FormFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_form_route(test_client):
    '''
    GIVEN a request to the POST /forms endpoint
    WHEN the request body carries form attributes
    THEN a new form object is created
    '''
    access_token = AdminFixture().access_token
    body = FormFixture().default_obj()
    body['name'] = 'my form'
    
    response: Response = test_client.post('/forms', json=body, headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_fetch_all_forms_route(test_client):
    '''
    GIVEN a request to the GET /forms endpoint
    WHEN there exist forms entities in database
    THEN the endpoint returns forms as list of dict
    '''
    access_token = AdminFixture().access_token
    response: Response = test_client.get('/forms', headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_fetch_form_by_id_route(test_client):
    '''
    GIVEN a request to the GET /forms/{form.id} endpoint
    WHEN the uri contains an existing form id
    THEN the endpoint returns corresponding form object
    '''
    access_token = AdminFixture().access_token
    form = FormFixture().form
    response: Response = test_client.get(f'/forms/{form.id}', headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_update_form_by_id_route(test_client):
    '''
    GIVEN a request to the PATCH /forms/{form.id} endpoint
    WHEN the request carries attributes of form to update
    THEN the form's attributes are updated
    '''
    access_token = AdminFixture().access_token
    form = FormFixture().form
    body = {
        "amount_presets": None,
        "anonymous_donation_allowed": True,
        "ask_mailing_address": True,
        "ask_phone_number": True,
        "auto_tag": True,
        "change_currency_for": None
    }
    response: Response = test_client.patch(f'/forms/{form.id}', json=body,
                                           headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_clone_form_by_id_route(test_client):
    '''
    GIVEN a request to the POST /forms/clone endpoint
    WHEN the request body carries list of form ids
    THEN a new form with same attributes is created
    '''
    access_token = AdminFixture().access_token
    form = FormFixture().form
    response: Response = test_client.post('/forms/clone', json={"forms": [form.id]}, 
                                          headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_archive_form_by_id_route(test_client):
    '''
    GIVEN a request to the POST /forms/archive endpoint
    WHEN the request carries list of forms to mark archive
    THEN the given forms are marked as archive
    '''
    access_token = AdminFixture().access_token
    form = FormFixture().form
    response: Response = test_client.post('/forms/archive', json={"forms": [form.id]},
                                          headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_get_archived_forms_route(test_client):
    '''
    GIVEN a request to the GET /forms/archive endpoint
    WHEN there are any forms marked as archived
    THEN the corresponding forms are returned
    '''
    access_token = AdminFixture().access_token
    response: Response = test_client.get('/forms/archive', headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)


def test_delete_form_by_id_route(test_client):
    '''
    GIVEN a request to the DELETE /forms endpoint
    WHEN the request carries list of form ids to delete
    THEN the corresponding forms are deleted
    '''
    access_token = AdminFixture().access_token
    form = FormFixture().form
    response: Response = test_client.delete('/forms', json={"forms": [form.id]},
                                            headers={'Authorization': f'Bearer {access_token}'})

    assert_is_ok(response)
