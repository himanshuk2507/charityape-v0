from skraggle.base_helpers.orgGen import getOrg
from skraggle.config import db
from skraggle.campaigns.models import Campaigns
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials
from skraggle.tests.integration.fixtures.contact_users import ContactUsersFixture


default_campaign = dict(
    fundraising_goal=100,
    name="test",
    description="test",
)

class CampaignFixture:
    def __init__(self) -> None:
        campaign = Campaigns.query.filter().first()

        if not campaign:
            contact = ContactUsersFixture().get().id
            default_campaign['followers'] = [contact]
            default_campaign['organization_id'] = TestAuthCredentials().admin.organization_id
            campaign = Campaigns(**default_campaign)

            db.session.add(campaign)
            db.session.flush()
            db.session.commit()

        self.campaign = campaign
        self.defaults = default_campaign

    def get(self):
        return self.campaign