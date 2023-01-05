from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import P2pDedication
from skraggle.config import db

dedicationviews = Blueprint("dedicationviews", __name__, template_folder="templates")


@dedicationviews.route("/create", methods=["POST"])
@user_required()
def add_dedication():
    dedication_text = request.form["dedication_text"]
    dedication = P2pDedication(dedication_text=dedication_text)
    db.session.add(dedication)
    db.session.flush()
    dedication.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Dedication with text: {dedication.dedication_text} was added successfully",
        "success": True,
    }
    return jsonify(data), 200


@dedicationviews.route("/update", methods=["PATCH"])
@user_required()
def update_dedication():
    dedication_id = request.args.get("id")
    dedications = P2pDedication.query.filter_by(
        id=dedication_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not dedications:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    dedication_text = request.form["dedication_text"]
    dedications.dedication_text = dedication_text
    P2pDedication(dedication_text=dedication_text)
    db.session.commit()
    data = {
        "message": f" Dedication with text: {dedications.dedication_text} was updated successfully",
        "success": True,
    }
    return jsonify(data), 200


@dedicationviews.route("/all")
@user_required()
def all_dedication():
    dedication = P2pDedication.query.all()
    return {"Dedication_list": [str(x.id) for x in dedication]}


@dedicationviews.route("/info/<dedication_id>")
@user_required()
def info_dedication(dedication_id):
    dedication = P2pDedication.query.filter_by(
        id=dedication_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not dedication:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = dedication.to_dict()
    return jsonify(data), 200


@dedicationviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_dedication():
    dedication_id = request.args.get("id")
    try:
        P2pDedication.query.filter_by(
            id=dedication_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {
            "message": f" ID: {dedication_id} was successfully deleted",
            "success": True,
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
