from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import P2pDonationAmount
from skraggle.config import db

donationamountviews = Blueprint("donationamountviews", __name__, template_folder="templates")


@donationamountviews.route("/create", methods=["POST"])
@user_required()
def add_donationamount():
    amount = request.form["amount"]
    name = request.form["name"]
    description = request.form["description"]
    donation = P2pDonationAmount(amount=amount, name=name, description=description)
    db.session.add(donation)
    db.session.flush()
    donation.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Donation with name: {donation.name} was added successfully",
        "success": True}
    return jsonify(data), 200


@donationamountviews.route("/update", methods=["PATCH"])
@user_required()
def update_donationamount():
    donationAmount_id = request.args.get('id')
    donation = P2pDonationAmount.query.filter_by(id=donationAmount_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not donation:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    amount = request.form["amount"]
    name = request.form["name"]
    description = request.form["description"]
    donation.amount = amount
    donation.name = name
    donation.description = description
    P2pDonationAmount(amount=amount, name=name, description=description)
    db.session.commit()
    data = {
        "message": f" Donation with name: {donation.name} was updated successfully",
        "success": True}
    return jsonify(data), 200


@donationamountviews.route("/all")
@user_required()
def all_donationamount():
    donationAmount= P2pDonationAmount.query.all()
    return {"DonationAmount_list": [str(x.id) for x in donationAmount]}


@donationamountviews.route("/info/<donationAmount_id>")
@user_required()
def donationamount_info(donationAmount_id):
    donationAmount = P2pDonationAmount.query.filter_by(id=donationAmount_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not donationAmount:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = donationAmount.to_dict()
    return jsonify(data), 200


@donationamountviews.route("/delete", methods=['DELETE'])
@user_required()
def delete_donationamount():
    donationAmount_id = request.args.get('id')
    try:
        P2pDonationAmount.query.filter_by(id=donationAmount_id,organization_id=getOrg(get_jwt())).delete()
        db.session.commit()
        data = {"message": f" ID: {donationAmount_id} was successfully deleted",
                "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
