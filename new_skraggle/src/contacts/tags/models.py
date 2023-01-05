from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db
from src.library.utility_classes.mutable_list import MutableList


class ContactTags(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "ContactTags"

    name = db.Column(db.String(255), nullable=False)

    def __init__(self, name=None, organization_id: str = None):
        self.organization_id = organization_id
        self.name = name 
    
    @classmethod
    def register(cls, data: dict):
        '''
        Create a new ContactTag from a dictionary, after performing validations.
        '''
        if not data:
            raise Exception('ContactTags.register() requires an argument for `data`')

        # validations
        required_fields = ['name']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"

        # does ContactTag already exist?
        tag = cls.query.filter_by(name=data.get('name'), organization_id=data.get('organization_id')).one_or_none()
        
        if tag:
            return False, "A ContactTag is already registered with this name. Try again with another name."

        tag = ContactTags(**data)
        db.session.add(tag)
        db.session.flush()
        db.session.commit()
        
        return True, tag