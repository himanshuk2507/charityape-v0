from skraggle.contact.models import ContactUsers
from skraggle.config import db
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.test_admin_auth import credentials

default_user = {
    "fullname": "Samson",
    "primary_phone": "123456789",
    "primary_email": "samson@gmail.com",
    "tags": "tag1,tag2,tag3",
    "total_donations": "10000",
    "donor_score": "50",
    "donations_this_year": "0",
    "donations_last_year": "11",
    "birth_date": "1992-04-17",
    "company": "Samson Inc",
    "address": "Lagos Nigeria",
    "city": "Lagos",
    "state": "Lagos",
    "postal_zip": "1234",
    "country": "Nigeria",
    "priority": "Good"
}

class ContactUsersFixture:
    def __init__(self):
        user = ContactUsers.query.filter().first()

        if not user:
            org_id = TestAuthCredentials(credentials).admin.organization_id

            default_user['organization_id'] = org_id

            user = ContactUsers(**default_user)

            db.session.add(user)
            db.session.flush()
            db.session.commit()
        self.user = user
        
    def get(self):
        return self.user