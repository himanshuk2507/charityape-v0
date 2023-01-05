from operator import and_, or_

from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db
from src.contacts.volunteering.models import VolunteerActivity
from src.library.base_helpers.date_manipulation import hours_between_dates
from src.library.utility_classes.mutable_list import MutableList


class Campaign(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'Campaign'

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    fundraising_goal = db.Column(db.Integer, nullable=True)
    followers = db.Column(MutableList.as_mutable(ARRAY(UUID(as_uuid=True))), nullable=False)
    status = db.Column(db.String(20), nullable=False)

    archived = db.Column(db.Boolean, nullable=False, default=False)

    p2ps = db.relationship('P2P', backref='Campaign', lazy=True, cascade="all,delete")
    pledges = db.relationship('Pledge', backref='Campaign', lazy=True, cascade="all,delete")
    elements = db.relationship('Element', backref='Campaign', lazy=True, cascade="all,delete")
    mailblasts = db.relationship('MailBlast', backref='Campaign', lazy=True, cascade="all,delete")
    one_time_transactions = db.relationship('OneTimeTransaction', backref='Campaign', lazy=True, cascade="all,delete")
    recurring_transactions = db.relationship('RecurringTransaction', backref='Campaign', lazy=True, cascade="all,delete")


    def __init__(
        self, name=None, description=None,
        fundraising_goal=None, followers=[],
        status='active', archived=False,
        organization_id=None
    ):
        self.name = name
        self.description = description
        self.fundraising_goal = fundraising_goal
        self.followers = followers or []
        self.status = status
        self.archived = archived
        
        self.organization_id = organization_id
        
    
    @classmethod
    def register(cls, data: dict = None):
        if not data:
            raise Exception('Campaign.register() requires an argument for `data`')

        # validations
        required_fields = ['name', 'followers', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"

        try:
            # does campaign with this name already exist?
            campaign = cls.query.filter_by(
                name=data.get('name'),
                organization_id=data.get('organization_id')
            ).one_or_none()
            if campaign:
                return False, "A campaign is already registered with this name. Try again with a different name."

            campaign = Campaign(**data)
            db.session.add(campaign)
            db.session.flush()
            db.session.commit()
            
            return True, campaign
        except Exception as e:
            print(str(e))
            return False, str(e)
            

    def update(self, data: dict = None):
        if not data:
            raise Exception('Campaign.update() requires an argument for `data`')

        try:
            unallowed_fields = ['id', 'organization_id']
            for field in data.keys():
                if field not in unallowed_fields:
                    setattr(self, field, data.get(field))
                
            db.session.add(self)
            db.session.commit()

            return True, self
        except Exception as e:
            print(e)
            return False, str(e)


    def get_amount_raised(self):
        from src.donations.one_time_transactions.models import OneTimeTransaction
        from src.donations.recurring_transactions.models import RecurringTransaction

        return sum([
            amount[0] for amount in
            db.session.query(OneTimeTransaction.amount).filter(
                and_(
                    OneTimeTransaction.organization_id == self.organization_id,
                    OneTimeTransaction.campaign_id == self.id
                )
            ).all() + \
                db.session.query(RecurringTransaction.amount).filter(
                    and_(
                        RecurringTransaction.organization_id == self.organization_id,
                        RecurringTransaction.campaign_id == self.id
                    )
                ).all()
        ])

    
    def get_donations_amount(self):
        from src.donations.one_time_transactions.models import OneTimeTransaction
        from src.donations.recurring_transactions.models import RecurringTransaction

        return sum([
            amount[0] for amount in
            db.session.query(OneTimeTransaction.amount).filter(
                and_(
                    OneTimeTransaction.organization_id == self.organization_id,
                    and_(
                        OneTimeTransaction.campaign_id == self.id,
                        OneTimeTransaction.is_revenue == False
                    )
                )
            ).all() + \
                db.session.query(RecurringTransaction.amount).filter(
                    and_(
                        RecurringTransaction.organization_id == self.organization_id,
                        and_(
                            RecurringTransaction.campaign_id == self.id,
                            RecurringTransaction.is_revenue == False
                        )
                    )
                ).all()
        ])
    
    
    def get_revenue_amount(self):
        from src.donations.one_time_transactions.models import OneTimeTransaction
        from src.donations.recurring_transactions.models import RecurringTransaction

        return sum([
            amount[0] for amount in
            db.session.query(OneTimeTransaction.amount).filter(
                and_(
                    OneTimeTransaction.organization_id == self.organization_id,
                    and_(
                        OneTimeTransaction.campaign_id == self.id,
                        OneTimeTransaction.is_revenue == True
                    )
                )
            ).all() + \
                db.session.query(RecurringTransaction.amount).filter(
                    and_(
                        RecurringTransaction.organization_id == self.organization_id,
                        and_(
                            RecurringTransaction.campaign_id == self.id,
                            RecurringTransaction.is_revenue == True
                        )
                    )
                ).all()
        ])
    
    
    def get_volunteer_hours(self):
        volunteers = VolunteerActivity.query.filter(
                and_(
                    VolunteerActivity.organization_id == self.organization_id,
                    or_(
                        VolunteerActivity.company_id.in_(self.followers),
                        VolunteerActivity.contact_id.in_(self.followers),
                    )
                )
            ).all()
        
        return sum([abs(hours_between_dates(volunteer.end_at, volunteer.start_at)) for volunteer in volunteers])

    
    amount_raised = property(get_amount_raised)
    donations_amount = property(get_donations_amount)
    revenue_amount = property(get_revenue_amount)
    volunteer_hours = property(get_volunteer_hours)