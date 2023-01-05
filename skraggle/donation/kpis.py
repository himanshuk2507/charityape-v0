from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt
import numpy as np
from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.base_helpers.responser import DataResponse

from skraggle.config import db
from skraggle.contact.models import ContactUsers, CompanyUsers
from sqlalchemy import extract, func
from datetime import datetime, timedelta

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.donation.models import TransactionDonation
from skraggle.profile.models import Admin

kpiview = Blueprint("kpiview", __name__)
delta = timedelta(days=30)
time_filter = TransactionDonation.created_at >= datetime.now() - delta

def total_donors(org_id):
    return (
        db.session.query(ContactUsers)
        .filter(ContactUsers.organization_id == org_id)
        .filter(ContactUsers.number_of_donations > 0)
        .count()
    )

@kpiview.route("/summary/kpis/median-gift-size", methods=["GET"])
@user_required()
def median_gift_size():
    donors = (
        db.session.query(ContactUsers)
        .filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .filter(ContactUsers.number_of_donations > 0)
        .all()
    )
    donations = []

    for donor in donors:
        donations.append(donor.total_donations)

    median = np.median(donations)
    data = dict(
        donations_count = len(donations),
        median = median
    )

    return DataResponse(True, data).status()
    

@kpiview.route("/summary/kpis/recurring-donors")
@user_required()
def recurring_donors():
    recurring = (
        db.session.query(ContactUsers)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .filter(ContactUsers.number_of_donations > 1)
            .count()
    )
    donor_count = total_donors(getOrg(get_jwt()))

    data = dict(
        count = recurring,
        total = donor_count,
        percentage = f"{recurring/donor_count * 100}%"
    )

    return DataResponse(True, data).status()    


@kpiview.route("/summary/kpis/donor-acquisition")
@user_required()
def donor_acquisition():
    donors_in_last_30_days = (
        db.session.query(ContactUsers)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .filter(ContactUsers.created_on >= datetime.now() - delta)
            .count()
    )
    donor_count = total_donors(getOrg(get_jwt()))

    data = dict(
        count = donors_in_last_30_days,
        total = donor_count,
        percentage = f"{donors_in_last_30_days/donor_count * 100}%"
    )

    return DataResponse(True, data).status()


@kpiview.route("/summary/kpis/donor-retention")
@user_required()
def donor_retention():
    donors_list = (
        ContactUsers.query.filter(ContactUsers.total_donations > 0)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .filter(ContactUsers.number_of_donations > 0)
            .count()
    )

    retained_donors = (
        db.session.query(ContactUsers)
            .filter(ContactUsers.donations_this_year > 0)
            .filter(ContactUsers.donations_last_year > 0)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .count()
    )
    try:
        retention_rate = abs(retained_donors - donors_list) / retained_donors * 100
        data = dict(
            count = retained_donors,
            percentage = retention_rate
        )
        return DataResponse(True, data).status()
    except ZeroDivisionError:
        return DataResponse(True, { "error": "We do not have enough data yet" }).status()

@kpiview.route('/summary/fundraising-activity')
@user_required()
def fundraising_activity():
    org_filter = TransactionDonation.organization_id == getOrg(get_jwt())
    donations = [donation.total_amount for donation in db.session.query(TransactionDonation).filter(
        org_filter
    ).filter(
        time_filter
    ).all()]
    contacts = db.session.query(ContactUsers).filter(
        org_filter
    ).filter(time_filter).all()

    return DataResponse(True, dict(donations = sum(donations), contacts = len(contacts), revenue = 0)).status()


@kpiview.route('/summary/recent-transactions')
@user_required()
def recent_transactions():
    org_filter = TransactionDonation.organization_id == getOrg(get_jwt())
    transactions = [dict_resp(transaction) for transaction in
        db.session.query(TransactionDonation).filter(
        org_filter
    ).filter(time_filter).all()]

    return DataResponse(True, transactions).status()


@kpiview.route("/summary/number-of-contacts")
@user_required()
def contact_count():
    count_1 = (
        db.session.query(ContactUsers)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .count()
    )
    count_2 = (
        db.session.query(CompanyUsers)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .count()
    )
    return DataResponse(True, count_1 + count_2).status()


