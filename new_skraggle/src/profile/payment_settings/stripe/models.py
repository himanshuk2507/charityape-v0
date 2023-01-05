from datetime import datetime
from os import getcwd
from pathlib import Path
from typing import List
import json
import rsa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db


class StripeSettings(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'StripeSettings'

    admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Admin.id'), nullable=False)
    secret_key = db.Column(db.LargeBinary, nullable=False)
    public_key = db.Column(db.Text, nullable=False)

    def __init__(
        self, admin_id = None, secret_key = None,
        public_key = None,
        organization_id = None
    ):
        self.admin_id = admin_id
        self.secret_key = secret_key
        self.public_key = public_key
        
        self.organization_id = organization_id


    def update(self, data: dict = None):
        if not data:
            raise Exception('StripeSettings.update() requires an argument for `data`') 
        
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
            raise Exception('StripeSettings.register() requires an argument for `data`')

        required_fields = ['admin_id', 'secret_key', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"

        # 1. create key pair
        # 2. store private key
        # 3. encrypt stripe secret
        # 4. save encrypted secret

        public_key, private_key = rsa.newkeys(512)

        file_path = Path(getcwd())/'enc'/'stripe'/data.get('organization_id')
        with open(file_path, 'w') as f:
            f.write(str(private_key)[11:-1])
        encrypted = rsa.encrypt(data.get('secret_key').encode(), public_key)

        data['secret_key'] = encrypted
        # data['secret_key'] = str(encrypted).encode('utf-8')
        data['public_key'] = str(public_key)[10:-1]
        print('===>', encrypted)
        print('===>', str(encrypted))
        print('===>', bytes(str(encrypted), 'utf-8') == encrypted)
        
        settings = cls(**data)
        db.session.add(settings)
        db.session.flush()
        db.session.commit()

        return True, settings