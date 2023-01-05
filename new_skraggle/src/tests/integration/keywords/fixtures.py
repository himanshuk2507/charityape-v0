from src.app_config import db
from src.keywords.models import Keyword
from src.tests.integration.admin.fixtures import AdminFixture


class KeywordFixture:
    '''
    Create an instance of Keyword for testing with.
    '''

    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        keyword = Keyword.query.filter_by(name=data["name"]).first()

        # if there is no Keyword, create one
        if not keyword:
            data["organization_id"] = AdminFixture().admin.organization_id
            keyword: Keyword = Keyword(**data)

            db.session.add(keyword)
            db.session.flush()
            db.session.commit()

        self.keyword = keyword
        self.id = keyword.id

    @classmethod
    def default_obj(cls):
        return dict(name="Test Keyword")
