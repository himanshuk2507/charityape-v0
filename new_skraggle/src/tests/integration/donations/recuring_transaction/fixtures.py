from src.app_config import db
from src.donations.recurring_transactions.models import RecurringTransaction
from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.donations.fixtures import DonationSourceFixture
from src.tests.integration.campaigns.fixtures import CampaignFixture
from src.tests.integration.donations.fixtures import PledgeFixture
from src.tests.integration.contacts.fixtures import ContactCompaniesFixture
from src.tests.integration.impact_area.fixtures import ImpactAreaFixture

class RecurringTransactionFixture:
    '''
    Create an instance of One Time Transaction for testing with.
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        self.organization_id = AdminFixture().admin.organization_id

        # if there is no Package, create one
        
        data["organization_id"] = self.organization_id
        recurring: RecurringTransaction = RecurringTransaction(**data)

        db.session.add(recurring)
        db.session.flush()
        db.session.commit()

        self.recurring = recurring
        self.id = recurring.id

    @classmethod
    def default_obj(cls):
        company = ContactCompaniesFixture()
        campaign = CampaignFixture()
        source = DonationSourceFixture()
        pledge = PledgeFixture()
        impact_area_id = ImpactAreaFixture(data={"name": "Donation Impact Test"}).id
        return dict(
            amount=240, currency="usd", is_from_different_currency=False,
            type="gift", payment_method="cash", impact_area=impact_area_id,
            source=source.id, keywords=[], 
            dedication="I dedicate this to Mr John", notes="This is not a cheerful giver",
            receipting_strategy="Log transaction without payment or receipt", pledge_id=pledge.id,
            campaign_id=campaign.id, company_id=company.id, billing_cycle = "month",
            billing_interval = 2,
            is_revenue=False
        )
