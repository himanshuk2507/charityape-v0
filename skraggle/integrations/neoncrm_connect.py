from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from skraggle.base_helpers.neoncrm_helper import NeonConnect
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.config import db
from skraggle.decarotor import user_required
from skraggle.integrations.models import NeonCrmDetails
from skraggle.profile.models import Admin

neoncrmconnect = Blueprint("neoncrmconnect", __name__, template_folder="templates")


@neoncrmconnect.route("/connect", methods=["GET"])
@user_required()
def connect_neon():
    api_key = request.form.get("api_key")
    org_id = request.form.get("org_id")
    connection = NeonConnect(api_key=api_key, org_id=org_id)
    success, session_resp = connection.getSession()
    if not success:
        resp = DataResponse(False, str(session_resp)[:105])
        return resp.status()
    try:
        admin = Admin.query.filter_by(
            organization_id=getOrg(get_jwt()), email=get_jwt()["email"],
        ).first()
        NeonCrm = NeonCrmDetails(
            api_key=api_key,
            org_id=org_id,
            session_id=session_resp,
            connected_on=datetime.now(),
            belongs_to=admin.admin_id,
        )
        db.session.add(NeonCrm)
        db.session.flush()
        NeonCrm.organization_id = getOrg(get_jwt())
        db.session.commit()
        resp = DataResponse(True, "Neon Crm Has Been Connected Successfully")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()
