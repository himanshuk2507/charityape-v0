from skraggle.donation.models import Pledges
from skraggle.config import db
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.test_admin_auth import credentials

default_pledge = {
    "contact_id": "14fce575-0f54-451d-8a79-6190d19745f6",
    "total_amount": 100,
    "pledge_name": "fresh_pledge",
    "pledge_type": "empty",
    "start_date": "Dec 19, 2021 - 00:00 AM",
    "end_date": "Dec 19, 2022 - 00:00 AM",
    "status": "processing",
    "is_installment": "True",
    "payment_interval": "monthly",
    "attachments": ["url_1", "url_2"]
}


class PledgesFixture:
    def __init__(self):
        pledge = Pledges.query.filter().first()

        if not pledge:
            pledge = Pledges(**default_pledge)

            db.session.add(pledge)
            db.session.flush()
            db.session.commit()
        self.pledge = pledge
        
    def get(self):
        return self.pledge
