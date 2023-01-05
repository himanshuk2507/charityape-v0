from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import Donors
from flask import request, Blueprint, jsonify
from skraggle.config import db
from distutils.util import strtobool


p2pdonors = Blueprint("p2pdonors", __name__)


# """
# Api to Add a donor
#
# @parameters : first_name,last_name,address,city,
# country,phone_number,classification,dedication,donate_to,
# email_permission,show_donation_name,show_donation_amount
# """


@p2pdonors.route("/add", methods=["POST"])
@user_required()
def add_donor():
    if request.method == "POST":
        donor_data = {
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "address": request.form["address"],
            "city": request.form["city"],
            "country": request.form["country"],
            "phone_number": request.form["phone_number"],
            "classification": request.form["classification"]
            if "classification" in request.form
            else None,
            "dedication": request.form["dedication"]
            if "dedication" in request.form
            else None,
            "donate_to": request.form["donate_to"],
            "email_permission": bool(strtobool(request.form["email_permission"])),
            "show_donation_name": bool(strtobool(request.form["show_donation_name"])),
            "show_donation_amount": bool(
                strtobool(request.form["show_donation_amount"])
            ),
        }
        donor = Donors(**donor_data)

        db.session.add(donor)
        db.session.flush()
        donor.organization_id = getOrg(get_jwt())
        db.session.commit()
        return jsonify({"status": True, "message": "Added Donor "}), 200


#
# """
# # Api to update a donor
#
# # @parameters : donor_id, first_name,last_name,address,city,
# country,phone_number,classification,dedication,donate_to,
# email_permission,show_donation_name,show_donation_amount
# """


@p2pdonors.route("/update", methods=["PATCH"])
@user_required()
def update_donor():
    updating_fields = [
        "first_name",
        "last_name",
        "address",
        "city",
        "country",
        "phone_number",
        "classification",
        "dedication",
        "donate_to",
        "email_permission",
        "show_donation_name",
        "show_donation_amount",
    ]
    donor_id = request.form["donor_id"]
    donor = Donors.query.filter_by(
        donor_id=donor_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if donor:
        try:
            bool_fields = [
                "email_permission",
                "show_donation_name",
                "show_donation_amount",
            ]
            for field in updating_fields:
                if field in request.form:
                    if field in bool_fields:
                        setattr(donor, field, bool(strtobool(request.form[field])))
                    else:
                        setattr(donor, field, request.form[field])
            db.session.add(donor)
            db.session.commit()
            return (
                jsonify(
                    {"status": True, "message": f"Donor with ID {donor_id} Updated  "}
                ),
                200,
            )
        except Exception as e:

            return (
                jsonify({"status": False, "message": str(e)[:105]}),
                404,
            )
    else:
        return (
            jsonify(
                {
                    "status": False,
                    "message": f"Donor with ID {donor_id} Does not Exist ",
                }
            ),
            404,
        )


# """
# Api to view list of  donors
#
# @parameters : No Parameters Required
# """


@p2pdonors.route("/donors", methods=["GET"])
@user_required()
def view_donors():
    donors_list = Donors.query.all()
    return jsonify({"Donors": [[donor.to_dict()] for donor in donors_list]}), 200


# """
# Api to view list of  donors
#
# @parameters : donor_id
# """


@p2pdonors.route("/donors/<donor_id>", methods=["GET"])
@user_required()
def get_donor(donor_id):
    donor = Donors.query.filter_by(
        donor_id=donor_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if donor:
        return jsonify(donor.to_dict()), 200
    else:
        return (
            jsonify(
                {
                    "status": False,
                    "message": f"Donor with ID {donor_id} Does not Exist ",
                }
            ),
            404,
        )
