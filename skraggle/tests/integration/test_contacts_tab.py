from uuid import uuid1

from skraggle.config import db
from skraggle.contact.models import SegmentUsers
from skraggle.tests.integration.fixtures.fixtures import segmentuser, user


segments_route = '/segments'
test_segment = {
    "contacts": [uuid1(), uuid1()],
    "name": "contact",
    "description": "contact"
}

"""
Test the Add Contact Segment endpoint
"""
def test_add_contact_segment(test_client, user):
    """
    GIVEN a request to the Add Contact Segment endpoint
    WHEN the request body contains the right data
    THEN a new segment is created
    """

    _user, _access_token = user
    response = test_client.post(f'{segments_route}/add', json=test_segment, headers={"Authorization": f"Bearer {_access_token}"})
    
    assert response.status_code == 200
    assert b'"success": true' in response.data


"""
Test the Add Contact Segment endpoint
"""
def test_add_contact_segment(test_client, user):
    """
    GIVEN a request to the Add Contact Segment endpoint
    WHEN the request body contains incorrect data
    THEN a new segment is NOT created
    """

    _user, _access_token = user
    fake_segment = {
        "fake": "segment"
    }
    response = test_client.post(f'{segments_route}/add', json=fake_segment, headers={"Authorization": f"Bearer {_access_token}"})
    
    assert b'"success": false' in response.data
    assert b"`name` and `contacts` are required fields" in response.data


"""
Test the View Specific Segment Details endpoint
"""
def test_view_specific_segment_details(test_client, user):
    """
    GIVEN a request to the View Specific Contact Segment endpoint
    WHEN the request url contains a valid segment id as a parameter
    THEN the corresponding segment is returned
    """
    _user, _access_token = user
    segment = segmentuser()
    segment.organization_id = _user.organization_id
    db.session.flush()
    db.session.commit()

    response = test_client.get(f'{segments_route}/segment/{segment.segment_id}', headers={"Authorization": f"Bearer {_access_token}"})
    data = response.data

    assert response.status_code == 200 
    assert bytes('"segment_id": "{}"'.format(segment.segment_id), encoding='utf8') in data


"""
Test the View All Segment Details endpoint
"""
def test_view_all_segment_details(test_client, user):
    """
    GIVEN a request to the View All Segment Details endpoint
    WHEN the request url contains a valid page number as a parameter
    THEN the corresponding segment is returned
    """
    _user, _access_token = user

    response = test_client.get(f'{segments_route}/all/1', headers={"Authorization": f"Bearer {_access_token}"})
    data = response.data

    assert response.status_code == 200
    assert b'"success": true' in data



"""
Test the Update Specific Segment Details endpoint
"""
def test_update_specific_segment_details(test_client, user):
    """
    GIVEN a request to the Update Specific Segment Details endpoint
    WHEN the request body contains a valid partial segment object
    AND the request URL has a 'segment_id' query parameter
    THEN the corresponding segment is updated
    """
    _user, _access_token = user

    response = test_client.patch(f'{segments_route}/update?segment_id={segmentuser().segment_id}', json={"name": "abc"}, headers={"Authorization": f"Bearer {_access_token}"})
    data = response.data

    assert response.status_code == 200
    assert b'"success": true' in data



"""
Test the Delete Specific Segment Details endpoint
"""
def test_delete_specific_segment_details(test_client, user):
    """
    GIVEN a request to the Delete Specific Segment Details endpoint
    WHEN the request URL contains a "segment_id" query parameter that points to a saved segment
    THEN the corresponding segment is deleted
    """
    _user, _access_token = user
    segment = segmentuser(retrieve_new=False)

    response = test_client.delete(f'{segments_route}/delete?segment_id={segment.segment_id}', headers={"Authorization": f"Bearer {_access_token}"})
    data = response.data
    
    is_undeleted = SegmentUsers.query.filter_by(segment_id=segment.segment_id).first()
    
    assert is_undeleted is None

    assert response.status_code == 200
    assert b'"success": true' in data