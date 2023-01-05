from itsdangerous import json
from skraggle.donation.models import Pledges, PledgeInstallments
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.contact_users import ContactUsersFixture
from skraggle.tests.integration.fixtures.donation_transaction import DonationTransaction, default_transaction
from skraggle.utils.bytes_to_dict_converter import byte_to_dict


def test_create_pledge_non_installment(test_client):
    '''
    GIVEN a request to the Create Donation Transactions endpoint
    WHEN the request URL has a query param of 'id' that points to a valid contact ID
    AND the request body contains the required fields
    THEN a new transaction is recorded
    '''

    access_token = TestAuthCredentials().access_token
    contact = ContactUsersFixture().user
    data = {
        "contact_id": contact.id,
        "total_amount": 100,
        "pledge_name": "fresh_pledge",
        "pledge_type": "empty",
        "start_date": "Dec 19, 2021 - 00:00 AM",
        "end_date": "Dec 19, 2022 - 00:00 AM",
        "status": "processing",
        "is_installment": "False",
        "payment_interval": "monthly",
        "attachments": ["url_!", "url_2"]
    }

    response = test_client.post(f'/pledges/add', json=data,
                                headers={"Authorization": f"Bearer {access_token}"})
    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] is True
    assert as_dict['message'] == f"Pledge Created for {contact.fullname}"


def test_create_pledge_installment(test_client):
    '''
    GIVEN a request to the Create Donation Transactions endpoint
    WHEN the request URL has a query param of 'id' that points to a valid contact ID
    AND the request body contains the required fields
    THEN a new transaction is recorded
    '''

    access_token = TestAuthCredentials().access_token
    contact = ContactUsersFixture().user
    data = {
        "contact_id": contact.id,
        "total_amount": 100,
        "pledge_name": "fresh_pledge",
        "pledge_type": "empty",
        "start_date": "Dec 19, 2021 - 00:00 AM",
        "end_date": "Dec 19, 2022 - 00:00 AM",
        "status": "processing",
        "is_installment": "True",
        "payment_interval": "monthly",
        "amount": 500,
        "attachments": ["url_!", "url_2"]
    }

    assert PledgeInstallments.query.count() > 0
    response = test_client.post(f'/pledges/add', json=data,
                                headers={"Authorization": f"Bearer {access_token}"})
    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] is True
    assert as_dict['message'] == f"Pledge Created for {contact.fullname}"

    assert PledgeInstallments.query.count() > 0


def test_pledges_view(test_client):
    '''
    GIVEN a request to the Create Donation Transactions endpoint
    WHEN the request URL has a query param of 'id' that points to a valid contact ID
    AND the request body contains the required fields
    THEN a new transaction is recorded
    '''

    access_token = TestAuthCredentials().access_token
    response = test_client.get(f'/pledges/1', headers={"Authorization": f"Bearer {access_token}"})
    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] is True
    assert len(as_dict['message']) > 0


def test_update_pledge(test_client):
    '''
    GIVEN a request to the Create Donation Transactions endpoint
    WHEN the request URL has a query param of 'id' that points to a valid contact ID
    AND the request body contains the required fields
    THEN a new transaction is recorded
    '''

    access_token = TestAuthCredentials().access_token
    pledge = Pledges.query.all()[0]
    data = {
        "total_amount": 100,
        "pledge_name": "fresh_pledge_updated",
        "pledge_type": "empty",
        "start_date": "Dec 19, 2021 - 00:00 AM",
        "end_date": "Dec 19, 2022 - 00:00 AM",
    }
    response = test_client.patch(f'/pledges/update/{pledge.id}',
                                 json=data,
                                 headers={"Authorization": f"Bearer {access_token}"})
    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] is True
    assert as_dict['message'] == f'Pledge ID: {pledge.id} Updated'


