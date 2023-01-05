from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy import or_, and_

from skraggle.contact.models import ContactUsers
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.filter_helper import get_filter_clause
from skraggle.base_helpers.pagination_helper import paginator_search
from .models import Pledges, PledgeInstallments
from skraggle.campaigns.models import Association, Campaigns
from skraggle.config import db
import json
import uuid
import os
from werkzeug.utils import secure_filename
from skraggle.config import upload_dir, allowed_file
from datetime import datetime
import math
from skraggle.base_helpers.responser import DataResponse

pledges = Blueprint("pledges", __name__)


@pledges.route("/<int:page_number>", methods=["GET"])
@user_required()
def pledges_view(page_number):
    table = Pledges.query.filter_by(organization_id=getOrg(get_jwt())).order_by("id")
    common_url = "pledges"
    return paginator_search(page_number, table, common_url)


@pledges.route("/search", methods=["GET"])
@user_required()
def pledges_search():
    search_string = request.args.get("query")
    page_number = request.args.get("page_number")
    order_by_column = 'id'
    table = Pledges.query.filter_by(organization_id=getOrg(get_jwt())).filter(
        or_(Pledges.pledge_name.ilike(f'%{search_string}%'),
            Pledges.contact_name.ilike(f'%{search_string}%'))).order_by(
        getattr(Pledges, order_by_column))
    common_url = "pledges"
    return paginator_search(page_number, table, common_url)


@pledges.route("/filter", methods=["GET"])
@user_required()
def filter_pledges():
    search_string = request.args.get("query")
    page_number = request.args.get("page_number")
    list_of_filters = []
    order_by_column = 'id'

    if request.args.get("total_amount"):
        total_amoount = json.loads(request.args.get("total_amount") or b'{}')
        filter_type = total_amoount.get("filter_type")
        values = total_amoount.get("values")
        list_of_filters.append(get_filter_clause(Pledges, "total_amoount", filter_type, values))

    if request.args.get("status"):
        status = json.loads(request.args.get("status") or b'{}')
        filter_type = status.get("filter_type")
        values = status.get("values")
        list_of_filters.append(get_filter_clause(Pledges, "status", filter_type, values))

    if request.args.get("start_date"):
        start_date = json.loads(request.args.get("start_date") or b'{}')
        filter_type = start_date.get("filter_type")
        values = start_date.get("values")
        list_of_filters.append(get_filter_clause(Pledges, "start_date", filter_type, values))

    if request.args.get("end_date"):
        end_date = json.loads(request.args.get("end_date") or b'{}')
        filter_type = end_date.get("filter_type")
        values = end_date.get("values")
        list_of_filters.append(get_filter_clause(Pledges, "end_date", filter_type, values))

    if request.args.get("pledge_type"):
        pledge_type = json.loads(request.args.get("pledge_type") or b'{}')
        filter_type = pledge_type.get("filter_type")
        values = pledge_type.get("values")
        list_of_filters.append(get_filter_clause(Pledges, "pledge_type", filter_type, values))

    if request.args.get("campaign"):
        campaign = json.loads(request.args.get("campaign") or b'{}')
        values = campaign.get("values")
        filter_type = campaign.get("filter_type")
        list_of_filters.append(Pledges.query.filter(
            get_filter_clause(Pledges, "associations", "in",
                              get_filter_clause(Campaigns, "name", filter_type, values).with_entities(
                                  Campaigns.associations).all())))

    if request.args.get("impact_area"):
        impact_area = json.loads(request.args.get("impact_area") or b'{}')
        values = impact_area.get("values")
        filter_type = impact_area.get("filter_type")
        list_of_filters.append(Pledges.query.filter(
            get_filter_clause(Pledges, "associations", "in", get_filter_clause(Association, "impact_area", filter_type, values))))

    common_url = "filter"
    if request.args.get("filter_by") == "all":
        pledges = Pledges.query
        if list_of_filters:
            pledges = pledges.filter(
                and_(a for a in list_of_filters)
            )
        if search_string:
            pledges.filter(
                or_(Pledges.pledge_name.ilike(f'%{search_string}%'),
                    Pledges.contact_name.ilike(f'%{search_string}%'))).order_by(
                getattr(Pledges, order_by_column))
        return paginator_search(page_number, pledges, common_url)
    else:
        pledges = Pledges.query
        if list_of_filters:
            pledges = pledges.filter(
                or_(a for a in list_of_filters)
            )
        if search_string:
            pledges.filter(
                or_(Pledges.pledge_name.ilike(f'%{search_string}%'),
                    Pledges.contact_name.ilike(f'%{search_string}%'))).order_by(
                getattr(Pledges, order_by_column))
        return paginator_search(page_number, pledges, common_url)


