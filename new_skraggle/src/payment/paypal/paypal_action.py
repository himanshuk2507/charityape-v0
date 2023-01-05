from flask_jwt_extended import get_jwt
import rsa
from src.donations.one_time_transactions.models import OneTimeTransaction, PayPalTransaction
from src.donations.recurring_transactions.models import PayPalRecurringTransaction
from src.profile.payment_settings.paypal.models import PayPalSettings

from src.app_config import db
from src.app_config import Config

from src.payment.paypal.paypal import PayPal
from src.library.base_helpers.rsa_helpers import paypal_client_id_private_key, paypal_client_secret_private_key


class PayPalKeys:
     def __init__(self, organization_id = None):
          self.organization_id = organization_id
     
     def _paypal(self):
          paypal_client_id_private = paypal_client_id_private_key(self.organization_id)
          paypal_client_secret_private = paypal_client_secret_private_key(self.organization_id)
          
          paypal_encrypt_data : PayPalSettings = PayPalSettings.query.filter_by(
               organization_id=self.organization_id
               ).one_or_none()
        
          client_id = rsa.decrypt(paypal_encrypt_data.client_id_secret_key, paypal_client_id_private).decode()
          client_secret = rsa.decrypt(paypal_encrypt_data.client_secret_sec_key, paypal_client_secret_private).decode()
          paypal: PayPal = PayPal(
            client_id=client_id, 
            client_secret=client_secret,
            base_url=Config.PAYPAL_BASE_URL
            )
          return paypal
     

class ProcessPayPal:
     '''
     Class to check paypal payment and process the status coming from paypal
     '''
     def __init__(self, token: str = None, data:dict = None):
          self.token = token
          self.data = data
          if not self.token:
               raise Exception('`token` is needed to complete the process')
          
     
     def update_paypal_transaction(self):
          '''
          Verify transaction and check before awarding value.
          '''
          paypal_trnx: PayPalTransaction = PayPalTransaction.query.filter_by(
               charge_transaction_rfx=self.token).first()
          paypal = PayPalKeys(paypal_trnx.organization_id)._paypal()
          if not paypal:
               return False, "Not found"
          
          authorize_bool, authorize = self.paypal.authorize_payment(self.token)
          if authorize_bool and authorize['status'] == "COMPLETED":
               check_bool, check = self.paypal.get_order(self.token)
               if check_bool and check['status'] == "COMPLETED":
                    data = {}
                    data['organization_id'] = paypal.organization_id
                    data['contact_id'] = paypal.contact_id
                    data['company_id'] = paypal.company_id
                    data['amount'] = paypal.amount
                    data['currency'] = paypal.currency
                    data['is_from_different_currency'] = paypal.is_from_different_currency
                    data['date_received'] = paypal.date_received
                    data['type'] = paypal.type
                    data['payment_method'] = paypal.payment_method
                    data['source'] = paypal.source
                    data['keywords'] = paypal.keywords
                    data['dedication'] = paypal.dedication
                    data['notes'] = paypal.notes
                    data['receipting_strategy'] = paypal.receipting_strategy
                    data['pledge_id'] = paypal.pledge_id
                    data['campaign_id'] = paypal.campaign_id
                    data['charge_processor'] = paypal.charge_processor
                    data['charge_transaction_rfx'] = paypal.charge_transaction_rfx
                    data['is_revenue'] = paypal.is_revenue
                    data['impact_area'] = paypal.impact_area
                    
                    OneTimeTransaction.register(data)
                    
                    # Delete completed transaction from PayPal Transaction Table
                    db.session.delete(paypal)
                    db.session.commit()
                    
                    return True, "Payment completed"
               return False, check
          return False, authorize
     
     
     def update_paypal_subscription(self, ba_token):
          '''
          Verify transaction and check before awarding value.
          '''
          paypal_trnx: PayPalRecurringTransaction = PayPalRecurringTransaction.query.filter_by(subscription_token=ba_token).first()
          
          if not paypal_trnx:
               return False, "Invalid transaction id"
          
          paypal = PayPalKeys(paypal_trnx.organization_id)._paypal()
          check_bool, check_data = paypal.get_subscription(self.token)
          if check_bool:
               status = check_data['status']
               plan_id = check_data['plan_id']
               
               if paypal_trnx.status == status:
                    return False, "Subscription is active"
               
               paypal_trnx.status = status
               paypal.subscription_id = self.token
               db.session.commit()
               return True, "Subscription activated"
          
          return False, check_data
     
     def suspend_paypal_subscription(self):
          '''
          Suspend PayPal Subscription
          '''
          
          required_fields = ['reason']
          for fields in required_fields:
               if fields not in self.data.keys():
                    return False, f'`{fields}` is required' 
               
          paypal: PayPalRecurringTransaction = PayPalRecurringTransaction.query.filter_by(subscription_id=self.token).first()
          if not paypal:
               return False, "Invalid subscription ID"
          
          if paypal.status == "SUSPENDEND":
               return False, "Subscription already suspended"
          
          paypal_ = PayPalKeys(paypal.organization_id)._paypal() 
          check_bool, check_data = paypal_.suspend_subscription(self.token, self.data.get('reason'))
          if check_bool:
               paypal.status = "SUSPENDEND"
               db.session.commit()
               return True, "Subscription suspended"
          return False, check_data
     
     
     def activate_paypal_subscription(self):
          '''
          Activate PayPal Subscription
          '''
          required_fields = ['reason']
          for fields in required_fields:
               if fields not in self.data.keys():
                    return False, f'`{fields}` is required' 
               
          paypal: PayPalRecurringTransaction = PayPalRecurringTransaction.query.filter_by(subscription_id=self.token).first()
          if not paypal:
               return False, "Invalid subscription ID"
          
          if paypal.status == "ACTIVE":
               return False, "Subscription is active"
          
          paypal_ = PayPalKeys(paypal.organization_id)._paypal() 
          check_bool, check_data = paypal_.activate_subscription(self.token, self.data.get('reason'))
          if check_bool:
               paypal.status = "ACTIVE"
               db.session.commit()
               return True, "Subscription activated"
          return False, check_data
     
     
     def cancle_paypal_subscription(self):
          '''
          Cancle PayPal Subscription
          '''
          
          required_fields = ['reason']
          for fields in required_fields:
               if fields not in self.data.keys():
                    return False, f'`{fields}` is required' 
               
          paypal: PayPalRecurringTransaction = PayPalRecurringTransaction.query.filter_by(subscription_id=self.token).first()
          if not paypal:
               return False, "Invalid subscription ID"
          
          if paypal.status == "CANCEL":
               return False, "Subscription canceled"
          
          paypal_ = PayPalKeys(paypal.organization_id)._paypal() 
          
          check_bool, check_data =  paypal_.cancle_subscription(self.token, self.data.get('reason'))
          if check_bool:
               paypal.status = "CANCEL"
               db.session.commit()
               return True, "Subscription activated"
          return False, check_data
     
     
     
     
               
               