import uuid
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from skraggle.base_helpers import crypter
from skraggle.base_helpers.crypter import Crypt
from skraggle.config import db
from skraggle.run import app

hider = Crypt()
default_mapping_rules = {
    "mappings": [
        {
            "rule": {
                "salesforce_object_name": "Campaign",
                "salesforce_field_name": "Name",
                "skraggle_object_name": "Campaigns",
                "skraggle_field_name": "name",
            }
        }
    ]
}


class SalesforceDetails(db.Model):
    __tablename__ = "SalesforceDetails"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    name = db.Column(db.String(255))
    salesforce_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    belongs_to = db.Column(UUID(as_uuid=True), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    instance_url = db.Column(db.String(255))
    username = db.Column(db.String(255))
    refresh_token = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    scopes = db.Column(db.String(255))
    mapping_rules = db.relationship(
        "SalesforceMappings",
        backref="SalesforceDetails",
        lazy=True,
        cascade="all,delete,delete-orphan",
    )
    connected_on = db.Column(db.DateTime, nullable=False, default=func.now())

    def __init__(
        self,
        name,
        email,
        belongs_to,
        instance_url,
        username,
        refresh_token,
        access_token,
        scopes,
        connected_on,
    ):
        self.belongs_to = belongs_to
        self.instance_url = instance_url
        self.username = username
        self.name = name
        self.email = email
        self.username = username
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.scopes = scopes
        self.connected_on = connected_on


class SalesforceMappings(db.Model):
    __tablename__ = "SalesforceMappings"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    mapping_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    salesforce_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("SalesforceDetails.salesforce_id")
    )
    mappings = db.Column(JSONB, default=default_mapping_rules)

    def __init__(self, organization_id):
        self.organization_id = organization_id


class FacebookDetails(db.Model):
    __tablename__ = "FacebookDetails"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    facebook_email = db.Column(db.String(255))
    facebook_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    belongs_to = db.Column(UUID(as_uuid=True), nullable=False)
    user_email = db.Column(db.String(255), nullable=True)
    facebook_user_id = db.Column(db.String(255))
    page_tokens = db.Column(JSONB, default={})
    access_token = db.Column(db.String(255))
    scopes = db.Column(db.String(255))
    connected_on = db.Column(db.DateTime, nullable=False, default=func.now())

    def __init__(
        self,
        facebook_email,
        user_email,
        belongs_to,
        page_tokens,
        facebook_user_id,
        access_token,
        scopes,
        organization_id,
        connected_on,
    ):
        self.belongs_to = belongs_to
        self.facebook_email = facebook_email
        self.user_email = user_email
        self.page_tokens = page_tokens
        self.access_token = access_token
        self.scopes = scopes
        self.facebook_user_id = facebook_user_id
        self.organization_id = organization_id
        self.connected_on = connected_on


class NeonCrmDetails(db.Model):
    __tablename__ = "NeonCrmDetails"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    neoncrm_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key = db.Column(db.Text())
    org_id = db.Column(db.Text())
    session_id = db.Column(db.Text())
    belongs_to = db.Column(UUID(as_uuid=True), nullable=False)
    connected_on = db.Column(db.DateTime, nullable=False, default=func.now())

    def __init__(self, api_key, org_id, session_id, connected_on,belongs_to):
        self.api_key = hider.encrypt(api_key)
        self.org_id = hider.encrypt(org_id)
        self.session_id = hider.encrypt(session_id)
        self.belongs_to = belongs_to
        self.connected_on = connected_on

    def get_creds(self):
        creds = {
            "api_key": hider.decrypt(self.api_key),
            "org_id": hider.decrypt(self.org_id),
            "session_id": hider.decrypt(self.session_id),
        }
        return creds
