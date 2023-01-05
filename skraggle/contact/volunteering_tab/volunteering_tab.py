from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt

from skraggle.contact.models import VolunteerActivity
from skraggle.config import db
from werkzeug.utils import secure_filename
import os
from skraggle.config import upload_dir
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg

volunteertab = Blueprint("volunteertab", __name__)
import uuid


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "docx"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@volunteertab.route("/activities/create", methods=["GET", "POST"])
@user_required()
def activity_add():
    resp = {"Data": "", "attachment": "NA"}
    if request.method == "POST":
        activity_name = request.form["activity_name"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        desc = request.form["desc"]
        impact_area = request.form["impact_area"]
        compaign = request.form["campaign"]
        activity = VolunteerActivity(
            activity_name=activity_name,
            start_date=start_date,
            end_date=end_date,
            desc=desc,
            impact_area=impact_area,
            compaign=compaign,
        )

        resp["Data"] = "Activity Created"
        db.session.add(activity)
        if "attachment" in request.files:

            file = request.files["attachment"]
            if file.filename == "":

                resp["attachment"] = "No file selected for uploading"

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                fileext = os.path.splitext(filename)
                print(fileext)
                activity_current = VolunteerActivity.query.order_by(
                    -VolunteerActivity.id
                ).first()
                filename = str(uuid.uuid4()) + fileext[-1]
                activity_current.attachment_name = filename
                file.save(os.path.join(upload_dir, filename))

                activity_current.attachments = "{}\{}".format(upload_dir, filename)
                activity_current.attachments_name = filename

                resp["attachment"] = "attachment uploaded succesfully"
            else:
                resp["attachment"] = "Filetype not Allowed"

        db.session.flush()
        activity.organization_id = getOrg(get_jwt())
        db.session.commit()

    return jsonify(resp)


@volunteertab.route("/activities/delete")
@user_required()
def activity_delete_multi():
    activity_ids = request.args.get("activity_id")
    resp = {"Status": ""}
    ids = activity_ids.split(",")

    activity = (
        db.session.query(VolunteerActivity)
        .filter(VolunteerActivity.organization_id == getOrg(get_jwt()))
        .filter(VolunteerActivity.id.in_(ids))
        .all()
    )

    if activity:
        for active in activity:
            db.session.delete(active)
        db.session.commit()
        resp["Status"] = "Activity Deleted"
    else:
        resp["Status"] = "Activity Does not Exist"
    return jsonify(resp)
