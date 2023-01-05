from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.events.models import Fields, Packages
from skraggle.config import db
from skraggle.base_helpers.orgGen import getOrg

fieldviews = Blueprint("fieldviews", __name__)


@fieldviews.route('/create', methods=["POST"])
@user_required()
def add_fields():
    package_id = request.args.get('id')
    packages = Packages.query.filter_by(id=package_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not packages:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    field_label = request.form["field_label"]
    reporting_label = request.form["reporting_label"]
    field_type = request.form["field_type"]
    field = Fields(field_label=field_label, reporting_label=reporting_label, field_type=field_type)
    packages.fields.append(field)
    db.session.flush()
    field.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Field with Label: {field.field_label} was added successfully",
        "success": True}
    return jsonify(data), 200


@fieldviews.route('/update', methods=["PATCH"])
@user_required()
def update_fields():
    field_id = request.args.get('id')
    fields = Fields.query.filter_by(id=field_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not fields:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    field_label = request.form["field_label"]
    reporting_label = request.form["reporting_label"]
    field_type = request.form["field_type"]
    fields.field_label = field_label
    fields.reporting_label = reporting_label
    fields.field_type = field_type
    Fields(field_label=field_label, reporting_label=reporting_label, field_type=field_type)
    db.session.commit()
    data = {
        "message": f" Field with Label: {fields.field_label} was updated successfully",
        "success": True}
    return jsonify(data), 200


@fieldviews.route('/all',methods=["GET"])
@user_required()
def all_fields():
    fields = Fields.query.all()
    data = {
        "message": f" Field_list: {[str(x.id) for x in fields]}",
        "success": True
    }
    return jsonify(data), 200


@fieldviews.route('/info/<field_id>',methods=["GET"])
@user_required()
def fields_info(field_id):
    fields = Fields.query.filter_by(id=field_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not fields:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    Data = fields.to_dict()
    return jsonify(Data), 200


@fieldviews.route('/delete', methods=["DELETE"])
@user_required()
def delete_fields():
    fields_id = request.args.get('id')
    try:
        Fields.query.filter_by(id=fields_id,organization_id=getOrg(get_jwt())).delete()
        db.session.commit()
        data = {"message": f" ID: {fields_id} was deleted successfully ",
                "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
