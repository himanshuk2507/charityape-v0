from skraggle.base_helpers.orgGen import getOrg
from skraggle.config import db
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.test_admin_auth import credentials
from skraggle.p2p.models import P2PFundraiser
from skraggle.p2p.peer_to_peer import get_p2p_id

default_p2p_user = {
     "campaign": "Test Campaign",
     "designation": "Test Designation",
     "display_name": "Test P2P",
     "first_name": "Test",
     "last_name": "Tests",
     "email": "test@gmail.com",
     "goal": "1000",
     "currency": "USD",
     "offline_amount": "1000",
     "offline_donation": "10000",
     "goal_date": "2022-04-17",
     "personal_message": "This is just Test",
     "supporter": "Partho Prothim"
}



class P2PUsersFixture:
   def __init__(self):
      p2p = P2PFundraiser.query.filter().first()

      if not p2p:
         org_id = TestAuthCredentials(credentials).admin.organization_id

         default_p2p_user['organization_id'] = org_id
         default_p2p_user['p2p_id'] = get_p2p_id()

         p2p = P2PFundraiser(**default_p2p_user)

         db.session.add(p2p)
         db.session.flush()
         db.session.commit()
      
      self.p2p = p2p
        
   def get(self):
      return self.p2p