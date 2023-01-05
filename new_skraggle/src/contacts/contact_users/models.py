from operator import and_
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db
from src.contacts.households.models import Households
from src.contacts.tags.models import ContactTags
from src.library.utility_classes.custom_validator import Validator
from src.library.utility_classes.mutable_list import MutableList


class ContactUsers(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "ContactUsers"

    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    preferred_name = db.Column(db.String(255), nullable=True)

    primary_email = db.Column(db.String(255), nullable=False)
    primary_phone = db.Column(db.String(20), nullable=True)

    birth_date = db.Column(db.DateTime, nullable=True)
    address = db.Column(db.String(255), nullable=True)

    tags = db.Column(MutableList.as_mutable(
        ARRAY(UUID(as_uuid=True))), nullable=False)

    home_email = db.Column(db.String(255), nullable=True)
    work_email = db.Column(db.String(255), nullable=True)
    other_emails = db.Column(ARRAY(db.String(255)), nullable=True)

    home_phone = db.Column(db.String(20), nullable=True)
    work_phone = db.Column(db.String(20), nullable=True)
    other_phones = db.Column(ARRAY(db.String(20)), nullable=True)

    home_address = db.Column(db.String(255), nullable=True)
    work_address = db.Column(db.String(255), nullable=True)
    other_addresses = db.Column(ARRAY(db.String(255)), nullable=True)

    website = db.Column(db.String(255), nullable=True)
    twitter = db.Column(db.String(255), nullable=True)
    facebook = db.Column(db.String(255), nullable=True)
    youtube = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    instagram = db.Column(db.String(255), nullable=True)
    other_websites = db.Column(ARRAY(db.String(255)), nullable=True)

    households = db.Column(MutableList.as_mutable(
        ARRAY(UUID(as_uuid=True))), nullable=False, default=[])

    priority = db.Column(db.String(20), nullable=True)
    unit = db.Column(db.String(255), nullable=True)
    postal_code = db.Column(db.String(255), nullable=True)
    state = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    company = db.Column(UUID(as_uuid=True), nullable=True)
    assignee = db.Column(UUID(as_uuid=True), nullable=True)

    is_subscribed_to_mailblasts = db.Column(
        db.Boolean, nullable=True, default=None)
    mailblasts_unsubscribe_feedback = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    t_shirt_size = db.Column(db.String(255), nullable=True)

    associated_contacts = db.relationship(
        'AssociatedContact', backref='ContactUsers', lazy=True, cascade="all,delete")
    interactions = db.relationship(
        'ContactInteraction', backref='ContactUsers', lazy=True, cascade="all,delete")
    volunteer_activity = db.relationship(
        'VolunteerActivity', backref='ContactUsers', lazy=True, cascade="all,delete")
    pledges = db.relationship(
        'Pledge', backref='ContactUsers', lazy=True, cascade="all,delete")
    assigned_mailblasts = db.relationship(
        'MailBlast', backref='ContactUsers', lazy=True, cascade="all,delete")
    one_time_transactions = db.relationship(
        'OneTimeTransaction', backref='ContactUsers', lazy=True, cascade="all,delete")
    recurring_transactions = db.relationship(
        'RecurringTransaction', backref='ContactUsers', lazy=True, cascade="all,delete")

    def __init__(
        self, first_name: str = None, last_name: str = None, preferred_name: str = None, primary_email: str = None, primary_phone: str = None,
        email_subscription_status: str = None, birth_date=None, address: str = None, organization_id: str = None, tags=[],
        home_email=None, work_email=None, other_emails=None,
        home_phone=None, work_phone=None, other_phones=None,
        home_address=None, work_address=None, other_addresses=None,
        website=None, twitter=None, facebook=None, youtube=None, linkedin=None, instagram=None, other_websites=None,
        households=[], priority=None, unit=None, postal_code=None,
        state=None, country=None, city=None,
        company=None, assignee=None, is_subscribed_to_mailblasts=True,
        mailblasts_unsubscribe_feedback=None, notes=None, t_shirt_size=None
    ) -> None:
        self.organization_id = organization_id
        self.first_name = first_name
        self.last_name = last_name
        self.preferred_name = preferred_name

        self.primary_email = primary_email.lower()
        self.primary_phone = primary_phone

        self.email_subscription_status = email_subscription_status

        self.birth_date = birth_date
        self.address = address

        self.tags = tags or []

        self.home_email = home_email
        self.work_email = work_email
        self.other_emails = other_emails
        self.home_phone = home_phone
        self.work_phone = work_phone
        self.other_phones = other_phones
        self.home_address = home_address
        self.work_address = work_address
        self.other_addresses = other_addresses
        self.website = website
        self.twitter = twitter
        self.facebook = facebook
        self.youtube = youtube
        self.linkedin = linkedin
        self.instagram = instagram
        self.other_websites = other_websites

        self.households = households

        self.postal_code = postal_code
        self.unit = unit
        self.priority = priority
        self.state = state
        self.country = country
        self.city = city
        self.company = company
        self.assignee = assignee

        self.is_subscribed_to_mailblasts = is_subscribed_to_mailblasts or True
        self.mailblasts_unsubscribe_feedback = mailblasts_unsubscribe_feedback
        self.notes = notes
        self.t_shirt_size = t_shirt_size

    def get_tag_names(self):
        return [
            names[0] for names in
            db.session.query(ContactTags.name).filter(
                and_(
                    ContactTags.id.in_(self.tags),
                    ContactTags.organization_id == self.organization_id
                )
            ).all()
        ]

    def load_tag_names(self):
        self.tags = self.get_tag_names()
        return self

    @classmethod
    def register(cls, data: dict = None):
        if not data:
            raise Exception(
                'ContactUsers.register() requires an argument for `data`')

        # validations
        required_fields = ['first_name', 'last_name',
                           'primary_email', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"
        if not Validator.is_email(data.get('primary_email')):
            return False, "A valid email address is required"

        # does ContactUser already exist?
        contact = cls.query.filter_by(primary_email=data.get(
            'primary_email'), organization_id=data.get('organization_id')).one_or_none()
        if contact:
            return False, "A contact is already registered with this email address. Try again with a different address."

        households = data.get('households')
        data.pop('households')
        data['company'] = None if data.get('company') == "" else data.get('company')
        contact = cls(**data)
        for household_id in households:
            if household_id:
                household: Households = Households.fetch_by_id(
                    id=household_id, organization_id=data.get('organization_id'))
                if not household:
                    return False, 'No household exists with this ID'
                contact.households.append(household_id)

        db.session.add(contact)
        db.session.flush()
        db.session.commit()

        return True, contact
