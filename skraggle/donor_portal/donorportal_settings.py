from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.base_helpers.updating_fields_fetch import get_fields
from skraggle.decarotor import user_required
from skraggle.donor_portal.models import DonorPortal
from skraggle.config import db

donorportalsettings = Blueprint("donorportalsettings", __name__)


@donorportalsettings.route("/settings", methods=["POST"])
@user_required()
def portal_settings():
    donor_settings = dict(
        portal_url=None,
        browse_icon=None,
        header_image=None,
        portal_title=None,
        recurring_donation_cancellation=False,
        reduce_donation_amount=False,
        skip_recurring_donation=False,
    )
    bool_fields = [
        "recurring_donation_cancellation",
        "reduce_donation_amount",
        "skip_recurring_donation",
    ]
    for field in donor_settings.keys():
        if field in request.form:
            if field in bool_fields:
                donor_settings[field] = bool(request.form.get(field))
            else:
                donor_settings[field] = request.form.get(field)
    try:
        donor_portal = DonorPortal(**donor_settings)
        db.session.add(donor_portal)
        db.session.flush()
        donor_portal.organization_id = getOrg(get_jwt())
        db.session.commit()
        resp = DataResponse(True, "Settings Created and Updated successfully")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()


@donorportalsettings.route("/update", methods=["PATCH"])
@user_required()
def update_donorportal():
    portal_id = request.form.get("portal_id")
    portal = DonorPortal.query.filter_by(
        id=portal_id, organization_id=getOrg(get_jwt())
    ).first()
    if portal:
        updating_fields = get_fields(DonorPortal)
        bool_fields = [
            "recurring_donation_cancellation",
            "reduce_donation_amount",
            "skip_recurring_donation",
        ]
        try:
            for field in updating_fields:
                if field in request.form:
                    if field in bool_fields:
                        setattr(portal, field, bool(request.form.get(field)))
                    else:
                        setattr(portal, field, request.form.get(field))
            db.session.add(portal)
            db.session.commit()
            resp = DataResponse(True, f"DonorPortal with Given {portal_id} Updated")
            return resp.status()
        except Exception as e:
            resp = DataResponse(False, str(e)[:105])
            return resp.status()
    else:
        resp = DataResponse(False, f"DonorPortal with Given {portal_id} does not exist")
        return resp.status()