def get_contacts_monthly():
    curr_month = datetime.now().month
    last_month = curr_month - 1 if curr_month > 1 else 12

    last_month_contacts = (
        db.session.query(ContactUsers)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .filter(extract("month", ContactUsers.joined_on) == last_month)
            .count()
    )
    last_month_companies = (
        db.session.query(CompanyUsers)
            .filter(CompanyUsers.organization_id == getOrg(get_jwt()))
            .filter(
            extract("month", CompanyUsers.created_on) == last_month,
            organization_id=getOrg(get_jwt()),
        )
            .count()
    )
    total_last_month = last_month_contacts + last_month_companies

    curr_month_contacts = (
        db.session.query(ContactUsers)
            .filter(extract("month", ContactUsers.joined_on) == int(curr_month), )
            .filter(CompanyUsers.organization_id == getOrg(get_jwt()))
            .count()
    )

    curr_month_companies = (
        db.session.query(CompanyUsers)
            .filter(extract("month", CompanyUsers.created_on) == int(curr_month))
            .filter(CompanyUsers.organization_id == getOrg(get_jwt()))
            .count()
    )
    total_curr_month = curr_month_contacts + curr_month_companies
    return {"total_last_month": total_last_month, "total_curr_month": total_curr_month}


@kpiview.route("/contact_acquisition_rate")
@user_required()
def contact_growth_rate():
    get_contacts = get_contacts_monthly()

    try:
        percent = (
                abs(get_contacts["total_last_month"] - get_contacts["total_curr_month"])
                / get_contacts["total_curr_month"]
                * 100
        )
    except ZeroDivisionError:
        resp = {"contact_growth_rate": "Not enough data"}
        return jsonify(resp)
    resp = {"contact_growth_rate": percent}
    return jsonify(resp)


@kpiview.route("/contacts_acquired_monthly")
@user_required()
def contacts_acquired():
    get_contacts = get_contacts_monthly()
    new_contacts = get_contacts["total_curr_month"]
    resp = {"contacts_acquired_monthly": new_contacts}
    return jsonify(resp)


@kpiview.route("/donor_churn")
@user_required()
def churn_rate():
    donor_all = (
        db.session.query(ContactUsers)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .filter(ContactUsers.donations_this_year > 0)
            .filter(ContactUsers.donations_last_year > 0)
            .count()
    )
    print(donor_all)
    donor_churns = (
        db.session.query(ContactUsers)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .count()
    )
    print(donor_churns)
    donor_churn_rate = abs(donor_all - donor_churns)
    print(donor_churn_rate)
    data = {"Donor_churn_rate": donor_churn_rate}
    return jsonify(data)


# ------------------------- merging ---------------


@kpiview.route("/donor_list_size/<contact_id>")
@user_required()
def donor_list(contact_id):
    donors_list = (
        (db.session.query(func.sum(TransactionDonation.total_amount).filter_by(id=contact_id)).all() > 0)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .count()
    )
    data = {"Donor_list": donors_list}
    return jsonify(data)


@kpiview.route("/second_gift_conversion/<contact_id>")
@user_required()
def info(contact_id):
    second_gift_conversion = (
        ContactUsers.query.filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .filter(TransactionDonation.query.filter_by(id=contact_id).count() >= 2)
            .count()
    )
    data = {"Second_gift_conversion_rate": second_gift_conversion}
    return jsonify(data)


@kpiview.route("/donor_rate/<contact_id>")
@user_required()
def get_donor_rate(contact_id):
    current_month = datetime.now().month
    last_month = current_month - 1 if current_month > 1 else 12

    last_month_donor = (
        db.session.query(ContactUsers)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .filter(extract("month", ContactUsers.joined_on) == last_month)
            .filter(db.session.query(func.sum(TransactionDonation.total_amount).filter_by(id=contact_id)).all() > 0)
            .count()
    )
    current_month_donor = (
        db.session.query(ContactUsers)
            .filter(ContactUsers.organization_id == getOrg(get_jwt()))
            .filter(extract("month", ContactUsers.joined_on) == current_month)
            .filter(db.session.query(func.sum(TransactionDonation.total_amount).filter_by(id=contact_id)).all() > 0)
            .count()
    )
    try:
        donor_rate = (
                abs(last_month_donor - current_month_donor) / current_month_donor * 100
        )
    except ZeroDivisionError:
        resp = {"contact_growth_rate": "Not enough data"}
        return jsonify(resp)
    data = {"Donor_rate": donor_rate}
    return jsonify(data)
