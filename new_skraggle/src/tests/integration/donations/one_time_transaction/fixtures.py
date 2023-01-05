from src.app_config import db
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.donations.fixtures import DonationSourceFixture
from src.tests.integration.contacts.fixtures import ContactUsersFixture
from src.tests.integration.campaigns.fixtures import CampaignFixture
from src.tests.integration.impact_area.fixtures import ImpactAreaFixture


class OneTimeTransactionFixture:
    '''
    Create an instance of One Time Transaction for testing with.
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        self.organization_id = AdminFixture().admin.organization_id

        # if there is no Package, create one
        
        data["organization_id"] = self.organization_id
        one_time_txn: OneTimeTransaction = OneTimeTransaction(**data)

        db.session.add(one_time_txn)
        db.session.flush()
        db.session.commit()

        self.one_time_txn = one_time_txn
        self.id = one_time_txn.id

    @classmethod
    def default_obj(cls):
        contact_user = ContactUsersFixture().contact_user
        campaign = CampaignFixture()
        source = DonationSourceFixture()
        impact_area_id = ImpactAreaFixture(data={"name": "Donation Impact Test"}).id
        return dict(
            amount=240, currency="usd", is_from_different_currency=False, 
            date_received="2022-06-08T18:50:00.000Z",
            type="gift", payment_method="cash", impact_area=impact_area_id,
            source=source.id, keywords=[], 
            dedication="I dedicate this to Mr John", notes="This is not a cheerful giver",
            receipting_strategy="Log transaction without payment or receipt",
            campaign_id=campaign.id, contact_id=contact_user.id,
            is_revenue=False
            )