@pledges.route('/view/<uuid:pledge_id>', methods=['GET'])
@user_required()
def view_pledge(pledge_id):
    pledge = Pledges.query.filter_by(
        id=pledge_id, organization_id=getOrg(get_jwt())
    ).first()
    if pledge:
        data = pledge.to_dict()
        return DataResponse(True, data).status()
    else:
        return DataResponse(False, f"No Pledge with ID: {pledge_id}").status()


@pledges.route("/installments/<uuid:pledge_id>", methods=["GET"])
@user_required()
def pledges_installments(pledge_id):
    pledge = Pledges.query.filter_by(
        id=pledge_id, organization_id=getOrg(get_jwt())
    ).first()

    installments = PledgeInstallments.query.filter_by(
        pledge_id=pledge_id, organization_id=getOrg(get_jwt())
    ).all()

    if installments:
        data = {
            f"Installments for Pledge = {pledge.pledge_name}": [
                installment.to_dict() for installment in installments
            ]
        }
        return DataResponse(True, data).status()
    else:
        return DataResponse(False, "No installments to display").status()


def calculate_installments(interval, start_date, end_date, total_amount):
    durations = []
    installments = {"dates": [], "amount": []}
    format_date = "%b %d, %Y - %H:%M %p"
    start_date = datetime.strptime(start_date, format_date)
    end_date = datetime.strptime(end_date, format_date)
    num_months = (end_date.year - start_date.year) * 12 + (
        end_date.month - start_date.month
    )
    deltas = 0

    print(num_months)
    if interval.lower() == "weekly":
        deltas = math.ceil((end_date - start_date).days / 7)
    elif interval.lower() == "monthly":
        deltas = math.ceil(num_months / 1)
    elif interval.lower() == "quarterly":
        deltas = math.ceil(num_months / 3)
        print(deltas)
    elif interval.lower() == "annual":
        deltas = math.ceil(num_months / 12)
    delta = (end_date - start_date) // deltas

    for weeks in range(0, deltas):
        durations.append(start_date + weeks * delta)
    amnt = len(durations)
    amnts = float(total_amount) / amnt
    installments["amount"].append(amnts)
    for dates in durations:
        installments["dates"].append(dates.strftime("%Y %b %d %H:%M:%S"))
    return installments


@pledges.route("/add", methods=["POST"])
@user_required()
def pledges_add():
    contact_id = request.json.get("contact_id")
    contact = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).first()
    if contact:
        total_amount = request.json.get("total_amount")
        pledge_type = request.json.get("pledge_type")
        pledge_name = request.json.get("pledge_name")
        start_date = request.json.get("start_date")
        end_date = request.json.get("end_date")
        status = request.json.get("status")
        attachments = request.json.get("attachments")
        contact_name = contact.fullname
        pledge = Pledges(
            total_amount=total_amount,
            pledge_type=pledge_type,
            pledge_name=pledge_name,
            start_date=start_date,
            end_date=end_date,
            status=status,
            contact_name=contact_name,
            attachments=attachments
        )
        contact.donation_pledges.append(pledge)
        db.session.flush()
        pledge.organization_id = getOrg(get_jwt())
        installment = request.json.get("is_installment")

        if installment:
            if "payment_interval" in request.json:
                interval = request.json.get("payment_interval")
                installs = calculate_installments(
                    interval, start_date, end_date, total_amount
                )
                expected_dates = installs["dates"]
                amount = installs["amount"]

                for date in expected_dates:
                    installments = PledgeInstallments(
                        expected_date=date,
                        amount=float(amount[0]),
                        status="pending",
                    )
                    pledge_current = Pledges.query.filter_by(id=pledge.id).first()
                    pledge_current.installments.append(installments)

            else:
                expected_date = request.json.get("expected_date")
                amount = request.json.get("amount")
                expected_dates = expected_date.split(",") if expected_date else []
                amounts = list(map(int, amount.split(","))) if amount else []
                for date, amount in zip(expected_dates, amounts):
                    installments = PledgeInstallments(
                        organization_id=getOrg(get_jwt),
                        expected_date=date, amount=amount, status="pending"
                    )
                    installments.organization_id = getOrg(get_jwt)
                    pledge_current = Pledges.query.filter_by(id=pledge.id, organization_id=getOrg(get_jwt())).first()
                    pledge_current.installments.append(installments)

        db.session.commit()
        resp = DataResponse(True, f"Pledge Created for {contact_name}")
    else:
        resp = DataResponse(False, "Contact Does not Exist to create pledge")
    return resp.status()


