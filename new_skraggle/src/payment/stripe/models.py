from src.app_config import ModelMixin, OrganizationMixin, db
from sqlalchemy.sql import func
from src.library.utility_classes.mutable_list import MutableList
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY, JSONB
from src.library.utility_classes.custom_validator import Validator


class AssociatedStripeCardInformation(ModelMixin, OrganizationMixin, db.Model):
     __tablename__ = "AssociatedStripeCardInformation"
     stripe_information_id = db.Column(UUID(as_uuid=True), db.ForeignKey('StripeInformation.id'), nullable=True)
     stripe_customer_id = db.Column(db.String(255), nullable=True)
     card_id = db.Column(db.String(255), nullable=True)
     card_brand = db.Column(db.String(30), nullable=True)
     last4 = db.Column(db.Integer, nullable=True)
     
     def __init__(
               self, stripe_customer_id, stripe_information_id, card_id, 
               card_brand, last4, 
               organization_id=None
          ):
          self.stripe_customer_id = stripe_customer_id,
          self.stripe_information_id = stripe_information_id
          self.card_id = card_id
          self.card_brand = card_brand
          self.last4 = last4
          self.organization_id = organization_id
     
     
     @classmethod
     def register(cls, data: dict):
          if not data:
               raise Exception('StripeCardInformation.register() requires an argument for `data`')

          require_data = ['organization_id']
          for field in require_data:
               if field not in data.keys():
                    return False, f"`{field}` is a required field"
          
          stripe = cls(**data)
          db.session.add(stripe)
          db.session.flush()
          db.session.commit()
          
          return True, stripe
                
     
class StripeInformation(ModelMixin, OrganizationMixin, db.Model):
     __tablename__ = "StripeInformation"
     contact_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactUsers.id'), nullable=True)
     company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ContactCompanies.id'), nullable=True)
     stripe_customer_id = db.Column(db.String(255), nullable=True)

     associated_stripe_cards = db.relationship('AssociatedStripeCardInformation', backref='StripeInformation', lazy=True, cascade="all,delete")
     
     def __init__(self, is_company = False, stripe_customer_id = None, organization_id = None, contact_id=None, company_id = None):
          self.contact_id = contact_id
          self.company_id = company_id
          self.stripe_customer_id = stripe_customer_id

          self.organization_id = organization_id
          
     @classmethod
     def register(cls, data: dict):
          if not data:
               raise Exception('StripeInformation.register() requires an argument for `data`')
          
          require_data = ['stripe_customer_id', 'organization_id']
          for field in require_data:
               if field not in data.keys():
                    return False, f"`{field}` is a required field"
          
          stripe = cls(**data)

          db.session.add(stripe)
          db.session.flush()
          db.session.commit()
          
          return True, stripe