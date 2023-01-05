from os import getcwd
from flask import request
from pathlib import Path
from types import NoneType

from src.app_config import Config

import rsa

from src.app_config import ModelMixin, OrganizationMixin, TransactionMixin, db
from src.campaigns.models import Campaign
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.donations.pledges.models import Pledge
from src.library.base_helpers.rsa_helpers import decrypt_rsa, stripe_secret_private_key, paypal_client_id_private_key, paypal_client_secret_private_key
from src.payment.stripe.stripe import Stripe
from src.profile.models import Admin
from src.profile.payment_settings.stripe.models import StripeSettings
from src.profile.payment_settings.paypal.models import PayPalSettings

from src.payment.paypal.paypal import PayPal


class OneTimeTransaction(ModelMixin, OrganizationMixin, TransactionMixin, db.Model):
    __tablename__ = 'OneTimeTransaction'

    date_received = db.Column(db.DateTime, nullable=False)


    def __init__(
        self, contact_id = None, company_id = None, amount: float = None,
        currency = 'usd', is_from_different_currency = False, date_received = None,
        type = None, payment_method = None, impact_area = None, source = None,
        soft_credit = None, keywords = [], dedication = None, notes = None,
        receipting_strategy = None, pledge_id = None, campaign_id = None,
        charge_processor = None, charge_receipt_url = None, charge_transaction_rfx = None,
        is_revenue = False,
        organization_id = None
    ):
        self.contact_id = contact_id
        self.company_id = company_id

        self.amount = amount
        self.currency = currency
        self.is_from_different_currency = is_from_different_currency
        self.date_received = date_received
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

        self.pledge_id = pledge_id
        self.campaign_id = campaign_id

        self.is_revenue = is_revenue
        
        self.organization_id = organization_id

    def charge_with_stripe(self, api_key: str = None, card_id: str = None):
        '''
        Creates the charge for this transaction using Stripe.\n
        :param `api_key` required
        :param `card_id` required
        '''
        if not api_key:
            # if this charge failed, delete the transaction object
            self.delete()
            raise Exception('`api_key` is required in OneTimeTransaction.charge_with_stripe()')
        if not card_id:
            # if this charge failed, delete the transaction object
            self.delete()
            raise Exception('`card_id` is required in OneTimeTransaction.charge_with_stripe()')

        if not self.company_id and not self.contact_id:
            # if this charge failed, delete the transaction object
            self.delete()
            raise Exception('Cannot make transaction because no contact has been specified')
        
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

        result_bool, charge_data = stripe.create_charge(
            card_id = card_id,
            amount = int(self.amount),
            currency = self.currency
        )

        if not result_bool:
            # if this charge failed, delete the transaction object
            self.delete()
            return False, charge_data

        charge = charge_data['charges']['data'][0]
        self.charge_transaction_rfx = charge['balance_transaction']
        self.charge_processor = 'stripe'
        self.charge_receipt_url = charge['receipt_url']

        db.session.add(self)
        db.session.flush()
        db.session.commit()

        return True, self

    
    def delete(self):
        try:
            organization_id = self.organization_id
            contact: ContactUsers = ContactUsers.fetch_by_id(id=self.contact_id, organization_id=organization_id) if self.contact_id else None
            company: ContactCompanies = ContactCompanies.fetch_by_id(id=self.company_id, organization_id=organization_id) if self.company_id else None
            pledge: Pledge = Pledge.fetch_by_id(id=self.pledge_id, organization_id=organization_id) if self.pledge_id else None
            campaign: Campaign = Campaign.fetch_by_id(id=self.campaign_id, organization_id=organization_id) if self.campaign_id else None

            if contact:
                contact.one_time_transactions.remove(self)
            if company:
                company.one_time_transactions.remove(self)
            if pledge:
                pledge.one_time_transactions.remove(self)
            if campaign:
                campaign.one_time_transactions.remove(self)

            self.delete_by_id(id=self.id, organization_id=self.organization_id)

            return True, None
        except Exception as e:
            print(e)
            return False, e


    def update(self, data: dict = None):
        if not data:
            raise Exception('OneTimeTransaction.update() requires an argument for `data`')

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
                new_contact.one_time_transactions.append(self)
                old_contact.one_time_transactions.remove(self)
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
                new_company.one_time_transactions.append(self)
                old_company.one_time_transactions.remove(self)
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
                new_campaign.one_time_transactions.append(self)
                old_campaign.one_time_transactions.remove(self)
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
                new_pledge.one_time_transactions.append(self)
                old_pledge.one_time_transactions.remove(self)
                db.session.add_all([pledge, new_pledge])

            return super().update(data=data)
        except Exception as e:
            print(e)
            return False, str(e)

    
    @classmethod
    def register(cls, data: dict = None):
        if not data:
            raise Exception('OneTimeTransaction.register() requires an argument for `data`')

        # validations
        required_fields = ['amount', 'date_received', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"
        card_id: str = data.get('card_id')
        if card_id:
            data.pop('card_id')

        organization_id = data.get('organization_id')

        contact = data.get('contact_id')
        company = data.get('company_id')
        pledge = data.get('pledge_id')
        campaign = data.get('campaign_id')
        source = data.get('source')

        if contact:
            contact: ContactUsers = ContactUsers.fetch_by_id(
                id=contact,
                organization_id=organization_id
            )
            if not contact:
                return False, 'No contact exists with this ID'
        if company:
            company: ContactCompanies = ContactCompanies.fetch_by_id(
                id=company,
                organization_id=organization_id
            )
            if not company:
                return False, 'No company exists with this ID'
        if campaign:
            campaign: Campaign = Campaign.fetch_by_id(
                id=campaign,
                organization_id=organization_id
            )
            if not campaign:
                return False, 'No campaign exists with this ID'
        if pledge:
            pledge: Pledge = Pledge.fetch_by_id(
                id=pledge,
                organization_id=organization_id
            )
            if not pledge:
                return False, 'No pledge exists with this ID'

        transaction = cls(**data)
        if not isinstance(contact, (str, NoneType)):
            contact.one_time_transactions.append(transaction)
        if not isinstance(company, (str, NoneType)):
            company.one_time_transactions.append(transaction)
        if not isinstance(pledge, (str, NoneType)):
            pledge.one_time_transactions.append(transaction)
        if not isinstance(campaign, (str, NoneType)):
            campaign.one_time_transactions.append(transaction)

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
                card_id=card_id,
                api_key=stripe_secret,
            )

        db.session.add(transaction)
        db.session.flush()
        db.session.commit()


        return True, transaction
    
    


