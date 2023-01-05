import datetime
from email.policy import default

from skraggle.config import db
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid
from flask_login import UserMixin
from skraggle.run import app
from skraggle.base_helpers.orgGen import orgGen
        

class Admin(UserMixin, db.Model):
    __tablename__ = "Admin"
    organization_id = db.Column(db.String(100), default=orgGen(), nullable=True)
    admin_id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(500))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    confirmed = db.Column(db.Boolean, default=False, nullable=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    extra_protection = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    type_of = db.Column(ENUM("user", "invitation", name="type_of", create_type=False,))
    permission_level = db.Column(
        ENUM(
            "administrator",
            "coordinator",
            "manager",
            name="permission_level",
            create_type=False,
        )
    )
    salesforce_connected = db.Column(db.Boolean, default=False)
    salesforce_id = db.Column(db.String(255))
    facebook_connected = db.Column(db.Boolean, default=False)
    facebook_id = db.Column(db.String(255))
    token_reset = db.Column(db.String(255), default=False)

    def __init__(
        self, type_of, permission_level, email, password, first_name, last_name
    ):
        self.type_of = type_of
        self.permission_level = permission_level
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        return self.admin_id


class OrganizationSettings(db.Model):
    __tablename__ = "OrganizationSettings"
    organization_id = db.Column(db.String(100), default="UNKNOWN", primary_key=True,)
    organization_name = db.Column(db.String(255))
    organization_email = db.Column(db.String(255))
    address = db.Column(db.String(255))
    organization_phone = db.Column(db.String(20))
    organization_website = db.Column(db.String(255))
    timezone = db.Column(db.String(255))
    organization_logo = db.Column(db.String(255))
    statement_description = db.Column(db.Text)
    is_legal = db.Column(db.Boolean, default=False)
    tax_exemption_verification = db.Column(db.String(255))

    def __init__(
        self,
        organization_name,
        organization_email,
        address,
        organization_phone,
        organization_website,
        timezone,
        organization_logo,
        statement_description,
        is_legal,
        tax_exemption_verification,
    ):
        self.organization_name = organization_name
        self.organization_email = organization_email
        self.address = address
        self.organization_phone = organization_phone
        self.organization_website = organization_website
        self.timezone = timezone
        self.organization_logo = organization_logo
        self.statement_description = statement_description
        self.is_legal = is_legal
        self.tax_exemption_verification = tax_exemption_verification


class Invitations(db.Model):
    __tablename__ = "Invitations"
    organization_id = db.Column(db.String(100), nullable=False)
    invitation_id = db.Column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
    )
    invitation_key = db.Column(db.String(55), unique=True, nullable=False)
    permission_level = db.Column(
        ENUM(
            "administrator",
            "coordinator",
            "manager",
            name="permission_level",
            create_type=False,
        )
    )
    expired = db.Column(db.Boolean, default=False)
    invited_by = db.Column(UUID(as_uuid=True), nullable=False)
    invited_user_email = db.Column(db.String(255))
    invited_on = db.Column(db.DateTime, default=datetime.datetime.now())
    invitation_url = db.Column(db.String(255))

    def __init__(
        self,
        permission_level,
        invited_by,
        invited_user_email,
        invitation_key,
        organization_id,
    ):
        self.permission_level = permission_level
        self.invited_by = invited_by
        self.invited_user_email = invited_user_email
        self.invitation_key = (invitation_key,)
        self.organization_id = organization_id


class AccessTokenBlocklist(db.Model):
    __tablename__ = "AccessTokenBlocklist"
    id = db.Column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
    )
    jti = db.Column(db.String(36), nullable=False)
    revoked_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, jti, revoked_on):
        self.jti = jti
        self.revoked_on = revoked_on
