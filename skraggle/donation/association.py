from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.campaigns.models import Association, Campaigns
from skraggle.config import db
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator

associationviews = Blueprint("associationviews", __name__, template_folder="templates")


@associationviews.route("/create", methods=["POST"])
@user_required()
def add_association():
    campaign_id = request.args.get('id')
    campaign = Campaigns.query.filter_by(id=campaign_id).one_or_none()
    if not campaign:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    pledges = request.form["pledges"]
    impact_area = request.form["impact_area"]
    source = request.form["source"]
    dedication = request.form["dedication"]
    associations = Association(
        pledges=pledges, impact_area=impact_area, source=source, dedication=dedication)
    campaign.associations.append(associations)
    db.session.flush()
    associations.organization_id = getOrg(get_jwt())
    db.session.commit()

    data = {
        "message": f" Association with source: {associations.source} was added successfully",
        "success": True,
    }
    return jsonify(data), 200


@associationviews.route("/update", methods=["PATCH"])
@user_required()
def update_association():
    association_id = request.args.get("id")
    association = Association.query.filter_by(
        id=association_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not association:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    pledges = request.form["pledges"]
    impact_area = request.form["impact_area"]
    source = request.form["source"]
    dedication = request.form["dedication"]
    association.pledges = pledges
    association.impact_area = impact_area
    association.source = source
    association.dedication = dedication
    Association(
        pledges=pledges, impact_area=impact_area, source=source, dedication=dedication
    )
    db.session.commit()
    data = {
        "message": f" Association with source: {association.source} was updated successfully",
        "success": True,
    }
    return jsonify(data), 200


@associationviews.route("/all/<int:page_number>")
@user_required()
def all_donations(page_number):
    common_url = "association-views/all"
    order_id = "id"
    return paginator(page_number, Association, order_id, common_url)


@associationviews.route("/info/<association_id>")
@user_required()
def donation_info(association_id):
    association = Association.query.filter_by(
        id=association_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not association:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = association.to_dict()
    return jsonify(data), 200


@associationviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_donation():
    association_id = request.args.get("id")
    try:
        Association.query.filter_by(id=association_id, organization_id=getOrg(get_jwt())).delete()
        db.session.commit()
        data = {"message": f" ID: {association_id} was successfully deleted", "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
