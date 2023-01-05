from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.p2p_user import P2PUsersFixture
from skraggle.tests.integration.test_admin_auth import credentials




def test_p2p_by_id(test_client):
     '''
     GIVEN a request to the peertopeer/id route
     WHEN the request carries the id of an existing p2p 
     THEN the endpoint return all information related to p2p id
    '''
    
     # Call the Test Auth Class
     access_token = TestAuthCredentials(credentials).auth_token()
    
     # Get Contacts User ID
     instance = P2PUsersFixture().get()
    
     response = test_client.get(f'/peertopeer/{instance.id}', headers={"Authorization": f"Bearer {access_token}"})
    
     assert response.status_code == 200
     
     

def test_delete_p2p(test_client):
     '''
     GIVEN a request to the peertopeer/id route
     WHEN the request carries the id of an existing p2p 
     THEN the endpoint return all information related to p2p id
    '''
    
     # Call the Test Auth Class
     access_token = TestAuthCredentials(credentials).auth_token()
    
     # Get Contacts User ID
     instance = P2PUsersFixture().get()
    
     response = test_client.delete(f'/peertopeer/{instance.id}', headers={"Authorization": f"Bearer {access_token}"})
    
     assert response.status_code == 200
     


def test_all_p2p(test_client):
     '''
     GIVEN a request to the peertopeer/all/1 route
     WHEN the request carries data in in the model
     THEN the endpoint return all information in store in the model
    '''
    
     # Call the Test Auth Class
     access_token = TestAuthCredentials(credentials).auth_token()
    
    
     response = test_client.get(f'/peertopeer/all/1', headers={"Authorization": f"Bearer {access_token}"})
    
     assert response.status_code == 200