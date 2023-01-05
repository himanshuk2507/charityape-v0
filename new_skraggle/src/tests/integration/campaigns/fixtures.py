from datetime import timedelta
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from src.app_config import db
from src.campaigns.models import Campaign
from src.tests.integration.admin.fixtures import AdminFixture


class CampaignFixture:
    '''
    Creates a Campaign object for testing with.
    :param campaign_data: (optional) dict[str, Any] with fields from Campaign
    '''
    def __init__(self, campaign_data=None):
        if not campaign_data:
            campaign_data = self.default_obj()
        campaign = Campaign.query.filter_by(name=campaign_data["name"]).first()

        # if there is no campaign, create one
        if not campaign:
            campaign_data["organization_id"] = AdminFixture().admin.organization_id
            campaign: Campaign = Campaign(**campaign_data)

            db.session.add(campaign)
            db.session.flush()
            db.session.commit()

        self.campaign = campaign
        self.id = campaign.id

    @classmethod
    def default_obj(cls):
        return dict(fundraising_goal=100, name="test", description="test")
