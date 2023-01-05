from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.config import db
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import P2pClassification

classificationviews = Blueprint("classificationviews", __name__, template_folder="templates")


@classificationviews.route('/create', methods=["POST"])
@user_required()
def add_classification():
    name = request.form['name']
    description = request.form['description']
    time_zone = request.form["time_zone"]
    classification = P2pClassification(name=name, description=description, time_zone=time_zone)
    db.session.add(classification)
    db.session.flush()
    classification.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Classification with name: {classification.name} was added successfully",
        "success": True}
    return jsonify(data), 200


@classificationviews.route('/update', methods=["PATCH"])
@user_required()
def update_classification():
    classification_id = request.args.get('id')
    classifications = P2pClassification.query.filter_by(id=classification_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not classifications:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    name = request.form['name']
    description = request.form['description']
    time_zone = request.form["time_zone"]
    classifications.name = name
    classifications.description = description
    classifications.time_zone = time_zone
    P2pClassification(name=name, description=description, time_zone=time_zone)
    db.session.commit()
    data = {
        "message": f" Classification with name: {classifications.name} was updated successfully",
        "success": True}
    return jsonify(data), 200


@classificationviews.route('/all')
@user_required()
def classification_info():
    classifications = P2pClassification.query.all()
    return {"Classification_list": [str(x.id) for x in classifications]}


@classificationviews.route('/info/<classification_id>')
@user_required()
def classification_information(classification_id):
    classifications = P2pClassification.query.filter_by(id=classification_id,organization_id = getOrg(get_jwt())).one_or_none()
    if not classifications:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )

    data = classifications.to_dict()
    return jsonify(data), 200


@classificationviews.route('/delete', methods=["DELETE"])
@user_required()
def classification_delete():
    classification_id = request.args.get('id')
    try:
        P2pClassification.query.filter_by(id=classification_id,organization_id = getOrg(get_jwt())).delete()
        db.session.commit()
        data = {"message": f" ID: {classification_id} was successfully deleted",
                "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
