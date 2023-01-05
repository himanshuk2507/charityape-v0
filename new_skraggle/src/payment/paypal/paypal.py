from tkinter.tix import Tree
from requests import request
from json import dumps as json_dumps, loads as json_loads
from time import time
from requests.auth import HTTPBasicAuth

from src.library.utility_classes.custom_validator import Validator
          

class PayPal:
     '''
     Take Paypal merchant credentials that will be use to authenticate all the function
     '''
     def __init__(self, client_id:str = None, client_secret:str = None, base_url:str = None):
          '''
          Handles payments, transactions and subscriptions using PayPal.
          :param client_id `Merchant Client ID`\
          :param client_secret `Merchant Client Secret`
          :param base_url `PayPal Endpoint base URL`
          '''
          if not base_url or not client_id or not client_secret:
               raise Exception("`base_url`, `client_id` and `client_secret` are required in PayPal()")
          
          self.base_url = base_url
          self.client_id = client_id
          self.client_secret = client_secret
          self.order_url = f"{self.base_url}/v2/checkout/orders"
          self.product_url = f"{self.base_url}/v1/catalogs/products"
          self.plan_url = f"{self.base_url}/v1/billing/plans"
          self.subscription_url = f"{self.base_url}/v1/billing/subscriptions"
          self.authenticate = HTTPBasicAuth(self.client_id, self.client_secret)
     
     
     @classmethod
     def default_request_headers(cls):
          return {
               'Content-Type': 'application/json',
               'Prefer': 'return=representation'
          }
     
     def create_order(self, detail:dict = None):
          '''
          Create order.\n
          This take dictionary data of order details and use it to create order.          
          '''
          
          if not detail:
               raise Exception("`detail` of the order that need to be created is needed in PayPal.create_order()")
          
          
          required_fields = [
               'amount',
               'name',
               'description',
               'return_url',
               'cancel_url'
          ]
          
          for field in required_fields:
               if field not in detail.keys():
                    return False, f"`{field}` is a required field"
          
          try:
               detail['amount'] = float(detail['amount'])
          except (TypeError, ValueError):
               raise Exception("detail.amount must be a valid number")
          
          
          payload = json_dumps({
               "intent": "CAPTURE",
               "purchase_units": [
                    {
                         "items": [
                              {
                                   "name": str(detail.get('name')),
                                   "description": detail.get('description'),
                                   "quantity": "1",
                                   "unit_amount": {
                                   "currency_code": detail.get('currency', 'USD').upper(),
                                   "value": detail.get('amount')
                              }
                    }
                         ],
                         "amount": {
                              "currency_code": detail.get('currency', 'USD').upper(),
                              "value": detail.get('amount'),
                              "breakdown": {
                                   "item_total": {
                                        "currency_code": detail.get('currency', 'USD').upper(),
                                        "value": detail.get('amount')
                                   }
                              }
                         }
                    }
               ],
               "application_context": {
                    "return_url": detail.get('return_url'),
                    "cancel_url": detail.get('cancel_url')
               }
          })
          
          try:
               response = request("POST", self.order_url, auth=self.authenticate, headers=PayPal.default_request_headers(), data=payload)
               json_data = json_loads(response.text)
               purchase_unit = json_data.get('purchase_units')
               purchase_units = purchase_unit[0] if purchase_unit != None and isinstance(purchase_unit, list) and len(purchase_unit) > 0 else None
               purchase_amount = purchase_units.get('amount') if purchase_units is not None else None
               purchase_breakdown = purchase_amount.get('breakdown') if purchase_amount is not None else None
               item_total = purchase_breakdown.get('item_total') if purchase_breakdown is not None else None
               resp_data = dict(
                    id=json_data.get('id'),
                    intent=json_data.get('intent'),
                    status=json_data.get('status'),
                    reference_id=purchase_units.get('reference_id'),
                    amount=item_total.get('value', detail.get('amount')),
                    currency=item_total.get('currency_code'),
                    create_time=json_data.get('create_time'),
                    payment_links=json_data['links'][1]['href']
               )
               return True, resp_data
          except Exception as e:
               return False, str(e)
     
     
     def get_order(self, order_id:str = None):
          '''
          get_order take order id and return details of the order from PayPal platform
          '''
          if order_id is None:
               raise Exception('`order_id` is required in PayPal.get_order()')
          
          url = f"{self.order_url}/{order_id}"
          try:
               response = request("GET", url, auth=self.authenticate)
               return True, json_loads(response.text)
          except Exception as e:
               return False, str(e)

     
     def authorize_payment(self, order_id:str = None):
          '''
          Authorize Payment. \n
          This take the order id and use it to authorize the order payment.
          '''
          if order_id is None:
               raise Exception('`order_id` is required in PayPal.authorize_payment()')
          
          url = f"{self.order_url}/{order_id}/capture"


          try:
               response = request("POST", url, auth=self.authenticate, headers=PayPal.default_request_headers(), data="")
               json_data = json_loads(response.text)
               
               purchase_unit = json_data.get('purchase_units')
               purchase_units = purchase_unit[0] if purchase_unit != None and isinstance(purchase_unit, list) and len(purchase_unit) > 0 else None
               purchase_amount = purchase_units.get('amount') if purchase_units is not None else None
               purchase_breakdown = purchase_amount.get('breakdown') if purchase_amount is not None else None
               item_total = purchase_breakdown.get('item_total') if purchase_breakdown is not None else None
               resp_data = dict(
                    id=json_data.get('id'),
                    intent=json_data.get('intent'),
                    status=json_data.get('status'),
                    reference_id=purchase_units.get('reference_id'),
                    amount=item_total.get('value'),
                    currency=item_total.get('currency_code'),
                    create_time=json_data.get('create_time')
               )
               return True, resp_data
          except Exception as e:
               return False, str(e)
     
     
     def create_product(self, detail:dict = None):
          '''
          Create Product. \n
          Take a dictionary data with all the required field and use it to create a product on paypal
          '''
          
          if not detail:
               raise Exception('`detail` of the products that need to be created is needed in PayPal.create_product()')
          
          ts = int(time())
          required_fields = [
               'name',
               'description',
               'category',
               'image_url',
               'home_url'
          ]
          
          for field in required_fields:
               if field not in detail.keys():
                    return False, f"`{field}` is a required field"
          
          
          payload = json_dumps({
               "name": detail.get('name'),
               "type": "SERVICE",
               "id": ts,
               "description": detail.get('description'),
               "category": detail.get('category'),
               "image_url": detail.get('image_url'),
               "home_url": detail.get('home_url')
          })
          headers = {
               'Content-Type': 'application/json'
          }
          try:
               response = request("POST", self.product_url, auth=self.authenticate, headers=headers, data=payload)
               return True, json_loads(response.text)
          except Exception as e:
               return False, str(e)
     
     
     def update_product(self, product_id:str = None, path:str = None, value:str = None):
          '''
          Update product \n
          Take the `product_id` of the product to be updated. \n
          Take the path of the product to be updated. \n
          The value that will override the previous value.
          '''
          
          if not product_id or not path or not value:
               raise Exception('`product_id`, `path` and `value` is required to update a product in PayPal.update_product()')
          
          url = f"{self.product_url}/{product_id}"

          payload = json_dumps([
               {
                    "op": "replace",
                    "path": f"/{path}",
                    "value": value
               }
          ])
          headers = {
               'Content-Type': 'application/json'
          }
          try:
               response = request("PATCH", url, auth=self.authenticate, headers=headers, data=payload)
               if response.status_code == 204:
                    return True, None
               return False, json_loads(response.text)
          except Exception as e:
               return False, str(e)
     
     
     def create_plan(self, data:dict = None):
          '''
          Create Plan \n
          Creates a plan that defines pricing and billing cycle details for subscriptions.
          Take a dictionary of data required to create a plan
          '''
          
          if not data:
               raise Exception('`data` about the plan to be created is needed in PayPal.create_plan()')
          
          
          required_fields = [
               'product_id',
               'product_name',
               'description',
               'interval',
               'amount',
               'setup_fee',
               'percentage',
               'cycles'
          ]
          
          for field in required_fields:
               if field not in data.keys():
                    return False, f"`{field}` is a required field"
               
          try:
               data['amount'] = float(data['amount'])
          except (TypeError, ValueError):
               raise Exception("data.amount must be a valid number")

          payload = json_dumps({
               "product_id": data.get('product_id'),
               "name": data.get('product_name'),
               "description": data.get('description'),
               "status": "ACTIVE",
               "billing_cycles": [
                    {
                         "frequency": {
                              "interval_unit": data.get('interval'),
                              "interval_count": 1
                         },
                         "tenure_type": "REGULAR",
                         "sequence": 1,
                         "total_cycles": data.get('cycles'),
                         "pricing_scheme": {
                              "fixed_price": {
                                   "value": data.get('amount'),
                                   "currency_code": data.get('currency', 'USD').upper()
                              }
                         }
                    }
               ],
               "payment_preferences": {
                    "auto_bill_outstanding": True,
                    "setup_fee": {
                         "value": data.get('setup_fee'),
                         "currency_code": data.get('currency', 'USD').upper()
                    },
                    "setup_fee_failure_action": "CONTINUE",
                    "payment_failure_threshold": 3
               },
               "taxes": {
                    "percentage": data.get('percentage'),
                    "inclusive": False
               }
          })
          
          try:
               response = request("POST", self.plan_url, auth=self.authenticate, headers=PayPal.default_request_headers(), data=payload)
               return True, json_loads(response.text)
          except Exception as e:
               return False, str(e)
     
     
     def deactivate_plan(self, plan_id:str = None):
          '''
          Deactivate plan \n
          Take the plan id and use it to deactivate the plan and remove it from use.
          '''
          
          if plan_id is None:
               raise Exception("`plan_id` is required in PayPal.deactivate_plan()")
          
          url = f"{self.plan_url}/{plan_id}/deactivate"

          headers = {
               'Prefer': 'return=representation'
          }
          
          try:
               response = request("POST", url, auth=self.authenticate, headers=headers)
               if response.status_code == 204:
                    return True, None
               return False, json_loads(response.text)
          except Exception as e:
               return False, str(e)
     
     
     def activate_plan(self, plan_id:str = None):
          '''
          Activate plan \n
          Take the plan id to activate the plan and made it available for use with any subscriptions.
          '''
          
          if plan_id is None:
               raise Exception("`plan_id` is required in PayPal.activate_plan()")
          
          url = f"{self.plan_url}/{plan_id}/activate"

          headers = {
               'Prefer': 'return=representation',
          }

          response = request("POST", url, auth=self.authenticate, headers=headers)
          
          try:
               if response.status_code == 204:
                    return True, None
               return False, json_loads(response.text)
          except Exception as e:
               return False, str(e)
     
     
     def show_plan(self, plan_id:str = None):
          '''
          Show plan with a particular ID. \n
          It take the plan id and return all the detail related to the plan
          '''
          
          if plan_id is None:
               raise Exception("`plan_id` is required in PayPal.show_plan()")
          
          url = f"{self.plan_url}/{plan_id}"
          
          try:
               response = request("GET", url, auth=self.authenticate)
               return json_loads(response.text)
          except Exception as e:
               return False, str(e)
     
     
     def create_subscription(self, detail:dict = None):
          '''
          Create Subscription \n
          It take the data needed to create the subscription as a dictionary.
          '''
          
          if not detail:
               raise Exception('`detail` about the subscription to be created is needed in PayPal.create_subscription()')
          
          
          if not Validator.is_email(detail.get('email')):
               return False, "A valid email address is required"
          
          
          
          # Check the required fields
          required_fields = [
               'plan_id',
               'start_date',
               'lastname',
               'firstname',
               'amount',
               'email',
               'fullname',
               'address_line_1',
               'address_line_2',
               'admin_area_1',
               'admin_area_2',
               'postal_code',
               'country_code',
               'brand_name',
               'return_url',
               'cancel_url'
          ]
          
          for field in required_fields:
               if field not in detail.keys():
                    return False, f"`{field}` is a required field"
          
          try:
               detail['amount'] = float(detail['amount'])
          except (TypeError, ValueError):
               raise Exception("data.amount must be a valid number")
          
          payload = json_dumps({
               "plan_id": detail.get('plan_id'),
               "start_time": detail.get('start_date'),
               "shipping_amount": {
                    "currency_code": detail.get('currency', 'USD').upper(),
                    "value": detail.get('amount')
               },
               "subscriber": {
                    "name": {
                         "given_name": detail.get('lastname'),
                         "surname": detail.get('firstname')
                    },
                    "email_address": detail.get('email'),
                    "shipping_address": {
                         "name": {
                              "full_name": detail.get('fullname')
                         },
                         "address": {
                              "address_line_1": detail.get('address_line_1'),
                              "address_line_2": detail.get('address_line_2'),
                              "admin_area_2": detail.get('admin_area_1'),
                              "admin_area_1": detail.get('admin_area_2'),
                              "postal_code": detail.get('postal_code'),
                              "country_code": detail.get('country_code')
                         }
                    }
               },
               "application_context": {
                    "brand_name": detail.get('brand_name'),
                    "locale": "en-US",
                    "shipping_preference": "SET_PROVIDED_ADDRESS",
                    "user_action": "SUBSCRIBE_NOW",
                    "payment_method": {
                         "payer_selected": "PAYPAL",
                         "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                    },
                    "return_url": detail.get('return_url'),
                    "cancel_url": detail.get('cancel_url')
               }
          })
          try:
               response = request("POST", self.subscription_url, auth=self.authenticate, headers=PayPal.default_request_headers(), data=payload)
               json_data = json_loads(response.text)
               links = json_data['links'][0]
               resp_data = dict(
                    status=json_data.get('status'),
                    id=json_data.get('status'),
                    plan_id=json_data.get('plan_id'),
                    start_time=json_data.get('start_time'),
                    shipping_amount=json_data.get('shipping_amount'),
                    subscriber=json_data.get('subscriber'),
                    approve_link=links.get('href')
               )
               return True, resp_data
          except Exception as e:
               return False, str(e)
          
     
     def get_subscription(self, subscription_id:str = None):
          '''
          Return all the subscriptions details base on the subscription id on paypal.
          '''
          if not subscription_id:
               raise Exception("`subscription_id` is required in PayPal.get_subscription()")
          
          url = f"{self.subscription_url}/{subscription_id}"
          
          try:
               response = request("GET", url, auth=self.authenticate)
               return True, json_loads(response.text)
          except Exception as e:
               return False, str(e)
     
     
     def suspend_subscription(self, subscription_id:str = None, reason:str = None):
          '''
          Suspend subscription. \n 
          Take subscription id and reason for suspending the subscription
          '''
          
          if not subscription_id or not reason:
               raise Exception("`subscription_id` and `reason` is required in PayPal.suspend_subscription()")
          
          url = f"{self.subscription_url}/{subscription_id}/suspend"

          payload = json_dumps({
               "reason": reason
          })

          response = request("POST", url, auth=self.authenticate, headers=PayPal.default_request_headers(), data=payload)
          
          try:
               if response.status_code == 204:
                    return True, None
               return False, json_loads(response.text)
          except Exception as e:
               return False, str(e)
     
     
     def activate_subscription(self, subscription_id:str = None, reason:str = None):
          '''
          Activate subscription. \n
          Take subscription Id and reason for activating the subscription
          '''
          
          if not subscription_id or not reason:
               raise Exception("`subscription_id` and `reason` is required in PayPal.activate_subscription()")
          
          url = f"{self.subscription_url}/{subscription_id}/activate"

          payload = json_dumps({
               "reason": reason
          })
          headers = {
               'Content-Type': 'application/json'
          }
          
          try:
               response = request("POST", url, auth=self.authenticate, headers=headers, data=payload)

               if response.status_code == 204:
                    return True, None
               return False, json_loads(response.text)
          except Exception as e:
               return False, str(e)
     
     
     def cancle_subscription(self, subscription_id:str = None, reason:str = None):
          '''
          Cancle Subscription. It take subscription id and reason for termination
          '''
          if not subscription_id or not reason:
               raise Exception("`subscription_id` and `reason` is required in PayPal.cancle_subscription()")
          
          url = f"{self.subscription_url}/{subscription_id}/cancel"
          payload = json_dumps({
               "reason": reason
          })
          headers = {
               'Content-Type': 'application/json'
          }
          
          try:
               response = request("POST", url, auth=self.authenticate, headers=headers, data=payload)

               if response.status_code == 204:
                    return True, None
               return False, json_loads(response.text)
          except Exception as e:
               return False, str(e)
     
     
     def capture_authorized_payment(self, details:dict = None, subscription_id:str = None):
          '''
          Capture subscription for payment. It take subscription id and a dictionary of details to be sent to paypal
          '''
          
          if not subscription_id or not details:
               raise Exception("`subscription_id` and `details` is required to authorize captured payments in PayPal.capture_authorized_payment()")
          
          try:
               details['amount'] = float(details['amount'])
          except (TypeError, ValueError):
               raise Exception("details.amount must be a valid number")
          
          required_fields = [
               'note',
               'amount'
          ]
          
          for field in required_fields:
               if field not in details.keys():
                    return False, f"`{field}` is a required field"
               
          url = f"{self.subscription_url}/{subscription_id}/capture"
          payload = json_dumps({
               "note": details.get('note'),
               "capture_type": "OUTSTANDING_BALANCE",
               "amount": {
                    "currency_code": details.get('currency', 'USD').upper(),
                    "value": details.get('amount')
               }
          })
          try:
               response = request("POST", url, auth=self.authenticate, headers=PayPal.default_request_headers(), data=payload)
               return True, json_loads(response.text)
          except Exception as e:
               return False, str(e)
