from src.app_config import ModelMixin, OrganizationMixin, db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
from src.library.utility_classes.custom_validator import Validator
from src.events.package.models import Packages
from src.library.utility_classes.mutable_list import MutableList



class PromoCodeAssociatedPackages(ModelMixin, OrganizationMixin, db.Model):
     __tablename__ = 'PromoCodeAssociatedPackages'
     promo_id = db.Column(UUID(as_uuid=True), db.ForeignKey('PromoCode.id'), nullable=True)
     package_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Packages.id'), nullable=True)
     

class PromoCode(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "PromoCode"
    code = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    discount = db.Column(db.Integer, nullable=True)
    max_user = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    associated_packages = db.relationship('PromoCodeAssociatedPackages', backref='PromoCode', lazy=True, cascade="all,delete")

    def __init__(self, code, description, discount, max_user, start_date, end_date, organization_id, associated_packages=None):
        self.code = code
        self.description = description
        self.discount = discount
        self.max_user = max_user
        self.start_date = start_date
        self.end_date = end_date
        self.organization_id = organization_id
        self.associated_packages = associated_packages or []

    @classmethod
    def register(cls, data: dict):
          if not data:
               raise Exception('PromoCode.register() requires an argument for `data`')

          # validations 
          required_fields = [
               'code', 'description', 
               'discount', 'max_user', 
               'start_date',
               'end_date'
               ]
          
          for field in required_fields:
               if field not in data.keys():
                    return False, f"`{field}` is a required field"
               
          
          
          # does ContactCompanies already exist?
          promocode = cls.query.filter_by(code=data.get('code'), organization_id=data.get('organization_id')).one_or_none()
          if promocode:
               return False, "Promo Code is already created."
          
          if data.get('start_date') == "" or data.get('end_date') == "":
               return False, "Start date or End date can't be empty."
          

          # save object
          promocode = cls(**data)
          db.session.add(promocode)
          db.session.flush()
          db.session.commit()

          return True, promocode