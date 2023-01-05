from flask import Response
from src.tests.integration.utils.assert_is_ok import assert_is_ok
from src.tests.integration.donations.one_time_transaction.fixtures import OneTimeTransactionFixture
from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.campaigns.fixtures import CampaignFixture



def test_create_one_time_transaction(test_client):
     '''
     GIVEN a request to the POST /donation/one-time-transactions endpoint
     WHEN the request body carries transactions details
     THEN a new transaction object is created
     '''
     access_token = AdminFixture().access_token
    
     body = OneTimeTransactionFixture().default_obj()
     response: Response = test_client.post('/donations/one-time-transactions', json=body, headers={'Authorization': f'Bearer {access_token}'})

     assert_is_ok(response)
     
     
def test_list_one_time_transaction(test_client):
     '''
     GIVEN a request to the GET /donation/one-time-transactions endpoint
     WHEN the request body carries transactions details
     THEN a list of transaction details is returned
     '''
     access_token = AdminFixture().access_token
    
     response: Response = test_client.get('/donations/one-time-transactions', headers={'Authorization': f'Bearer {access_token}'})

     assert_is_ok(response)
     
     
def test_fetch_by_id_one_time_transaction(test_client):
     '''
     GIVEN a request to the GET /donation/one-time-transactions/<id> endpoint
     WHEN the request carries transactions id
     THEN a transaction details attached to the id is returned
     '''
     access_token = AdminFixture().access_token
     one_time_txn = OneTimeTransactionFixture()
     response: Response = test_client.get(f'/donations/one-time-transactions/{one_time_txn.id}', headers={'Authorization': f'Bearer {access_token}'})

     assert_is_ok(response)
     
     
def test_update_one_time_transaction(test_client):
     '''
     GIVEN a request to the PATCH /donation/one-time-transactions/<id> endpoint
     WHEN the request carries transactions id and the body of data to be updated
     THEN a transaction details attached to the id is updated
     '''
     
     campaign = CampaignFixture()
     body = dict(
          amount = 1000,
          campaign_id = campaign.id
     )
     
     access_token = AdminFixture().access_token
     one_time_txn = OneTimeTransactionFixture()
     response: Response = test_client.patch(f'/donations/one-time-transactions/{one_time_txn.id}', json=body, headers={'Authorization': f'Bearer {access_token}'})

     assert_is_ok(response)
     
     
def test_delete_one_time_transaction(test_client):
     '''
     GIVEN a request to the DELETE /donation/one-time-transactions endpoint
     WHEN the request carries transactions ids of data to be deleted
     THEN a transaction details attached to the ids is deleted
     '''
     
     one_time_txn = OneTimeTransactionFixture()
     body = dict(
          ids = [one_time_txn.id]
     )
     
     access_token = AdminFixture().access_token
     response: Response = test_client.delete(f'/donations/one-time-transactions', json=body, headers={'Authorization': f'Bearer {access_token}'})

     assert_is_ok(response)