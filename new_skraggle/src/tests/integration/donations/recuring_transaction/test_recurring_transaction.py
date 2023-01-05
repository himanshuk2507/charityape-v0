from flask import Response
from src.tests.integration.utils.assert_is_ok import assert_is_ok
from src.tests.integration.donations.recuring_transaction.fixtures import RecurringTransactionFixture
from src.tests.integration.admin.fixtures import AdminFixture



def test_create_recurring_transaction(test_client):
     '''
     GIVEN a request to the POST /donation/recurring-transactions endpoint
     WHEN the request body carries transactions details
     THEN a new transaction object is created
     '''
     access_token = AdminFixture().access_token
    
     body = RecurringTransactionFixture().default_obj()
     response: Response = test_client.post('/donations/recurring-transactions', json=body, headers={'Authorization': f'Bearer {access_token}'})

     assert_is_ok(response)
     


def test_list_recurring_transaction(test_client):
     '''
     GIVEN a request to the GET /donation/recurring-transactions endpoint
     WHEN the request body carries transactions details
     THEN a list of recurring transaction details is returned
     '''
     access_token = AdminFixture().access_token
    
     response: Response = test_client.get('/donations/recurring-transactions', headers={'Authorization': f'Bearer {access_token}'})

     assert_is_ok(response)
     

def test_fetch_by_id_recurring_transaction(test_client):
     '''
     GIVEN a request to the GET /donation/recurring-transactions/<id> endpoint
     WHEN the request carries transactions id
     THEN a transaction details attached to the id is returned
     '''
     access_token = AdminFixture().access_token
     recurring = RecurringTransactionFixture()
     response: Response = test_client.get(f'/donations/recurring-transactions/{recurring.id}', headers={'Authorization': f'Bearer {access_token}'})

     assert_is_ok(response)
     
     

def test_update_recurring_transaction(test_client):
     '''
     GIVEN a request to the PATCH /donation/recurring-transactions/<id> endpoint
     WHEN the request carries transactions id and the body of data to be updated
     THEN a transaction details attached to the id is updated
     '''
     
     body = dict(
          amount = 1000
     )
     
     access_token = AdminFixture().access_token
     recurring = RecurringTransactionFixture()
     response: Response = test_client.patch(f'/donations/recurring-transactions/{recurring.id}', json=body, headers={'Authorization': f'Bearer {access_token}'})

     assert_is_ok(response)
     


def test_delete_recurring_transaction(test_client):
     '''
     GIVEN a request to the DELETE /donation/recurring-transactions endpoint
     WHEN the request carries transactions ids of data to be deleted
     THEN a transaction details attached to the ids is deleted
     '''
     
     recurring = RecurringTransactionFixture()
     body = dict(
          ids = [recurring.id]
     )
     
     access_token = AdminFixture().access_token
     response: Response = test_client.delete(f'/donations/recurring-transactions', json=body, headers={'Authorization': f'Bearer {access_token}'})

     assert_is_ok(response)