from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials, credentials

from skraggle.events.models import Packages


def test_add_package(test_client):
    '''
        GIVEN a request to the event-package/create route
        WHEN the request carries cprrect package data
        THEN the endpoint adds an entry with those package details
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()

    response = test_client.post(f'/event-package/create',
                                json={
                                    "name": "Kunal",
                                    "description": "efe",
                                    "price": 12,
                                    "direct_cost": 32,
                                    "number_of_packages_for_sale": 3,
                                    "qty_purchase_limit": 1
                                },
                                headers={"Authorization": f"Bearer {access_token}"}, )

    assert response.status_code == 200
    assert b'"success": true' in response.data


def test_all_packages(test_client):
    '''
        GIVEN a request to the event-package/all/1 route
        WHEN the request carries page number as query parameter
        THEN the endpoint returns list of packages based on indexing and that page
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()

    response = test_client.get(f'/event-package/all/1', headers={"Authorization": f"Bearer {access_token}"}, )

    assert response.status_code == 200
    assert b'"success": true' in response.data


def test_update_package(test_client):
    '''
        GIVEN a request to the event-package/update route
        WHEN the request carries cprrect package data and id of package to update
        THEN the endpoint updates the details passed on in the request
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()

    package = Packages.query.first()
    response = test_client.patch(f'/event-package/update?id={package.id}',
                                 json={
                                     "name": "Updated",
                                     "description": "updated description",
                                     "price": 10,
                                     "number_of_packages_for_sale": 3,
                                     "qty_purchase_limit": 1
                                 },
                                 headers={"Authorization": f"Bearer {access_token}"}, )

    assert response.status_code == 200
    assert b'"success": true' in response.data
    package = Packages.query.first()
    assert package.name == "Updated"
    assert package.description == "updated description"
    assert package.price == 10
    assert package.direct_cost == 32


def test_package_info(test_client):
    '''
        GIVEN a request to the event-package/info route
        WHEN the request carries id of the package to fetch details for
        THEN the endpoint returns details of that package
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()
    package = Packages.query.first()
    response = test_client.get(f'/event-package/info/{package.id}', headers={"Authorization": f"Bearer {access_token}"}, )

    assert response.status_code == 200
    assert b'"success": true' in response.data


def test_toggle_is_enabled(test_client):
    '''
        GIVEN a request to the event-package/toggle-is-enables route
        WHEN the request carries id of the package to fetch details for
        THEN the endpoint toggles is_enabled field for package
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()
    package = Packages.query.first()
    response = test_client.put(f'/event-package/toggle-is-enabled?id={package.id}', headers={"Authorization": f"Bearer {access_token}"}, )

    assert response.status_code == 200
    assert b'"success": true' in response.data


def test_add_participnts(test_client):
    '''
        GIVEN a request to the event-package/add-participants route
        WHEN the request carries id of the package to add the contacts to
        THEN the endpoint adds participants to the package
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()
    contacts = {
        "ids": [
            "397594cd-e16a-4740-aa36-aa6827fbca71",
            "7f236837-377a-469e-b974-3373fc43ee43",
            "a3c62304-aed6-4686-bd83-948b37a98c08"
        ]
    }
    package = Packages.query.first()
    response = test_client.post(f'/event-package/add-participants?id={package.id}',
                                json=contacts,
                                headers={"Authorization": f"Bearer {access_token}"}, )

    assert response.status_code == 200
    assert b'"success": true' in response.data


def test_remove_participants(test_client):
    '''
        GIVEN a request to the event-package/remove-participants route
        WHEN the request carries id of the package to remove the contacts from
        THEN the endpoint deletes participants from the package
        '''

    # Call the Test Auth Class
    access_token = TestAuthCredentials(credentials).auth_token()
    contacts = {
        "ids": [
            "397594cd-e16a-4740-aa36-aa6827fbca71",
            "7f236837-377a-469e-b974-3373fc43ee43",
            "a3c62304-aed6-4686-bd83-948b37a98c08"
        ]
    }
    package = Packages.query.first()
    response = test_client.delete(f'/event-package/remove-participants?id={package.id}',
                                  json=contacts,
                                  headers={"Authorization": f"Bearer {access_token}"}, )

    assert response.status_code == 200
    assert b'"success": true' in response.data


def test_delete_package(test_client):
    '''
        GIVEN a request to the event-package/delete route
        WHEN the request carries id of the package to be deleted
        THEN the endpoint deletes the corresponding package
        '''

    access_token = TestAuthCredentials(credentials).auth_token()
    package = Packages.query.first()
    response = test_client.delete(f'/event-package/delete?id={package.id}', headers={"Authorization": f"Bearer {access_token}"}, )

    assert response.status_code == 200
    assert b'"success": true' in response.data