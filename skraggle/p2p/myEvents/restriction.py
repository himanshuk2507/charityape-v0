from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import P2pRestrictions
from skraggle.config import db

restrictionviews = Blueprint("restrictionviews", __name__, template_folder="templates")


@restrictionviews.route("/create", methods=["POST"])
@user_required()
def add_restriction():
    name = request.form["name"]
    description = request.form["description"]
    restrictions = P2pRestrictions(name=name, description=description)
    db.session.add(restrictions)
    db.session.flush()
    restrictions.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Restriction with Name: {restrictions.name} was added successfully",
        "success": True}
    return jsonify(data), 200


@restrictionviews.route("/update", methods=["PATCH"])
@user_required()
def update_restriction():
    restriction_id = request.args.get('id')
    restrictions = P2pRestrictions.query.filter_by(id=restriction_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not restrictions:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    name = request.form["name"]
    description = request.form["description"]
    restrictions.name = name
    restrictions.description = description
    P2pRestrictions(name=name, description=description)
    db.session.commit()
    data = {
        "message": f" Restriction with Name: {restrictions.name} was updated successfully",
        "success": True}
    return jsonify(data), 200


@restrictionviews.route("/all")
@user_required()
def all_restriction():
    restriction = P2pRestrictions.query.all()
    return {"Restriction_list": [str(x.id) for x in restriction]}


@restrictionviews.route("/info/<restriction_id>")
@user_required()
def info_restriction(restriction_id):
    restriction = P2pRestrictions.query.filter_by(id=restriction_id,organization_id = getOrg(get_jwt())).one_or_none()
    if not restriction:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = restriction.to_dict()
    return jsonify(data), 200


@restrictionviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_restriction():
    restriction_id = request.args.get('id')
    try:
        P2pRestrictions.query.filter_by(id=restriction_id,organization_id = getOrg(get_jwt())).delete()
        db.session.commit()
        data = {"message": f" ID: {restriction_id} was successfully deleted",
                "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400

