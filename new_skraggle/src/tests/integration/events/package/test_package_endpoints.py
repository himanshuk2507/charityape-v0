from flask import Response

from src.tests.integration.admin.fixtures import authorization_header
from src.tests.integration.events.fixtures import PackagesFixture
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_package(test_client):
    """
    GIVEN a request to the POST /package/create endpoint
    WHEN the request body contains package attributes
    THEN a new package object is created
    """
    data = PackagesFixture.default_obj()
    response: Response = test_client.post('/package/create', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_list_packages(test_client):
    """
    GIVEN a request to the GET /package endpoint
    WHEN there exist package entities in database
    THEN the endpoint returns packages as list of dicts
    """
    response: Response = test_client.get('/package', headers=authorization_header())
    assert_is_ok(response)


def test_clone_package(test_client):
    """
    GIVEN a request to the DELETE /package/clone endpoint
    WHEN the request carries list of package ids to clone
    THEN the corresponding packages are cloned
    """
    package_id = PackagesFixture().id
    data = {
        "packages": [package_id]
    }
    response: Response = test_client.post('/package/clone', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_update_package(test_client):
    """
    GIVEN a request to the PATCH /package/{package.id} endpoint
    WHEN the request carries attributes of package to update
    THEN the package's attributes are updated
    """
    package_id = PackagesFixture().id
    data = {
        "name": "Update Integration Test",
        "description": "This is Integration Test",
        "price": 120,
        "direct_cost": 20,
        "number_of_packages_for_sale": 10,
        "qty_purchase_limit": 1,
        "early_bird_discount_enabled": True,
        "early_bird_discount_amount": 100,
        "early_bird_discount_cutoff_time": "2022-05-30:20:00",
        "early_bird_discount_type": "percentage"
    }
    response: Response = test_client.patch(f'/package/{package_id}', json=data, headers=authorization_header())
    assert_is_ok(response)


def test_package_info_by_id(test_client):
    """
    GIVEN a request to the GET /package/info/{package.id} endpoint
    WHEN the uri contains an existing package id
    THEN the endpoint returns corresponding package object
    """
    package_id = PackagesFixture().id
    response: Response = test_client.get(f'/package/info/{package_id}', headers=authorization_header())
    assert_is_ok(response)


def test_delete_package(test_client):
    """
    GIVEN a request to the DELETE /package/{package.id} endpoint
    WHEN the request carries list of package ids to delete
    THEN the corresponding packages are deleted
    """
    package_id = PackagesFixture().id
    data = {"packages": [package_id]}
    response: Response = test_client.delete('/package', json=data, headers=authorization_header())
    assert_is_ok(response)


# def test_toggle_is_enabled(test_client):
# To be implemented after endpoint is fixed