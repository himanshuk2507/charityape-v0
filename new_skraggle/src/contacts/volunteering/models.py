from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers


class VolunteerActivity(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "VolunteerActivity"

    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactUsers.id'), nullable=True)
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactCompanies.id'), nullable=True)
    # is this 'contact' a ContactUser or ContactCompany
    is_individual = db.Column(db.Boolean, nullable=False, default=True)

    name = db.Column(db.String(255), nullable=False)

    start_at = db.Column(db.DateTime, nullable=True)
    end_at = db.Column(db.DateTime, nullable=True)

    description = db.Column(db.String(255), nullable=True)
    impact_area = db.Column(db.String(255), nullable=True)

    attachments = db.Column(ARRAY(db.String(255)), nullable=False, default=[])
    
    fee_currency = db.Column(db.String(6), nullable=True, default='usd')
    fee = db.Column(db.Integer, nullable=True)

    t_shirt_size = db.Column(db.String(5), nullable=True)

    def __init__(
        self, contact_id=None, company_id=None, is_individual=None, name=None,
        start_at=None, end_at=None, impact_area=None,
        description=None, attachments=[], organization_id=None,
        fee_currency = None, fee = None, t_shirt_size=None
    ):
        self.contact_id = contact_id
        self.company_id = company_id
        self.is_individual = is_individual

        self.name = name

        self.start_at = start_at
        self.end_at = end_at

        self.description = description
        self.impact_area = impact_area
        self.attachments = attachments

        self.fee = fee
        self.fee_currency = fee_currency
        self.t_shirt_size = t_shirt_size

        self.organization_id = organization_id

    @classmethod
    def regsiter(cls, data: dict):
        if not data:
            raise Exception('VolunteerActivity.register() requires an argument for `data`')

        # validations
        required_fields = ['name', 'organization_id']
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

        volunteer_activity = VolunteerActivity(**data)
        contact.volunteer_activity.append(volunteer_activity)

        db.session.add_all([volunteer_activity, contact])
        db.session.flush()
        db.session.commit()

        return True, volunteer_activity