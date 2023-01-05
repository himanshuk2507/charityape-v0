from flask import Response

from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.campaigns.fixtures import CampaignFixture
from src.campaigns.models import Campaign
from src.tests.integration.utils.assert_is_ok import assert_is_ok


def test_create_campaign_route(test_client):
    '''
    GIVEN a request to POST /campaigns endpoint
    WHEN the request body carries accurate data
    THEN the route creates a new campaign entry
    '''
    access_token = AdminFixture().access_token
    data = {
        "name": "World peace",
        "description": "(Optional)",
        "fundraising_goal": 10000,
        "followers": []
    }
    response: Response = test_client.post('/campaigns', json=data, headers={'Authorization': f'Bearer {access_token}'})
    
    assert_is_ok(response)


def test_fetch_all_campaigns_route(test_client):
    '''
    GIVEN a request to GET /campaigns endpoint
    WHEN there exist campaign entities
    THEN the route returns dict of entities
    '''
    access_token = AdminFixture().access_token
    response: Response = test_client.get('/campaigns', headers={'Authorization': f'Bearer {access_token}'})
    
    assert_is_ok(response)


def test_update_campaign_route(test_client):
    '''
    GIVEN a request to PATCH /campaigns/<uuid> endpoint
    WHEN the request carries campaign id to edit and fields to update
    THEN the route updates fields if the campaign with id x exists
    '''
    access_token = AdminFixture().access_token
    campaign = Campaign.query.first()

    body = {
        "name": "Save America"
    }

    response: Response = test_client.patch(f'/campaigns/{campaign.id}', json=body,
                                           headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_campaign_by_id_route(test_client):
    '''
    GIVEN a request to GET /campaigns/<uuid> endpoint
    WHEN the uri consists of campaign id to fetch
    THEN the route returns dict of campaign if id exists
    '''
    access_token = AdminFixture().access_token
    campaign = Campaign.query.first()

    response: Response = test_client.get(f'/campaigns/{campaign.id}',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_campaign_p2ps_route(test_client):
    '''
    GIVEN a request GET /campaigns/<uuic>/p2p endpoint
    WHEN uuid is a valid campaign id
    THEN the route returns p2p entities for given campaign id
    '''
    access_token = AdminFixture().access_token
    campaign = CampaignFixture().campaign

    response: Response = test_client.get(f'/campaigns/{campaign.id}/p2p',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_campaign_forms_route(test_client):
    '''
    GIVEN a request GET /campaigns/<uuic>/forms endpoint
    WHEN uuid is a valid campaign id
    THEN the route returns forms entities for given campaign id
    '''
    access_token = AdminFixture().access_token
    campaign = CampaignFixture().campaign

    response: Response = test_client.get(f'/campaigns/{campaign.id}/forms',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_fetch_campaign_elements_route(test_client):
    '''
    GIVEN a request GET /campaigns/<uuic>/elements endpoint
    WHEN uuid is a valid campaign id
    THEN the route returns elements entities for given campaign id
    '''
    access_token = AdminFixture().access_token
    campaign = CampaignFixture().campaign

    response: Response = test_client.get(f'/campaigns/{campaign.id}/elements',
                                         headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)


def test_delete_campaign_route(test_client):
    '''
    GIVEN a request to DELETE /campaigns endpoint
    WHEN request carries json of campaign ids as list
    THEN the route deletes the given campaigns
    '''
    access_token = AdminFixture().access_token
    campaigns = Campaign.query.all()

    campaign_ids = {"campaigns": [campaign.id for campaign in campaigns]}

    response: Response = test_client.delete(f'/campaigns', json=campaign_ids,
                                            headers={'Authorization': f'Bearer {access_token}'})
    assert_is_ok(response)
