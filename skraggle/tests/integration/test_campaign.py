from itsdangerous import json
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials, credentials
from skraggle.tests.integration.fixtures.campaign import CampaignFixture
from skraggle.tests.integration.fixtures.contact_users import ContactUsersFixture

'''
test Create Campaign endpoint
'''
def test_create_campaign(test_client):
    '''
    GIVEN a request to the Create Campaign endpoint
    WHEN the correct values is passed in the request body
    THEN the campaign is created
    '''
    campaign = dict(
        fundraising_goal=100,
        name="test",
        description="test",
    )
    contact = ContactUsersFixture().get().id
    campaign['followers'] = [contact]
    
    access_token = TestAuthCredentials(credentials).access_token
    
    response = test_client.post('/campaigns/create', json=campaign, headers={"Authorization": f"Bearer {access_token}"})

    assert b"Campaign Created Successfully" in response.data
    assert response.status_code == 200



'''
test the Update Campaign endpoint
'''
def test_update_campaign(test_client):
    '''
    GIVEN a request to the Update Campaign endpoint
    WHEN the request URL contains an `id` query param that points to a valid campaign
    THEN the campaign is updated
    '''

    access_token = TestAuthCredentials(credentials).access_token
    
    campaign = CampaignFixture().campaign

    new_assignee = 456
    modified_campaign = dict(
        **CampaignFixture().defaults
    )
    modified_campaign['assignee']  = new_assignee

    response = test_client.patch(f'/campaigns/update?id={campaign.id}', json=modified_campaign, headers={"Authorization": f"Bearer {access_token}"})
    
    assert bytes(f"Campaign with id {campaign.id} Updated", "utf-8") in response.data
    assert response.status_code == 200



'''
test the List All Campaigns endpoint
'''
def test_list_all_campaigns(test_client):
    '''
    GIVEN a request to the List All Campaigns endpoint
    WHEN the request has a valid page URL parameter
    THEN the appropriate page is returned
    '''

    access_token = TestAuthCredentials(credentials).access_token
    page = 1

    response = test_client.get(f'/campaigns/all/{page}', headers={"Authorization": f"Bearer {access_token}"})
    
    assert response.status_code == 200
    assert b'"success": true' in response.data



'''
test the Fetch Campaign By ID endpoint
'''
def test_fetch_campaign_by_id(test_client):
    '''
    GIVEN a request to the Fetch Campaign By ID endpoint
    WHEN the `campaign_id` URL parameter points to a valid campaign
    THEN the corresponding campaign is returned
    '''

    access_token = TestAuthCredentials(credentials).access_token
    campaign = CampaignFixture().get()

    response = test_client.get(f'/campaigns/info/{campaign.id}', headers={"Authorization": f"Bearer {access_token}"})
    
    assert response.status_code == 200
    assert bytes(f'"name": "{campaign.name}"', "utf-8") in response.data



'''
test the Delete Campaign By ID endpoint
'''
def test_delete_campaign_by_id(test_client):
    '''
    GIVEN a request to the Delete Campaign endpoint
    WHEN the request URL has an `id` parameter that points to a valid campaign
    THEN the corresponding campaign is deleted
    '''

    access_token = TestAuthCredentials(credentials).access_token
    campaign = CampaignFixture().get()

    response = test_client.delete(f'/campaigns/delete?id={campaign.id}', headers={"Authorization": f"Bearer {access_token}"})
    
    assert response.status_code == 200
    assert bytes(f'"success": true', "utf-8") in response.data