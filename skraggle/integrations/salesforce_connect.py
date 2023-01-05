import os
import webbrowser
import urllib.parse as urlparse
from datetime import datetime

from simple_salesforce import Salesforce
from flask import Flask, Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy import and_

from skraggle.base_helpers.orgGen import getOrg, cache_id_gen
from skraggle.base_helpers.responser import DataResponse
from skraggle.base_helpers.salesforce_helper import (
    SalesforceOAuth2,
    SalesforceMapper,
    SalesforceConnect,
)
from skraggle.config import db
from skraggle.base_helpers.crypter import Crypt
from skraggle.decarotor import user_required
from skraggle.profile.models import Admin
if os.getenv("REDIS_ENABLED"):
    from skraggle.run import cache
from .models import SalesforceDetails, SalesforceMappings

salesforceconnect = Blueprint(
    "salesforceconnect", __name__, template_folder="templates"
)

oauth = SalesforceOAuth2(
    client_id=os.environ.get("SALESFORCE_ID"),
    client_secret=os.environ.get("SALESFORCE_SECRET"),
    redirect_uri=os.environ.get("SALESFORCE_URI"),
    sandbox=False,  # True = test.salesforce.com, False = login.salesforce.com
)


@salesforceconnect.route("/connect", methods=["GET", "POST"])
@user_required()
def sf_call():
    admin = Admin.query.filter_by(
        organization_id=get_jwt()["org"], email=get_jwt()["email"]
    ).first()
    cache_id = cache_id_gen()
    cache.set(
        cache_id,
        {
            "email": admin.email,
            "user_id": str(admin.admin_id),
            "org_id": get_jwt()["org"],
        },
    )
    oauth_redirect = oauth.authorize_login_url(state=cache_id)
    webbrowser.open(oauth_redirect)
    resp = DataResponse(
        True, "Allow Permissions to Connect Your Salesforce Account"
    )
    return resp.status()


@salesforceconnect.route("/callback", methods=["GET"])
def sf_callback():
    code = request.args.get("code")
    cache_id = request.args.get("state")
    logged_user_info = cache.get(cache_id)
    try:
        response = oauth.get_access_token(code)
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    instance_url = response.json()["instance_url"]
    meta_info_url = response.json()["id"]
    scopes = response.json()["scope"]
    try:
        user_info = oauth.get_user_info(access_token, meta_info_url)
        name = user_info.json().get("display_name")
        username = user_info.json().get("username")
        email = user_info.json().get("email")
        hider = Crypt()
        admin = Admin.query.filter_by(
            organization_id=logged_user_info.get("org_id"),
            admin_id=logged_user_info.get("user_id"),
        ).first()
        connection_info = dict(
            belongs_to=admin.admin_id,
            instance_url=instance_url,
            username=username,
            email=email,
            name=name,
            scopes=scopes,
            access_token=hider.encrypt(access_token),
            refresh_token=hider.encrypt(refresh_token),
            connected_on = datetime.now()
        )
        try:
            if admin.salesforce_connected:
                org_id = logged_user_info.get("org_id")
                db.session.query(SalesforceDetails).filter(
                    and_(
                        SalesforceDetails.organization_id == org_id,
                        SalesforceDetails.salesforce_id == admin.salesforce_id,
                    )
                ).update(connection_info, synchronize_session="fetch")
                db.session.commit()
                resp = DataResponse(
                    True, "Salesforce Connection Reauthenticated Successfully "
                )
                return resp.status()
            else:
                connect_salesforce = SalesforceDetails(**connection_info)
                db.session.add(connect_salesforce)
                db.session.flush()
                connect_salesforce.organization_id = logged_user_info.get("org_id")
                admin.salesforce_connected = True
                admin.salesforce_id = connect_salesforce.salesforce_id
                default_mappings = SalesforceMappings(logged_user_info.get("org_id"))
                connect_salesforce.mapping_rules.append(default_mappings)
                db.session.commit()
                resp = DataResponse(True, "Salesforce Connected Successfully ")
                return resp.status()
        except Exception as e:
            resp = DataResponse(False, str(e))
            return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()


@salesforceconnect.route("/create_mapping_rules", methods=["POST"])
@user_required()
def map_rules():
    logged_user = Admin.query.filter_by(
        email=get_jwt()["email"], organization_id=getOrg(get_jwt())
    ).first()
    if logged_user.salesforce_connected:
        try:
            salesforce_id = logged_user.salesforce_id
            default_mappings = SalesforceMappings.query.filter_by(
                organization_id=getOrg(get_jwt()), salesforce_id=salesforce_id
            ).first()
            default_mappings.mappings = request.json
            db.session.commit()
            resp = DataResponse(True, "New Mapping Rules has been created and saved.")
            return resp.status()

        except Exception as e:
            resp = DataResponse(False, str(e))
            return resp.status()
    else:
        resp = DataResponse(True, "User Not yet connected salesforce Account")
        return resp.status()


