from email.policy import default
from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy import Integer

from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.base_helpers.next_schedule_day import ScheduleDay
from skraggle.base_helpers.responser import DataResponse
from skraggle.base_helpers.updating_fields_fetch import get_fields
from skraggle.constants import BASE_URL, DEFAULT_PAGE_SIZE
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator
from skraggle.paginator_util import paginated_response
from .models import ScheduleRecurringDonation
from skraggle.contact.models import ContactUsers
from skraggle.config import db
import stripe

schedule_recurring_donations = Blueprint(
    "schedule_recurring_donations", __name__, template_folder="templates"
)

def is_valid_payload(fields: list=[], payload: dict={}):
    for field in fields:
        if field not in payload.keys():
            return False, field
    return True, ""

def donation_amount(amount):
    total_amount_as_float = float(amount)
    stripe_amount = int(total_amount_as_float * 100)
    return dict(float = total_amount_as_float, stripe = stripe_amount)

@schedule_recurring_donations.route("", methods=["POST"])
@user_required()
def create_recurring():
    body = request.json
    is_valid, missing_field = is_valid_payload(fields=[
        'total_amount', 'billing_cycle', 'campaign_id', 'receipt_setting', 'contact_id', 'source'
    ], payload=body)
    if not is_valid:
        return DataResponse(False, f'{missing_field} is required in request payload').status()

    contact_id = body.get('contact_id')
    if not contact_id:
        return DataResponse(False, 'a valid `contact_id` query param is required').status()

    contact = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not contact:
        return DataResponse(False, 'This contact ID is invalid or does not exist').status()
    
    amount = donation_amount(body.get('total_amount'))
    body['organization_id'] = getOrg(get_jwt())
    body['total_amount'] = amount['float']

    try:
        donation = ScheduleRecurringDonation(**body)
        contact.schedule_recurring_donations.append(donation)
        db.session.flush()

        customer = stripe.Customer.create(
            description="recurring_donor",
            email=contact.primary_email,
            name=contact.fullname,
        )
        recurring_product = stripe.Product.create(name="Recurring donation")
        num, days_type = body.get('billing_cycle').split(" ")

        pricing = stripe.Price.create(
            unit_amount=amount['stripe'],
            currency="usd",
            recurring={"interval_count": num, "interval": days_type},
            product=recurring_product["id"],
        )

        donation.customer_id = customer["id"]
        donation.product_id = recurring_product["id"]
        donation.plan_id = pricing["id"]

        db.session.commit()
        return DataResponse(True, 'Recurring donation scheduled successfully').status()
    except Exception as e:
        return DataResponse(False, str(e)).status()


@schedule_recurring_donations.route("/info/<uuid:id>", methods=["PATCH"])
@user_required()
def update_donation(id):
    donation = ScheduleRecurringDonation.query.filter_by(
        id=id, organization_id=getOrg(get_jwt())
    ).one_or_none()

    try:
        if not donation:
            return DataResponse(False, 'This recurring donation does not exist').status()

        donation_obj = dict.fromkeys(get_fields(ScheduleRecurringDonation))
        body = request.json
        try:
            for field in body:
                if field in donation_obj.keys():
                    setattr(donation, field, body.get(field))
        except Exception as e:
            return DataResponse(False, str(e)[:105]).status()

        num, days_type = donation.billing_cycle.split(" ")
        amount = donation_amount(body.get('total_amount') or donation.total_amount)
        donation.total_amount = amount['float']
        
        pricing = stripe.Price.create(
            unit_amount=amount['stripe'],
            currency='usd',
            recurring={"interval_count": num, "interval": days_type},
            product=donation.product_id,
        )
        
        donation.plan_id = pricing.id
        db.session.commit()

        return DataResponse(True, 'Recurring donation updated successfully').status()
    except Exception as e:
        return DataResponse(False, str(e)).status()


@schedule_recurring_donations.route("/all", methods=["GET"], defaults={'page_number': 1})
@schedule_recurring_donations.route("/all/<int:page_number>", methods=["GET"])
@user_required()
def all_donation(page_number):
    common_url = "donations/recurring/all"
    order_id = "id"
    table = ScheduleRecurringDonation
    count = db.session.query(table).count()
    base_url = BASE_URL
    processed = (page_number - 1) * DEFAULT_PAGE_SIZE if page_number > 1 else 0
    donations = (
        table.query.order_by(getattr(table, order_id))
        .offset(processed)
        .limit(DEFAULT_PAGE_SIZE)
        .all()
    )
    donations = [dict_resp(donation) for donation in donations]
    next_page = f"{BASE_URL}/{common_url}/{page_number + 1}"
    previous_page = f"{BASE_URL}/{common_url}/{page_number - 1}"

    # fetch contacts using memoization for efficiency
    contacts_memo = {}
    for donation in donations:
        contact_id = donation['contact_id']
        contact = None
        if contact_id in contacts_memo.keys():
            contact = contacts_memo[contact_id]
        else:
            contact = ContactUsers.query.filter_by(
                id=contact_id, organization_id=getOrg(get_jwt())
            ).one_or_none()
            contacts_memo[contact_id] = contact
        
        donation['contact'] = dict_resp(contact)

    return paginated_response(
        page_number, count, donations, previous_page, next_page
    )


@schedule_recurring_donations.route("/info/<uuid:id>", methods=["GET"])
@user_required()
def donation_info(id):
    donation = ScheduleRecurringDonation.query.filter_by(
        id=id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not donation:
        return DataResponse(False, 'No recurring donation exists with this ID').status()
    data = dict_resp(donation)
    num, days_type = donation.billing_cycle.split(" ")
    get_day = ScheduleDay(num, days_type.lower())
    data["next_scheduled_date"] = get_day.next_date()
    data['contact'] = ContactUsers.query.filter_by(
        id=donation.contact_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    data['contact'] = dict_resp(data['contact']) if data['contact'] is not None else data['contact']
    return DataResponse(True, data).status()


@schedule_recurring_donations.route("/info/<uuid:id>", methods=["DELETE"])
@user_required()
def delete_donation(id):
    try:
        donation = ScheduleRecurringDonation.query.filter_by(
            id=id, organization_id=getOrg(get_jwt())
        ).one_or_none()

        if not donation:
            return DataResponse(False, 'This donation does not exist').status()

        subscription = stripe.Subscription.list(
            customer=donation.customer_id,
            price=donation.plan_id,
            limit=1,
        )
        
        subscription_id = subscription['data'][0]['id'] if len(subscription['data']) > 0 else None
        if subscription_id:
            stripe.Subscription.delete(subscription_id["data"][0]["id"])

        ScheduleRecurringDonation.query.filter_by(
            id=id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        
        return DataResponse(True, 'Recurring donation successfully cancelled and deleted').status()
    except Exception as e:
        return DataResponse(False, str(e)[:105]).status()
