from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.contact_users import ContactUsersFixture
from skraggle.tests.integration.fixtures.donation_admin import DonationAdminFixture


def test_create_admin(test_client):
     '''
     GIVEN a request to the Create Donation's Admin endpoint
     WHEN the correct values is passed in the request body
     THEN the Donation admin is created
     '''
     
     
     access_token = TestAuthCredentials().access_token
     instance = ContactUsersFixture().get()
     new_admin = dict(
          name = 'Samson',
          description = 'This is just Test',
          contact_id = instance.id
     )
     
     response = test_client.post(f'/donations/create-admin', json=new_admin, headers={"Authorization": f"Bearer {access_token}"})

     assert response.status_code == 200
     
     

def test_all_admin(test_client):
     '''
     GIVEN a request to the List Admin endpoint
     WHEN the request URL has a dynamic param that points to a valid page number
     THEN a list of receipts for that page is returned
     '''

     access_token = TestAuthCredentials().access_token
     # create a new transaction so that the list is not empty

     response = test_client.get('/donations/all-admin/1', headers={"Authorization": f"Bearer {access_token}"})

     assert response.status_code == 200
   
     
def test_update_admin(test_client):
     '''
     GIVEN a request to the Update Admin endpoint
     WHEN the request URL has a dynamic param that points to a valid admin id
     THEN the endpoint update the admin with the supplied id
     '''
     update_data = dict(
          name = "Samson19",
          description = "This is Just a Test 19"
     )

     access_token = TestAuthCredentials().access_token
     # create a new transaction so that the list is not empty
     instance = DonationAdminFixture().get()
     print(instance.id)
     response = test_client.patch(f'/donations/update-admin/{instance.id}', json=update_data, headers={"Authorization": f"Bearer {access_token}"})

     assert response.status_code == 200
     
     
def test_delete_admin(test_client):
     '''
     GIVEN a request to the delete Admin endpoint
     WHEN the request URL has a dynamic param that points to a valid admin id
     THEN the endpoint delete the admin with the supplied id
     '''

     access_token = TestAuthCredentials().access_token
     # create a new transaction so that the list is not empty
     instance = DonationAdminFixture().get()
     response = test_client.delete(f'/donations/delete-admin/{instance.id}', headers={"Authorization": f"Bearer {access_token}"})

     assert response.status_code == 200