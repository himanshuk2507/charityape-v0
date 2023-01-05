from datetime import timedelta
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from skraggle.profile.models import Admin
from skraggle.config import db


credentials = dict(first_name="test", last_name="test", email="test@test.com", password="12345")

class TestAuthCredentials:
     def __init__(self, credentials=credentials):
          # create an access token for the first user in the DB 
          admin = Admin.query.filter_by(email=credentials["email"]).first()

          # if there is no Admin, create one
          if not admin:
               admin_data = {
                    "first_name": credentials['first_name'],
                    "last_name": credentials['last_name'],
                    "email": credentials['email'],
                    "password": generate_password_hash(credentials['password'], method="sha256"),
                    "type_of": "user",
                    "permission_level": "administrator"
               }
               admin = Admin(**admin_data)
               admin.is_admin = True
               db.session.add(admin)
               db.session.flush()
               db.session.commit()

          self.access_token = create_access_token(
               identity=admin.admin_id,
               expires_delta=timedelta(days=1),
               additional_claims={
                    "is_admin": True,
                    "org": admin.organization_id,
                    "activated": True,
                    "email": credentials['email'],
               },
          )
          self.admin = admin
     
     def auth_token(self):
          return self.access_token