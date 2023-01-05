from skraggle.config import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
import uuid

from skraggle.run import app


class EventsInformation(db.Model):
    __tablename__ = "EventsInformation"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    venue = db.Column(db.String(255))
    address = db.Column(db.String(255))
    state = db.Column(db.String(255))
    zip_country = db.Column(db.Integer)

    def __init__(self, name, description, venue, address, state, zip_country):
        self.name = name
        self.description = description
        self.venue = venue
        self.address = address
        self.state = state
        self.zip_country = zip_country

    def to_dict(self):
        eventinfo = {
            "name": self.name,
            "description": self.description,
            "venue": self.venue,
            "address": self.address,
            "state": self.state,
            "zip_country": self.zip_country
        }
        return eventinfo


class EventSetting(db.Model):
    __tablename__ = "EventSetting"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    max_number_of_total_participants = db.Column(db.String(255))
    event_start_date_setup = db.Column(db.DateTime, nullable=False, default=func.now)
    event_end_date_setup = db.Column(db.DateTime, nullable=False, default=func.now)
    event_reg_cut_off_date = db.Column(db.DateTime, nullable=False, default=func.now)
    one_time_donation = db.Column(db.Boolean)

    def __init__(self, max_number_of_total_participants, event_start_date_setup, event_end_date_setup,
                 event_reg_cut_off_date):
        self.max_number_of_total_participants = max_number_of_total_participants
        self.event_start_date_setup = event_start_date_setup
        self.event_end_date_setup = event_end_date_setup
        self.event_reg_cut_off_date = event_reg_cut_off_date

    def to_dict(self):
        eventsettings = {
            "max_number_of_total_participants": self.max_number_of_total_participants,
            "event_start_date_setup": self.event_start_date_setup,
            "event_end_date_setup": self.event_end_date_setup,
            "event_reg_cut_off_date": self.event_reg_cut_off_date,
        }
        return eventsettings


class EventRegisterationReciept(db.Model):
    __tablename__ = "EventRegisterationReciept"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    from_name = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    body = db.Column(db.String(255))

    def __init__(self, title, description, from_name, subject, body):
        self.title = title
        self.description = description
        self.from_name = from_name
        self.subject = subject
        self.body = body

    def to_dict(self):
        eventregisterarionreciept = {
            "title": self.title,
            "description": self.description,
            "from_name": self.from_name,
            "subject": self.subject,
            "body": self.body
        }
        return eventregisterarionreciept


class Packages(db.Model):
    __tablename__ = "Packages"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    private_package = db.Column(db.Boolean)
    is_enabled = db.Column(db.Boolean)
    price = db.Column(db.Integer)
    direct_cost = db.Column(db.Integer)
    number_of_packages_for_sale = db.Column(db.Integer)
    qty_purchase_limit = db.Column(db.Integer)
    early_bird_discount_enabled = db.Column(db.Boolean)
    early_bird_discount_amount = db.Column(db.Integer)
    early_bird_discount_cutoff_time = db.Column(db.DateTime)
    early_bird_discount_type = db.Column(ENUM("percentage", "amount", name="early_bird_discount_type") )
    participants = db.Column("participants", ARRAY(UUID))
    fields = db.relationship(
        "Fields", backref="Packages", cascade="all,delete", lazy=True
    )
    promocode = db.relationship(
        "PromoCode", backref="Packages", cascade="all,delete", lazy=True
    )

    def __init__(self, name, description, price, direct_cost, number_of_packages_for_sale, qty_purchase_limit,
                 organization_id, is_enabled, early_bird_discount_enabled=None, early_bird_discount_amount=None,
                 early_bird_discount_cutoff_time=None, early_bird_discount_type=None):
        self.name = name
        self.description = description
        self.price = price
        self.direct_cost = direct_cost
        self.number_of_packages_for_sale = number_of_packages_for_sale
        self.qty_purchase_limit = qty_purchase_limit
        self.is_enabled = is_enabled
        self.organization_id = organization_id
        self.early_bird_discount_enabled = early_bird_discount_enabled
        self.early_bird_discount_amount = early_bird_discount_amount
        self.early_bird_discount_cutoff_time = early_bird_discount_cutoff_time
        self.early_bird_discount_type = early_bird_discount_type

    def to_dict(self):
        package = {
            "name": self.name,
            "description": self.description,
            "direct_cost": self.direct_cost,
            "number_of_packages_for_sale": self.number_of_packages_for_sale,
            "qty_purchase_limit": self.qty_purchase_limit,
            "is_enabled": self.is_enabled,
            "early_bird_discount_enabled": self.early_bird_discount_enabled,
            "early_bird_discount_amount": self.early_bird_discount_amount,
            "early_bird_discount_cutoff_time": self.early_bird_discount_cutoff_time,
            "early_bird_discount_type": self.early_bird_discount_type
        }
        return package


class Fields(db.Model):
    __tablename__ = "Fields"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_label = db.Column(db.String(255))
    reporting_label = db.Column(db.String(255))
    field_type = db.Column(
        ENUM("Text Box", "Text Area", "Dropdown", "Checkbox", name="fields", create_type=False), nullable=False
    )
    associate_field_with_specific_package = db.Column(UUID(as_uuid=True), db.ForeignKey("Packages.id"))

    def __init__(self, field_label, reporting_label, field_type):
        self.field_label = field_label
        self.reporting_label = reporting_label
        self.field_type = field_type

    def to_dict(self):
        fields = {
            "field_label": self.field_label,
            "reporting_label": self.reporting_label,
            "field_type": self.field_type,
        }
        return fields


class PromoCode(db.Model):
    __tablename__ = "PromoCode"
    organization_id = db.Column(db.String(100),default=app.config["ORGANIZATION_ID"],nullable=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    promo_code = db.Column(db.String(255))
    description = db.Column(db.String(255))
    discount = db.Column(db.Integer)
    max_user = db.Column(db.Integer)
    start_date = db.Column(db.DateTime, nullable=False, default=func.now)
    end_date = db.Column(db.DateTime, nullable=False, default=func.now)
    promo_code_applied_to_package = db.Column(UUID(as_uuid=True), db.ForeignKey("Packages.id"))

    def __init__(self, promo_code, description, discount, max_user, start_date, end_date, organization_id):
        self.promo_code = promo_code
        self.description = description
        self.discount = discount
        self.max_user = max_user
        self.start_date = start_date
        self.end_date = end_date
        self.organization_id = organization_id

    def to_dict(self):
        promocode = {
            "promo_code": self.promo_code,
            "description": self.description,
            "discount": self.discount,
            "max_user": self.max_user,
            "start_date": self.start_date,
            "end_date": self.end_date
        }
        return promocode
