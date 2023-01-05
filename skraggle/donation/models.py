from flask_jwt_extended import get_jwt
from datetime import datetime
from stripe.api_resources import subscription, customer
from skraggle.base_helpers.dict_responser import dict_resp

from skraggle.config import db
from skraggle.base_helpers.orgGen import getOrg
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
import uuid
from skraggle.run import app


class ScheduleRecurringDonation(db.Model):
    __schema__ = "donations"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True,
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    total_amount = db.Column(db.Float)
    billing_cycle = db.Column(db.String(255))
    status = db.Column(
        ENUM(
            "active",
            "draft",
            name="recurring_donation_status",
        ),
        nullable=False,
    )
    receipt_setting = db.Column(db.String(255))
    impact_area = db.Column(db.String(255))
    campaign_id = db.Column(UUID(as_uuid=True), db.ForeignKey("Campaigns.id"), nullable=False)
    keywords = db.Column(ARRAY(db.String(255)))
    dedication = db.Column(db.Text())
    notes = db.Column(db.Text())
    gift_type = db.Column(db.String(255), nullable=False)
    plan_id = db.Column(db.String(255))
    product_id = db.Column(db.String(255))
    customer_id = db.Column(db.String(255))
    source = db.Column(db.String(255))
    

    def __init__(
        self,
        organization_id,
        contact_id,
        total_amount,
        billing_cycle,
        receipt_setting,
        campaign_id,
        source,
        gift_type = 'money',
        impact_area = '',
        notes = '',
        dedication = '',
        keywords = [],
        status = 'draft',
    ):
        self.organization_id = organization_id
        self.contact_id = contact_id
        self.total_amount = total_amount
        self.billing_cycle = billing_cycle
        self.receipt_setting = receipt_setting
        self.campaign_id = campaign_id
        self.gift_type = gift_type
        self.impact_area = impact_area
        self.notes = notes
        self.dedication = dedication
        self.keywords = keywords
        self.status = status
        self.source = source

    def to_dict(self):
        return dict_resp(self)


class ScheduleRecurringRevenue(db.Model):
    __schema__ = "donations"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True,
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    transaction_type = db.Column(db.String(50))
    total_amount = db.Column(db.Integer)
    billing_cycle = db.Column(db.String(255))
    status = db.Column(
        ENUM(
            "processing",
            "completed",
            "pending",
            name="recurring_status",
            create_type=False,
        ),
        nullable=False,
    )

    def __init__(self, total_amount, billing_cycle, status):
        self.total_amount = total_amount
        self.billing_cycle = billing_cycle
        self.status = status


class TransactionDonation(db.Model):
    __schema__ = "donations"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True,
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    transaction_type = db.Column(db.String(255))
    total_amount = db.Column(db.Integer)
    payment_method = db.Column(db.String(255))
    date_received = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def __init__(self, total_amount, payment_method, date_received, organization_id, contact_id, transaction_type=None):
        self.total_amount = total_amount
        self.payment_method = payment_method
        self.transaction_type = transaction_type
        self.date_received = date_received
        self.organization_id = organization_id
        self.contact_id = contact_id
        self.created_at = datetime.now()

    def to_dict(self):
        donation = {
            "total_amount": self.total_amount,
            "payment_method": self.payment_method,
            "date_received": self.date_received,
            "organization_id": self.organization_id,
            "id": self.id,
            "transaction_type": self.transaction_type,
            "created_at": self.created_at,
        }
        return donation


class TransactionsRevenue(db.Model):
    __schema__ = "donations"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True,
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    transaction_type = db.Column(db.String(255))
    total_amount = db.Column(db.Integer)
    date_received = db.Column(db.DateTime)
    payment_method = db.Column(db.String(255))

    def __init__(self, total_amount, payment_method, date_received):
        self.total_amount = total_amount
        self.date_received = date_received
        self.payment_method = payment_method

    def to_dict(self):
        revenue = {
            "total_amount": self.total_amount,
            "payment_method": self.payment_method,
            "date_received": self.date_received,
        }
        return revenue


class Pledges(db.Model):
    __tablename__ = "Pledges"
    __schema__ = "pledges"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True,
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pledge_name = db.Column(db.String(255))
    total_amount = db.Column(db.Integer)
    pledge_type = db.Column(db.String(255))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(
        ENUM(
            "processing",
            "completed",
            "pending",
            name="pledge_Status",
            create_type=False,
        ),
        nullable=False,
    )

    is_installment = db.Column(db.Boolean, default=False, nullable=False)
    installments = db.relationship("PledgeInstallments", backref="Pledges", lazy=True)
    attachments = db.Column(ARRAY(db.String(255)), default=[])
    associations = db.relationship(
        "Association", backref="Pledges", cascade="all,delete", lazy=True
    )
    contact = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    contact_name = db.Column(db.String(255))
    payment_interval = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, server_default=func.now())

    def __init__(
            self,
            total_amount,
            pledge_type,
            start_date,
            end_date,
            status,
            pledge_name,
            contact_name,
            attachments=[]
    ):
        self.pledge_name = pledge_name
        self.total_amount = total_amount
        self.pledge_type = pledge_type
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.contact_name = contact_name
        self.attachments = attachments

    def to_dict(self):
        pledges = {
            "pledge_name": self.pledge_name,
            "total_amount": self.total_amount,
            "pledge_type": self.pledge_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
            "contact_name": self.contact_name,
            "attachments": self.attachments
        }
        return pledges


class PledgeInstallments(db.Model):
    __tablename__ = "PledgeInstallments"
    __schema__ = "pledges"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True,
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = db.Column(
        ENUM(
            "processing",
            "completed",
            "pending",
            name="pledge_Status",
            create_type=False,
        ),
        nullable=False,
    )
    expected_date = db.Column(db.DateTime())
    amount = db.Column(db.Float)
    pledge_id = db.Column(UUID(as_uuid=True), db.ForeignKey("Pledges.id"))

    def __init__(self, expected_date, amount, status):
        self.organization_id = getOrg(get_jwt())
        self.expected_date = expected_date
        self.amount = amount
        self.status = status

    def to_dict(self):
        pledge = {
            "expected_date": self.expected_date,
            "amount": self.amount,
        }
        return pledge
    

class AdminDonations(db.Model):
    __schema__ = 'donations'
    __tablename__ = "AdminDonations"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True,
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    status = db.Column(db.String(50), default='active')
    date_created = db.Column(db.DateTime, nullable=False, default=func.now())
    
    def __init__(
        self,
        organization_id,
        contact,
        name,
        description,
        status=None,
        date_created=None
    ):
        self.organization_id = organization_id,
        self.contact = contact
        self.name = name,
        self.description = description,
        self.status = status
        self.date_created = date_created
    
    def __repr__(self):
        return "<Admin %r>" % self.name