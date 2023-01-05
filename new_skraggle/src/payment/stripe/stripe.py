from operator import and_, or_
from typing import List, Tuple
import uuid

import stripe
from src.contacts.companies.models import ContactCompanies

from src.contacts.contact_users.models import ContactUsers

from .models import StripeInformation, AssociatedStripeCardInformation



class StripeRecurringTransactionResult:
     def __init__(
          self, subscription_id = None, product_id = None,
          plan_id = None, subscription_url = None,
     ):
          self.subscription_id = subscription_id,
          self.product_id = product_id,
          self.plan_id = plan_id
          self.subscription_url = subscription_url



class CreditCard:
     def __init__(
          self, card_number: int = None, cvc: int = None, 
          exp_month: str = None, exp_year: str = None
     ):
          if not card_number or not cvc or not exp_month or not exp_year:
               raise Exception('Required params missing in CreditCard()')
          self.card_number = card_number
          self.cvc = cvc 
          self.exp_month = exp_month
          self.exp_year = exp_year



class Stripe:
     '''
     Handles payments, transactions and subscriptions using Stripe.
     :param contact_id `The ID of the contact this transaction is for`
     '''
     def __init__(
          self, contact_id:uuid = None, organization_id = None,
          api_key: str = None
     ):
          if not contact_id or not organization_id or not api_key:
               raise Exception("`contact_id`, `api_key` and `organization_id` are required in Stripe()")
          
          self.contact_id = contact_id
          self.api_key = api_key
          self.organization_id = organization_id
          
          self.contact: ContactUsers = ContactUsers.fetch_by_id(contact_id, organization_id=self.organization_id)
          self.company: ContactCompanies = ContactCompanies.fetch_by_id(contact_id, organization_id=self.organization_id)

          if not self.contact and not self.company:
               raise Exception('No contact exists with this ID')

          self.contact_name = f'{self.contact.first_name} {self.contact.last_name}' if self.contact else self.company.name
          self.contact_email = self.contact.primary_email if self.contact else self.company.email

     @classmethod
     def get_all_saved_cards_for_organization(cls, organization_id = None) -> List[StripeInformation]:
          return StripeInformation.query.filter_by(
               organization_id = organization_id
          ).all()
     
     def get_all_saved_cards_for_contact(self) -> List[AssociatedStripeCardInformation]:
          customer = self.find_customer()
          if customer is None:
               return []
          return customer.associated_stripe_cards

     def remove_saved_card(self, id: str = None):
          if not id:
               raise Exception('`id` is required in Stripe.remove_saved_card()')
          card: AssociatedStripeCardInformation = AssociatedStripeCardInformation.query.filter_by(
               id = id,
               organization_id = self.organization_id
          ).one_or_none()
          if not card:
               return False, 'This card isn\'t saved'
          customer = self.find_customer()
          customer.associated_stripe_cards.remove(card)
          card.delete_by_id(
               id = card.id,
               organization_id = self.organization_id
          )
          return True, None
     
     @classmethod
     def calculate_amount(self, amount):
          '''
          Returns the given amount in hundredth denomination.\n
          E.g.\n
          ```
          amount = 100 # 100 USD
          print(Stripe.calculate_amount(100))
          # prints '10000'
          ```
          '''
          new_amt = int(float(amount) * 100)
          return new_amt

     def find_customer(self) -> StripeInformation:
          return StripeInformation.query.filter(
               and_(
                    or_(
                         StripeInformation.contact_id == self.contact_id,
                         StripeInformation.company_id == self.contact_id
                    ),
                    StripeInformation.organization_id == self.organization_id
               )
          ).one_or_none()
     
     def create_customer(self):
          '''
          Function to Create Customer on stripe and save the customer ID on skraggle
          for future use.
          '''
          try:
               stripe.api_key = self.api_key
               customer = self.find_customer()
               
               if customer:
                    return True, customer

               new_customer = stripe.Customer.create(
                    email=self.contact_email,
                    name=self.contact_name
               )
               
               # Get the data as dictionary and save it to the model
               body = dict(
                    organization_id = self.organization_id,
                    stripe_customer_id = new_customer.id,
                    contact_id = self.contact.id if self.contact else None,
                    company_id = self.company.id if self.company else None
               )
               
               return StripeInformation.register(body)
          except Exception as e:
               return False, e   
     
     def add_card_payment_method(self, card: CreditCard = None, as_default: bool = True):
          '''
          Adds a debit/credit card to a registered customer
          '''
          if not card:
               raise Exception('`card` is a required parameter in Stripe.add_card_payment_method()')

          stripe.api_key = self.api_key
          
          customer = self.find_customer()
          
          if not customer:
               return False, "This user is not registered as a Stripe customer"
          
          last4 = str(card.card_number)[-4:]
          card_already_saved = AssociatedStripeCardInformation.query.filter_by(
               last4=last4, stripe_information_id=customer.id
          ).one_or_none()
          if card_already_saved:
               return False, "This card has already been added"
          
          try:    
               # fetch the corresponding Stripe customer,
               # create a PaymentMethod of type 'card',
               # and associate this new card with the Stripe customer
               stripe_customer_ids = stripe.Customer.list(email=self.contact_email, limit=1)
               if 'data' not in stripe_customer_ids or len(stripe_customer_ids['data']) == 0:
                    return False, 'Something went wrong'    
               stripe_customer_id = stripe_customer_ids["data"][0].get('id')
               if stripe_customer_id:
                    payment_method = stripe.PaymentMethod.create(
                         type="card",
                         card={
                              "number": str(card.card_number),
                              "exp_month": str(card.exp_month),
                              "exp_year": str(card.exp_year),
                              "cvc": str(card.cvc),
                         }
                    )

                    payment_id = payment_method.id
                    newcard = stripe.PaymentMethod.attach(
                         payment_id, customer=stripe_customer_id
                    )
                    
                    # Should this card should be used in future transactions as the default?
                    if as_default:
                         stripe.Customer.modify(
                              stripe_customer_id,
                              invoice_settings={"default_payment_method": payment_id},
                         )
                    
                    # Save the updated customer
                    body = dict(
                         stripe_customer_id = stripe_customer_id,
                         organization_id = self.organization_id,
                         stripe_information_id = customer.id,
                         card_id = payment_id,
                         card_brand = newcard['card']['brand'] if newcard.get('card') and newcard.get('card').get('brand') else None,
                         last4 = int(last4)
                    )
               
                    _, associated_stripe_card = AssociatedStripeCardInformation.register(body)
                    customer.associated_stripe_cards.append(associated_stripe_card)
                    return True, associated_stripe_card
          except Exception as e:
               return False, e   
     
     def create_charge(self, card_id: str = None, amount: float = None, currency: str = 'usd'):
          '''
          Create charge and make payment with the default card set on stripe 
          '''
          try:
               if not card_id or not amount or not currency:
                    raise Exception('`card_id`, `amount` and `currency` are required in Stripe.create_charge()')
                    
               stripe.api_key = self.api_key
               
               customer = self.find_customer()
               if not customer:
                    return False, 'The provided contact ID is invalid'
               
               converted_amt = Stripe.calculate_amount(amount)
                    
               charge = stripe.PaymentIntent.create(
                    amount=converted_amt,
                    currency=currency,
                    payment_method_types=['card'],
                    customer=customer.stripe_customer_id,
                    payment_method=card_id,
                    confirm=True
               )
               return True, charge
          except Exception as e:
               print(e)
               return False, e
     
     def create_recurring(
          self, product_name = None, interval_count = None, 
          billing_cycle = None, amount = None, currency = 'usd'
     ) -> Tuple[bool, StripeRecurringTransactionResult | Exception] :
          '''
          Schedule recurring payment.
          '''  
          stripe.api_key = self.api_key
          
          try:
               recurring_product = stripe.Product.create(name=product_name)
               customer = self.find_customer()
               
               converted_amt = Stripe.calculate_amount(amount)
               pricing = stripe.Price.create(
                    unit_amount=converted_amt,
                    currency=currency,
                    recurring={
                         "interval_count": int(interval_count),
                         "interval": billing_cycle
                    },
                    product = recurring_product.get("id"),
               )
               subscription = stripe.Subscription.create(
                    customer=customer.stripe_customer_id,
                    items=[
                         {'price': pricing["id"] }
                    ]
               )
               
               subscription_dict = {}
               for item in list(subscription.items()):
                    subscription_dict[item[0]] = item[1]
               subscription_items = subscription_dict.get('items')

               data = StripeRecurringTransactionResult(
                    subscription_id = subscription.id,
                    product_id = recurring_product.get("id"),
                    plan_id = pricing.get("id"),
                    subscription_url = subscription_items.get('url') if subscription_items is not None else None
               )
               
               return True, data
          except Exception as e:
               print(e)
               return False, e
          
     
     def cancel_recurring(self, plan_id):
          '''
          Cancel recurring payment
          '''
          try:
               stripe.api_key = self.api_key
               customer = self.find_customer()
               subscription = stripe.Subscription.list(
                    customer=customer.stripe_customer_id,
                    price=plan_id,
                    limit=1,
               )

               if not subscription.get('data'):
                    return False, 'There are no current recurring payments with this plan ID'
               
               if len(subscription['data']) == 0:
                    return False, 'No recurring payments have been scheduled'

               subscription_id = subscription['data'][0]['id']
               deleted_subscription = stripe.Subscription.delete(subscription_id)
               
               return True, deleted_subscription
          except Exception as e:
               print(e)
               return False, e