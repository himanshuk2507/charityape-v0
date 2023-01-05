from datetime import datetime
from os import getcwd
from pathlib import Path
from typing import List
import json
import rsa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db


class PayPalSettings(ModelMixin, OrganizationMixin, db.Model):
     __tablename__ = 'PayPalSettings'

     admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Admin.id'), nullable=False)
     client_id_secret_key = db.Column(db.LargeBinary, nullable=False)
     public_key = db.Column(db.Text, nullable=False)
     client_secret_sec_key = db.Column(db.LargeBinary, nullable=False)

     def __init__(
          self, admin_id = None, client_id_secret_key = None,
          public_key = None,
          client_secret_sec_key = None,
          organization_id = None
     ):
          self.admin_id = admin_id
          self.client_id_secret_key = client_id_secret_key
          self.public_key = public_key
          self.client_secret_sec_key = client_secret_sec_key
          
          self.organization_id = organization_id


     def update(self, data: dict = None):
          if not data:
               raise Exception('PayPalSettings.update() requires an argument for `data`') 
          
          try:
               for field in data:
                    setattr(self, field, data.get(field))
               return super().update(data=data)
          except Exception as e:
               print(e)
               return False, e

     
     @classmethod
     def register(cls, data: dict = None):
          if not data:
               raise Exception('PayPalSettings.register() requires an argument for `data`')

          required_fields = ['admin_id', 'client_id', 'client_secret', 'organization_id']
          for field in required_fields:
               if field not in data.keys():
                    return False, f"{field} is a required field"

          # 1. create key pair
          # 2. store private key
          # 3. encrypt paypal secret
          # 4. save encrypted secret

          publicKey, privateKey = rsa.newkeys(1024)
          

          file_path = Path(getcwd())/'enc'/'paypal'/'cl_secret{}'.format(data.get('organization_id'))
          file_path1 = Path(getcwd())/'enc'/'paypal'/'cl_id{}'.format(data.get('organization_id'))
          with open(file_path, 'w') as f:
               f.write(str(privateKey)[11:-1])
               
          
          with open(file_path1, 'w') as f:
               f.write(str(privateKey)[11:-1])
               
          
          encrypted_client_secret = rsa.encrypt(data.get('client_secret').encode(), publicKey)
          
          encrypted_client_id = rsa.encrypt(data.get('client_id').encode(), publicKey)
          
          datas = {}
          datas['public_key'] = str(publicKey)[10:-1]
          datas['client_secret_sec_key'] = encrypted_client_secret
          datas['client_id_secret_key'] = encrypted_client_id
          datas['admin_id'] = data.get('admin_id')
          datas['organization_id'] = data.get('organization_id')
          
          settings = cls(**datas)
          db.session.add(settings)
          db.session.flush()
          db.session.commit()

          return True, settings