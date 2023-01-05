from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.package import PackageFixture
from skraggle.tests.integration.fixtures.promo import PromoCodeFixture
from skraggle.tests.integration.test_admin_auth import credentials
from skraggle.tests.integration.fixtures.promo import default_promo_code


def test_create_promo(test_client):
     '''
     GIVEN a request to the Create Promo Code
     WHEN the request body contains the required fields
     THEN a new promo is created
     '''
    
     # Call the Test Auth Class
     access_token = TestAuthCredentials(credentials).auth_token()
     package_id = PackageFixture().get().id
    
     response = test_client.post(f'/event-promocode/create?package_id={package_id}', json=default_promo_code, headers={"Authorization": f"Bearer {access_token}"})
    
     assert response.status_code == 200


def test_fetch_promo_code_by_id(test_client):
     '''
     GIVEN a request to the Promo Code/id route
     WHEN the request carries the id of an existing promo 
     THEN the endpoint return all information related to promo id
     '''
    
     # Call the Test Auth Class
     access_token = TestAuthCredentials(credentials).auth_token()
    
     # Get Promo code ID
     instance = PromoCodeFixture().get()
    
     response = test_client.get(f'/event-promocode/info/{instance.id}', headers={"Authorization": f"Bearer {access_token}"})
    
     assert response.status_code == 200
     
     
     

def test_delete_promo_code_by_id(test_client):
     '''
     GIVEN a request to the Promo Code/id route
     WHEN the request carries the id of an existing Promo 
     THEN the endpoint return delete related to promo id
     '''
    
     # Call the Test Auth Class
     access_token = TestAuthCredentials(credentials).auth_token()
    
     # Get Promo code ID
     instance = PromoCodeFixture().get()
    
     response = test_client.delete(f'/event-promocode/delete/{instance.id}', headers={"Authorization": f"Bearer {access_token}"})
    
     assert response.status_code == 200
     
     
     

def test_fetch_all_promo_codes(test_client):
     '''
     GIVEN a request to the event-promocode/all/1 route
     WHEN the request carries data in in the model
     THEN the endpoint return all information in store in the model
     '''
    
     # Call the Test Auth Class
     access_token = TestAuthCredentials(credentials).auth_token()
    
    
     response = test_client.get(f'/event-promocode/all/1', headers={"Authorization": f"Bearer {access_token}"})
    
     assert response.status_code == 200