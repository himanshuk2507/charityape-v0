from datetime import datetime
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from skraggle.config import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
import uuid

from skraggle.eblasts.models import MutableList
from skraggle.run import app
from skraggle.base_helpers.updating_fields_fetch import get_fields


class DemoUsers(db.Model):
    __tablename__ = "demo_users"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    orgName = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)


class GoogleUsers(db.Model):
    __tablename__ = "GoogleUsers"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    google_id = db.Column(db.String(30), primary_key=True)
    fullname = db.Column(db.String(255))
    fname = db.Column(db.String(255))
    lname = db.Column(db.String(255))
    email = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    location = db.Column(db.String(225))
    joined_on = db.Column(db.DateTime, nullable=False, default=func.now())

    def __init__(
        self,
        google_id,
        fullname,
        fname,
        lname,
        email,
        is_verified,
        location,
        joined_on=None,
    ):
        self.google_id = google_id
        self.fullname = fullname
        self.fname = fname
        self.lname = lname
        self.email = email
        self.is_verified = is_verified
        self.location = location
        self.joined_on = joined_on

    def __repr__(self):
        return "<User %r>" % self.fullname


class ContactUsers(db.Model):
    __schema__ = "contacts"
    __tablename__ = "ContactUsers"
    organization_id = db.Column(db.String(100), nullable=False)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    todo_id = db.relationship(
        "ContactTodo", backref="ContactUsers", cascade="all,delete", lazy=True
    )
    activities = db.relationship(
        "VolunteerActivity", backref="ContactUsers", lazy=True, cascade="all,delete",
    )
    info = db.relationship(
        "PersonalInfo", backref="ContactUsers", lazy=True, cascade="all,delete",
    )
    donation_pledges = db.relationship(
        "Pledges", backref="ContactUsers", lazy=True, cascade="all,delete",
    )
    fullname = db.Column(db.String(255))
    primary_phone = db.Column(db.String(255), nullable=True)
    primary_email = db.Column(db.String(255))
    address = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.String(255), nullable=True)
    best_way_to_reach_out = db.Column(db.String(155), nullable=True)
    birth_date = db.Column(db.DateTime, server_default=func.now())
    state = db.Column(db.String(155), nullable=True)
    city = db.Column(db.String(155), nullable=True)
    postal_zip = db.Column(db.String(155), nullable=True)
    # companies = db.Column(db.String(155), nullable=True)
    company = db.Column(db.String(155), nullable=True)
    type = db.Column(db.String(155), nullable=True)
    unit = db.Column(db.String(155), nullable=True)
    assignee = db.Column(db.String(155), nullable=True)
    contact_type = db.Column(db.String(155), nullable=True)
    country = db.Column(db.String(155), nullable=True)
    has_membership = db.Column(db.Boolean, default=False)
    membership = db.relationship(
        "Memberships", backref="ContactUsers", lazy=True, cascade="all,delete",
    )
    schedule_recurring_donations = db.relationship(
        "ScheduleRecurringDonation",
        backref="ContactUsers",
        cascade="all,delete",
        lazy=True,
    )
    schedule_recurring_revenues = db.relationship(
        "ScheduleRecurringRevenue",
        backref="ContactUsers",
        cascade="all,delete",
        lazy=True,
    )
    transaction_donations = db.relationship(
        "TransactionDonation", backref="ContactUsers", cascade="all,delete", lazy=True
    )
    transaction_revenues = db.relationship(
        "TransactionsRevenue", backref="ContactUsers", cascade="all,delete", lazy=True
    )
    donations_last_year = db.Column(db.Numeric(1000, 2))
    donations_this_year = db.Column(db.Numeric(1000, 2))
    donor_score = db.Column(db.Integer, nullable=True)
    email_subscription_status = db.Column(db.String(255), nullable=True)
    engagement_stage = db.Column(db.String(50), nullable=True)
    established_date = db.Column(db.DateTime, server_default=func.now())
    gender = db.Column(db.String(255), nullable=True)
    household = db.Column(db.String(255), nullable=True)
    household_Role = db.Column(db.String(255), nullable=True)
    major_gift_amount = db.Column(db.Integer, nullable=True)
    major_gift_donor = db.Column(db.Integer, nullable=True)
    preferred_name = db.Column(db.String(255), nullable=True)
    priority = db.Column(db.String(255), nullable=True)
    smart_Ask = db.Column(db.String(255), nullable=True)
    solicitation = db.Column(db.String(255), nullable=True)
    time_of_year = db.Column(db.DateTime, server_default=func.now())
    title = db.Column(db.String(255), default=None, nullable=True)
    number_of_donations = db.Column(db.Integer, nullable=True)
    total_donations = db.Column(db.Numeric(1000, 2))
    Transactions = db.relationship(
        "Transactions", backref="ContactUsers", lazy=True, cascade="all,delete",
    )
    total_transactions = db.Column(db.Integer, nullable=True)
    total_volunteering = db.Column(db.Numeric(1000, 2))
    volunteering_this_year = db.Column(db.String(255), nullable=True)
    facebook = db.Column(db.String(255), nullable=True)
    instagram = db.Column(db.String(255), nullable=True)
    linkedln = db.Column(db.String(255), nullable=True)
    twitter = db.Column(db.String(255), nullable=True)
    youtube = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(225), nullable=True)
    othersite = db.Column(db.String(255), nullable=True)
    created_on = db.Column(db.DateTime, server_default=func.now())
    
    def __init__(
        self,
        fullname,
        primary_phone,
        primary_email,
        tags,
        birth_date,
        address,
        city,
        state,
        postal_zip,
        country,
        priority,
        company,
        organization_id,
        best_way_to_reach_out=None,
        type=None,
        unit=None,
        assignee=None,
        contact_type=None,
        has_membership=None,
        email_subscription_status=None,
        engagement_stage=None,
        established_date=None,
        gender=None,
        household=None,
        household_Role=None,
        major_gift_amount=None,
        major_gift_donor=None,
        preferred_name=None,
        smart_Ask=None,
        solicitation=None,
        time_of_year=None,
        title=None,
        total_transactions=0,
        total_volunteering=0,
        volunteering_this_year=0,
        facebook=None,
        instagram=None,
        linkedln=None,
        twitter=None,
        youtube=None,
        website=None,
        total_donations=1,
        donor_score=None,
        donations_this_year=1,
        donations_last_year=0,
        othersite=None,
        created_on=datetime.now(),
        number_of_donations=0
    ):
        self.created_on = created_on
        self.gender = gender
        self.household = household
        self.established_date = established_date
        self.email_subscription_status = email_subscription_status
        self.engagement_stage = engagement_stage
        self.has_membership = has_membership
        self.contact_type = contact_type
        self.assignee = assignee
        self.unit = unit
        self.type = type
        self.fullname = fullname
        self.primary_phone = primary_phone
        self.primary_email = primary_email
        self.tags = tags
        self.total_donations = total_donations
        self.donor_score = donor_score
        self.donations_this_year = donations_this_year
        self.donations_last_year = donations_last_year
        self.birth_date = birth_date
        self.address = address
        self.city = city
        self.state = state
        self.postal_zip = postal_zip
        self.country = country
        self.priority = priority
        self.company = company
        self.organization_id = organization_id
        self.best_way_to_reach_out = best_way_to_reach_out
        self.household_Role = household_Role
        self.major_gift_amount = major_gift_amount
        self.major_gift_donor = major_gift_donor
        self.preferred_name = preferred_name
        self.smart_Ask = smart_Ask
        self.solicitation = solicitation
        self.time_of_year = time_of_year
        self.title = title
        self.total_transactions = total_transactions
        self.total_volunteering = total_volunteering
        self.volunteering_this_year = volunteering_this_year
        self.facebook = facebook
        self.instagram = instagram
        self.linkedln = linkedln
        self.twitter = twitter
        self.youtube = youtube
        self.website = website
        self.othersite = othersite

    def __repr__(self):
        return "<User %r>" % self.fullname
    