@pledges.route("/update/<uuid:pledge_id>", methods=["PATCH"])
@user_required()
def pledges_update(pledge_id):
    pledge = Pledges.query.filter_by(id=pledge_id).first()
    if not pledge:
        return DataResponse(False, f"Pledge with id: {pledge_id} does not exist").status()

    total_amount = request.json.get("total_amount")
    pledge_type = request.json.get("pledge_type")
    pledge_name = request.json.get("pledge_name")
    start_date = request.json.get("start_date")
    end_date = request.json.get("end_date")
    attachments = request.json.get("attachments")

    pledge.total_amount = total_amount or pledge.total_amount
    pledge.pledge_type = pledge_type or pledge.pledge_type
    pledge.pledge_name = pledge_name or pledge.pledge_name
    pledge.start_date = start_date or pledge.start_date
    pledge.end_date = end_date or pledge.end_date
    pledge.attachments = attachments or pledge.attachments
    db.session.commit()

    return DataResponse(True, f"Pledge ID: {pledge_id} Updated").status()


@pledges.route("/associations/<uuid:pledge_id>", methods=["GET"])
@user_required()
def pledges_associations(pledge_id):
    pledge = Pledges.query.filter_by(id=pledge_id, organization_id=getOrg(get_jwt())).first()
    if not pledge:
        return DataResponse(False, f"Pledge ID: {pledge.id} does not exist").status()

    associations = Association.query.filter_by(pledges=pledge.id).first()
    if associations:
        data = associations.to_dict()
        return DataResponse(True, data).status()
    else:
        return DataResponse(False, f"Pledge ID: {pledge.id} has no associations").status()


@pledges.route("/status/<uuid:pledge_id>", methods=["PATCH"])
@user_required()
def pledges_status(pledge_id):
    pledge = Pledges.query.filter_by(id=pledge_id, organization_id=getOrg(get_jwt())).first()
    try:
        if pledge:
            pledge.status = request.json.get("pledge_status")
            db.session.commit()
            resp = DataResponse(True, f"Pledge Status updated to { pledge.status}")
            return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@pledges.route("/installment/status/<uuid:installment_id>", methods=["PATCH"])
@user_required()
def installment_status(installment_id):
    installment = PledgeInstallments.query.filter_by(id=installment_id, organization_id=getOrg(get_jwt())).first()
    try:
        if installment:
            installment.status = request.json.get("installment_status")
            db.session.commit()
            resp = DataResponse(
                True, f"Pledge Installment Status updated to {installment.status}"
            )
            return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@pledges.route("/delete/<uuid:pledge_id>", methods=["DELETE"])
@user_required()
def delete_pledge(pledge_id):
    try:
        PledgeInstallments.query.filter_by(pledge_id=pledge_id, organization_id=getOrg(get_jwt())).delete()
        Pledges.query.filter_by(id=pledge_id, organization_id=getOrg(get_jwt())).delete()

        return DataResponse(True, f"Pledge ID {pledge_id} deleted successfully").status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()