"""
parameters : sync_type : [import,export]
import: to import  data from salesforce
export: to export data from skraggle db to salesforce
both: sync data from both sides
"""


@salesforceconnect.route("/synchronize/<sync_type>", methods=["GET"])
@user_required()
def synchronize_imports(sync_type):
    logged_user = Admin.query.filter_by(
        email=get_jwt()["email"], organization_id=getOrg(get_jwt())
    ).first()
    if logged_user.salesforce_connected:
        sf = SalesforceConnect(oauth, logged_user)
        conn = sf.get_connection()
        sf = Salesforce(
            instance_url=conn["instance_url"], session_id=conn["access_token"]
        )
        salesforce_id = logged_user.salesforce_id
        mappings_obj = SalesforceMappings.query.filter_by(
            organization_id=getOrg(get_jwt()), salesforce_id=salesforce_id
        ).first()
        map_rules = mappings_obj.mappings
        synchronizer = SalesforceMapper()
        sync_success = synchronizer.sync(
            map_rules["mappings"], getOrg(get_jwt()), sf, sync_type=sync_type
        )
        if not sync_success["success"]:
            resp = DataResponse(False, sync_success["message"])
            return resp.status()
        return jsonify(sync_success), 200
    else:
        resp = DataResponse(True, "User Not yet connected salesforce Account")
        return resp.status()


@salesforceconnect.route("/fields/<object_name>", methods=["GET"])
@user_required()
def fetch_fields(object_name):
    query_url = f"/services/data/v53.0/sobjects/{object_name}/describe/"
    logged_user = Admin.query.filter_by(
        email=get_jwt()["email"], organization_id=getOrg(get_jwt())
    ).first()
    if logged_user.salesforce_connected:
        try:
            sf = SalesforceConnect(oauth, logged_user)
            conn = sf.get_connection()
            columns = sf.get_fields(
                conn["access_token"], conn["instance_url"] + query_url
            )
            fields = [
                {"field_name": x["name"], "field_type": x["type"]}
                for x in columns.json()["fields"]
            ]
            mapper = SalesforceMapper()
            normalized_fields = mapper.normalize_fields(fields)
            field_template = {
                "object_name": object_name,
                "object_fields": normalized_fields,
            }

            return jsonify(field_template)
        except Exception as e:
            resp = DataResponse(False, str(e))
            return resp.status()
    else:
        resp = DataResponse(True, "User Not yet connected salesforce Account")
        return resp.status()


@salesforceconnect.route("/objects", methods=["GET"])
@user_required()
def fetch_objects():
    query_url = f"/services/data/v53.0/sobjects/"
    logged_user = Admin.query.filter_by(
        email=get_jwt()["email"], organization_id=getOrg(get_jwt())
    ).first()
    if logged_user.salesforce_connected:
        sf = SalesforceConnect(oauth, logged_user)
        conn = sf.get_connection()
        columns = sf.get_fields(conn["access_token"], conn["instance_url"] + query_url)
        objs = [
            {
                "object_name": v["name"],
                "object_type": "custom" if v["custom"] else "standard",
            }
            for v in columns.json()["sobjects"]
        ]

        return jsonify(objs), 200
    else:
        resp = DataResponse(True, "User Not yet connected salesforce Account")
        return resp.status()


@salesforceconnect.route("/delete", methods=["DELETE"])
@user_required()
def delete_sf_connection():
    admin = Admin.query.filter_by(
        organization_id=get_jwt().get("org"), email=get_jwt().get("email"),
    ).first()
    if admin.salesforce_connected:
        try:
            SalesforceMappings.query.filter_by(
                organization_id=get_jwt().get("org"), salesforce_id=admin.salesforce_id,
            ).delete()
            SalesforceDetails.query.filter_by(
                organization_id=get_jwt().get("org"), salesforce_id=admin.salesforce_id,
            ).delete()
            db.session.commit()
            admin.facebook_connected = False
            admin.facebook_id = None
            resp = DataResponse(True, "Connection has been Revoked")
            return resp.status()
        except Exception as e:
            resp = DataResponse(False, str(e)[:105])
            return resp.status()
    else:
        resp = DataResponse(False, "User not Yet Connected his Salesforce Account")
        return resp.status()