class ContactTodo(db.Model):
    __schema__ = "contacts"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    interaction_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("Interactions.interaction_id")
    )
    todo = db.Column(db.String(255))
    details = db.Column(db.String(255), nullable=True)
    assignee = db.Column(UUID(as_uuid=True), nullable=True)
    due_date = db.Column(db.DateTime, server_default=func.now())
    completed = db.Column(db.Boolean, default=False, nullable=False)
    attachment_name = db.Column(db.String(255))
    attachments = db.Column(db.String(255))

    def __init__(self, todo, due_date, details, assignee):
        self.todo = todo
        self.details = details
        self.assigned = assignee
        self.due_date = due_date


class HouseholdUsers(db.Model):
    __tablename__ = "HouseholdUsers"
    __schema__ = "contacts"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    household_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, server_default=func.now())
    contacts = db.Column(
        MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=True
    )
    # created_on = db.Column(db.DateTime)

    def __init__(self, name, created_on, contacts):
        self.name = name
        self.created_on = created_on
        self.contacts = contacts

    def __repr__(self):
        return "<User %r>" % self.name


class SegmentUsers(db.Model):
    __tablename__ = "SegmentUsers"
    __schema__ = "contacts"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    segment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contacts = db.Column(
        MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=True
    )
    name = db.Column(db.String(255))
    description = db.Column(db.String(255), nullable=True)
    created_on = db.Column(db.DateTime)

    def __init__(self, name, created_on, contacts, description):
        self.name = name
        self.created_on = created_on
        self.contacts = contacts
        self.description = description

    def __repr__(self):
        return "<User %r>" % self.name


