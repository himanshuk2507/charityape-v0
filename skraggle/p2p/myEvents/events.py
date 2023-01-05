from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt
from skraggle.config import db
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import P2pEventContactInformation

eventviews = Blueprint("eventviews", __name__, template_folder="templates")


@eventviews.route("/create", methods=["POST"])
@user_required()
def event_add():
    contact_first_name = request.form["contact_first_name"]
    contact_last_name = request.form["contact_last_name"]
    contact_email = request.form["contact_email"]
    contact_address = request.form["contact_address"]
    contact_phone_number = request.form["contact_phone_number"]
    from_email_address = request.form["from_email_address"]
    from_name = request.form["from_name"]

    events = P2pEventContactInformation(
        contact_first_name=contact_first_name,
        contact_last_name=contact_last_name,
        contact_email=contact_email,
        contact_address=contact_address,
        contact_phone_number=contact_phone_number,
        from_email_address=from_email_address,
        from_name=from_name
    )
    db.session.add(events)
    db.session.flush()
    events.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Events with Contact first name: {events.contact_first_name} was added successfully",
        "success": True,
    }
    return jsonify(data), 200


@eventviews.route("/update", methods=["PATCH"])
@user_required()
def event_update():
    event_id = request.args.get("id")
    update_event = P2pEventContactInformation.query.filter_by(
        id=event_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not update_event:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    if update_event:
        data = dict(request.form)
        fields_to_update = [
            "contact_first_name",
            "contact_last_name",
            "contact_email",
            "contact_address",
            "contact_phone_number",
            "from_email_address",
            "from_name"
        ]

        for field in fields_to_update:

            if getattr(update_event, field) != data[field]:
                setattr(update_event, field, data[field])
        db.session.commit()
    else:
        return jsonify({"Error": "Event Does not exist"})
    data = {
        "message": f" Events with Contact first name: {update_event.contact_first_name} was updated successfully",
        "success": True,
    }
    return jsonify(data), 200


@eventviews.route("/all")
@user_required()
def event_all():
    events = P2pEventContactInformation.query.all()
    data = {"Events_list": [str(x.id) for x in events]}
    return jsonify(data), 200


@eventviews.route("/info/<event_id>")
@user_required()
def event_info(event_id):
    events = P2pEventContactInformation.query.filter_by(
        id=event_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not events:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = events.to_dict()
    return jsonify(data), 200


@eventviews.route("/delete", methods=["DELETE"])
@user_required()
def event_delete():
    event_id = request.args.get("id")
    try:
        P2pEventContactInformation.query.filter_by(
            id=event_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {"message": f" ID: {event_id} was successfully deleted", "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
