from crypt import methods
from uuid import UUID
from flask import Blueprint, jsonify, session
from skraggle.base_helpers.responser import DataResponse
from skraggle.base_helpers.pagination_helper import paginator, paginate_memberships
from ..models import ContactUsers, Memberships
from flask_jwt_extended import get_jwt
from sqlalchemy import and_
from skraggle.base_helpers.orgGen import getOrg
from skraggle.decarotor import user_required

profiletab = Blueprint("profiletab", __name__)


@profiletab.route("/general_updates")
@user_required()
def general_update():
    donation_amount = 0
    revenue_amount = 0
    volunteer_hours = 0
    data = {
        "donation_amount": donation_amount,
        "revenue_amount": revenue_amount,
        "volunteer_hours": volunteer_hours,
    }
    return jsonify(data)


@profiletab.route("/contact_insight")
@user_required()
def contact_insight():
    donor_score = 0
    data = {
        "donor_score": donor_score,
    }
    return jsonify(data)


@profiletab.route("/smart_recommendations")
@user_required()
def smart_recommendations():
    smark_ask = ("NA",)
    time_of_year = (0000,)
    best_way_to_connect = ("NA",)
    compaign_recommendation = ("NA",)

    data = {
        "smart Ask": smark_ask,
        "time of Year": time_of_year,
        "best Way to connect": best_way_to_connect,
        "campaign Recommendation": compaign_recommendation,
    }
    return jsonify(data)


@profiletab.route("/personal_info")
@user_required()
def personal_info():
    title = "NA"
    fname = ("NA",)
    lname = ("NA",)
    gen = ("NA",)
    bday = ("00/00/0000",)
    email = ("pravs@mailer.com",)
    phone = "0123456789"

    data = {
        "title": title,
        "first name": fname,
        "last name": lname,
        "gender": gen,
        "birthday": bday,
        "primary_email": email,
        "primary_phone": phone,
    }
    return jsonify(data)


@profiletab.route("/admin")
@user_required()
def admin():
    id = 0
    priority = (1,)
    assignee = ("NA",)
    tags = ("NA",)
    notes = ("None",)
    solication = ("NA",)
    email = ("NA",)
    subscription = "NA"

    data = {
        "id": id,
        "priority": priority,
        "tags": tags,
        "assignee": assignee,
        "notes": notes,
        "solication": solication,
        "email": email,
        "subscription": subscription,
    }
    return jsonify(data)


@profiletab.route("/contact_profile/<uuid:contact_id>")
@user_required()
def contact_info(contact_id):
    contacts = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not contacts:
        resp = DataResponse(
            False, f"Contact ID: {contact_id} doesn't correspond to a valid contact"
        )
        return resp.status()
    else:
        data = {
            "id": contacts.id,
            "title": contacts.title,
            "fullname": contacts.fullname,
            "primary Email": contacts.primary_email,
            "primary phone": contacts.primary_phone,
            "address": contacts.address,
            "assignee": contacts.assignee,
            "priority": contacts.priority,
            "tags": contacts.tags,
            "donor_score": contacts.donor_score,
            "total_donations": contacts.total_donations,
            "gender": contacts.gender,
            "birth_date": contacts.birth_date,
            "email_subscription_status": contacts.email_subscription_status,
            "solicitation": contacts.solicitation,
            "preferred_name": contacts.preferred_name,
            "best_way_to_reach_out": contacts.best_way_to_reach_out,
            "city": contacts.city,
            "state": contacts.state,
            "postal_zip": contacts.postal_zip,
            # "companies": contacts.companies,
            "company": contacts.company,
            "type": contacts.type,
            "unit": contacts.unit,
            "contact_type": contacts.contact_type,
            "country": contacts.country,
            "has_membership": contacts.has_membership,
            "schedule_recurring_donations": contacts.schedule_recurring_donations,
            "schedule_recurring_revenues": contacts.schedule_recurring_revenues,
            "transaction_donations": contacts.transaction_donations,
            "transaction_revenues": contacts.transaction_revenues,
            "donations_last_year": contacts.donations_last_year,
            "donations_this_year": contacts.donations_this_year,
            "engagement_stage": contacts.engagement_stage,
            "established_date": contacts.established_date,
            "household": contacts.household,
            "household_Role": contacts.household_Role,
            "major_gift_amount": contacts.major_gift_amount,
            "major_gift_donor": contacts.major_gift_donor,
            "smart_Ask": contacts.smart_Ask,
            "time_of_year": contacts.time_of_year,
            "transactions": contacts.Transactions,
            "total_transactions": contacts.total_transactions,
            "total_volunteering": contacts.total_volunteering,
            "volunteering_this_year": contacts.volunteering_this_year,
            "websites": {
                "facebook": contacts.facebook,
                "instagram": contacts.instagram,
                "linkedln": contacts.linkedln,
                "twitter": contacts.twitter,
                "youtube": contacts.youtube,
                "website": contacts.website,
                "othersite": contacts.othersite
            },
            "created_on": contacts.created_on
        }
        return DataResponse(True, data).status()


@profiletab.route("/websites")
@user_required()
def websites():
    website = "None"
    twitter = ("NA",)
    facebook = ("NA",)
    youtube = ("NA",)
    linkedin = ("None",)
    instagram = ("NA",)
    othersites = ("NA",)
    data = {
        "website": website,
        "twitter": twitter,
        "facebook": facebook,
        "youtube": youtube,
        "linkedin": linkedin,
        "instagram": instagram,
        "othersites": othersites,
    }
    return jsonify(data)


@profiletab.route("/association")
@user_required()
def association():
    companies = "None"
    household = ("NA",)
    householdrole = ("NA",)
    data = {
        "companies": companies,
        "household": household,
        "household Role": householdrole,
    }
    return jsonify(data)


@profiletab.route("/volunteer_info")
@user_required()
def volunteer_info():
    volunteer_info = "None"
    data = {"Volunteer_info": volunteer_info}
    return jsonify(data)