class PayPalTransaction(ModelMixin, OrganizationMixin, TransactionMixin, db.Model):
    __tablename__ = 'PayPalTransaction'
    payment_link = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="CREATED")
    date_received = db.Column(db.DateTime, nullable=False)


    def __init__(
        self, contact_id = None, company_id = None, amount: float = None,
        currency = 'usd', is_from_different_currency = False, date_received = None,
        status = None, payment_link = None, type = None, payment_method = None, 
        impact_area = None, source = None, soft_credit = None, keywords = [], 
        dedication = None, notes = None, receipting_strategy = None, pledge_id = None, 
        campaign_id = None, charge_processor = None, charge_receipt_url = None, 
        charge_transaction_rfx = None, is_revenue = False, organization_id = None
    ):
        self.contact_id = contact_id
        self.company_id = company_id

        self.amount = amount
        self.currency = currency
        self.is_from_different_currency = is_from_different_currency
        self.date_received = date_received
        self.status = status
        self.payment_link = payment_link
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

        self.pledge_id = pledge_id
        self.campaign_id = campaign_id

        self.is_revenue = is_revenue
        
        self.organization_id = organization_id
    
    
    @classmethod
    def register(cls, data: dict = None, admin_id = None):
        if not data:
            raise Exception('PayPalTransaction.register() requires an argument for `data`')

        # validations
        required_fields = ['amount', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"
        card_id: str = data.get('card_id')
        if card_id:
            data.pop('card_id')

        organization_id = data.get('organization_id')

        contact = data.get('contact_id')
        company = data.get('company_id')
        pledge = data.get('pledge_id')
        campaign = data.get('campaign_id')
        source = data.get('source')

        if contact:
            contact: ContactUsers = ContactUsers.fetch_by_id(
                id=contact,
                organization_id=organization_id
            )
            if not contact:
                return False, 'No contact exists with this ID'
        if company:
            company: ContactCompanies = ContactCompanies.fetch_by_id(
                id=company,
                organization_id=organization_id
            )
            if not company:
                return False, 'No company exists with this ID'
        if campaign:
            campaign: Campaign = Campaign.fetch_by_id(
                id=campaign,
                organization_id=organization_id
            )
            if not campaign:
                return False, 'No campaign exists with this ID'
        if pledge:
            pledge: Pledge = Pledge.fetch_by_id(
                id=pledge,
                organization_id=organization_id
            )
            if not pledge:
                return False, 'No pledge exists with this ID'
        # print(organization_id)
        paypal_encrypt_data : PayPalSettings = PayPalSettings.query.filter_by(organization_id=organization_id, admin_id=admin_id).one_or_none()
        
        paypal_client_id_private = paypal_client_id_private_key(organization_id)
        paypal_client_secret_private = paypal_client_secret_private_key(organization_id)
        
        client_id = rsa.decrypt(paypal_encrypt_data.client_id_secret_key, paypal_client_id_private).decode()
        client_secret = rsa.decrypt(paypal_encrypt_data.client_secret_sec_key, paypal_client_secret_private).decode()
        
        paypal: PayPal = PayPal(
            client_id=client_id, 
            client_secret=client_secret, 
            base_url=Config.PAYPAL_BASE_URL
            )
        
        order_detail = dict(
            amount = int(data.get('amount')),
            name = 'donation',
            description = data.get('notes'),
            return_url = f"{request.base_url}/success",
            cancel_url = f"{request.base_url}/cancel"
        )
        result_bool, order = paypal.create_order(order_detail)
        if not result_bool:
            return False, order
        
        data['charge_transaction_rfx'] = order['id']
        data['charge_processor'] = 'paypal'
        data['payment_link'] = order['payment_links']
        data['date_received'] = order['create_time']
        
        
        transaction = cls(**data)
        

        admin: Admin = Admin.query.filter_by(
            organization_id = transaction.organization_id
        ).one_or_none()
            

        db.session.add(transaction)
        db.session.flush()
        db.session.commit()


        return True, transaction