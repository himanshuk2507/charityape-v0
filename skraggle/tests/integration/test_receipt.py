from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.donation_transaction import DonationTransaction



def test_all_receipt(test_client):
     '''
     GIVEN a request to the List Receipt endpoint
     WHEN the request URL has a dynamic param that points to a valid page number
     THEN a list of receipts for that page is returned
     '''

     access_token = TestAuthCredentials().access_token
     # create a new transaction so that the list is not empty

     response = test_client.get('/reports/transactions/receipts/1', headers={"Authorization": f"Bearer {access_token}"})

     assert response.status_code == 200
     
     
     
     


def test_reciept_by_id(test_client):
     '''
     GIVEN a request to the get receipt by id route
     WHEN the request carries the donation transaction id of an existing transaction 
     THEN the endpoint return all information related to transaction id
     '''
    
     # Call the Test Auth Class
     access_token = TestAuthCredentials().access_token
     
     # Get Contacts User ID
     instance = DonationTransaction().get()
     id = instance.id
     
     response = test_client.get(f'/reports/transactions/receipts/{id}', headers={"Authorization": f"Bearer {access_token}"})
     
     assert response.status_code == 200