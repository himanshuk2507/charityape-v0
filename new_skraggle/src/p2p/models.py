from datetime import datetime
from operator import and_
from typing import List
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from run import send_mail_in_background

from src.app_config import ModelMixin, OrganizationMixin, db
from src.campaigns.models import Campaign
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction
from src.library.base_helpers.date_manipulation import days_left_until, hours_left_until
from src.library.html_templates.p2p_templates import OnP2PCreatedTemplate
from src.library.utility_classes.custom_validator import Validator


class P2PEmail(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'P2PEmail'

    p2p_id = db.Column(UUID(as_uuid=True), db.ForeignKey('P2P.id'), nullable=True)
    
    subject = db.Column(db.String(255), nullable=False)
    recipients = db.Column(ARRAY(db.String(255)), nullable=False, default=[])

    def __init__(
        self, p2p_id = None, subject = None, recipients = [],
        organization_id = None
    ):
        self.p2p_id = p2p_id
        
        self.subject = subject
        self.recipients = recipients or []
        
        self.organization_id = organization_id


class P2P(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'P2P'

    campaign_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Campaign.id'), nullable=True)
    designation = db.Column(db.String(255), nullable=True)
    fundraiser_display_name = db.Column(db.String(255), nullable=True)
    
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.Text, nullable=True)

    goal = db.Column(db.Float, nullable=True)
    goal_currency = db.Column(db.String(5), nullable=True, default='usd')

    offline_amount = db.Column(db.Integer, nullable=True)
    offline_donation = db.Column(db.Integer, nullable=True)

    goal_date = db.Column(db.DateTime, nullable=True)

    personal_message = db.Column(db.Text, nullable=True)
    profile_photo = db.Column(db.String(255), nullable=True)
    display_photos = db.Column(ARRAY(db.String(255)), nullable=True, default=[])

    archived = db.Column(db.Boolean, nullable=False, default=False)
    paused = db.Column(db.Boolean, nullable=False, default=False)

    type = db.Column(db.String(255), nullable=True)

    sent_emails = db.relationship('P2PEmail', backref='P2P', lazy=True, cascade="all,delete")

    def __init__(
        self, campaign_id = None, designation = None,
        fundraiser_display_name = None, first_name = None, last_name = None,
        email = None, goal = None, goal_currency = None,
        offline_amount = None, offline_donation = None,
        goal_date = None, personal_message = None, profile_photo = None,
        display_photos = [], archived = False, paused = False, type: str = None,
        organization_id = None
    ):
        self.campaign_id = campaign_id
        self.designation = designation
        self.fundraiser_display_name = fundraiser_display_name
        
        self.first_name = first_name
        self.last_name = last_name
        self.email = email 
        
        self.goal = goal 
        self.goal_currency = goal_currency
        
        self.offline_amount = offline_amount
        self.offline_donation = offline_donation
        self.goal_date = goal_date
        
        self.personal_message = personal_message
        self.profile_photo = profile_photo
        self.display_photos = display_photos
        
        self.archived = archived
        self.paused = paused

        self.type = type
        
        self.organization_id = organization_id

    def update(self, data: dict = None):
        if not data:
            return False, 'No data was provided for update'

        if data.get('email') and not Validator.is_email(data.get('email')):
            return False, "`email` is not a valid email address"

        unallowed_fields = ['id', 'organization_id', 'campaign_id']

        for field in data.keys():
            if field not in unallowed_fields:
                setattr(self, field, data.get(field))
        
        db.session.add(self)
        db.session.commit()

        return True, self

    @classmethod
    def register(cls, data: dict = None):
        try:
            if not data:
                raise Exception('P2P.register() requires an argument for `data`')

            # validations 
            required_fields = ['organization_id']
            for field in required_fields:
                if field not in data.keys():
                    return False, f"`{field}` is a required field"
            if data.get('email') and not Validator.is_email(data.get('email')):
                return False, "A valid email address is required"

            campaign = data.get('campaign_id')    
            if campaign:
                campaign: Campaign = Campaign.fetch_by_id(id=campaign, organization_id=data.get('organization_id'))
                if not campaign:
                    return False, 'This campaign does not exist. Select a valid campaign and try again.'

                p2p: P2P = P2P(**data)
                campaign.p2ps.append(p2p)

                db.session.add_all([p2p, campaign])
                db.session.flush()
                db.session.commit()

                if p2p.goal and p2p.goal_date and p2p.goal_date > datetime.now():
                    days_left_string=days_left_until(p2p.goal_date)
                    if days_left_string > 1:
                        days_left_string = f'{days_left_string} days'
                    elif days_left_string == 1:
                        days_left_string = f'{days_left_string} day'
                    else:
                        days_left_string = hours_left_until(p2p.goal_date)
                        if days_left_string == 0:
                            days_left_string = 'a few minutes'
                        elif days_left_string == 1:
                            days_left_string = f'{days_left_string} hour'
                        else:
                            days_left_string = f'{days_left_string} hours'

                    p2p.send_email(dict(
                        html = OnP2PCreatedTemplate().render(
                            target_amount=p2p.goal,
                            amount_raised=p2p.amount_raised(),
                            target_date=datetime.strftime(p2p.goal_date, '%b %d, %Y'),
                            days_left_string=f'{days_left_string} left',
                        ),
                        text = 'New P2P created. This email template will be replaced after a better one is designed.',
                        recipients = [p2p.email],                       
                        subject = 'Your new fundraiser'
                    ))

                return True, p2p
        except Exception as e:
            print(e)
            return False, str(e)

    
    def amount_raised(self):
        if not self.campaign_id:
            return 0
        return sum([
            amount[0] for amount in
            db.session.query(OneTimeTransaction.amount).filter(
                and_(
                    OneTimeTransaction.organization_id == self.organization_id,
                    OneTimeTransaction.campaign_id == self.campaign_id
                )
            ).all() + \
                db.session.query(RecurringTransaction.amount).filter(
                    and_(
                        RecurringTransaction.organization_id == self.organization_id,
                        RecurringTransaction.campaign_id == self.campaign_id
                    )
                ).all()
        ])


    def get_donations_count(self):
        campaigns: List[Campaign] = Campaign.query.filter(
            and_(
                Campaign.organization_id == self.organization_id,
                Campaign.p2ps.contains(self),
            )
        ).all()
        donations = 0
        for campaign in campaigns:
            donations += len(
                OneTimeTransaction.query.filter_by(
                    organization_id = campaign.organization_id,
                    campaign_id = campaign.id,
                    is_revenue = False
                ).all() + \
                RecurringTransaction.query.filter_by(
                    organization_id = campaign.organization_id,
                    campaign_id = campaign.id,
                    is_revenue = False
                ).all()
            )
        return donations


    def send_email(self, data: dict = None):
        '''
        Send an email and make a log of the email for this P2P by creating a new P2PEmail entry.
        ```
        :param data: a dictionary containing the following fields:\n
            1. html: compiled HTML
            2. text: plain text to be rendered by the recipient's Mail client if it is unable to render the html
            3. recipients: a list of email addresses
            4. subject: the subject of this email
        ```
        '''
        required_fields = ['subject', 'recipients', 'html']
        for field in required_fields:
            if field not in data.keys():
                raise Exception(f"{field} is required in P2P.send_email()")

        email = P2PEmail(**{
            "subject": data.get('subject'),
            "recipients": data.get('recipients'),
            "p2p_id": self.id,
            "organization_id": self.organization_id
        })
        self.sent_emails.append(email)

        send_mail_in_background.delay(mail_options=data)

        db.session.add_all([email, self])
        db.session.flush()
        db.session.commit()

    
    donations_count = property(get_donations_count)