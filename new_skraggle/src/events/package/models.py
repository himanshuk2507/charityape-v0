from src.app_config import ModelMixin, OrganizationMixin, db
from sqlalchemy.sql import func
from src.library.utility_classes.mutable_list import MutableList
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY


class Packages(ModelMixin, OrganizationMixin, db.Model):
     __tablename__ = "Packages"
     name = db.Column(db.String(255), nullable=False)
     description = db.Column(db.String(255), nullable=False)
     private_package = db.Column(db.Boolean, nullable=False, default=False)
     is_enabled = db.Column(db.Boolean, default=True, nullable=True)
     price = db.Column(db.Integer, nullable=False)
     direct_cost = db.Column(db.Integer, nullable=False)
     number_of_packages_for_sale = db.Column(db.Integer, nullable=False)
     qty_purchase_limit = db.Column(db.Integer, nullable=False)
     early_bird_discount_enabled = db.Column(db.Boolean, nullable=False)
     early_bird_discount_amount = db.Column(db.Integer, nullable=True)
     early_bird_discount_cutoff_time = db.Column(db.DateTime, nullable=True)
     early_bird_discount_type = db.Column(db.String(50), nullable=True)
     participants = db.Column(db.Integer, nullable=True)
     pre_select_qty = db.Column(db.Integer, nullable=True)
     custom_event_field = db.Column(db.String(255), nullable=True)
     

     def __init__(self, name, description, price, direct_cost, 
          number_of_packages_for_sale, qty_purchase_limit,
          organization_id, early_bird_discount_enabled, 
          early_bird_discount_amount=None, 
          early_bird_discount_cutoff_time=None, 
          early_bird_discount_type=None, is_enabled=None, 
          participants=None, pre_select_qty=None,
          custom_event_field=None, private_package=None
          ):
          self.name = name
          self.description = description
          self.price = price
          self.direct_cost = direct_cost
          self.number_of_packages_for_sale = number_of_packages_for_sale
          self.qty_purchase_limit = qty_purchase_limit
          self.is_enabled = is_enabled
          self.organization_id = organization_id
          self.early_bird_discount_enabled = early_bird_discount_enabled
          self.early_bird_discount_amount = early_bird_discount_amount
          self.early_bird_discount_cutoff_time = early_bird_discount_cutoff_time
          self.early_bird_discount_type = early_bird_discount_type
          self.participants = participants
          self.pre_select_qty = pre_select_qty
          self.custom_event_field = custom_event_field
          self.private_package = private_package

     
     @classmethod
     def register(cls, data: dict):
          if not data:
               raise Exception('Package.register() requires an argument for `data`')

          # validations 
          required_fields = [
               'name', 'description', 
               'price', 'direct_cost', 
               'number_of_packages_for_sale',
               'qty_purchase_limit',
               'early_bird_discount_enabled'
          ]
          
          for field in required_fields:
               if field not in data.keys():
                    return False, f"`{field}` is a required field"
               
          
          if type(data['early_bird_discount_enabled']) is not bool:
               return False, "early_bird_discount_enabled field accept only boolean value"
          
          optional_fields = [
               'early_bird_discount_amount',
               'early_bird_discount_cutoff_time',
               'early_bird_discount_type',
               'participants',
               'pre_select_qty',
               'custom_event_field'
               
          ]
          
          for field in optional_fields:
               if data['early_bird_discount_enabled'] == True and field not in data.keys():
                    return False, f"`{field}` is a required field"
          


          # save object
          package = cls(**data)
          db.session.add(package)
          db.session.flush()
          db.session.commit()

          return True, package
     
     
     
     