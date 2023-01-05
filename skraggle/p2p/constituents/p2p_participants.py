from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import Participants
from flask import request, redirect, Blueprint, jsonify
from skraggle.config import db

p2pparticipants = Blueprint("p2pparticipants", __name__)


@p2pparticipants.route("/add", methods=["POST"])
@user_required()
def add_participants():
    if request.method == "POST":
        participant_data = {
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "full_name": request.form["full_name"],
            "address": request.form["address"],
            "phone_number": request.form["phone_number"],
            "donation_amount": request.form["donation_amount"],
        }
        participant = Participants(**participant_data)
        db.session.add(participant)
        db.session.flush()
        participant.organization_id = getOrg(get_jwt())
        db.session.commit()
        return (
            jsonify(
                {"created": True, "participant_name": participant_data["full_name"]}
            ),
            200,
        )


@p2pparticipants.route("/delete", methods=["DELETE"])
@user_required()
def delete_participants():
    participant_id = request.args.get("participant_id")
    participant = Participants.query.filter_by(
        participant_id=participant_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if participant:
        try:
            db.session.delete(participant)
            db.session.commit()
            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"Deleted {participant_id} Successfully",
                    }
                ),
                200,
            )
        except Exception as e:
            return jsonify({"success": False, "message": str(e)[:105]}), 400
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Participant with ID {participant_id} not found",
                }
            ),
            200,
        )


@p2pparticipants.route("/active-participants", methods=["GET"])
@user_required()
def active_participants():
    participants_list = Participants.query.all()
    data = {
        "Participants": [
            {
                "Participant_id": participant.participant_id,
                "Full_name": participant.full_name,
                "First_name": participant.first_name,
                "Last_name": participant.last_name,
                "Address": participant.address,
                "Phone_number": participant.phone_number,
                "Team": participant.team,
                "Category": participant.category,
                "Classification": participant.classification,
            }
            for participant in participants_list
        ]
    }
    return jsonify(data), 200


@p2pparticipants.route("/participant/<participant_id>", methods=["GET"])
@user_required()
def get_info(participant_id):
    participant = Participants.query.filter_by(
        participant_id=participant_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if participant:
        return jsonify(participant.to_dict()), 200

    else:
        return jsonify({"Error": "Participant Does not Exist"}), 404


# API to update a single participant
@p2pparticipants.route("/participant/update", methods=["PATCH"])
@user_required()
def update_participants():
    participant_id = request.form["participant_id"]
    participant_to_update = Participants.filter_by(
        participant_id=participant_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not participant_to_update:
        return (
            jsonify(
                {"success": False, "message": "The given participant doesn't exist"}
            ),
            404,
        )
    updating_fields = [
        "first_name",
        "last_name",
        "full_name",
        "donation_amount",
        "address",
        "phone_number",
    ]
    try:
        for column in updating_fields:
            setattr(participant_to_update, column, request.form[column]) or None
        db.session.add(participant_to_update)
        db.session.commit()
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Team corresponding to ID: {participant_to_update} updated successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]})
