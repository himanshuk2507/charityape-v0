import datetime

from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.config import db
from skraggle.decarotor import user_required
from skraggle.events.models import EventSetting
from skraggle.base_helpers.orgGen import getOrg

eventsettingsviews = Blueprint("eventsettingsviews", __name__)


@eventsettingsviews.route("/create", methods=["POST"])
@user_required()
def add_eventsetting():
    max_number_of_total_participants = request.form["max_number_of_total_participants"]
    event_start_date_setup = datetime.datetime.now()
    event_end_date_setup = datetime.datetime.now()
    event_reg_cut_off_date = datetime.datetime.now()

    eventsettings = EventSetting(
        max_number_of_total_participants=max_number_of_total_participants,
        event_start_date_setup=event_start_date_setup,
        event_end_date_setup=event_end_date_setup,
        event_reg_cut_off_date=event_reg_cut_off_date,
    )
    db.session.add(eventsettings)
    db.session.flush()
    eventsettings.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Event Setting with Max number of total participants: {eventsettings.max_number_of_total_participants} was added successfully",
        "success": True,
    }
    return jsonify(data), 200


@eventsettingsviews.route("/clone", methods=["POST"])
@user_required()
def clone_event():
    eventsetting_id = request.args.get("id")
    clone_eventsSettings = EventSetting.query.filter_by(
        id=eventsetting_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not clone_eventsSettings:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    max_number_of_total_participants = (
        clone_eventsSettings.max_number_of_total_participants
    )
    event_start_date_setup = clone_eventsSettings.event_start_date_setup
    event_end_date_setup = clone_eventsSettings.event_end_date_setup
    event_reg_cut_off_date = clone_eventsSettings.event_reg_cut_off_date
    eventsettings = EventSetting(
        max_number_of_total_participants=max_number_of_total_participants,
        event_start_date_setup=event_start_date_setup,
        event_end_date_setup=event_end_date_setup,
        event_reg_cut_off_date=event_reg_cut_off_date,
    )
    db.session.add(eventsettings)
    db.session.flush()
    eventsettings.organization_id = getOrg(get_jwt())
    db.session.commit()

    data = {
        "message": f" Event with name: {eventsettings.max_number_of_total_participants} was clone successfully from "
        f"Event Setting ID {eventsetting_id} ",
        "success": True,
    }
    return jsonify(data), 200


@eventsettingsviews.route("/update", methods=["PATCH"])
@user_required()
def update_eventsettings():
    eventsetting_id = request.args.get("id")
    update_eventsettings = EventSetting.query.filter_by(
        id=eventsetting_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not update_eventsettings:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )

    max_number_of_total_participants = request.form["max_number_of_total_participants"]
    event_start_date_setup = datetime.datetime.now()
    event_end_date_setup = datetime.datetime.now()
    event_reg_cut_off_date = datetime.datetime.now()
    update_eventsettings.max_number_of_total_participants = (
        max_number_of_total_participants
    )
    update_eventsettings.event_start_date_setup = event_start_date_setup
    update_eventsettings.event_end_date_setup = event_end_date_setup
    update_eventsettings.event_reg_cut_off_date = event_reg_cut_off_date

    EventSetting(
        max_number_of_total_participants=max_number_of_total_participants,
        event_start_date_setup=event_start_date_setup,
        event_end_date_setup=event_end_date_setup,
        event_reg_cut_off_date=event_reg_cut_off_date,
    )
    db.session.commit()
    data = {
        "message": f" Event Setting with Max number of total participants: {update_eventsettings.max_number_of_total_participants} was updated successfully",
        "success": True,
    }
    return jsonify(data), 200


@eventsettingsviews.route("/all")
@user_required()
def all_eventsettings():
    event_settings = EventSetting.query.all()
    data = {
        "message": f" Event Setting_list: {[str(x.id) for x in event_settings]}",
        "success": True,
    }
    return jsonify(data), 200


@eventsettingsviews.route("/info/<eventsetting_id>")
@user_required()
def info_eventsettings(eventsetting_id):
    eventsetting = EventSetting.query.filter_by(
        id=eventsetting_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not eventsetting:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    Data = eventsetting.to_dict()
    return jsonify(Data), 200


@eventsettingsviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_eventsettings():
    eventsetting_id = request.args.get("id")
    try:
        EventSetting.query.filter_by(
            id=eventsetting_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {
            "message": f" ID: {eventsetting_id} was successfully deleted",
            "success": True,
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
