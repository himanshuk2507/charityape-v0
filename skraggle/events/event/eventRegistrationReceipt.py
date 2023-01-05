from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.config import db
from skraggle.decarotor import user_required
from skraggle.events.models import EventRegisterationReciept
from skraggle.base_helpers.orgGen import getOrg

eventregisterationrecieptviews = Blueprint("eventregisterationrecieptviews", __name__)


@eventregisterationrecieptviews.route("/create", methods=["POST"])
@user_required()
def add_reciept():
    title = request.form["title"]
    description = request.form["description"]
    from_name = request.form["from_name"]
    subject = request.form["subject"]
    body = request.form["body"]

    reciept = EventRegisterationReciept(
        title=title,
        description=description,
        from_name=from_name,
        subject=subject,
        body=body,
    )
    db.session.add(reciept)
    db.session.flush()
    reciept.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Event Registeration Reciept with title: {reciept.title} was added successfully",
        "success": True,
    }
    return jsonify(data), 200


@eventregisterationrecieptviews.route("/clone", methods=["POST"])
@user_required()
def clone_event():
    reciept_id = request.args.get("id")
    clone_EventRegisterationReciept = EventRegisterationReciept.query.filter_by(
        id=reciept_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not clone_EventRegisterationReciept:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    title = clone_EventRegisterationReciept.title
    description = clone_EventRegisterationReciept.description
    from_name = clone_EventRegisterationReciept.from_name
    subject = clone_EventRegisterationReciept.subject
    body = clone_EventRegisterationReciept.body
    reciept = EventRegisterationReciept(
        title=title,
        description=description,
        from_name=from_name,
        subject=subject,
        body=body,
    )
    db.session.add(reciept)
    db.session.flush()
    reciept.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Event Registeration Reciept with title: {reciept.title} was clone successfully fom Receipt_id  {reciept_id}",
        "success": True,
    }
    return jsonify(data), 200


@eventregisterationrecieptviews.route("/update", methods=["PATCH"])
@user_required()
def update_reciept():
    reciept_id = request.args.get("id")
    reciepts = EventRegisterationReciept.query.filter_by(
        id=reciept_id, organization_id=getOrg(get_jwt())
    ).one_or_none()

    title = request.form["title"]
    description = request.form["description"]
    from_name = request.form["from_name"]
    subject = request.form["subject"]
    body = request.form["body"]
    reciepts.title = title
    reciepts.description = description
    reciepts.from_name = from_name
    reciepts.subject = subject
    reciepts.body = body
    EventRegisterationReciept(
        title=title,
        description=description,
        from_name=from_name,
        subject=subject,
        body=body,
    )
    db.session.commit()
    data = {
        "message": f" Event Registeration Reciept with title: {reciepts.title} was updated successfully",
        "success": True,
    }
    return jsonify(data), 200


@eventregisterationrecieptviews.route("/all")
@user_required()
def all_reciept():
    reciepts = EventRegisterationReciept.query.all()
    data = {
        "message": f" Event Registeration Reciept_list: {[str(x.id) for x in reciepts]}",
        "success": True,
    }
    return jsonify(data), 200


@eventregisterationrecieptviews.route("/info/<reciept_id>")
@user_required()
def reciept_info(reciept_id):
    reciepts = EventRegisterationReciept.query.filter_by(
        id=reciept_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not reciepts:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )

    Data = reciepts.to_dict()
    return jsonify(Data), 200


@eventregisterationrecieptviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_reciept():
    reciept_id = request.args.get("id")
    try:
        EventRegisterationReciept.query.filter_by(
            id=reciept_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {
            "message": f" ID: {reciept_id} was successfully deleted",
            "success": True,
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
