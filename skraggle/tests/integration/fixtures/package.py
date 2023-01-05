from skraggle.events.models import PromoCode, Packages
from skraggle.tests.integration.fixtures.auth_credentials import TestAuthCredentials, credentials
from skraggle.config import db

default_package = dict(
    name = 'test package',
    description = 'test package',
    price = 100,
    direct_cost = 100,
    number_of_packages_for_sale = 10,
    qty_purchase_limit = 10
)


class PackageFixture:
    def __init__(self):
        package = Packages.query.filter().first()

        if not package:
            org_id = TestAuthCredentials(credentials).admin.organization_id
            default_package['organization_id'] = org_id
            default_package['is_enabled'] = False
            package = Packages(**default_package)
            
            db.session.add(package)
            db.session.flush()
            db.session.commit()

        self.package = package

    def get(self):
        return self.package