class CompanyUsers(db.Model):
    __tablename__ = "CompanyUsers"
    __schema__ = "contacts"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    company_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = db.Column(db.String(255))
    primary_phone = db.Column(db.VARCHAR)
    tag = db.Column(db.String(50))
    created_on = db.Column(db.DateTime, server_default=func.now())

    def __init__(self, company_name, primary_phone, tag, created_on):
        self.company_name = company_name
        self.primary_phone = primary_phone
        self.created_on = created_on
        self.tag = tag

    def __repr__(self):
        return "<User %r>" % self.company_name


class TagUsers(db.Model):
    __tablename__ = "TagUsers"
    __schema__ = "contacts"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    contacts = db.Column(
        MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=True
    )
    tag_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tag_name = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, server_default=func.now())

    def __init__(self, tag_name, created):
        self.tag_name = tag_name
        self.created = created

    def __repr__(self):
        return "<User %r>" % self.tag_name


class VolunteerActivity(db.Model):
    __tablename__ = "VolunteerActivity"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_name = db.Column(db.String(255))
    start_date = db.Column(db.DateTime, server_default=func.now())
    end_date = db.Column(db.DateTime, server_default=func.now())
    desc = db.Column(db.String(255))
    impact_area = db.Column(db.String(255))
    compaign = db.Column(db.String(255))
    attachment_name = db.Column(db.String(255))
    attachments = db.Column(db.String(255))

    def __init__(
        self, activity_name, start_date, end_date, desc, impact_area, compaign
    ):
        self.activity_name = activity_name
        self.start_date = start_date
        self.end_date = end_date
        self.desc = desc
        self.impact_area = impact_area
        self.compaign = compaign

    def __repr__(self):
        return "<User %r>" % self.activity_name


class PersonalInfo(db.Model):
    __tablename__ = "PersonalInfo"
    __schema__ = "contacts"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    todo = db.Column(db.String(255))
    due_date = db.Column(db.DateTime, server_default=func.now())
    completed = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, todo, due_date):
        self.todo = todo
        self.due_date = due_date


class Memberships(db.Model):
    __tablename__ = "Memberships"
    __schema__ = "memberships"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    membership_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    membership_status = db.Column(
        ENUM(
            "active",
            "expired",
            "cancelled",
            name="membership_status",
            create_type=False,
        ),
        nullable=True,
    )
    start_date = db.Column(db.DateTime, server_default=func.now())
    end_date = db.Column(db.DateTime, server_default=func.now())
    auto_renew = db.Column(db.Boolean, default=True)
    auto_send_email = db.Column(db.Boolean, default=True)
    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey("ContactUsers.id"))
    receipt_name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    email_address = db.Column(db.String(100))
    membership_fee = db.Column(db.Integer)
    cancelled_date = db.Column(db.DateTime, nullable=True)
    payment_method = db.Column(
        ENUM(
            "stripe", "paypal", "offline", name="membership_payment", create_type=False,
        ),
        nullable=False,
    )

    def __init__(
        self,
        start_date,
        end_date,
        auto_renew,
        auto_send_email,
        receipt_name,
        address,
        email_address,
        payment_method,
        membership_fee,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.auto_renew = auto_renew
        self.auto_send_email = auto_send_email
        self.receipt_name = receipt_name
        self.address = address
        self.email_address = email_address
        self.payment_method = payment_method
        self.membership_fee = membership_fee

    def to_dict(self):
        d = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "auto_renew": self.auto_renew,
            "auto_send_email": self.auto_send_email,
            "receipt_name": self.receipt_name,
            "address": self.address,
            "email_address": self.email_address,
            "payment_method": self.payment_method,
            "membership_fee": self.membership_fee,
        }
        return d


class Interactions(db.Model):
    __tablename__ = "Interactions"
    __schema__ = "contacts"
    organization_id = db.Column(
        db.String(100), default=app.config["ORGANIZATION_ID"], nullable=True
    )
    interaction_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact = db.Column(UUID(as_uuid=True), nullable=False)
    interaction_type = db.Column(
        ENUM(
            "email",
            "phone",
            "mail",
            "inperson",
            "onlinechat",
            "videoconference",
            "socialmedia",
            "other",
            "event",
            name="interaction_type",
            create_type=False,
        ),
        nullable=True,
    )
    date = db.Column(db.DateTime, server_default=func.now())
    subject = db.Column(db.String(255))
    desc = db.Column(db.String(255), nullable=True)
    attachments = db.Column(db.String(255), nullable=True)
    has_todo = db.Column(db.Boolean, default=False)
    todo = db.relationship(
        "ContactTodo", backref="Interactions", cascade="all,delete", lazy=True
    )

    def __init__(
        self, contact, interaction_type, date, subject, desc, attachments, has_todo
    ):
        self.contact = contact
        self.interaction_type = interaction_type
        self.date = date
        self.subject = subject
        self.desc = desc
        self.attachments = attachments
        self.has_todo = has_todo
