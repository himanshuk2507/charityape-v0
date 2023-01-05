from flask import session, jsonify
from functools import wraps
from skraggle.config import Config
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.profile.models import Admin


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = dict(session).get("profile", None)
        # You would add a check here and usethe user id or something to fetch
        # the other data for that user/check if they exist
        if user:
            return f(*args, **kwargs)
        return "You aint logged in, no page for u!"

    return decorated_function


def user_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            admin = Admin.query.filter_by(
                email=claims["email"], organization_id=getOrg(get_jwt())
            ).first()
            if not admin:
                msg = "Access Restricted ,Please Login or regenerate valid access token"
                resp = DataResponse(False, msg)
                return resp.status()
            elif not claims["activated"]:
                msg = "Access Restricted ,Please Confirm your account to activate your account"
                resp = DataResponse(False, msg)
                return resp.status()
            if claims["org"] == admin.organization_id:
                return fn(*args, **kwargs)

            else:
                msg = "Access Restricted ,User doesn't belongs to Organization or no permission to access the resources"
                resp = DataResponse(False, msg)
                return resp.status()

        return decorator

    return wrapper


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            admin = Admin.query.filter_by(
                email=claims["email"], organization_id=getOrg(get_jwt())
            ).first()
            if not admin:
                msg = "Access Restricted ,Please Login or regenrate valid access token "
                resp = DataResponse(False, msg)
                return resp.status()
            elif not claims["activated"]:
                msg = (
                    "Access Restricted ,Please Confirm your account to activate your account and regenerate Access "
                    "token "
                )
                resp = DataResponse(False, msg)
                return resp.status()
            if claims["is_admin"] and claims["org"] == admin.organization_id:
                return fn(*args, **kwargs)
            else:
                msg = "Access Restricted ,User doesn't belongs to Organization or no permission to access the resources"
                resp = DataResponse(False, msg)
                return resp.status()

        return decorator

    return wrapper


def user_admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            admin = Admin.query.filter_by(
                email=claims["email"], organization_id=getOrg(get_jwt())
            ).first()
            if not admin:
                msg = "Access Restricted ,Please Login or regenrate valid access token "
                resp = DataResponse(False, msg)
                return resp.status()
            elif not claims["activated"]:
                msg = (
                    "Access Restricted ,Please Confirm your account to activate your account and regenerate Access "
                    "token "
                )
                resp = DataResponse(False, msg)
                return resp.status()
            if (
                claims["org"] == admin.organization_id
                and admin.type_of == "user"
                and claims["is_admin"]
                and admin.permission_level == "administrator"
            ):
                return fn(*args, **kwargs)

            else:
                msg = "Access Restricted ,User doesn't belongs to Organization or no permission to access the resources"
                resp = DataResponse(False, msg)
                return resp.status()

        return decorator

    return wrapper
