from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import WelcomeGuests
from skraggle.config import db
from distutils import util

p2pwalkthrough = Blueprint("p2pwalkthrough", __name__, template_folder="templates")


@p2pwalkthrough.route("/walkthrough/<walkthrough_id>", methods=["GET"])
@user_required()
def get_walkthrough(walkthrough_id):
    walkthrough = WelcomeGuests.query.filter_by(walkthrough=walkthrough_id,organization_id=getOrg(get_jwt())).first()
    return jsonify(walkthrough.to_dict()), 200


# api to update a walkthrough : Parameters [walkthrough_id]
@p2pwalkthrough.route("/update", methods=["PATCH"])
@user_required()
def update_walkthrough():
    walkthrough_id = request.form["walkthrough_id"]
    walkthrough = WelcomeGuests.query.filter_by(walkthrough=walkthrough_id,organization_id=getOrg(get_jwt())).first()
    if walkthrough:
        fields_to_update = [
            "welcome_quest",
            "upload_your_avatar",
            "update_your_personal_page",
            "send_a_fundraising_email",
            "raise_your_first_donation",
            "recruit_a_team_member",
            "share_on",
        ]
        try:
            for field in fields_to_update:
                setattr(
                    walkthrough, field, bool(util.strtobool(request.form[field]))
                ) or True
            db.session.add(walkthrough)
            db.session.flush()
            # to calculate steps by fetching number of fields enabled to True in a Walkthrough out of 6 fields
            curent_walkthrough = WelcomeGuests.query.filter_by(
                walkthrough=walkthrough.walkthrough
            ).first()
            walkthrough_steps = curent_walkthrough.to_dict()
            steps = 0
            for step in walkthrough_steps.keys():
                if (
                    step in fields_to_update
                    and step != "welcome_quest"
                    and walkthrough_steps[step]
                ):
                    steps += 1
            curent_walkthrough.steps = steps
            db.session.commit()
            return (
                jsonify(
                    {"success": True, "message": f"walkthrough updated successfully."}
                ),
                200,
            )
        except Exception as e:
            return jsonify({"success": False, "message": str(e)[:105]}), 404
    else:
        return jsonify({"success": False, "message": "Walkthrough not found"}), 404


@p2pwalkthrough.route("/add", methods=["POST"])
@user_required()
def create_walkthrough():
    walkthrough_info = {
        "welcome_quest": True,
        "upload_your_avatar": True,
        "update_your_personal_page": True,
        "send_a_fundraising_email": True,
        "raise_your_first_donation": True,
        "recruit_a_team_member": True,
        "share_on": True,
    }
    for key in walkthrough_info.keys():
        if key in request.form:
            walkthrough_info[key] = bool(util.strtobool(request.form[key]))
    walkthrough_data = WelcomeGuests(**walkthrough_info)
    db.session.add(walkthrough_data)
    db.session.flush()
    walkthrough_data.organization_id = getOrg(get_jwt())
    # to calculate steps by fetching number of fields enabled to True in a Walkthrough out of 6 fields
    curent_walkthrough = WelcomeGuests.query.filter_by(
        walkthrough=walkthrough_data.walkthrough,organization_id=getOrg(get_jwt())
    ).first()
    walkthrough_steps = curent_walkthrough.to_dict()
    steps = 0
    for step in walkthrough_steps.keys():
        if (
            step in walkthrough_info.keys()
            and step != "welcome_quest"
            and walkthrough_steps[step]
        ):
            steps += 1
    curent_walkthrough.steps = steps
    db.session.commit()
    return (
        jsonify({"success": True, "message": f"walkthrough created successfully."}),
        200,
    )
