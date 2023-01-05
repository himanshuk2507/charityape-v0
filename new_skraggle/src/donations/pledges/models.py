from datetime import datetime
from typing import List
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db
from src.campaigns.models import Campaign
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.library.utility_classes.mutable_list import MutableList


class PledgeInstallment(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'PledgeInstallment'

    pledge_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Pledge.id'), nullable=True)

    expected_at = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    amount_currency = db.Column(db.String(4), nullable=False)


    def __init__(
        self, pledge_id = None, expected_at: datetime = None,
        amount: int = None, amount_currency: str = None, organization_id = None
    ):
        self.pledge_id = pledge_id

        self.expected_at = expected_at
        self.amount = amount
        self.amount_currency = amount_currency

        self.organization_id = organization_id
    

class Pledge(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'Pledge'

    contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactUsers.id'), nullable=True)
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactCompanies.id'), nullable=True)
    campaign_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Campaign.id'), nullable=True)
    
    name = db.Column(db.String(255), nullable=False)
    
    amount = db.Column(db.Integer, nullable=False)
    amount_currency = db.Column(db.String(4), nullable=False, default='usd')

    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    type = db.Column(db.String(255), nullable=True)
    cancelled = db.Column(db.Boolean, nullable=False, default=False)

    attachments = db.Column(MutableList.as_mutable(ARRAY(db.String(255))), nullable=False, default=[])
    payment_interval = db.Column(db.String(255), nullable=True)
    impact_area = db.Column(UUID(as_uuid=True), db.ForeignKey('ImpactArea.id'), nullable=True)
    soft_credit = db.Column(UUID(as_uuid=True), nullable=True)
    source = db.Column(db.String(255), nullable=True)
    keywords = db.Column(MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=False, default=[])
    dedication = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    installments = db.relationship('PledgeInstallment', backref='Pledge', lazy=True, cascade='all,delete')
    one_time_transactions = db.relationship('OneTimeTransaction', backref='Pledge', lazy=True, cascade="all,delete")
    recurring_transactions = db.relationship('RecurringTransaction', backref='Pledge', lazy=True, cascade="all,delete")


    def __init__(
        self, contact_id = None, company_id = None, campaign_id = None, name: str = None, amount: int = None, amount_currency: str = None,
        start_date: datetime = None, end_date: datetime = None, type: str = None,
        attachments: List[str] = None, payment_interval: str = None, impact_area: str = None, soft_credit = None,
        source: str = None, keywords: List[str] = None, dedication: str = None, notes: str = None, 
        cancelled: bool = False, 
        organization_id = None,
    ):
        self.contact_id = contact_id
        self.company_id = company_id
        self.campaign_id = campaign_id
        
        self.name = name
        
        self.amount = amount
        self.amount_currency = amount_currency
        
        self.start_date = start_date
        self.end_date = end_date
        
        self.type = type
        self.cancelled = cancelled
        
        self.attachments = attachments
        self.payment_interval = payment_interval
        self.impact_area = impact_area
        self.soft_credit = soft_credit
        self.source = source
        self.keywords = keywords
        self.dedication = dedication
        self.notes = notes
        
        self.organization_id = organization_id


    def update(self, data: dict = None):
        try:
            old_contact: ContactUsers = ContactUsers.fetch_by_id(id=self.contact_id, organization_id=self.organization_id) if self.contact_id else None
            new_contact: ContactUsers = ContactUsers.fetch_by_id(id=data.get('contact_id')) if data.get('contact_id') else None
            
            old_company: ContactCompanies = ContactCompanies.fetch_by_id(id=self.company_id, organization_id=self.organization_id) if self.company_id else None
            new_company: ContactCompanies = ContactCompanies.fetch_by_id(id=data.get('company_id')) if data.get('company_id') else None
            
            old_campaign: Campaign = Campaign.fetch_by_id(id=self.campaign_id, organization_id=self.organization_id) if self.campaign_id else None
            new_campaign: Campaign = Campaign.fetch_by_id(id=data.get('campaign_id')) if data.get('campaign_id') else None

            # change contact
            if new_contact:
                if old_contact:
                    old_contact.pledges.remove(self)
                    db.session.add(old_contact)
                new_contact.pledges.append(self)
                db.session.add(new_contact)

            # change company
            if new_company:
                if old_company:
                    old_company.pledges.remove(self)
                    db.session.add(old_company)
                new_company.pledges.append(self)
                db.session.add(new_company)
            
            # change campaign
            if new_campaign:
                if old_campaign:
                    old_campaign.pledges.remove(self)
                    db.session.add(old_campaign)
                new_campaign.pledges.append(self)
                db.session.add(new_campaign)
            
            return super().update(data=data)
        except Exception as e:
            print(e)
            return False, str(e)


    @classmethod
    def register(cls, data: dict = None):
        if not data:
            raise Exception('Campaign.register() requires an argument for `data`')

        # validations
        required_fields = ['name', 'amount', 'amount_currency', 'start_date', 'end_date', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"
        
        contact = data.get('contact_id')
        company = data.get('company_id')
        campaign = data.get('campaign_id')
        installments = data.get('installments')
        
        for key in ['contact_id', 'company_id', 'campaign_id', 'installments']:
            if key in data.keys():
                data.pop(key)
        try:
            pledge = cls(**data)

            # does this contact user exist?
            if contact:
                contact: ContactUsers = ContactUsers.fetch_by_id(contact)
                if contact:
                    contact.pledges.append(pledge)
                    db.session.add(contact)
            if company:
                company: ContactCompanies = ContactCompanies.fetch_by_id(company)
                if company:
                    company.pledges.append(pledge)
                    db.session.add(company)

            # does this campaign exist?
            if campaign:
                campaign: Campaign = Campaign.fetch_by_id(campaign)
                if campaign:
                    campaign.pledges.append(pledge)
                    db.session.add(campaign)

            # create PledgeInstallments
            if installments and isinstance(installments, list):
                for installment in installments:
                    if 'amount_currency' not in installment:
                        installment['amount_currency'] = 'usd'
                    installment = PledgeInstallment(**installment, pledge_id=pledge.id, organization_id=pledge.organization_id)
                    pledge.installments.append(installment)
                    db.session.add(installment)

            db.session.add(pledge)
            db.session.flush()
            db.session.commit()

            return True, pledge
        except Exception as e:
            print(str(e))
            return False, str(e)