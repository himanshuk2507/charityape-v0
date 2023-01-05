from src.app_config import db
from src.tests.integration.admin.fixtures import AdminFixture
from src.events.event.models import EventsInformation
from src.events.fields.models import Fields
from src.events.package.models import Packages
from src.events.promocode.models import PromoCodeAssociatedPackages, PromoCode


class FieldsFixture:
    '''
    Create an instance of Field for testing with.
    '''

    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        self.organization_id = AdminFixture().admin.organization_id

        data["organization_id"] = self.organization_id
        field: Fields = Fields(**data)

        db.session.add(field)
        db.session.flush()
        db.session.commit()

        self.field = field
        self.id = field.id

    @classmethod
    def default_obj(cls):
        package_id = PackagesFixture().id
        return dict(field_label="Fixture Field", reporting_label="This is Fixture Label", type="Checkbox",
                    event_wide_field=True, show_field_on_separate_line=True,
                    associated_packages=[package_id]
                    )


class PackagesFixture:
    '''
    Create an instance of Package for testing with.
    '''

    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        self.organization_id = AdminFixture().admin.organization_id

        package = Packages.query.filter_by(name=data["name"]).first()

        # if there is no Package, create one
        if not package:
            data["organization_id"] = self.organization_id
            package: Packages = Packages(**data)

            db.session.add(package)
            db.session.flush()
            db.session.commit()

        self.package = package
        self.id = package.id

    @classmethod
    def default_obj(cls):
        return dict(name="Donnor", description="This is Test", price=120, direct_cost=20,
                    number_of_packages_for_sale=10, qty_purchase_limit=1, early_bird_discount_enabled=True,
                    early_bird_discount_amount=100, early_bird_discount_cutoff_time="2022-05-30:20:00",
                    early_bird_discount_type="percentage", participants="5", pre_select_qty="2",
                    custom_event_field=["abc@example.com"], private_package=True
                    )


class EventsInformationFixture:
    '''
    Create an instance of EventsInformation for testing with.
    '''

    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        self.organization_id = AdminFixture().admin.organization_id

        event_info = EventsInformation.query.filter_by(name=data["name"]).first()

        # if there is no EventsInformation, create one
        if not event_info:
            data["organization_id"] = self.organization_id
            event_info: EventsInformation = EventsInformation(**data)

            db.session.add(event_info)
            db.session.flush()
            db.session.commit()

        self.event_info = event_info
        self.id = event_info.id

    @classmethod
    def default_obj(cls):
        return dict(name="Samson", description="This is Test", event_image="www.image.com",
                    event_sold_out_message="This is Test", venue="Test", address="test", city="test",
                    state="test", zip_country="12345", enable_map=True, display_option="mobile",
                    total_participant="5", enable_one_time_donation=True, start_at="2022-05-30:12:00",
                    end_at="2022-05-30:12:00", event_has_reg_cutoff_date=True,
                    admin_notification=["samson@gmail.com"], reciept_type="Test", reciept_title="Title",
                    reciept_category="email Test", reciept_description="Test", sender_name="samson",
                    reply_email="samson@gmail.com", subject="Test", body="This is just Test"
                    )


class PromoCodeFixture:
    '''
    Create an instance of PromoCode for testing with.
    '''

    def __init__(self, data=None):
        if not data:
            data = self.default_obj()

        self.organization_id = AdminFixture().admin.organization_id

        promo_code = PromoCode.query.filter_by(code=data["code"]).first()

        # if there is no PromoCode, create one
        if not promo_code:
            data["organization_id"] = self.organization_id
            promo_code: PromoCode = PromoCode(**data)

            db.session.add(promo_code)
            db.session.flush()
            db.session.commit()

        self.promo_code = promo_code
        self.id = promo_code.id

    @classmethod
    def default_obj(cls):
        return dict(code="Code520", description="Testing", discount="200", max_user="1",
                    start_date="2022-05-30:10:00", end_date="2022-06-30:10:00"
                    )
