from datetime import datetime
from math import ceil
from pathlib import Path
import os
from typing import Any, List
import uuid

from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declared_attr
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_sqlalchemy import SQLAlchemy
from sendgrid import SendGridAPIClient
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import Query
import socket

from src.library.utility_classes.mutable_list import MutableList


basedir = Path(__file__).parent.parent
load_dotenv(basedir / '.env')

upload_dir = os.path.join(basedir, "attachments")
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "docx"}
DATABASE_URI = os.getenv(
    "DATABASE_URI") or "postgresql://postgres:postgres@database/postgres"


class OrgFilterQuery(Query):
    def all(self):
        org_id = None
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            org_id = claims["org"]
        except Exception:
            pass

        return (
            self.limit(None)
            .offset(None)
            .filter_by(organization_id=org_id)
            ._iter()
            .all()
        )


db = SQLAlchemy(query_class=OrgFilterQuery)
engine = create_engine(
    DATABASE_URI
)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class Config(object):
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    UPLOAD_FOLDER = "attachments"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEST_TRUE = True
    FLASK_ENV = "development"
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = True
    SESSION_PERMANENT = True
    DB_NAME = os.environ.get("DB_NAME")
    HEROKU_DB_USERNAME = os.getenv("HEROKU_DB_USERNAME")
    HEROKU_DB_PASSWORD = os.getenv("HEROKU_DB_PASSWORD")
    HEROKU_DB_NAME = os.getenv("HEROKU_DB_NAME")
    HEROKU_HOST = os.getenv("HEROKU_HOST")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = True
    SENDGRID_MAIL = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ORGANIZATION_ID = "ORG_SUPER_SECRET@012345"
    ENC_KEY = os.getenv("ENC_KEY")
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL") or 'redis://'
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    PAYPAL_BASE_URL = os.getenv("PAYPAL_BASE_URL")
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
    PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
    EVENTBRITE_BASE_URL = os.getenv('EVENTBRITE_BASE_URL')

    RELEASE_LEVEL = (
        os.getenv("RELEASE_LEVEL") if "RELEASE_LEVEL" in os.environ else "local"
    )

    host = str(socket.gethostname())
    if RELEASE_LEVEL:
        if RELEASE_LEVEL == "local" or RELEASE_LEVEL == "stage" or RELEASE_LEVEL == "production":
            SQLALCHEMY_DATABASE_URI = (
                DATABASE_URI
            )
        else:
            raise ValueError("Invalid or Malformed release level")
    else:
        raise ValueError("Release level not set")

    print("Host serving the application =>", host)
    print("SQL_ALCHEMY_CONNECTION string =>", SQLALCHEMY_DATABASE_URI)
    print(
        f"Environment and Database successfully configured for {RELEASE_LEVEL}")


class ModelMixin(object):
    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)
    row_deleted = db.Column(db.Boolean, default=False, nullable=False)
    sn = db.Column(db.Integer, db.Identity(start=1, cycle=True), index=True)

    @classmethod
    def delete_many_by_id(cls, ids: List[str] = [], organization_id: str = None):
        query = db.session.query(cls).filter(cls.id.in_(ids))
        if organization_id:
            query = query.filter_by(organization_id=organization_id)
        rows = query.all()
        for row in rows:
            row.row_deleted = True
            row.deleted_at = datetime.utcnow()
        db.session.add_all(rows)
        db.session.commit()

    @classmethod
    def fetch_by_id(cls, id: str = None, organization_id: str = None):
        query = db.session.query(cls).filter_by(id=id)
        if organization_id:
            query = query.filter_by(organization_id=organization_id)
        return query.one_or_none()

    @classmethod
    def delete_by_id(cls, id: str = None, organization_id: str = None):
        query = db.session.query(cls).filter_by(id=id)
        if organization_id:
            query = query.filter_by(organization_id=organization_id)
        row = query.one_or_none()
        row.row_deleted = True
        row.deleted_at = datetime.utcnow()
        db.session.commit()

    @classmethod
    def id_exists(cls, id: str = None, organization_id: str = None):
        query = db.session.query(cls.id).filter_by(id=id)
        if organization_id:
            query = query.filter_by(organization_id=organization_id)
        return query.one_or_none() is not None

    def update(self, data: dict[str, Any] = None, unallowed_fields: List[str] = []):
        '''
        Updates a model. \n
        `data`: A dictionary `dict[str, Any]` of the data to update with.\n
        `unallowed_fields`: A list `List[str]` of fields to preclude from the update operation.
        '''
        if not data:
            raise Exception(
                'ModelMixin.update() requires an argument for `data`')

        try:
            unallowed_fields = unallowed_fields + ['id', 'organization_id']
            for field in data.keys():
                if field not in unallowed_fields:
                    setattr(self, field, data.get(field))

            db.session.add(self)
            db.session.commit()

            return True, self
        except Exception as e:
            print(e)
            return False, str(e)


