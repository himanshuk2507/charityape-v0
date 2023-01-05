from src.app_config import db
from src.p2p.models import P2P, P2PEmail
from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.campaigns.fixtures import CampaignFixture


class P2PFixture:
    '''
    Create an instance of P2P for testing with.
    '''

    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        self.organization_id = AdminFixture().admin.organization_id

        data["organization_id"] = self.organization_id
        p2p: P2P = P2P(**data)

        db.session.add(p2p)
        db.session.flush()
        db.session.commit()

        self.p2p = p2p
        self.id = p2p.id

    @classmethod
    def default_obj(cls):
        campaign_id = CampaignFixture().id
        return dict(
            campaign_id=campaign_id, designation="My P2P",
            fundraiser_display_name="Icheka Ozuru", first_name="Icheka", last_name="Ozuru",
            email="fehig99164@steamoh.com", goal=10000, goal_currency="USD", offline_amount=1000,
            offline_donation=None, goal_date="2022-06-02T11:55:23.560Z", personal_message="My P2P",
            profile_photo=None, display_photos=[]
        )
