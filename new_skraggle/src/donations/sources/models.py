from typing import List

from src.app_config import ModelMixin, OrganizationMixin, TransactionMixin, db
from src.donations.one_time_transactions.models import OneTimeTransaction


class DonationSource(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'DonationSource'

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(
        self, name = None, description = None, is_active = True,
        organization_id = None,
    ):
        self.name = name 
        self.description = description
        self.is_active = is_active

        self.organization_id = organization_id

    def delete(self):
        # find transactions that use this source and reset their `source` fields
        transactions: List[TransactionMixin] = OneTimeTransaction.query\
            .filter_by(
                source = self.id, organization_id = self.organization_id
            ).all()
        for transaction in transactions:
            transaction.source = None
        db.session.add_all(transactions)
        db.session.commit()

        self.delete_by_id(id=self.id, organization_id=self.organization_id)

    def update(self, data: dict = None):
        new_name = data.get('name')
        if new_name:
            if self.name_has_been_used(name=new_name, organization_id=self.organization_id):
                return False, 'This name has already been used for a different source. Try again with a different name.'

        return super().update(data=data)

    @classmethod
    def register(cls, data: dict = None):
        if not data:
            raise Exception('DonationSource.register() requires an argument for `data`')

        required_fields = ['name', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"

        if cls.name_has_been_used(name=data.get('name'), organization_id=data.get('organization_id')):
            return False, 'A source has already been registered with this name. Please, try again with another name.'
        
        source = cls(**data)

        db.session.add(source)
        db.session.flush()
        db.session.commit()

        return True, source
    
    @classmethod
    def fetch_by_name(cls, name = None, organization_id = None):
        return cls.query.filter_by(
            name = name,
            organization_id = organization_id
        ).one_or_none()

    @classmethod 
    def name_has_been_used(cls, name = None, organization_id = None):
        return cls.fetch_by_name(name = name, organization_id = organization_id) is not None