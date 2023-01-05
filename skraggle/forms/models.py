from datetime import datetime

from skraggle.config import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid

from skraggle.run import app


class Forms(db.Model):
    __schema__ = "Forms"
    __tablename__ = "Forms"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    form_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_name = db.Column(db.String(255))
    campaign = db.Column(UUID(as_uuid=True), db.ForeignKey("Campaigns.id"))
    form_type = db.Column(db.String(200))
    tags = db.Column(db.String(255))
    desc = db.Column(db.String(255), default="Draft")
    is_minimum_amount = db.Column(db.Boolean(), default=False)
    is_default_currency = db.Column(db.Boolean(), default=False)
    is_default_donation = db.Column(db.Boolean(), default=False)
    is_tribute = db.Column(db.Boolean(), default=False)
    is_processing_fee = db.Column(db.Boolean(), default=True)
    responses = db.relationship(
        "Responses", backref="Forms", cascade="all,delete", lazy=True
    )
    followers = db.Column(db.String(255))

    # enum field
    status = db.Column(
        ENUM("published", "closed", name="form_status", create_type=False), nullable=False
    )
    created_on = db.Column(db.DateTime(), server_default=func.now())

    def __init__(
        self,
        form_name,
        form_type,
        desc,
        followers,
        status,
        created,
        tags,
        is_minimum_amount,
        is_default_donation,
        is_processing_fee,
        is_tribute,
        is_default_currency
    ):
        self.form_name = form_name
        self.form_type = form_type
        self.tags = tags
        self.desc = desc
        self.followers = followers
        self.status = status
        self.created = created
        self.is_minimum_amount = is_minimum_amount
        self.is_default_donation = is_default_donation
        self.is_processing_fee = is_processing_fee
        self.is_tribute = is_tribute
        self.is_default_currency = is_default_currency
        
    def to_dict(self):
        return {
            "form_name": self.form_name,
            "form_type": self.form_type,
            "tags": self.tags,
            "desc": self.desc,
            "followers": self.followers,
            "status": self.status,
            "created": self.created,
            "is_minimum_amount": self.is_minimum_amount,
            "is_default_donation": self.is_default_donation,
            "is_processing_fee": self.is_processing_fee,
            "is_tribute": self.is_tribute,
            "is_default_currency": self.is_default_currency
        }


class Responses(db.Model):
    __schema__ = "Forms"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    response_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = db.Column(UUID(as_uuid=True), db.ForeignKey("Forms.form_id"))
    created = db.Column(db.DateTime, server_default=func.now())
    fullname = db.Column(db.String(255))
    gender = db.Column(db.String(50))
    birth_date = db.Column(db.DateTime)
    last_name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    payment_method = db.Column(db.String(255))
    default_currency = db.Column(db.String(155))
    payment_type = db.Column(db.String(255))
    minimum_amount = db.Column(db.Integer)
    comments = db.Column(db.String(255))

    def __init__(
        self,
        fullname,
        gender,
        birth_date,
        last_name,
        address,
        payment_method,
        payment_type,
        minimum_amount,
        comments,
        default_currency,
    ):
        self.fullname = fullname
        self.gender = gender
        self.birth_date = birth_date
        self.last_name = last_name
        self.address = address
        self.payment_method = payment_method
        self.payment_type = payment_type
        self.minimum_amount = minimum_amount
        self.comments = comments
        self.default_currency = default_currency


class UrlShortener(db.Model):
    __tablename__ = "UrlShortener"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    shorten_url_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_url = db.Column(db.String(255))
    custom_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, original_url, custom_id, created_at):
        self.original_url = original_url
        self.custom_id = custom_id
        self.created_at = created_at

