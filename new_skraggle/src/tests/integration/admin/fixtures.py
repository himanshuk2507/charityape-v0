from datetime import timedelta
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from src.app_config import db
from src.profile.models import Admin


class AdminFixture:
    def __init__(self, credentials=None):
        if not credentials:
            credentials = self.default_obj()
        admin = Admin.query.filter_by(email=credentials["email"]).first()

        # if there is no Admin, create one
        if not admin:
            credentials["password"] = generate_password_hash(credentials['password'], method="sha256")

            admin: Admin = Admin(**credentials)
            
            db.session.add(admin)
            db.session.flush()
            db.session.commit()

        self.access_token = admin.create_access_token()
        self.organization_id = admin.organization_id
        self.admin = admin

    @classmethod
    def default_obj(cls):
        return dict(first_name="test", last_name="test", email="test@test.com", password="12345")


def authorization_header():
    access_token = AdminFixture().access_token
    return dict(
        Authorization=f'Bearer {access_token}'
    )