class OrganizationMixin(object):
    organization_id = db.Column(UUID(
        as_uuid=True), primary_key=False, default=uuid.uuid4, nullable=False, index=True)


class TransactionMixin(object):
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(4), nullable=False, default='usd')
    is_from_different_currency = db.Column(
        db.Boolean, nullable=False, default=False)
    type = db.Column(db.String(30), nullable=True)
    payment_method = db.Column(db.String(255), nullable=True)

    keywords = db.Column(MutableList.as_mutable(
        ARRAY(UUID(as_uuid=True))), nullable=False, default=[])
    dedication = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    receipting_strategy = db.Column(db.String(255), nullable=True)

    charge_processor = db.Column(db.String(10), nullable=True)
    charge_receipt_url = db.Column(db.Text, nullable=True)
    charge_transaction_rfx = db.Column(db.String(255), nullable=True)

    is_revenue = db.Column(db.Boolean(), nullable=False, default=False)

    @declared_attr
    def contact_id(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('ContactUsers.id'), nullable=True)

    @declared_attr
    def company_id(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('ContactCompanies.id'), nullable=True)

    @declared_attr
    def pledge_id(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('Pledge.id'), nullable=True)

    @declared_attr
    def campaign_id(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('Campaign.id'), nullable=True)

    @declared_attr
    def source(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('DonationSource.id'), nullable=True)

    @declared_attr
    def impact_area(cls):
        return db.Column(UUID(as_uuid=True), db.ForeignKey('ImpactArea.id'), nullable=True)

    @classmethod
    def rank_by_amount_donated(cls, donations=[]):
        if not donations or not isinstance(donations, List):
            raise Exception(
                'TransactionMixin.rank_by_amount_donated() requires a list argument for `donations`')

        rank = {}
        for donation in donations:
            contact = donation.contact_id or donation.company_id
            if not contact:
                continue
            if not str(contact) in rank:
                rank[str(contact)] = donation.amount
            else:
                rank[str(contact)] += donation.amount

        return rank

    @classmethod
    def donor_score(cls, donations=[], contact: str = None):
        if donations is None or not isinstance(donations, List):
            raise Exception(
                'TransactionMixin.donor_score() requires a list argument for `donations`')
        if not contact:
            raise Exception(
                'TransactionMixin.donor_score() requires an argument for `contact`')

        rank = cls.rank_by_amount_donated(donations)
        values = sorted(rank.values())
        if len(values) == 0:
            return 0

        maximum = values[-1]
        score = rank.get(str(contact))
        if not score:
            return 0
        return ceil((100*score)/maximum)

    @classmethod
    def rank_by_donor_score(cls, donations=[]):
        if donations is None or not isinstance(donations, List):
            raise Exception(
                'TransactionMixin.rank_by_donor_score() requires a list argument for `donations`')

        scores = {}
        for donation in donations:
            contact = donation.contact_id or donation.company_id
            if not contact or str(contact) in scores:
                continue
            scores[str(contact)] = cls.donor_score(donations, contact)

        return scores
