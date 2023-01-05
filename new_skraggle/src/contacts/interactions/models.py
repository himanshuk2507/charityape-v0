from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers


class ContactInteraction(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "ContactInteraction"

    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactUsers.id'), nullable=True)
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactCompanies.id'), nullable=True)
    # is this 'contact' a ContactUser or ContactCompany
    is_individual = db.Column(db.Boolean, nullable=False, default=True)

    type = db.Column(db.String(64), nullable=False)
    interacted_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    attachments = db.Column(ARRAY(db.String(255)), nullable=False)
    
    todos = db.Column(ARRAY(db.String(255)), nullable=True, default=[])

    def __init__(
        self, contact_id=None, company_id=None, is_individual=None,
        type=None, interacted_at=None, subject=None,
        description=None, attachments=[], organization_id=None, todos=[]
    ):
        self.contact_id = contact_id
        self.company_id = company_id
        self.is_individual = is_individual

        self.type = type
        self.interacted_at = interacted_at
        
        self.subject = subject
        self.description = description
        self.attachments = attachments or []
        
        self.organization_id = organization_id
        
        self.todos = todos or []

    @classmethod
    def register(cls, data: dict=None):
        if not data:
            raise Exception('ContactInteraction.register() requires an argument for `data`')

        # validations
        required_fields = ['type', 'interacted_at', 'subject', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"`{field}` is a required field"
        
        # using short-circuit logic to evaluate the next few lines for performance
        is_individual = True 
        
        if not data.get('contact_id') and not data.get('company_id'):
            return False, "One of `contact_id` or `company_id` is required"
        if data.get('company_id'):
            is_individual = False

        data['is_individual'] = is_individual
        
        contact = None 
        if is_individual:
            contact = db.session.query(ContactUsers).filter_by(
                id=data.get('contact_id'),
                organization_id=data.get('organization_id')
            ).one_or_none()
        else:
            contact = db.session.query(ContactCompanies).filter_by(
                id=data.get('company_id'),
                organization_id=data.get('organization_id')
            ).one_or_none()
        if not contact:
            return False, "This contact does not exist"

        interaction = cls(**data)
        contact.interactions.append(interaction)
        
        db.session.add_all([interaction, contact])
        db.session.flush()
        db.session.commit()

        return True, interaction
