from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from pydantic import ValidationError

from skraggle.constants import DEFAULT_PAGE_SIZE, BASE_URL
from skraggle.decarotor import user_required
from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.config import db
from datetime import datetime
from skraggle.base_helpers.pagination_helper import paginate_memberships
from skraggle.contact.models import ContactUsers, Memberships
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.paginator_util import paginated_response
from skraggle.validators_logics.validators import MembershipValidator

membershipview = Blueprint("membershipview", __name__)


@membershipview.route("/create", methods=["POST"])
@user_required()
def membership_create():
    json_data = request.json
    contact_id =json_data['contact_id']
    contact = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).first()
    print(contact)
    if contact:
        if type(json_data['auto_renew']) != bool:
            resp = DataResponse(False, "auto_renew field must be boolean (true or false)")
            return resp.status()
        elif type(json_data['auto_send_email']) != bool:
            resp = DataResponse(False, "auto_send_email field must be boolean (true or false)")
            return resp.status()
        else:
            membership_data = {
                "start_date": json_data['start_date'],
                "end_date": json_data['end_date'],
                "auto_renew": bool(json_data['auto_renew']),
                "auto_send_email": bool(json_data['auto_send_email']),
                "receipt_name": json_data['receipt_name'],
                "address": json_data['address'],
                "email_address": json_data['email_address'],
                "payment_method": json_data['payment_method'],
                "membership_fee": json_data['membership_fee'],
            }
            try:
                MembershipValidator(**membership_data)
                membership = Memberships(**membership_data)
                contact.membership.append(membership)
                contact.primary_email = membership_data["email_address"]
                contact.has_membership = True
                db.session.flush()
                membership.membership_status = "active"
                membership.organization_id = getOrg(get_jwt())
                db.session.commit()
                resp = DataResponse(True, "Membership Created Successfully")
                return resp.status()
            except ValidationError as e:
                return e.json()
            except Exception as e:
                print(e)
                resp = DataResponse(False, str(e)[:105])
                return resp.status()

    resp = DataResponse(False, "Required fields missing")
    return resp.status()


@membershipview.route("/all/<int:page_number>", methods=["GET"])
@user_required()
def memberships_list(page_number):
    memberships = Memberships.query.all()
    total_records = len(memberships)
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    data = (
        Memberships.query.order_by(Memberships.membership_id)
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    data = [m.to_dict() for m in data]
    next_page = f"{BASE_URL}/memberships/all/{page_number + 1}"
    previous_page = f"{BASE_URL}/memberships/all/{page_number - 1}"
    return paginated_response(
        page_number, total_records, data, previous_page, next_page
    )


@membershipview.route("/<membership_id>", methods=["GET"])
@user_required()
def view_membership(membership_id):
    membership = Memberships.query.filter_by(
        membership_id=membership_id, organization_id=getOrg(get_jwt())
    ).first()
    if membership:
        return jsonify(dict_resp(membership)), 200
    else:
        resp = DataResponse(False, "No Membership to display")
        return resp.status()


@membershipview.route("/contact/<uuid:contact_id>/<int:page_number>", methods=['GET'])
@user_required()
def view_contact_membership(contact_id, page_number):
    instance = Memberships
    api_path = "memberships/contact/{}".format(contact_id)
    return paginate_memberships(page_number, instance, contact_id, api_path)


@membershipview.route("/expired", methods=["PATCH"])
@user_required()
def view_expired_memberships():
    memberships = (
        Memberships.query.filter(Memberships.organization_id == getOrg(get_jwt()))
        .filter(datetime.now() > Memberships.end_date)
        .all()
    )
    if memberships:
        resp = []
        for membership in memberships:
            membership.membership_status = "expired"
            db.session.commit()
            resp.append(dict_resp(membership))
        return jsonify(resp), 200
    else:
        resp = DataResponse(False, "No Expired Memberships to display")
        return resp.status()


@membershipview.route("/<membership_id>/cancel", methods=["PATCH"])
@user_required()
def cancel_membership(membership_id):
    membership = Memberships.query.filter_by(membership_id=membership_id,organization_id=getOrg(get_jwt())).first()
    if membership:
        if membership.membership_status == "active":
            membership.membership_status = "cancelled"
            contact = ContactUsers.query.filter_by(id=membership.contact).first()
            contact.has_membership = False
            db.session.commit()
            resp = DataResponse(True, "Memberships has been cancelled")
            return resp.status()
    resp = DataResponse(False, "The Membership has already been cancelled")
    return resp.status()
