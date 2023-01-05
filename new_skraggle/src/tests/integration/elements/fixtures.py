from src.app_config import db
from src.elements.models import Element
from src.tests.integration.admin.fixtures import AdminFixture
from src.tests.integration.campaigns.fixtures import CampaignFixture


class ElementFixture:
    '''
    Create an instance of Element for testing with.
    '''

    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        self.organization_id = AdminFixture().admin.organization_id

        element = Element.query.filter_by(name=data["name"]).first()

        # if there is no Element, create one
        if not element:
            data["organization_id"] = self.organization_id
            element: Element = Element(**data)

            db.session.add(element)
            db.session.flush()
            db.session.commit()

        self.element = element
        self.id = element.id

    @classmethod
    def default_obj(cls):
        campaign_id = CampaignFixture().id
        return dict(name="My Button", type="button", campaign_id=campaign_id)
