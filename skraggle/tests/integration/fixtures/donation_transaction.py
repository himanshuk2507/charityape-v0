from datetime import datetime
from skraggle.donation.models import TransactionDonation
from skraggle.config import db

from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.contact_users import ContactUsersFixture


default_transaction = dict(
    total_amount = 100,
    payment_method = 'payment_A', # this will be updated to an enum when Victoria finalises on the design
)

class DonationTransaction:
    def __init__(self) -> None:
        transaction = TransactionDonation.query.filter().first()
        
        if not transaction:
            transaction = default_transaction
            admin = TestAuthCredentials().admin
            
            transaction['organization_id'] = admin.organization_id
            transaction['date_received'] = datetime.now()
            transaction['contact_id'] = ContactUsersFixture().get().id
            transaction = TransactionDonation(**transaction)

            db.session.add(transaction)
            db.session.flush()
            db.session.commit()

        self.transaction = transaction

    def get(self):
        return self.transaction