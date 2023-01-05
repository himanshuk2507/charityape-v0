from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.base_helpers.next_schedule_day import ScheduleDay
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator
from .models import ScheduleRecurringRevenue
from skraggle.contact.models import ContactUsers
from skraggle.config import db

schedule_recurring_revenues = Blueprint(
    "schedule_recurring_revenues", __name__, template_folder="templates"
)


@schedule_recurring_revenues.route("/create", methods=["POST"])
@user_required()
def add_revenue():
    contact_id = request.args.get("id")
    contact = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not contact:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    total_amount = request.form["total_amount"]
    billing_cycle = request.form["billing_cycle"]
    value = request.form["status"]
    status = value
    revenue = ScheduleRecurringRevenue(
        total_amount=total_amount, billing_cycle=billing_cycle, status=status
    )
    contact.schedule_recurring_revenues.append(revenue)
    db.session.flush()
    revenue.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Schedule Recurring Revenue with billing cycle: {revenue.billing_cycle} was added successfully",
        "success": True,
    }
    return jsonify(data), 200


@schedule_recurring_revenues.route("/update", methods=["PATCH"])
@user_required()
def update_revenue():
    scheduleRevenue_id = request.args.get("id")
    revenue = ScheduleRecurringRevenue.query.filter_by(
        id=scheduleRevenue_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not revenue:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    total_amount = request.form["total_amount"]
    billing_cycle = request.form["billing_cycle"]
    value = request.form["status"]
    status = value
    revenue.total_amount = total_amount
    revenue.billing_cycle = billing_cycle
    revenue.status = status
    ScheduleRecurringRevenue(
        total_amount=total_amount, billing_cycle=billing_cycle, status=status
    )
    db.session.commit()
    data = {
        "message": f" Schedule Recurring Revenue with billing cycle: {revenue.billing_cycle} was updated successfully",
        "success": True,
    }
    return jsonify(data), 200


@schedule_recurring_revenues.route("/all/<int:page_number>", methods=["GET"])
@user_required()
def all_revenue(page_number):
    common_url = "schedule-recurring-revenues/all"
    order_id = "id"
    return paginator(page_number, ScheduleRecurringRevenue, order_id, common_url)


@schedule_recurring_revenues.route("/info/<scheduleRevenue_id>", methods=["GET"])
@user_required()
def revenue_info(scheduleRevenue_id):
    scheduleRevenue = ScheduleRecurringRevenue.query.filter_by(
        id=scheduleRevenue_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not scheduleRevenue:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = dict_resp(scheduleRevenue)
    num, days_type = scheduleRevenue.billing_cycle.split(" ")
    get_day = ScheduleDay(num, days_type.lower())
    data["next_scheduled_date"] = get_day.next_date()
    return jsonify(data), 200


@schedule_recurring_revenues.route("/delete", methods=["DELETE"])
@user_required()
def delete_revenue():
    scheduleRevenue_id = request.args.get("id")
    try:
        ScheduleRecurringRevenue.query.filter_by(
            id=scheduleRevenue_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {
            "message": f" ID: {scheduleRevenue_id} was successfully deleted",
            "success": True,
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
