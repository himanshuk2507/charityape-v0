from skraggle.donation.models import AdminDonations
from skraggle.config import db
from skraggle.contact.models import ContactUsers
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials


class DonationAdminFixture:
    def __init__(self) -> None:
        donation_admin = AdminDonations.query.filter().first()
    
        if not donation_admin:
            contact = ContactUsers.query.filter().first()
            new_admin = dict(
                name = 'Samson',
                description = 'This is the Test',
                contact = contact.id
                )
            admin = TestAuthCredentials().admin
            new_admin['organization_id'] = admin.organization_id
            new = AdminDonations(**new_admin)
            db.session.add(new)
            db.session.flush()
            db.session.commit()


        self.donation_admin = donation_admin


    def get(self):
        return self.donation_admin