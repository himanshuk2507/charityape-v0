from flask import Response

from src.tests.integration.admin.fixtures import authorization_header
from src.tests.integration.keywords.fixtures import KeywordFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_fetch_all_keywords_route(test_client):
    """
    GIVEN a request to the GET /keyword endpoint
    WHEN there exist keyword entities in database
    THEN the endpoint returns keywords as list of dicts
    """
    response: Response = test_client.get('/keyword', headers=authorization_header())
    assert_is_ok(response)


def test_create_keywords_route(test_client):
    """
    GIVEN a request to the POST /keyword endpoint
    WHEN the request body contains keyword attributes
    THEN a new keyword object is created
    """
    data = KeywordFixture.default_obj()
    response: Response = test_client.post('/keyword', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_update_keywords_route(test_client):
    """
    GIVEN a request to the PATCH /keyword/{keyword.id} endpoint
    WHEN the request carries attributes of keyword to update
    THEN the keyword's attributes are updated
    """
    keyword_id = KeywordFixture().id
    data = {"name": "Test Update"}
    response: Response = test_client.patch(f'/keyword/{keyword_id}', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_fetch_keyword_by_id_route(test_client):
    """
    GIVEN a request to the GET /keyword/{keyword.id} endpoint
    WHEN the uri contains an existing keyword id
    THEN the endpoint returns corresponding keyword object
    """
    keyword_id = KeywordFixture().id
    response: Response = test_client.get(f'/keyword/{keyword_id}', headers=authorization_header())
    assert_is_ok(response)


def test_delete_keywords_by_id_route(test_client):
    """
    GIVEN a request to the DELETE /keyword endpoint
    WHEN the request carries list of keyword ids to delete
    THEN the corresponding keywords are deleted
    """
    keyword_id = KeywordFixture().id
    data = {"ids": [keyword_id]}
    response: Response = test_client.delete('/keyword', json=data, headers=authorization_header())
    assert_is_ok(response)
