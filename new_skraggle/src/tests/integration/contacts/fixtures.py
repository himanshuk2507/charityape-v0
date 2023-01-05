from datetime import timedelta
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from src.app_config import db
from src.tests.integration.admin.fixtures import AdminFixture
from src.contacts.companies.models import AssociatedContact, ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.contacts.households.models import Households
from src.contacts.interactions.models import ContactInteraction
from src.contacts.tags.models import ContactTags
from src.contacts.todos.models import ContactTodo
from src.contacts.volunteering.models import VolunteerActivity


class ContactCompaniesFixture:
    '''
    Creates a ContactCompanies object for testing with.
    :param campaign_data: (optional) dict[str, Any] with fields from ContactCompanies
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()
        contact_companies = ContactCompanies.query.filter_by(name=data["name"]).one_or_none()

        # if there is no ContactCompanies, create one
        if not contact_companies:
            data["organization_id"] = AdminFixture().admin.organization_id
            contact_companies: ContactCompanies = ContactCompanies(**data)

            db.session.add(contact_companies)
            db.session.flush()
            db.session.commit()

        self.company = contact_companies
        self.id = contact_companies.id

    @classmethod
    def default_obj(cls):
        return dict(
            name="Microsoft", type="IT", email="msft1@msn.com", established_at="2022-05-26T11:55:23.560Z",
            phone="0987609809"
        )


class AssociatedContactFixture:
    '''
    Creates an AssociatedContact object for testing with.
    :param data: (optional) dict[str, Any] with fields from AssociatedContact
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()
        associated_contact = AssociatedContact.query.filter_by(name=data["name"]).one_or_none()

        # if there is no AssociatedContact, create one
        if not associated_contact:
            data["organization_id"] = AdminFixture().admin.organization_id
            associated_contact: AssociatedContact = AssociatedContact(**data)

            db.session.add(associated_contact)
            db.session.flush()
            db.session.commit()

        self.associated_contact = associated_contact
        self.id = associated_contact.id

    @classmethod
    def default_obj(cls):
        company = ContactCompaniesFixture().company
        contact_user = ContactUsersFixture().contact_user

        return dict(
            contacts=dict(contact_id=contact_user.id, company_id=company.id, position="CEO")
        )


class ContactUsersFixture:
    '''
    Creates a ContactUsers object for testing with.
    :param data: (optional) dict[str, Any] with fields from ContactUsers
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()
        contact_user = ContactUsers.query.filter_by(primary_email=data["primary_email"]).one_or_none()

        # if there is no ContactUsers, create one
        if not contact_user:
            data["organization_id"] = AdminFixture().admin.organization_id
            contact_user: ContactUsers = ContactUsers(**data)

            db.session.add(contact_user)
            db.session.flush()
            db.session.commit()

        self.contact_user = contact_user
        self.id = contact_user.id

    @classmethod
    def default_obj(cls):
        company = ContactCompaniesFixture().company
        household = HouseHoldsFixture().household
        return dict(first_name="mercy", last_name="quark", primary_email="fastsseah@yahoo.com",
                    address="ayoodele street", birth_date=None, email_subscription_status=None, facebook=None,
                    households=[household.id], priority="", unit="unit 1", postal_code="87778",
                    state="Rivers", country="Bethlehem", city="Asia", company=company.id
                    )


class HouseHoldsFixture:
    '''
    Creates a Households object for testing with.
    :param data: (optional) dict[str, Any] with fields from Households
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()
        household = Households.query.filter_by(name=data["name"]).one_or_none()

        # if there is no HouseHolds, create one
        if not household:
            data["organization_id"] = AdminFixture().admin.organization_id
            household: Households = Households(**data)

            db.session.add(household)
            db.session.flush()
            db.session.commit()

        self.household = household
        self.id = household.id

    @classmethod
    def default_obj(cls):
        return dict(name="Chris Rock Household")


class ContactInteractionFixture:
    '''
    Creates a ContactInteraction object for testing with.
    :param data: (optional) dict[str, Any] with fields from ContactInteraction
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        data["organization_id"] = AdminFixture().admin.organization_id
        contact_interaction: ContactInteraction = ContactInteraction(**data)

        db.session.add(contact_interaction)
        db.session.flush()
        db.session.commit()

        self.contact_interaction = contact_interaction
        self.id = contact_interaction.id

    @classmethod
    def default_obj(cls):
        contact = ContactUsersFixture().contact_user
        return dict(type="Email", subject="Merry Christmas", interacted_at="2022-05-26T10:57:10.621Z",
                    contact_id=contact.id, todos=[])


class ContactTagsFixture:
    '''
    Creates a ContactTags object for testing with.
    :param data: (optional) dict[str, Any] with fields from ContactTags
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()
        contact_tag = ContactTags.query.filter_by(name=data["name"]).one_or_none()

        # if there is no ContactTags, create one
        if not contact_tag:
            data["organization_id"] = AdminFixture().admin.organization_id
            contact_tag: ContactTags = ContactTags(**data)

            db.session.add(contact_tag)
            db.session.flush()
            db.session.commit()

        self.contact_tag = contact_tag
        self.id = contact_tag.id

    @classmethod
    def default_obj(cls):
        return dict(name="Folks in Asia")


class ContactTodoFixture:
    '''
    Creates a ContactTodo object for testing with.
    :param data: (optional) dict[str, Any] with fields from ContactTodo
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        # if there is no ContactTodo, create one
        data["organization_id"] = AdminFixture().admin.organization_id
        contact_todo: ContactTodo = ContactTodo(**data)

        db.session.add(contact_todo)
        db.session.flush()
        db.session.commit()

        self.contact_todo = contact_todo
        self.id = contact_todo.id

    @classmethod
    def default_obj(cls):
        contact = ContactUsersFixture().contact_user
        return dict(todo="Wish John Doe a happy marriage anniversary", details="(Optional) Details about this to-do",
                    due_at="2022-05-26T11:55:23.560Z",
                    assignees=[contact.id],
                    attachments=["url_to_attachment"])


class VolunteerActivityFixture:
    '''
    Creates a VolunteerActivity object for testing with.
    :param data: (optional) dict[str, Any] with fields from VolunteerActivity
    '''
    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        # if there is no VolunteerActivity, create one
        data["organization_id"] = AdminFixture().admin.organization_id
        volunteer_activity: VolunteerActivity = VolunteerActivity(**data)

        db.session.add(volunteer_activity)
        db.session.flush()
        db.session.commit()

        self.volunteer_activity = volunteer_activity
        self.id = volunteer_activity.id

    @classmethod
    def default_obj(cls):
        contact = ContactUsersFixture().contact_user
        return dict(
            contact_id=contact.id, name="My activity", start_at="2022-05-26T11:55:23.560Z",
            end_at="2022-05-26T11:55:23.560Z", description="An optional description",
            impact_area="Save the Children", attachments=[], fee=1000, fee_currency="USD"
        )
