from skraggle.events.models import PromoCode
from skraggle.config import db
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.package import PackageFixture
from skraggle.tests.integration.test_admin_auth import credentials
import datetime

default_promo_code = {
    "promo_code": "TESTCODE100",
    "description": "Test Code",
    "discount": 100,
    "max_user": 2,
    "start_date": datetime.datetime.now(),
    "end_date": datetime.datetime.now()
}

class PromoCodeFixture:
     def __init__(self):
          code = PromoCode.query.filter().first()

          if not code:
               code = PromoCode(**default_promo_code)

               db.session.add(code)
               db.session.flush()
               db.session.commit()
          self.code = code
          self.package_id = PackageFixture().get().id
          self.default_promo_code = default_promo_code
        
     def get(self):
        return self.code