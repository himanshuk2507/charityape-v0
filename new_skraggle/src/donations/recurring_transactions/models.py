from datetime import datetime
from flask import request
from os import getcwd
from pathlib import Path

import rsa

from src.app_config import ModelMixin, OrganizationMixin, TransactionMixin, db
from src.campaigns.models import Campaign
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.donations.pledges.models import Pledge
from src.donations.sources.models import DonationSource
from src.library.base_helpers.rsa_helpers import decrypt_rsa, stripe_secret_private_key, paypal_client_id_private_key, paypal_client_secret_private_key
from src.payment.stripe.stripe import Stripe
from src.profile.models import Admin
from src.profile.payment_settings.stripe.models import StripeSettings
from src.profile.payment_settings.paypal.models import PayPalSettings

from src.app_config import Config
from src.payment.paypal.paypal import PayPal


class RecurringTransaction(ModelMixin, OrganizationMixin, TransactionMixin, db.Model):
    __tablename__ = 'RecurringTransaction'

    billing_cycle = db.Column(db.String(20), nullable=True)
    billing_interval = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    stripe_product_name = db.Column(db.String(255), nullable=True)
    stripe_recurring_plan_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_url = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    stripe_product_id = db.Column(db.String(255), nullable=True)


    def __init__(
        self, contact_id = None, company_id = None, amount: float = None,
        currency = 'usd', is_from_different_currency = False,
        type = None, payment_method = None, impact_area = None, source = None,
        soft_credit = None, keywords = [], dedication = None, notes = None,
        receipting_strategy = None, pledge_id = None, campaign_id = None,
        charge_processor = None, charge_receipt_url = None, charge_transaction_rfx = None,
        billing_cycle = None, billing_interval = None, is_active = True,
        stripe_product_name = None, stripe_recurring_plan_id = None, 
        stripe_subscription_url = None, stripe_subscription_id = None, stripe_product_id = None,
        is_revenue = False,
        organization_id = None
    ):
        self.contact_id = contact_id
        self.company_id = company_id

        self.amount = amount
        self.currency = currency
        self.is_from_different_currency = is_from_different_currency
        self.type = type
        self.payment_method = payment_method

        self.impact_area = impact_area
        self.source = source
        self.soft_credit = soft_credit
        self.keywords = keywords
        self.dedication = dedication
        self.notes = notes
        self.receipting_strategy = receipting_strategy

        self.charge_processor = charge_processor
        self.charge_receipt_url = charge_receipt_url
        self.charge_transaction_rfx = charge_transaction_rfx

        self.billing_cycle = billing_cycle
        self.billing_interval = billing_interval
        self.is_active = is_active
        self.stripe_product_name = stripe_product_name
        self.stripe_recurring_plan_id = stripe_recurring_plan_id

        self.pledge_id = pledge_id
        self.campaign_id = campaign_id

        self.stripe_subscription_url = stripe_subscription_url
        self.stripe_subscription_id = stripe_subscription_id
        self.stripe_product_id = stripe_product_id

        self.is_revenue = is_revenue
        
        self.organization_id = organization_id


    @classmethod
    def register(cls, data: dict = None):
        if not data:
            raise Exception('RecurringTransaction.register() requires an argument for `data`')

        # validations
        required_fields = ['amount', 'billing_cycle', 'billing_interval', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"

        organization_id = data.get('organization_id')
        transaction = cls(**data)

        contact = data.get('contact_id')
        company = data.get('company_id')
        pledge = data.get('pledge_id')
        campaign = data.get('campaign_id')

        if contact:
            contact: ContactUsers = ContactUsers.fetch_by_id(
                id=contact,
                organization_id=organization_id
            )
            if not contact:
                return False, 'No contact exists with this ID'
            contact.recurring_transactions.append(transaction)
        if company:
            company: ContactCompanies = ContactCompanies.fetch_by_id(
                id=company,
                organization_id=organization_id
            )
            if not company:
                return False, 'No company exists with this ID'
            company.recurring_transactions.append(transaction)
        if campaign:
            campaign: Campaign = Campaign.fetch_by_id(
                id=campaign,
                organization_id=organization_id
            )
            if not campaign:
                return False, 'No campaign exists with this ID'
            campaign.recurring_transactions.append(transaction)
        if pledge:
            pledge: Pledge = Pledge.fetch_by_id(
                id=pledge,
                organization_id=organization_id
            )
            if not pledge:
                return False, 'No pledge exists with this ID'
            pledge.recurring_transactions.append(transaction)

        admin: Admin = Admin.query.filter_by(
            organization_id = transaction.organization_id
        ).one_or_none()
        
        if transaction.payment_method == 'online_with_stripe':
            stripe_settings: StripeSettings = admin.get_stripe_settings()
            if not stripe_settings:
                db.session.rollback()
                return False, 'Connect your Stripe account first to continue'

            private_key = stripe_secret_private_key(organization_id)
            if private_key is None:
                return False, 'Connect your Stripe account first to continue'

            stripe_secret = stripe_secret = decrypt_rsa(
                stripe_settings.secret_key,
                private_key
            )

            return transaction.charge_with_stripe(
                api_key=stripe_secret,
            )

        db.session.add(transaction)
        db.session.flush()
        db.session.commit()

        return True, transaction


    def charge_with_stripe(self, api_key: str = None):
        '''
        Creates the charge for this transaction using Stripe.\n
        :param `api_key` required
        :param `card_id` required
        '''
        if not api_key:
            # if this charge failed, delete the transaction object
            self.delete()
            raise Exception('`api_key` is required in RecurringTransaction().charge_with_stripe()')

        if not self.company_id and not self.contact_id:
            # if this charge failed, delete the transaction object
            self.delete()
            raise Exception('Cannot create transaction because no contact has been specified')
        
        if not self.billing_cycle or not self.billing_interval:
            self.delete()
            raise Exception('Cannot create transaction because billing cycle has not been set')

        if not self.is_active:
            self.delete()
            raise Exception('Cannot create transaction because transaction is marked as `paused`')
        
        stripe: Stripe = Stripe(
            api_key=api_key,
            contact_id=self.contact_id or self.company_id,
            organization_id=self.organization_id
        )

        # fetch the corresponding Stripe customer or create one if there is none
        customer_fetched, stripe_customer_data = stripe.create_customer()
        if not customer_fetched:
            # if this charge failed, delete the transaction object
            self.delete()
            return False, stripe_customer_data

        # does this customer have an attached card?
        if len(stripe_customer_data.associated_stripe_cards) == 0:
            self.delete()
            return False, 'Cannot create transaction because this contact has no saved cards. Add a credit/debit card and try again.'

        source: str = DonationSource.fetch_by_id(
            id=self.source,
            organization_id=self.organization_id
        ).name if self.source else None
        now = datetime.now().strftime('%Y-%m-%d')
        product_name = f'Recurring donation by {stripe.contact_name} for source: {source} at {now}'
        
        result_bool, subscription_data = stripe.create_recurring(
            product_name=self.stripe_product_name or product_name,
            interval_count=self.billing_interval,
            billing_cycle=self.billing_cycle,
            amount = int(self.amount),
            currency = self.currency
        )

        if not result_bool:
            # if this charge failed, delete the transaction object
            self.delete()
            return False, subscription_data

        self.stripe_product_name = product_name
        self.stripe_recurring_plan_id = subscription_data.plan_id
        self.stripe_subscription_url = subscription_data.subscription_url

        db.session.add(self)
        db.session.commit()

        return True, self


    def update(self, data: dict = None, api_key: str = None):
        if not data:
            raise Exception('RecurringTransaction.update() requires an argument for `data`')

        try:
            organization_id = data.get('organization_id')

            contact: ContactUsers = data.get('contact_id')
            company: ContactCompanies = data.get('company_id')
            pledge: Pledge = data.get('pledge_id')
            campaign: Campaign = data.get('campaign_id')

            if contact:
                new_contact: ContactUsers = ContactUsers.fetch_by_id(
                    id=contact,
                    organization_id=organization_id
                )
                old_contact: ContactUsers = ContactUsers.fetch_by_id(
                    id=self.contact_id,
                    organization_id=organization_id
                )
                if not new_contact:
                    return False, 'No contact exists with this ID'
                new_contact.recurring_transactions.append(self)
                old_contact.recurring_transactions.remove(self)
                db.session.add_all([old_contact, new_contact])
            if company:
                new_company: ContactCompanies = ContactCompanies.fetch_by_id(
                    id=company,
                    organization_id=organization_id
                )
                old_company = ContactCompanies = ContactCompanies.fetch_by_id(
                    id=company,
                    organization_id=organization_id
                )
                if not new_company:
                    return False, 'No company exists with this ID'
                new_company.recurring_transactions.append(self)
                old_company.recurring_transactions.remove(self)
                db.session.add_all([old_company, new_company])
            if campaign:
                new_campaign: Campaign = Campaign.fetch_by_id(
                    id=campaign,
                    organization_id=organization_id
                )
                old_campaign: Campaign = Campaign.fetch_by_id(
                    id=campaign,
                    organization_id=organization_id
                )
                if not new_campaign:
                    return False, 'No campaign exists with this ID'
                new_campaign.recurring_transactions.append(self)
                old_campaign.recurring_transactions.remove(self)
                db.session.add_all([old_campaign, new_campaign])
            if pledge:
                new_pledge: Pledge = Pledge.fetch_by_id(
                    id=pledge,
                    organization_id=organization_id
                )
                old_pledge= Pledge.fetch_by_id(
                    id=pledge,
                    organization_id=organization_id
                )
                if not pledge:
                    return False, 'No pledge exists with this ID'
                new_pledge.recurring_transactions.append(self)
                old_pledge.recurring_transactions.remove(self)
                db.session.add_all([pledge, new_pledge])

            result_bool, result_data = super().update(data=data)
            
            if self.payment_method == 'online_with_stripe':
                self.cancel_stripe_charge(api_key=api_key)
                self.charge_with_stripe(api_key=api_key)

            return result_bool, result_data
        except Exception as e:
            print(e)
            return False, str(e)

        
    def cancel_stripe_charge(self, api_key: str = None):
        stripe: Stripe = Stripe(
            api_key=api_key,
            contact_id=self.contact_id or self.company_id,
            organization_id=self.organization_id
        )
        return stripe.cancel_recurring(
            self.stripe_recurring_plan_id
        )


    def delete(self, api_key = None):
        # save this before removing associations so that it can be used 
        # to cancel any subscriptions
        contact_id = self.contact_id or self.company_id
        try:
            organization_id = self.organization_id
            contact: ContactUsers = ContactUsers.fetch_by_id(id=self.contact_id, organization_id=organization_id) if self.contact_id else None
            company: ContactCompanies = ContactCompanies.fetch_by_id(id=self.company_id, organization_id=organization_id) if self.company_id else None
            pledge: Pledge = Pledge.fetch_by_id(id=self.pledge_id, organization_id=organization_id) if self.pledge_id else None
            campaign: Campaign = Campaign.fetch_by_id(id=self.campaign_id, organization_id=organization_id) if self.campaign_id else None

            if contact:
                contact.recurring_transactions.remove(self)
            if company:
                company.recurring_transactions.remove(self)
            if pledge:
                pledge.recurring_transactions.remove(self)
            if campaign:
                campaign.recurring_transactions.remove(self)

            try:
                stripe: Stripe = Stripe(
                    api_key=api_key,
                    contact_id=contact_id,
                    organization_id=self.organization_id
                )
                stripe.cancel_recurring(
                    self.stripe_recurring_plan_id
                )
            except Exception as e:
                # fail silently because exceptions will most likely occurr due to a transaction
                # that does not have a Stripe subscription
                pass
            self.delete_by_id(id=self.id, organization_id=self.organization_id)

            return True, None
        except Exception as e:
            print(e)
            return False, e
        
        

class PayPalRecurringTransaction(ModelMixin, OrganizationMixin, TransactionMixin, db.Model):
     __tablename__ = 'PayPalRecurringTransaction'
     
     prod_id = db.Column(db.String(50), nullable=True)
     prod_name = db.Column(db.String(255), nullable=True)
     prod_desc = db.Column(db.Text, nullable=True)
     plan_id = db.Column(db.String(50), nullable=True)
     interval = db.Column(db.String(50), nullable=True)
     cycles = db.Column(db.String(50), nullable=True)
     currency = db.Column(db.String(50), nullable=True)
     subscription_id = db.Column(db.String(100), nullable=True)
     status = db.Column(db.String(50), default="PENDING")
     country_code = db.Column(db.String(10), nullable=True)
     start_date = db.Column(db.String(100), nullable=True)
     subscription_token = db.Column(db.String(50), nullable=True)
     approve_link = db.Column(db.Text, nullable=True)
     
     def __init__(
          self, contact_id = None, company_id = None, amount: float = None,
          currency = 'usd', is_from_different_currency = False,
          type = None, payment_method = None, impact_area = None, source = None,
          soft_credit = None, keywords = [], dedication = None, notes = None,
          receipting_strategy = None, pledge_id = None, campaign_id = None,
          charge_processor = None, charge_receipt_url = None, charge_transaction_rfx = None,
          prod_id = None, prod_name = None, prod_desc = None, subscription_token = None,
          plan_id = None, interval = None, cycles = None, subscription_id = None, approve_link = None,
          is_revenue = False, country_code = None, start_date = None,
          organization_id = None
          ):
          self.contact_id = contact_id
          self.company_id = company_id

          self.amount = amount
          self.currency = currency
          self.is_from_different_currency = is_from_different_currency
          self.type = type
          self.payment_method = payment_method

          self.impact_area = impact_area
          self.source = source
          self.soft_credit = soft_credit
          self.keywords = keywords
          self.dedication = dedication
          self.notes = notes
          self.receipting_strategy = receipting_strategy

          self.charge_processor = charge_processor
          self.charge_receipt_url = charge_receipt_url
          self.charge_transaction_rfx = charge_transaction_rfx
          
          self.prod_id = prod_id
          self.prod_name = prod_name
          self.prod_desc = prod_desc
          self.plan_id = plan_id
          self.interval = interval
          self.cycles = cycles
          self.currency = currency
          self.subscription_id = subscription_id
          self.subscription_token = subscription_token
          self.approve_link = approve_link
          
          self.pledge_id = pledge_id
          self.campaign_id = campaign_id
          
          self.is_revenue = is_revenue
          self.country_code = country_code
          
          self.start_date = start_date
        
          self.organization_id = organization_id
          
     
     @classmethod
     def register(cls, data:dict = None):
        if not data:
            raise Exception('PayPalRecurringTransaction.register() requires an argument for `data`')
        
        
        required_fields = ['amount', 'interval', 'cycles', 'country_code', 'prod_name', 'prod_desc', 'start_date', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"

        organization_id = data.get('organization_id')
        transaction = cls(**data)

        contact = data.get('contact_id')
        # company = data.get('company_id')
        pledge = data.get('pledge_id')
        campaign = data.get('campaign_id')
        
        # print(company)
        contact: ContactUsers = ContactUsers.fetch_by_id(id=contact,organization_id=organization_id)
        if not contact:
            return False, 'No contact exists with this ID'
        
        # company: ContactCompanies = ContactCompanies.fetch_by_id(id=company,organization_id=organization_id)
        
        # if not company:
        #     return False, 'No company exists with this ID'
        
        campaign: Campaign = Campaign.fetch_by_id(id=campaign,organization_id=organization_id)
        
        if not campaign:
            return False, 'No campaign exists with this ID'
        
        pledge: Pledge = Pledge.fetch_by_id(id=pledge,organization_id=organization_id)
        
        if not pledge:
            return False, 'No pledge exists with this ID'
        
        admin: Admin = Admin.query.filter_by(
            organization_id = transaction.organization_id
        ).one_or_none()
        
        paypal_encrypt_data : PayPalSettings = PayPalSettings.query.filter_by(organization_id=organization_id, admin_id=admin.id).one_or_none()
        
        paypal_client_id_private = paypal_client_id_private_key(organization_id)
        paypal_client_secret_private = paypal_client_secret_private_key(organization_id)
        
        client_id = rsa.decrypt(paypal_encrypt_data.client_id_secret_key, paypal_client_id_private).decode()
        client_secret = rsa.decrypt(paypal_encrypt_data.client_secret_sec_key, paypal_client_secret_private).decode()
        
        paypal: PayPal = PayPal(
            client_id=client_id, 
            client_secret=client_secret, 
            base_url=Config.PAYPAL_BASE_URL
            )
        
        prod_detail = dict(
            name = data.get('prod_name'),
            description = data.get('prod_desc'),
            category = "BUSINESS",
            image_url="https://example.com/gallary/images/663774737.jpg",
            home_url="https://example.com/catalog/663774737.jpg"
        )
        
        # Create Product
        product_bool, product_data = paypal.create_product(prod_detail)
        if product_bool:
            prod_id = product_data['id']
            
            plan_details = dict(
                product_id=prod_id,
                product_name=data.get('prod_name'),
                description=data.get('prod_desc'),
                interval=data.get('interval'),
                amount=data.get('amount'),
                currency=data.get('currency').upper(),
                setup_fee=data.get('amount'),
                percentage="0",
                cycles=data.get('cycles')
            )
            plan_bool, plan_data = paypal.create_plan(plan_details)
            if plan_bool:
                plan_id = plan_data['id']
                
                
                detail = dict(
                        plan_id=plan_id,
                        start_date=data.get('start_date'),
                        lastname=contact.last_name,
                        firstname=contact.first_name,
                        amount=data.get('amount'),
                        currency=data.get('currency').upper(),
                        email=contact.primary_email,
                        fullname=f"{contact.last_name} {contact.first_name}",
                        address_line_1=contact.address,
                        address_line_2="",
                        admin_area_1="",
                        admin_area_2="",
                        postal_code=contact.postal_code,
                        country_code=data.get('country_code'),
                        brand_name="Skraggle",
                        return_url=f"{request.base_url}/subscription/success",
                        cancel_url=f"{request.base_url}/subscription/cancle"
                )
                
                subcription_bool, subcription_data = paypal.create_subscription(detail)
                if subcription_bool:
                        data['prod_id'] = prod_id
                        data['plan_id'] = plan_id
                        data['subscription_id'] = subcription_data['id']
                        data['approve_link'] = subcription_data['approve_link']
                        data['subscription_token'] = subcription_data['approve_link'].split('=')[1]
                        transaction = cls(**data)
                        db.session.add(transaction)
                        db.session.flush()
                        db.session.commit()
                        
                        return True, transaction
                
                return True, subcription_data
            return True, plan_data
        return True, product_data