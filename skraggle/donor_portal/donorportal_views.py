from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy import or_

from skraggle.base_helpers.dict_responser import dict_resp, multi_dict_resp
from skraggle.base_helpers.next_schedule_day import ScheduleDay
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.contact.models import ContactUsers
from skraggle.decarotor import user_required
from skraggle.donation.models import ScheduleRecurringDonation
from skraggle.contact.Fundraising.models import Transactions, TransactionReceipts

donorportalviews = Blueprint("donorportalviews", __name__)


@donorportalviews.route("/recurring_donation/<contact_id>")
@user_required()
def recurring_donation(contact_id):
    recurring_donation = ScheduleRecurringDonation.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not donation_history:
        resp = DataResponse(False, "No Recurring Donations found ")
        return resp.status()
    data = dict_resp(recurring_donation)
    num, days_type = recurring_donation.billing_cycle.split(" ")
    get_day = ScheduleDay(num, days_type.lower())
    data["next_scheduled_date"] = get_day.next_date()
    return jsonify(data), 200


@donorportalviews.route("/donation_history/<contact_id>")
@user_required()
def donation_history(contact_id):
    donation_history = (
        Transactions.query.filter(
            or_(
                Transactions.contact_id == contact_id,
                Transactions.donor_id == contact_id,
            )
        )
        .filter(Transactions.organization_id == getOrg(get_jwt()))
        .all()
    )
    if not donation_history:
        resp = DataResponse(False, "Donation History Empty ")
        return resp.status()
    donations = {}
    for idx, donation in enumerate(donation_history):
        donations[f"Donation-{idx+1}"] = dict_resp(donation)
        trans_receipt = donation.receipts if donation.receipts else ""
        donations[f"Donation-{idx+1}"]["receipt"] = (
            dict_resp(trans_receipt[0]) if trans_receipt != "" else "No Receipt"
        )
    return jsonify(donations), 200


@donorportalviews.route("/donor_details/<contact_id>")
@user_required()
def donor_details(contact_id):
    contact = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).first()
    if not contact:
        resp = DataResponse(
            False, "No Contact Found with the given ID - {}".format(contact_id)
        )
        return resp.status()
    donor_data = dict(donor_name=contact.fullname, donor_email=contact.primary_email)
    return jsonify(donor_data), 200
