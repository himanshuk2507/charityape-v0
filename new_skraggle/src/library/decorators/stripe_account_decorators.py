from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from src.library.utility_classes.request_response import Response
from src.profile.models import Admin

from src.profile.payment_settings.stripe.models import StripeSettings


def stripe_account_required():
    '''
    Ensures that the decorated route is only accessible if the Admin's Stripe account has been connected.
    '''
    def callback(func):
        @wraps(func)

        def decorator(*args, **kwargs):
            claims = get_jwt()
            organization_id = claims.get('org')
            admin_id = claims.get('id')

            stripe_settings: StripeSettings = Admin.fetch_by_id(id=admin_id, organization_id=organization_id).get_stripe_settings()
            if not stripe_settings:
                return Response(False, 'You need to connect your Stripe account first!').respond()

            return func(*args, **kwargs)

        return decorator

    return callback