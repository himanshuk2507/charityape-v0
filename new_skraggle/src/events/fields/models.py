from src.app_config import ModelMixin, OrganizationMixin, db
from sqlalchemy.sql import func
from flask_jwt_extended import get_jwt
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
from src.events.package.models import Packages
from src.library.utility_classes.mutable_list import MutableList


class Fields(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "Fields"
    field_label = db.Column(db.String(255))
    reporting_label = db.Column(db.String(255))
    type = db.Column(db.String(255), nullable=False)
    event_wide_field = db.Column(db.String(255))
    show_field_on_separate_line = db.Column(db.Boolean)
    associated_packages = db.Column("associated_packages", ARRAY(UUID(as_uuid=True)), nullable=False)

    def __init__(self,
                 field_label, reporting_label,
                 type, event_wide_field,
                 show_field_on_separate_line,
                 organization_id,
                 associated_packages=None
                 ):
        self.field_label = field_label
        self.reporting_label = reporting_label
        self.type = type
        self.event_wide_field = event_wide_field,
        self.show_field_on_separate_line = show_field_on_separate_line
        self.associated_packages = associated_packages
        self.organization_id = organization_id

    @classmethod
    def register(cls, data: dict):
        if not data:
            raise Exception('Fields.register() requires an argument for `data`')

        # validations
        required_fields = [
            'field_label', 'reporting_label',
            'type', 'event_wide_field',
            'show_field_on_separate_line',
            'associated_packages'
        ]

        for field in required_fields:
            if field not in data.keys():
                return False, f"`{field}` is a required field"

        if type(data['show_field_on_separate_line']) is not bool:
            return False, "show_field_on_separate_line field accept only boolean value"

        if type(data['event_wide_field']) is not bool:
            return False, "event_wide_field field accept only boolean value"

        if len(data.get("associated_packages")) > 0:
            for package in data.get("associated_packages"):
                packages: Packages = Packages.fetch_by_id(package, organization_id=get_jwt().get('org'))
                if not packages:
                    return False, f"Package ID: {package} is not valid"
        else:
            return False, "Associated package must be assigned"

        # save object
        field = cls(**data)
        db.session.add(field)
        db.session.flush()
        db.session.commit()

        return True, field
