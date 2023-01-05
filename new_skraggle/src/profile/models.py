from datetime import datetime, timedelta
from os import getcwd, path
from pathlib import Path
import rsa

from flask_security import UserMixin
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import ARRAY
from werkzeug.security import generate_password_hash

from run import send_mail_in_background
from src.app_config import Config, ModelMixin, OrganizationMixin, db
from src.library.base_helpers.model_to_dict import model_to_dict
from src.library.html_templates.admin_auth_flow_templates import OnAdminSignupTemplate, WelcomeToSkraggleMailTemplate
from src.library.utility_classes.custom_validator import Validator
from src.library.utility_classes.mutable_list import MutableList
from src.library.utility_classes.text_generator import TextGenerator
from src.profile.payment_settings.stripe.models import StripeSettings


class AccessTokenBlocklist(db.Model, ModelMixin):
    __tablename__ = "AccessTokenBlocklist"
    jti = db.Column(db.String(36), nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, jti, revoked_at=datetime.now()):
        self.jti = jti
        self.revoked_at = revoked_at


class Admin(UserMixin, ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "Admin"

    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(500))

    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    middle_name = db.Column(db.String(255))

    confirmed = db.Column(db.Boolean, default=False, nullable=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    
    last_generated_token = db.Column(db.String(255), default=None)
    token_generated_at = db.Column(db.DateTime, nullable=True)

    donor_kpis = db.Column(MutableList.as_mutable(ARRAY(db.String(255))), nullable=False, default=[])
    fundraising_kpis = db.Column(MutableList.as_mutable(ARRAY(db.String(255))), nullable=False, default=[])
    email_marketing_kpis = db.Column(MutableList.as_mutable(ARRAY(db.String(255))), nullable=False, default=[])

    monthly_donation_goal = db.Column(db.Float, nullable=True)
    quarterly_donation_goal = db.Column(db.Float, nullable=True)
    yearly_donation_goal = db.Column(db.Float, nullable=True)
    
    monthly_revenue_goal = db.Column(db.Float, nullable=True)
    quarterly_revenue_goal = db.Column(db.Float, nullable=True)
    yearly_revenue_goal = db.Column(db.Float, nullable=True)


    def __init__(
        self, email, password, first_name, last_name, 
        organization_id=None, middle_name=None, confirmed=None, 
        confirmed_at=None, last_generated_token=None, token_generated_at=None,
        donor_kpis=[], fundraising_kpis=[], email_marketing_kpis=[],
        monthly_donation_goal = None, quarterly_donation_goal = None, yearly_donation_goal = None,
        monthly_revenue_goal = None, quarterly_revenue_goal = None, yearly_revenue_goal = None,
    ):
        self.email = email.lower()
        self.password = password

        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        
        self.organization_id = organization_id
        
        self.confirmed = confirmed 
        self.confirmed_at = confirmed_at 
        self.last_generated_token = last_generated_token
        self.token_generated_at = token_generated_at

        self.donor_kpis = donor_kpis
        self.fundraising_kpis = fundraising_kpis
        self.email_marketing_kpis = email_marketing_kpis

        self.monthly_donation_goal = monthly_donation_goal
        self.quarterly_donation_goal = quarterly_donation_goal
        self.yearly_donation_goal = yearly_donation_goal
        
        self.monthly_revenue_goal = monthly_revenue_goal
        self.quarterly_revenue_goal = quarterly_revenue_goal
        self.yearly_revenue_goal = yearly_revenue_goal


    def is_stripe_configured(self):
        return self.get_stripe_settings() is not None


    def get_stripe_settings(self) -> StripeSettings:
        return StripeSettings.query.filter_by(
            admin_id = self.id,
            organization_id = self.organization_id
        ).one_or_none()


    @classmethod
    def register(cls, **kwargs):
        '''
        Register a new Admin.
        This is not the same as 'creating' a new Admin object.
        register() will typically be called by a signup route handler and will 
        orchestrate the entire registration flow: validating input, creating/saving Admin object and sending account confirmation email
        '''
        
        # validate input
        required_fields = ['first_name', 'last_name', 'email', 'password']
        for field in required_fields:
            if field not in kwargs:
                return False, f"`{field}` is a required field"

        if not Validator.is_email(kwargs.get('email')):
            return False, 'A valid email address must be provided'

        # does this Admin already exist?
        admin_exists = db.session.query(Admin.id).filter_by(email=kwargs.get('email')).one_or_none()

        if admin_exists:
            return False, "An account with this email address already exists"
        
        password = generate_password_hash(kwargs.get('password'), method="sha256")
        kwargs['password'] = password
        admin = Admin(**kwargs)

        db.session.add(admin)
        db.session.flush()
        db.session.commit()

        try:
            admin.send_verification_mail()
        except Exception as e:
            print(e)

        return True, "New Admin account created successfully. An OTP for verifying your email address has been sent to your mail"
    
    
    def send_verification_mail(self):
        '''
        Generates a new OTP token, updates the Admin object (self) and sends the OTP to the Admin via email
        '''
        otp = TextGenerator(length=6).otp()
        print(otp)

        self.last_generated_token = otp
        self.token_generated_at = datetime.now()
        db.session.commit()

        # send account verification mail asynchronously in separate worker
        mail_body = f'Use this OTP ({otp}) to verify your account. Valid for 10 minutes.'
        send_mail_in_background.delay(mail_options=dict(
            subject='[Important] Verify your new Skraggle account',
            recipients=[self.email],
            text=mail_body,
            html=OnAdminSignupTemplate().render(name=self.first_name, otp=otp)
        ))


    def confirm_account_with_otp(self, otp: str):
        '''
        Handles logic for validating a confirmation token and verifying an Admin account
        '''
        now = datetime.now()
        validity = timedelta(minutes=10)

        if self.last_generated_token == otp and now <= self.token_generated_at + validity:
            # OTP is valid
            self.last_generated_token = None 
            self.token_generated_at = None
            self.confirm_account()
            return True

        return False


    def confirm_account(self):
        '''
        Simply updates the `Admin::confirmed` field to `True` and saves the current time to `Admin::confirmed_at`.
        This is meant to be called after a check (e.g after verifying that an OTP is valid).
        '''
        self.confirmed = True 
        self.confirmed_at = datetime.now()

        db.session.flush()
        db.session.commit()

        mail_body = f'Hi, {self.first_name}. Welcome to Skraggle'
        send_mail_in_background.delay(mail_options=dict(
            subject='Welcome to Skraggle',
            recipients=[self.email],
            text=mail_body,
            html=WelcomeToSkraggleMailTemplate().render(name=self.first_name)
        ))


    @classmethod
    def fetch_one_by_email(cls, email: str):
        '''
        Find an Admin that has this email and return the result or `None` if no match is found
        '''
        return cls.query.filter_by(email=email).one_or_none()
    
    
    @classmethod
    def fetch_one_by_id(cls, id, org_id = None):
        '''
        Find an Admin that has this ID and return the result or `None` if no match is found
        '''
        query = cls.query.filter_by(id=id)
        if org_id:
            query = query.filter_by(organization_id=org_id)
        return query.one_or_none()

    
    def create_access_token(self):
        '''
        Creates and returns an `access_token` for the Admin
        '''
        # access token will expire in 2 days in non-production environments
        validity = timedelta(days=2)
        if Config.RELEASE_LEVEL == 'production':
            validity = timedelta(hours=2)

        return create_access_token(
            identity=self.id,
            expires_delta=validity,
            additional_claims=dict(
                id=self.id,
                email=self.email,
                org=self.organization_id,
            )
        )


    def create_refresh_token(self):
        '''
        Creates and returns a `refresh_token` for the Admin
        '''
        return create_refresh_token(
            identity=self.id,
            additional_claims=dict(
                id=self.id,
                email=self.email,
                org=self.organization_id,
            )
        )


    def change_password(self, new_password=None):
        '''
        Handles logic for changing the Admin password
        '''
        try:
            new_password = new_password or TextGenerator(
                length=12
            ).random_string(
                selection=TextGenerator.password_level_string()
            )
            self.password = generate_password_hash(new_password)
            db.session.commit()

            return True, new_password
        except Exception as e:
            print(e)
            return False, str(e)


    def get_authorization_details(self):
        return dict(
        access_token=self.create_access_token(),
        refresh_token=self.create_refresh_token(),
        profile=model_to_dict(self)
    )


    authorization_details = property(get_authorization_details)