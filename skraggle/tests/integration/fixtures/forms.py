from skraggle.forms.models import Forms
from skraggle.config import db
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.test_admin_auth import credentials

default_form = {
    "form_name": "testform732",
    "form_type":"donation",
    "desc": "linking form to a compaign",
    "status": "closed",
    "followers": ["folower1", "follower2", "follower3"],
    "is_default_donation": True,
    "is_default_currency": True,
    "tags": "",
    "is_minimum_amount": True,
    "is_processing_fee": True,
    "is_tribute": True
}


class FormsFixture:
    def __init__(self):
        form = Forms.query.filter().first()

        if not form:
            form = Forms(**default_form)

            db.session.add(form)
            db.session.flush()
            db.session.commit()
        self.form = form
        
    def get(self):
        return self.form