def test_pledges_installments(test_client):
    '''
        GIVEN a request to the Create Donation Transactions endpoint
        WHEN the request URL has a query param of 'id' that points to a valid contact ID
        AND the request body contains the required fields
        THEN a new transaction is recorded
        '''

    access_token = TestAuthCredentials().access_token

    pledges = Pledges.query.all()
    for pledge in pledges:
        pledge_id = pledge.id
        url = f'/pledges/installments/{pledge_id}'
        response = test_client.get(url, headers={"Authorization": f"Bearer {access_token}"})
        as_dict = byte_to_dict(response.data)

        install_count = PledgeInstallments.query.filter_by(pledge_id=pledge_id).count()
        if install_count > 0:
            assert as_dict['success'] is True
            assert f'Installments for Pledge = {pledge.pledge_name}' in as_dict['message']
            assert len(as_dict['message'].get(f'Installments for Pledge = {pledge.pledge_name}')) == install_count
        else:
            assert as_dict['success'] is False
            assert 'No installments to display' in as_dict['message']


def test_view_pledge(test_client):
    '''
        GIVEN a request to the Create Donation Transactions endpoint
        WHEN the request URL has a query param of 'id' that points to a valid contact ID
        AND the request body contains the required fields
        THEN a new transaction is recorded
        '''

    access_token = TestAuthCredentials().access_token
    pledge_id = Pledges.query.all()[0].id
    response = test_client.get(f'/pledges/view/{pledge_id}', headers={"Authorization": f"Bearer {access_token}"})
    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] is True
    assert 'contact_name' in as_dict['message']
    assert 'end_date' in as_dict['message']
    assert 'pledge_type' in as_dict['message']
    assert 'start_date' in as_dict['message']
    assert 'status' in as_dict['message']
    assert 'total_amount' in as_dict['message']


def test_search_pledge(test_client):
    '''
        GIVEN a request to the Create Donation Transactions endpoint
        WHEN the request URL has a query param of 'id' that points to a valid contact ID
        AND the request body contains the required fields
        THEN a new transaction is recorded
        '''

    access_token = TestAuthCredentials().access_token
    response = test_client.get('/pledges/search?query=fresh_pledge&page_number=1',
                               headers={"Authorization": f"Bearer {access_token}"})
    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] is True
    assert len(as_dict['message']) > 0


def test_pledges_associations(test_client):
    '''
        GIVEN a request to the Create Donation Transactions endpoint
        WHEN the request URL has a query param of 'id' that points to a valid contact ID
        AND the request body contains the required fields
        THEN a new transaction is recorded
    '''

    access_token = TestAuthCredentials().access_token
    pledge_id = Pledges.query.all()[0].id
    response = test_client.get(f'/pledges/associations/{pledge_id}', headers={"Authorization": f"Bearer {access_token}"})
    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] is False
    assert 'has no associations' in as_dict['message']


def test_filter_pledges(test_client):
    '''
    GIVEN a request to the Create Donation Transactions endpoint
    WHEN the request URL has a query param of 'id' that points to a valid contact ID
    AND the request body contains the required fields
    THEN a new transaction is recorded
    '''
    access_token = TestAuthCredentials().access_token
    response = test_client.get('/pledges/filter?query=fresh_pledge&page_number=1&pledge_type={"filter_type":"matches","values":"empty"}&filter_by=all', headers={"Authorization": f"Bearer {access_token}"})

    as_dict = byte_to_dict(response.data)
    assert as_dict['success'] is True
    assert len(as_dict['message']) > 0


def test_delete_pledge(test_client):
    '''
    GIVEN a request to the Create Donation Transactions endpoint
    WHEN the request URL has a query param of 'id' that points to a valid contact ID
    AND the request body contains the required fields
    THEN a new transaction is recorded
    '''

    access_token = TestAuthCredentials().access_token
    pledge_id = Pledges.query.all()[0].id
    response = test_client.delete(f'/pledges/delete/{pledge_id}', headers={"Authorization": f"Bearer {access_token}"})
    as_dict = byte_to_dict(response.data)

    assert as_dict['success'] is True
    assert as_dict['message'] == f"Pledge ID {pledge_id} deleted successfully"
