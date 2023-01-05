from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db
from src.library.utility_classes.mutable_list import MutableList


class Households(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "Households"

    name = db.Column(db.String(255), nullable=False)

    def __init__(self, name=None, organization_id: str = None):
        self.name = name
        self.organization_id = organization_id

    @classmethod
    def register(cls, data: dict):
        '''
        Create a new Household from a dictionary, after performing validations.
        '''
        if not data:
            raise Exception(
                'Households.register() requires an argument for `data`')

        # validations
        required_fields = ['name', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"

        # does Household already exist?
        household = cls.query.filter_by(name=data.get(
            'name'), organization_id=data.get('organization_id')).one_or_none()
        if household:
            return False, "A Household is already registered with this name. Try again with another name."

        household = Households(**data)
        db.session.add(household)
        db.session.flush()
        db.session.commit()

        return True, household
