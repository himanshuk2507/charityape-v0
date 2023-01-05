from src.app_config import db
from src.forms.models import Form
from src.tests.integration.admin.fixtures import AdminFixture


class FormFixture:
    '''
    Create an instance of Form for testing with.
    '''
    def __init__(self, form_data=None):
        if not form_data:
            form_data = self.default_obj()
        
        self.organization_id = AdminFixture().admin.organization_id
        
        form = Form.query.filter_by(name=form_data["name"]).first()
        
        # if there is no Form, create one
        if not form:
            form_data["organization_id"] = self.organization_id
            form: Form = Form(**form_data)

            db.session.add(form)
            db.session.flush()
            db.session.commit()

        self.form = form

    @classmethod
    def default_obj(cls):
        return dict(name="test", type="test", status="active")
