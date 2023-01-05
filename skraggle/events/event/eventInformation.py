from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.events.models import EventsInformation
from skraggle.config import db
from skraggle.base_helpers.orgGen import getOrg

eventinfoviews = Blueprint("eventinfoviews", __name__)


@eventinfoviews.route("/create", methods=["POST"])
@user_required()
def add_eventinfo():
    name = request.form["name"]
    description = request.form["description"]
    venue = request.form["venue"]
    address = request.form["address"]
    state = request.form["state"]
    zip_country = request.form["zip_country"]

    eventinfo = EventsInformation(
        name=name,
        description=description,
        venue=venue,
        address=address,
        state=state,
        zip_country=zip_country,
    )
    db.session.add(eventinfo)
    db.session.flush()
    eventinfo.organization_id = getOrg(get_jwt())
    db.session.commit()

    data = {
        "message": f" Event with name: {eventinfo.name} was added successfully",
        "success": True,
    }
    return jsonify(data), 200


@eventinfoviews.route("/clone", methods=["POST"])
@user_required()
def clone_event():
    event_id = request.args.get("id")
    clone_events = EventsInformation.query.filter_by(
        id=event_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not clone_events:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    name = clone_events.name
    description = clone_events.description
    venue = clone_events.venue
    address = clone_events.address
    state = clone_events.state
    zip_country = clone_events.zip_country
    eventinfo = EventsInformation(
        name=name,
        description=description,
        venue=venue,
        address=address,
        state=state,
        zip_country=zip_country,
    )
    db.session.add(eventinfo)
    db.session.flush()
    eventinfo.organization_id = getOrg(get_jwt())
    db.session.commit()

    data = {
        "message": f" Event with name: {eventinfo.name} was clone successfully from Event_ID {event_id}",
        "success": True,
    }
    return jsonify(data), 200


@eventinfoviews.route("/update", methods=["PATCH"])
@user_required()
def update_eventinfo():
    eventinfo_id = request.args.get("id")
    eventinfo = EventsInformation.query.filter_by(
        id=eventinfo_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not eventinfo:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    name = request.form["name"]
    description = request.form["description"]
    venue = request.form["venue"]
    address = request.form["address"]
    state = request.form["state"]
    zip_country = request.form["zip_country"]
    eventinfo.name = name
    eventinfo.description = description
    eventinfo.venue = venue
    eventinfo.address = address
    eventinfo.state = state
    eventinfo.zip_country = zip_country

    EventsInformation(
        name=name,
        description=description,
        venue=venue,
        address=address,
        state=state,
        zip_country=zip_country,
    )
    db.session.commit()
    data = {
        "message": f" Event with name: {eventinfo.name} was updated successfully",
        "success": True,
    }
    return jsonify(data), 200


@eventinfoviews.route("/all")
@user_required()
def all_eventinfo():
    eventinfo = EventsInformation.query.all()
    data = {
        "message": f" Event_list: {[str(x.id) for x in eventinfo]}",
        "success": True,
    }
    return jsonify(data), 200


@eventinfoviews.route("/info/<event_id>")
@user_required()
def event_info(event_id):
    eventinfo = EventsInformation.query.filter_by(
        id=event_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not eventinfo:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )

    Data = eventinfo.to_dict()
    return jsonify(Data), 200


@eventinfoviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_eventinfo():
    eventinfo_id = request.args.get("id")
    try:
        EventsInformation.query.filter_by(
            id=eventinfo_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {
            "message": f" ID: {eventinfo_id} was successfully deleted",
            "success": True,
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
