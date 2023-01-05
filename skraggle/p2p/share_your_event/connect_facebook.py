import os
import webbrowser
from datetime import datetime

from flask import Blueprint, redirect, request, session
import requests
from flask_jwt_extended import get_jwt
import ast

from sqlalchemy import and_

from skraggle.base_helpers.crypter import Crypt
from skraggle.base_helpers.orgGen import cache_id_gen
from skraggle.config import db
from skraggle.profile.models import Admin
from skraggle.run import cache
from skraggle.base_helpers.facebook_helper import FaceConnect
from skraggle.base_helpers.responser import DataResponse
from skraggle.decarotor import user_required
from skraggle.integrations.models import FacebookDetails

facebookconnect = Blueprint("facebookconnect", __name__, template_folder="templates")


APP_ID = os.getenv("FB_APP_ID")
SECRET_KEY = os.getenv("FB_APP_SECRET_KEY")
REDIRECT_URL = os.getenv("FB_REDIRECT_URI")
hider = Crypt()

fb = FaceConnect(app_id=APP_ID, app_secret=SECRET_KEY, redirect_uri=REDIRECT_URL)


@facebookconnect.route("/connect", methods=["GET"])
@user_required()
def connect_facebook():
    admin = Admin.query.filter_by(
        organization_id=get_jwt()["org"], email=get_jwt()["email"]
    ).first()
    perms = [
        "public_profile",
        "pages_show_list",
        "pages_manage_metadata",
        "email",
        "pages_manage_posts",
    ]
    cache_id = cache_id_gen()
    cache.set(
        cache_id,
        {
            "email": admin.email,
            "user_id": str(admin.admin_id),
            "org_id": get_jwt()["org"],
        },
    )
    fb_login_url = fb.get_client_auth_url(session_id=cache_id, perms=perms)
    webbrowser.open(fb_login_url)
    resp = DataResponse(True, "Allow Permissions to Connect Your Facebook Account")
    return resp.status()


@facebookconnect.route("/call", methods=["GET"])
def fb_callback():
    code = request.args.get("code")
    cache_id = request.args.get("state")
    logged_user_info = cache.get(cache_id)
    short_success, short_access_token = fb.fetch_access_token(code)
    if not short_success:
        resp = DataResponse(False, short_access_token)
        return resp.status()
    long_success, extended_access_token = fb.extend_access_token(short_access_token)
    if not long_success:
        resp = DataResponse(False, extended_access_token)
        return resp.status()
    page_success, _page_access_tokens_obj = fb.get_extended_page_tokens(
        extended_access_token
    )
    if not page_success:
        resp = DataResponse(False, _page_access_tokens_obj)
        return resp.status()

    user_info = fb.fetch_info(
        access_token=extended_access_token, fields="id,name,email"
    )
    admin = Admin.query.filter_by(
        organization_id=logged_user_info.get("org_id"),
        admin_id=logged_user_info.get("user_id"),
    ).first()
    connection_info = dict(
        facebook_email=user_info.get("email"),
        user_email=logged_user_info.get("email"),
        belongs_to=logged_user_info.get("user_id"),
        page_tokens=hider.encrypt(str(_page_access_tokens_obj)),
        facebook_user_id=user_info.get("id"),
        access_token=hider.encrypt(extended_access_token),
        scopes="None",
        organization_id=logged_user_info.get("org_id"),
        connected_on=datetime.now(),
    )
    try:
        # deleting old facebook connection details if user connected before
        if admin.facebook_connected:
            org_id = logged_user_info.get("org_id")
            db.session.query(FacebookDetails).filter(
                and_(
                    FacebookDetails.organization_id == org_id,
                    FacebookDetails.facebook_id == admin.facebook_id,
                )
            ).update(connection_info, synchronize_session="fetch")
            db.session.commit()
            resp = DataResponse(
                True, "Facebook Connection Reauthenticated Successfully "
            )
            return resp.status()
        else:
            fb_connection = FacebookDetails(**connection_info)
            db.session.add(fb_connection)
            db.session.flush()
            cache.delete(cache_id)
            admin.facebook_connected = True
            admin.facebook_id = fb_connection.facebook_id
            db.session.commit()
            resp = DataResponse(True, "Facebook has been Connected Successfully")
            return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@facebookconnect.route("/page/create", methods=["POST"])
@user_required()
def fb_page_post():

    admin = Admin.query.filter_by(
        organization_id=get_jwt().get("org"), email=get_jwt().get("email"),
    ).first()

    if admin.facebook_connected:
        message = request.json.get("message")
        link = request.json.get("link")
        fb_connection = FacebookDetails.query.filter_by(
            organization_id=get_jwt()["org"], facebook_id=admin.facebook_id
        ).first()
        _page_access_tokens_obj = ast.literal_eval(
            hider.decrypt(fb_connection.page_tokens)
        )
        _msg_response = None
        for _pages in _page_access_tokens_obj.keys():
            page_obj = _page_access_tokens_obj[_pages]
            page_id = page_obj["page_id"]
            page_token = page_obj["page_access_token"]
            params = (
                ("message", message),
                ("link", link),
                ("access_token", page_token),
            )
            _msg_response = requests.post(
                f"https://graph.facebook.com/v12.0/{page_id}/feed", params=params
            )
            if not _msg_response:
                resp = DataResponse(False, _msg_response.json().get("error"))
                return resp.status()
        resp = DataResponse(True, _msg_response.json())
        return resp.status()


@facebookconnect.route("/delete", methods=["DELETE"])
@user_required()
def delete_fb_connection():
    admin = Admin.query.filter_by(
        organization_id=get_jwt().get("org"), email=get_jwt().get("email"),
    ).first()
    if admin.facebook_connected:
        FacebookDetails.query.filter_by(
            organization_id=get_jwt().get("org"), facebook_id=admin.facebook_id,
        ).delete()
        admin.facebook_connected = False
        admin.facebook_id = None
        db.session.commit()
        resp = DataResponse(True, "Connection has been Revoked")
        return resp.status()
    else:
        resp = DataResponse(False, "User not Yet Connected his Facebook Account")
        return resp.status()
