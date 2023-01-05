from uuid import uuid1

from skraggle.config import db
from skraggle.contact.models import TagUsers
from skraggle.tests.integration.fixtures.fixtures import segmentuser, user

tags_route = '/tags'


def test_add_tag(test_client, user):
    """
    GIVEN a request to the Add Tag endpoint
    WHEN the request body contains the right data
    THEN a new Tag is created
    """

    _user, _access_token = user
    response = test_client.post(f'{tags_route}/add',
                                json={
                                    "tag_name": "test_tag"
                                },
                                headers={"Authorization": f"Bearer {_access_token}"})

    assert response.status_code == 200
    assert b'"message": "Tag Created Successfully"' in response.data
    assert b'"success": true' in response.data

    response = test_client.post(f'{tags_route}/add',
                                json={
                                    "tag_name": "test_tag"
                                },
                                headers={"Authorization": f"Bearer {_access_token}"})

    assert response.status_code == 200
    assert b'"message": "Tag Name already exists"' in response.data
    assert b'"success": true' in response.data


def test_update_tag(test_client, user):
    """
    GIVEN a request to the Update Tag endpoint
    WHEN the request body contains correct data
    THEN a the tag is updated if there is no tag already existing with that name
    """

    _user, _access_token = user
    tag = TagUsers.query.first()
    response = test_client.patch(f'{tags_route}/update?tag_id={tag.tag_id}',
                                json={
                                    "tag_name": "update_tag"
                                },
                                headers={"Authorization": f"Bearer {_access_token}"})

    assert response.status_code == 200
    response_string = f"Tag with id {tag.tag_id} Updated"
    assert bytes(response_string, 'utf-8') in response.data

    response = test_client.patch(f'{tags_route}/update?tag_id={tag.tag_id}',
                                json={
                                    "tag_name": "update_tag"
                                },
                                headers={"Authorization": f"Bearer {_access_token}"})

    assert response.status_code == 406
    assert b'"message": "Tag Name already exists"' in response.data
    assert b'"success": false' in response.data


def test_get_tag_info(test_client, user):
    """
    GIVEN a request to the View All Tag Details endpoint
    WHEN the request url contains a valid page number as a parameter
    THEN the corresponding Tags are returned
    """
    _user, _access_token = user
    response = test_client.get(f'{tags_route}/details/1',
                                 headers={"Authorization": f"Bearer {_access_token}"})

    assert response.status_code == 200
    assert b'"success": true' in response.data


def test_get_tag_information(test_client, user):
    """
    GIVEN a request to the View Specific Tag endpoint
    WHEN the request url contains a valid Tag id as a parameter
    THEN the corresponding Tag is returned
    """
    _user, _access_token = user
    tag = TagUsers.query.first()
    response = test_client.get(f'{tags_route}/{tag.tag_id}',
                               headers={"Authorization": f"Bearer {_access_token}"})

    assert response.status_code == 200
    response_string = f'"tag_id": "{tag.tag_id}"'
    assert bytes(response_string, 'utf-8') in response.data


def test_add_contact_to_tag(test_client, user):
    """
    GIVEN a request to the Add contact to Tag endpoint
    WHEN the request URL contains a "tag_id" query parameter that points to a saved tag
    THEN the contact ids are added to corresponding tag
    """
    contacts = {
        "contacts": [
            "397594cd-e16a-4740-aa36-aa6827fbca71",
            "7f236837-377a-469e-b974-3373fc43ee43",
            "a3c62304-aed6-4686-bd83-948b37a98c08"
        ]
    }
    _user, _access_token = user
    tag = TagUsers.query.first()
    response = test_client.patch(f'{tags_route}/{tag.tag_id}/add-contact',
                               json=contacts,
                               headers={"Authorization": f"Bearer {_access_token}"})

    assert response.status_code == 200
    response_string = f'"message": "Contacts Added to Tags with id  {tag.tag_id} "'
    assert bytes(response_string, 'utf-8') in response.data
    assert b'"success": true' in response.data


def test_delete_Contacts_from_tag(test_client, user):
    """
    GIVEN a request to the Delete contact from Tag endpoint
    WHEN the request URL contains a "tag_id" query parameter that points to a saved tag
    THEN the contact ids are removed from corresponding tag
    """
    contacts = {
        "contacts": [
            "397594cd-e16a-4740-aa36-aa6827fbca71",
            "7f236837-377a-469e-b974-3373fc43ee43",
            "a3c62304-aed6-4686-bd83-948b37a98c08"
        ]
    }
    _user, _access_token = user
    tag = TagUsers.query.first()
    response = test_client.delete(f'{tags_route}/{tag.tag_id}/delete-contact',
                                 json=contacts,
                                 headers={"Authorization": f"Bearer {_access_token}"})

    assert response.status_code == 200
    assert b'"Contacts Deleted from Tags' in response.data
    assert b'"success": true' in response.data


def test_search(test_client, user):
    '''
        GIVEN a request to the tags/search route
        WHEN the request carries search_string and page_number as query_paramenters
        THEN the endpoint returns paginated list of tags where search_string is found in any of the fields
        '''

    # Call the Test Auth Class
    _user, _access_token = user
    search_string = 'update_tag'
    response = test_client.get(f'/tags/search?search_string={search_string}&page=1',
                               headers={"Authorization": f"Bearer {_access_token}"}
                               )
    assert response.status_code == 200
    tag = TagUsers.query.first()
    response_string = '"tag_id": "{tag_id}"'.format(tag_id=tag.tag_id)
    assert bytes(response_string, 'utf-8') in response.data
    assert b'"success": true' in response.data

    search_string = 'notsomething'
    response = test_client.get(f'/tags/search?search_string={search_string}&page=1',
                               headers={"Authorization": f"Bearer {_access_token}"}
                               )
    assert response.status_code == 200
    assert b'"message": []' in response.data
    assert b'"success": true' in response.data


def test_delete_tag(test_client, user):
    """
    GIVEN a request to the Delete Tag endpoint
    WHEN the request body contains a list of tag)ids to delete
    THEN the corresponding tags are deleted
    """
    _user, _access_token = user
    tag = TagUsers.query.first()
    response = test_client.delete(f'{tags_route}/delete',
                                  json={"tags": [tag.tag_id]},
                                  headers={"Authorization": f"Bearer {_access_token}"})

    assert response.status_code == 200
    assert b'Deleted Successfully' in response.data