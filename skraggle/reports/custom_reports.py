from datetime import datetime, date
from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from flask_mail import Message
from sqlalchemy import and_, or_, extract
from skraggle.constants import DEFAULT_PAGE_SIZE, BASE_URL
from skraggle.decarotor import user_required
from skraggle.donation.models import Pledges, ScheduleRecurringDonation
from skraggle.base_helpers.email_sender import report_sender
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.paginator_util import paginated_response
from skraggle.base_helpers.dict_responser import multi_dict_resp
from skraggle.contact.models import ContactUsers, Memberships
from skraggle.run import mail

customreports = Blueprint("customreports", __name__, template_folder="templates")


@customreports.route("/lybunt_contacts/<int:page_number>", methods=["GET"])
@user_required()
def lybunt_contacts(page_number):
    common_url = "reports/lybunt_contacts"
    report_for = "lybunt_users"
    file_path = request.json["file_path"] if request.json else None
    lybunt_users = (
        ContactUsers.query.filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .where(
            and_(
                ContactUsers.donations_last_year > 1,
                ContactUsers.donations_this_year < 1,
            )
        )
        .all()
    )
    if not lybunt_users:
        resp = DataResponse(False, "No Data to Display")
        return resp.status()
    total_records = len(lybunt_users)
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    lybunt_users = (
        ContactUsers.query.order_by(getattr(ContactUsers, "id"))
        .filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .where(
            and_(
                ContactUsers.donations_last_year > 1,
                ContactUsers.donations_this_year < 1,
            )
        )
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    resp = multi_dict_resp(lybunt_users)
    for member in lybunt_users:
        report_sender(member.primary_email, "", member.fullname, report_for, file_path)
    return paginated_response(
        page_number, total_records, resp, previous_page, next_page
    )


@customreports.route("/sybunt_contacts/<int:page_number>", methods=["GET"])
@user_required()
def sybant_contacts(page_number):
    common_url = "reports/sybunt_contacts"
    report_for = "sybunt_users"
    sybunt_users = (
        ContactUsers.query.order_by(getattr(ContactUsers, "id"))
        .filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .where(
            and_(ContactUsers.total_donations > 1, ContactUsers.donations_this_year < 1)
        )
        .all()
    )
    if not sybunt_users:
        resp = DataResponse(False, "No Data to Display")
        return resp.status()
    total_records = len(sybunt_users)
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    sybunt_users = (
        ContactUsers.query.order_by(getattr(ContactUsers, "id"))
        .filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .where(
            and_(ContactUsers.total_donations > 1, ContactUsers.donations_this_year < 1)
        )
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    resp = multi_dict_resp(sybunt_users)
    for member in sybunt_users:
        report_sender(member.primary_email, "", member.fullname, report_for)
    return paginated_response(
        page_number, total_records, resp, previous_page, next_page
    )


@customreports.route("/active_members/<int:page_number>", methods=["GET"])
@user_required()
def active_members(page_number):
    common_url = "reports/active_members"
    report_for = "active_members"
    active_memberships = (
        Memberships.query.join(ContactUsers)
        .filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .filter(Memberships.organization_id == getOrg(get_jwt()))
        .filter(ContactUsers.has_membership)
        .filter(Memberships.membership_status == "active")
    ).all()
    if not active_memberships:
        resp = DataResponse(False, "No Data to Display")
        return resp.status()
    total_records = len(active_memberships)
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    active_memberships = (
        Memberships.query.join(ContactUsers)
        .filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .filter(Memberships.organization_id == getOrg(get_jwt()))
        .filter(ContactUsers.has_membership)
        .filter(Memberships.membership_status == "active")
        .order_by(getattr(ContactUsers, "id"))
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    resp = multi_dict_resp(active_memberships)
    for member in active_memberships:
        report_sender(member.email_address, "", member.receipt_name, report_for)
    return paginated_response(
        page_number, total_records, resp, previous_page, next_page
    )


@customreports.route("/subscriptions_expiring/<int:page_number>", methods=["GET"])
@user_required()
def expiring_subscriptions(page_number):
    common_url = "reports/subscriptions_expiring"
    report_for = "expiring_soon"
    file_path = request.json["file_path"] if request.json else None
    curr_month = (date.today()).month
    next_month = curr_month + 1 if curr_month < 12 else 1
    expiring_subscriptions = (
        Memberships.query.join(ContactUsers)
        .filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .filter(Memberships.organization_id == getOrg(get_jwt()))
        .filter(ContactUsers.has_membership)
        .filter(Memberships.membership_status == "active")
        .filter(extract("month", Memberships.end_date) == next_month)
        .all()
    )
    if not expiring_subscriptions:
        resp = DataResponse(False, "No Data to Display")
        return resp.status()
    total_records = len(expiring_subscriptions)
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    expiring_subscriptions = (
        Memberships.query.join(ContactUsers)
        .filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .filter(Memberships.organization_id == getOrg(get_jwt()))
        .filter(ContactUsers.has_membership)
        .filter(Memberships.membership_status == "active")
        .filter(extract("month", Memberships.end_date) == next_month)
        .order_by(getattr(Memberships, "membership_id"))
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    resp = multi_dict_resp(expiring_subscriptions)
    for member in expiring_subscriptions:
        report_sender(
            member.email_address, "", member.receipt_name, report_for, file_path
        )
    return paginated_response(
        page_number, total_records, resp, previous_page, next_page
    )


@customreports.route("/elapsed_memberships/<int:page_number>", methods=["GET"])
@user_required()
def elapsed_subscriptions(page_number):
    common_url = "reports/elapsed_memberships"
    report_for = "elapsed_memberships"
    file_path = request.json["file_path"] if request.json else None
    elapsed_memberships = (
        Memberships.query.filter(Memberships.organization_id == getOrg(get_jwt()))
        .where(
            or_(
                Memberships.membership_status == "expired",
                Memberships.membership_status == "cancelled",
            )
        )
        .all()
    )
    if not elapsed_memberships:
        resp = DataResponse(False, "No Data to Display")
        return resp.status()
    total_records = len(elapsed_memberships)
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    elapsed_memberships = (
        Memberships.query.filter(Memberships.organization_id == getOrg(get_jwt()))
        .where(
            or_(
                Memberships.membership_status == "expired",
                Memberships.membership_status == "cancelled",
            )
        )
        .order_by(getattr(Memberships, "membership_id"))
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    resp = multi_dict_resp(elapsed_memberships)
    for member in elapsed_memberships:
        report_sender(
            member.email_address, "", member.receipt_name, report_for, file_path
        )
    return paginated_response(
        page_number, total_records, resp, previous_page, next_page
    )


@customreports.route("/inactive_volunteers/<int:page_number>", methods=["GET"])
@user_required()
def inactive_volunteers(page_number):
    common_url = "reports/inactive_volunteers"
    report_for = "inactive_volunteers"
    file_path = request.json["file_path"] if request.json else None
    inactive_volunteers = (
        ContactUsers.query.filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .filter(ContactUsers.total_volunteering == None,)
        .all()
    )
    if not inactive_volunteers:
        resp = DataResponse(False, "No Data to Display")
        return resp.status()
    total_records = len(inactive_volunteers)
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    inactive_volunteers = (
        ContactUsers.query.filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .filter(ContactUsers.total_volunteering == None,)
        .order_by(getattr(ContactUsers, "id"))
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    resp = multi_dict_resp(inactive_volunteers)
    for member in inactive_volunteers:
        report_sender(member.primary_email, "", member.fullname, report_for, file_path)
    return paginated_response(
        page_number, total_records, resp, previous_page, next_page
    )


@customreports.route("/active_volunteers/<int:page_number>", methods=["GET"])
@user_required()
def active_volunteers(page_number):
    common_url = "reports/active_volunteers"
    report_for = "active_volunteers"
    file_path = request.json["file_path"] if request.json else None
    active_volunteers = (
        ContactUsers.query.filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .filter(ContactUsers.volunteering_this_year > "1")
        .all()
    )
    if not active_volunteers:
        resp = DataResponse(False, "No Data to Display")
        return resp.status()
    total_records = len(active_volunteers)
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    active_volunteers = (
        ContactUsers.query.filter(ContactUsers.organization_id == getOrg(get_jwt()))
        .filter(ContactUsers.volunteering_this_year > "1")
        .order_by(getattr(ContactUsers, "id"))
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )

    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    resp = multi_dict_resp(active_volunteers)
    for member in active_volunteers:
        mailer = report_sender(
            member.primary_email, None, member.fullname, report_for, file_path
        )
        print(mailer)
    return paginated_response(
        page_number, total_records, resp, previous_page, next_page
    )


@customreports.route("/outstanding_pledges/<int:page_number>", methods=["GET"])
@user_required()
def oustanding_pledges(page_number):
    common_url = "reports/outstanding_pledges"
    report_for = "outstanding_pledges"
    file_path = request.json["file_path"] if request.json else None
    outstanding_pledges = (
        Pledges.query.filter(Pledges.organization_id == getOrg(get_jwt()))
        .where(and_(Pledges.status == "pending", datetime.now() > Pledges.end_date))
        .all()
    )
    if not outstanding_pledges:
        resp = DataResponse(False, "No Data to Display")
        return resp.status()
    total_records = len(outstanding_pledges)
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    outstanding_pledges = (
        Pledges.query.where(
            and_(Pledges.status == "pending", datetime.now() > Pledges.end_date)
        )
        .order_by(getattr(ContactUsers, "id"))
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"
    resp = multi_dict_resp(inactive_volunteers)
    for member in outstanding_pledges:
        report_sender(member.contact_name, "", member.fullname, report_for, file_path)

    return paginated_response(
        page_number, total_records, resp, previous_page, next_page
    )


@customreports.route("/active-recurring-donors")
def active_recurring_donors():
    active_status = ScheduleRecurringDonation.query.all()
    for x in active_status:
        contact_id = x.contact
        contact = ContactUsers.query.filter_by(id=contact_id).one_or_none()
        mail_id = contact.primary_email
        status = x.status
        if status == "Active":
            msg = Message("Testing", recipients=[mail_id])
            msg.body = "Thank you for continuing with us "
            mail.send(msg)
        return "Mail Sent"
