from src.app_config import db
from src.impact_area.models import ImpactArea
from src.tests.integration.admin.fixtures import AdminFixture


class ImpactAreaFixture:
    '''
    Create an instance of ImpactArea for testing with.
    '''

    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        impact_area = ImpactArea.query.filter_by(name=data["name"]).first()

        # if there is no ImpactArea, create one
        if not impact_area:
            data["organization_id"] = AdminFixture().admin.organization_id
            impact_area: ImpactArea = ImpactArea(**data)

            db.session.add(impact_area)
            db.session.flush()
            db.session.commit()

        self.impact_area = impact_area
        self.id = impact_area.id

    @classmethod
    def default_obj(cls):
        return dict(name="Test Impact", description="This is just test")
