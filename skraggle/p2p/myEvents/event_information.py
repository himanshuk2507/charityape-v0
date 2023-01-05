import datetime
from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.base_helpers.orgGen import getOrg
from skraggle.decarotor import user_required
from skraggle.p2p.models import P2pEventInformation
from skraggle.config import db
eventinformationviews = Blueprint("eventinformationviews", __name__)


@eventinformationviews.route("/create", methods=["POST"])
@user_required()
def add_eventinformation():
    internal_event_name = request.form["internal_event_name"]
    event_name = request.form["event_name"]
    status = request.form["status"]
    event_status = status
    fundraising_goal = request.form["fundraising_goal"]
    event_start_date = datetime.datetime.now()
    event_end_date = datetime.datetime.now()
    event_registration_cutoff_date = datetime.datetime.now()
    eventinfo = P2pEventInformation(internal_event_name=internal_event_name, event_name=event_name,
                                    event_start_date=event_start_date, event_end_date=event_end_date,
                                    event_registration_cutoff_date=event_registration_cutoff_date,
                                    event_status=event_status, fundraising_goal=fundraising_goal)
    db.session.add(eventinfo)
    db.session.flush()
    event_status.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Event with Internal Event Name: {eventinfo.internal_event_name} was added successfully",
        "success": True}
    return jsonify(data), 200


@eventinformationviews.route('/update', methods=["PATCH"])
@user_required()
def update_eventinfo():
    eventinfo_id = request.args.get('id')
    eventinformation = P2pEventInformation.query.filter_by(id=eventinfo_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not eventinformation:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    internal_event_name = request.form["internal_event_name"]
    event_name = request.form["event_name"]
    status = request.form["status"]
    event_status = status
    fundraising_goal = request.form["fundraising_goal"]
    eventinformation.internal_event_name = internal_event_name
    eventinformation.event_name = event_name
    eventinformation.event_status = event_status
    eventinformation.fundraising_goal = fundraising_goal
    P2pEventInformation(internal_event_name=internal_event_name, event_name=event_name,
                        event_status=event_status, fundraising_goal=fundraising_goal)
    db.session.commit()
    data = {
        "message": f" Event with Internal Event Name: {eventinformation.internal_event_name} was updated successfully",
        "success": True}
    return jsonify(data), 200


@eventinformationviews.route('/all')
def all_eventinformation():
    eventinfo = P2pEventInformation.query.all()
    data = {
        "message": f" Event Information_list: {[str(x.id) for x in eventinfo]}",
        "success": True
    }
    return jsonify(data), 200


@eventinformationviews.route('/info/<eventinfo_id>')
@user_required()
def info_eventinformation(eventinfo_id):
    eventinfo = P2pEventInformation.query.filter_by(id=eventinfo_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not eventinfo:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = eventinfo.to_dict()
    return jsonify(data), 200


@eventinformationviews.route('/delete', methods=["DELETE"])
@user_required()
def delete_eventinfo():
    events_id = request.args.get("id")
    try:
        eventinfo = P2pEventInformation.query.filter_by(id=events_id,organization_id=getOrg(get_jwt())).delete()
        db.session.commit()
        data = {"message": f" ID: {events_id} was successfully deleted",
                "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
