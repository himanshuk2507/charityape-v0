from datetime import timedelta
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from src.app_config import db
from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.campaigns.fixtures import CampaignFixture
from src.tests.integration.contacts.fixtures import ContactUsersFixture
from src.tests.integration.impact_area.fixtures import ImpactAreaFixture
from src.tests.integration.keywords.fixtures import KeywordFixture
from src.donations.pledges.models import Pledge, PledgeInstallment
from src.donations.sources.models import DonationSource

class PledgeFixture:
    '''
    Creates a Pledge object for testing with.
    :param data: (optional) dict[str, Any] with fields from Pledge
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()
        pledge = Pledge.query.filter_by(name=data["name"]).one_or_none()

        # if there is no Pledge, create one
        if not pledge:
            data["organization_id"] = AdminFixture().admin.organization_id
            pledge: Pledge = Pledge(**data)

            db.session.add(pledge)
            db.session.flush()
            db.session.commit()

        self.pledge = pledge
        self.id = pledge.id

    @classmethod
    def default_obj(cls):
        campaign_id = CampaignFixture().id
        contact_id = ContactUsersFixture().id
        impact_area_id = ImpactAreaFixture(data={"name": "Donation Impact Test"}).id
        keyword1 = KeywordFixture(data={"name": "A Keyword"}).id
        keyword2 = KeywordFixture(data={"name": "Another Keyword"}).id

        return dict(
            contact_id=contact_id, campaign_id=campaign_id,
            name="A pledge", amount=1000, amount_currency="USD", start_date="2022-05-26T11:55:23.560Z",
            end_date="2022-05-26T11:55:23.560Z", type="donation", attachments=[], payment_interval="monthly",
            impact_area=impact_area_id, source="Save a Life Foundation", keywords=[keyword1, keyword2],
            dedication="I dedicate this to...", notes="My notes..."
        )



class DonationSourceFixture:
    '''
    Creates a DonationSource object for testing with.
    :param data: (optional) dict[str, Any] with fields from DonationSource
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()
        source = DonationSource.query.filter_by(name=data["name"]).one_or_none()

        # if there is no DonationSource, create one
        if not source:
            data["organization_id"] = AdminFixture().admin.organization_id
            source: DonationSource = DonationSource(**data)

            db.session.add(source)
            db.session.flush()
            db.session.commit()

        self.source = source
        self.id = source.id

    @classmethod
    def default_obj(cls):
        return dict(name="Outreach at GRA IIe", description="Went to GRA to help the needy")
