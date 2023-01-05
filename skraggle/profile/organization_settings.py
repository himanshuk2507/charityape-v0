import os
import uuid
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt
from werkzeug.utils import secure_filename
from skraggle.config import Config, db, allowed_file, upload_dir
from skraggle.decarotor import user_required, admin_required, user_admin_required
from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.profile.models import OrganizationSettings
from skraggle.validators_logics.validators import OrganizationValidator
from pydantic import ValidationError

orgsettings = Blueprint("orgsettings", __name__, template_folder="templates")


@orgsettings.route("", methods=["GET"])
@user_required()
def org_details():
    organization = OrganizationSettings.query.all()
    return jsonify(dict_resp(organization)), 200


@orgsettings.route("/add", methods=["POST"])
@user_admin_required()
def org_create():
    org_data = {
        "organization_name": request.form.get("organization_name"),
        "organization_email": request.form.get("organization_email"),
        "address": request.form.get("address"),
        "organization_phone": request.form.get("organization_phone"),
        "organization_website": request.form.get("organization_website"),
        "timezone": request.form.get("timezone"),
        "organization_logo": None,
        "statement_description": request.form.get("statement_description"),
        "is_legal": bool(request.form.get("is_legal")),
        "tax_exemption_verification": None,
    }

    uploads = ["organization_logo", "tax_exemption_verification"]
    for file in uploads:
        if file in request.files:
            fileObj = request.files[file]
            if fileObj and allowed_file(fileObj.filename):
                filename = secure_filename(fileObj.filename)
                fileext = os.path.splitext(filename)
                filename = str(uuid.uuid4()) + fileext[-1]
                if not os.path.exists(f"{upload_dir}/others"):
                    os.makedirs(f"{upload_dir}/others")
                fileObj.save(os.path.join(f"{upload_dir}/others", filename))
                org_data[file] = "{}/{}".format(f"{upload_dir}/others", filename)
    print(org_data)
    try:
        is_valid = OrganizationValidator(**org_data)
        if is_valid:
            print(type(org_data["organization_logo"]))
            add_organization = OrganizationSettings(**org_data)
            db.session.add(add_organization)
            db.session.flush()
            add_organization.organization_id = getOrg(get_jwt())
            db.session.commit()
            resp = DataResponse(True, "Organization Added")
            return resp.status()
    except ValidationError as e:
        return e.json()


@orgsettings.route("/settings", methods=["PATCH"])
@user_admin_required()
def org_update():
    updating_fields = [
        "organization_name",
        "organization_email",
        "address",
        "organization_phone",
        "organization_website",
        "timezone",
        "organization_logo",
        "statement_description",
        "is_legal",
        "tax_exemption_verification",
    ]
    if request.method == "PATCH":
        organization = OrganizationSettings.query.filter_by(
            organization_id=getOrg(get_jwt())
        ).first()
        try:
            for fields in updating_fields:
                if fields in request.form:
                    if fields == "is_legal":
                        setattr(
                            organization,
                            fields,
                            None
                            if not request.form[fields]
                            else bool(request.form[fields]),
                        )
                    else:
                        setattr(
                            organization,
                            fields,
                            None if not request.form[fields] else request.form[fields],
                        )
            db.session.add(organization)
            db.session.commit()
            resp = DataResponse(True, "Organization Settings were Updated")
            return resp.status()
        except Exception as e:
            resp = DataResponse(False, str(e))
            return resp.status()
