from operator import and_
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db
from src.contacts.contact_users.models import ContactUsers
from src.contacts.tags.models import ContactTags
from src.library.utility_classes.custom_validator import Validator
from src.library.utility_classes.mutable_list import MutableList


class AssociatedContact(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'AssociatedContact'

    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactCompanies.id'), nullable=True)
    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactUsers.id'), nullable=True)
    position = db.Column(db.String(255), nullable=True)


class ContactCompanies(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "ContactCompanies"

    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    address = db.Column(db.String(255), nullable=True)
    assignee = db.Column(UUID(as_uuid=True), nullable=True)
    priority = db.Column(db.String(20), nullable=True)
    
    established_at = db.Column(db.DateTime, server_default=db.func.now())
    tags = db.Column(MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=False)

    notes = db.Column(db.Text, nullable=True)
    solicitation = db.Column(db.Boolean, nullable=True)
    primary_contact = db.Column(UUID(as_uuid=True), nullable=True)

    is_subscribed_to_mailblasts = db.Column(db.Boolean, nullable=True, default=None)
    mailblasts_unsubscribe_feedback = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    associated_contacts = db.relationship('AssociatedContact', backref='ContactCompanies', lazy=True, cascade="all,delete")
    interactions = db.relationship('ContactInteraction', backref='ContactCompanies', lazy=True, cascade="all,delete")
    volunteer_activity = db.relationship('VolunteerActivity', backref='ContactCompanies', lazy=True, cascade="all,delete")
    pledges = db.relationship('Pledge', backref='ContactCompanies', lazy=True, cascade="all,delete")
    assigned_mailblasts = db.relationship('MailBlast', backref='ContactCompanies', lazy=True, cascade="all,delete")
    one_time_transactions = db.relationship('OneTimeTransaction', backref='ContactCompanies', lazy=True, cascade="all,delete")
    recurring_transactions = db.relationship('RecurringTransaction', backref='ContactCompanies', lazy=True, cascade="all,delete")


    def __init__(
        self, name=None, type=None, email=None,
        phone=None,
        address=None, assignee=None, priority=None,
        established_at=None, tags=[], organization_id=None,
        notes=None, solicitation=None, primary_contact=None,
        associated_contacts=None, is_subscribed_to_mailblasts = True,
        mailblasts_unsubscribe_feedback = None
    ):
        self.name = name 
        self.type = type 
        self.email = email 
        self.phone = phone 

        self.address = address
        self.assignee = assignee
        self.priority = priority
        
        self.established_at = established_at
        self.tags = tags or []
        
        self.organization_id = organization_id
        
        self.notes = notes
        self.solicitation = solicitation
        self.primary_contact = primary_contact

        self.associated_contacts = associated_contacts or []
        self.is_subscribed_to_mailblasts = is_subscribed_to_mailblasts or True 
        self.mailblasts_unsubscribe_feedback = mailblasts_unsubscribe_feedback
        self.notes = notes


    def get_tag_names(self):
        return  [
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
            raise Exception('ContactCompanies.register() requires an argument for `data`')

        # validations 
        required_fields = ['name', 'email', 'phone', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"`{field}` is a required field"
        if not Validator.is_email(data.get('email')):
            return False, "A valid email address is required"

        # does ContactCompanies already exist?
        company = cls.query.filter_by(email=data.get('email'), organization_id=data.get('organization_id')).one_or_none()
        if company:
            return False, "A company is already registered with this email address. Try again with a different address."

        # if `assignee` field is provided, does it reference a valid ContactUser object?
        if data.get('assignee'):
            if not ContactUsers.id_exists(data.get('assignee'), data.get('organization_id')):
                return False, "`assignee` should be a valid contact"

        # save object
        company = cls(**data)
        db.session.add(company)
        db.session.flush()
        db.session.commit()

        return True, company