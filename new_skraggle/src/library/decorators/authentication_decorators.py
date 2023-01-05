from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from src.library.utility_classes.custom_validator import Validator

from src.library.utility_classes.request_response import Response
from src.profile.models import Admin


def admin_required():
    '''
    Ensures that the decorated route is only accessed by an authenticated Admin
    '''
    def callback(func):
        @wraps(func)

        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            if not claims.get('id'):
                return Response(False, 'Sign in to access this route', 401).respond()

            claims_id = claims.get('id')
            admin: Admin = Admin.query.filter_by(id=claims_id).one_or_none()

            if not admin:
                return Response(False, 'Sign up to access this route', 401).respond()
            
            claims_org = claims.get('org')

            if str(admin.organization_id) != claims_org:
                # Actually, if this condition is ever True, that would mean that the Admin object was updated after the
                # last sign in event and the `organization_id` column was changed.
                # This is not likely to ever happen, but we'll play safe...
                return Response(False, 'Access to this organisation has been revoked', 403).respond()

            return func(*args, **kwargs)

        return decorator

    return callback


def admin_with_email_exists():
    '''
    For public routes that require the request payload to contain a valid `email` field that points to a valid Admin,
    this decorator verifies the `email` field and passes an Admin object to the decorared route.

    It can be used thus:
    @admin_endpoints.route('/verify-account', methods=['POST'])
    @admin_with_email_exists()
    def verify_account_route(admin):
        # the `admin` parameter is an Admin instance
        pass

    If the decorated route does not contain a valid `email` field, or if the `email` field doesn't belong to 
    an Admin account, the appropriate error message is returned.
    '''
    def callback(func):
        @wraps(func)

        def decorator(*args, **kwargs):
            if not request.json:
                return Response(False, 'This endpoint requires a JSON payload with a `Content-Type: application/json` header').respond()

            email = request.json.get('email')

            if not email or not Validator.is_email(email):
                return Response(False, 'A valid email address is required').respond()

            admin: Admin = Admin.fetch_one_by_email(email)

            if not admin:
                return Response(False, 'No Admin account is registered with this email address').respond()

            return func(*args, **kwargs, admin=admin)

        return decorator

    return callback