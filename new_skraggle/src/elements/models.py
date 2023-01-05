from sqlalchemy.dialects.postgresql import UUID

from src.app_config import ModelMixin, OrganizationMixin, db
from src.campaigns.models import Campaign


class Element(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'Element'

    campaign_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Campaign.id'), nullable=True)

    name = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(255), nullable=True)

    def __init__(
        self, name = None, type = None, campaign_id = None, organization_id = None
    ):
        self.name = name 
        self.type = type 
        
        self.campaign_id = campaign_id 
        
        self.organization_id = organization_id 

    def update(self, data: dict = None):
        if not data:
            return False, 'No data was provided for update'

        old_campaign: Campaign = Campaign.fetch_by_id(
            id=self.campaign_id,
            organization_id=data.get('organization_id')
        ) if self.campaign_id else None

        if data.get('campaign_id'):
            if old_campaign:
                old_campaign.elements.remove(self)

            new_campaign: Campaign = Campaign.fetch_by_id(
                id=data.get('campaign_id'),
                organization_id=data.get('organization_id')
            )
            if not new_campaign:
                return False, 'No campaign exists with this ID'

            new_campaign.elements.append(self)
            db.session.add(new_campaign)
        
        return super().update(data)

    @classmethod
    def register(cls, data: dict = None):
        if not data:
            raise Exception('Element.register() requires an argument for `data`')

        # validations 
        required_fields = ['organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"`{field}` is a required field"

        element = cls(**data)
        if data.get('campaign_id'):
            campaign: Campaign = Campaign.fetch_by_id(
                id=data.get('campaign_id'),
                organization_id=data.get('organization_id')
            )
            if not campaign:
                return False, 'No campaign exists with this ID'

            campaign.elements.append(element)
            db.session.add(campaign)
        db.session.add(element)
        db.session.flush()
        db.session.commit()

        return True, element