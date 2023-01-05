from itsdangerous import json
from skraggle.donation.models import TransactionDonation
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.contact_users import ContactUsersFixture
from skraggle.tests.integration.fixtures.donation_transaction import DonationTransaction, default_transaction
from skraggle.utils.bytes_to_dict_converter import byte_to_dict


def test_list_transactions(test_client):
    '''
    GIVEN a request to the List Donation Transactions endpoint
    WHEN the request URL has a dynamic param that points to a valid page number
    THEN a list of transactions for that page is returned
    '''

    access_token = TestAuthCredentials().access_token
    # create a new transaction so that the list is not empty
    DonationTransaction()

    response = test_client.get('/transaction-donations/all/1', headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] == True
    assert len(as_dict['message']) != 0


def test_create_transaction(test_client):
    '''
    GIVEN a request to the Create Donation Transactions endpoint
    WHEN the request URL has a query param of 'id' that points to a valid contact ID
    AND the request body contains the required fields
    THEN a new transaction is recorded
    '''

    access_token = TestAuthCredentials().access_token
    contact = ContactUsersFixture().user
    
    response = test_client.post(f'transaction-donations/create?id={contact.id}', json=default_transaction, headers={"Authorization": f"Bearer {access_token}"})
    data = byte_to_dict(response.data)

    assert data['success'] == True 
    assert data['message'] == 'Transaction was recorded successfully'


def test_update_transaction(test_client):
    '''
    GIVEN a request to the Update Donation Transactions endpoint
    WHEN the request URL has a query param of 'id' that points to a valid contact ID
    AND the request body contains the required fields
    THEN the corresponding transaction is updated
    '''

    access_token = TestAuthCredentials().access_token
    transaction = DonationTransaction().get()
    update = dict(
        total_amount = transaction.total_amount + 100
    )
    
    response = test_client.patch(f'transaction-donations/update?id={transaction.id}', json=update, headers={"Authorization": f"Bearer {access_token}"})
    data = byte_to_dict(response.data)

    assert data['success'] == True 
    assert data['message'] == 'Transaction updated successfully!'


def test_delete_transaction(test_client):
    '''
    GIVEN a request to the Delete Donation Transactions endpoint
    WHEN the request URL has a query param of 'id' that points to a valid contact ID
    THEN the corresponding transaction is deleted
    '''

    access_token = TestAuthCredentials().access_token
    transaction = DonationTransaction().get()
    
    response = test_client.delete(f'transaction-donations/delete?id={transaction.id}', headers={"Authorization": f"Bearer {access_token}"})
    data = byte_to_dict(response.data)

    assert data['success'] == True 
    assert data['message'] == 'Transaction deleted successfully!'



def test_search_transactions(test_client):
    '''
    GIVEN a request to the Search Donation Transactions endpoint
    WHEN the request URL has a query param of 'query'
    AND a query param of 'page' that is an integer
    THEN the a list of transactions that match this query is returned
    '''

    access_token = TestAuthCredentials().access_token
    transaction = DonationTransaction().get()
    
    response = test_client.get(f'transaction-donations/search?query={transaction.payment_method}&page=1', headers={"Authorization": f"Bearer {access_token}"})
    data = byte_to_dict(response.data)

    assert data['success'] == True 
    assert len(data['message']) != 0