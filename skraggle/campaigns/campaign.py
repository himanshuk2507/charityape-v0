from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt

from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.base_helpers.object_utility import ObjectHandler
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.base_helpers.updating_fields_fetch import get_fields
from skraggle.config import db
from skraggle.base_helpers.pagination_helper import paginator
from skraggle.contact.Fundraising.models import Transactions
from skraggle.contact.models import ContactUsers
from skraggle.decarotor import user_required
from skraggle.paginator_util import paginated_response
from .models import Campaigns
from skraggle.constants import BASE_URL, DEFAULT_PAGE_SIZE

campaignviews = Blueprint("campaignviews", __name__, template_folder="templates")


@campaignviews.route("/create", methods=["POST"])
@user_required()
def campaign_add():
    campaign_obj = ObjectHandler("Campaigns", getOrg(get_jwt()))
    campaign_data = campaign_obj.make()
    try:
        for keys in request.json:
            if keys in campaign_data.keys():
                campaign_data[keys] = request.json[keys]
        campaign = Campaigns(**campaign_data)
        db.session.add(campaign)
        db.session.commit()
        resp = DataResponse(True, "Campaign Created Successfully")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@campaignviews.route("/update", methods=["PATCH"])
@user_required()
def campaign_update():
    campaign_id = request.args.get("id")
    campaign = Campaigns.query.filter_by(
        id=campaign_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not campaign:
        resp = DataResponse(
            False, f"Campaign ID: {campaign_id} doesn't correspond to a valid campaign"
        )
        return resp.status()
    campaign_obj = dict.fromkeys(get_fields(Campaigns))
    try:
        for keys in request.json:
            if keys in campaign_obj.keys():
                setattr(campaign, keys, request.json[keys])
        db.session.commit()
        resp = DataResponse(True, f"Campaign with id {campaign_id} Updated")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@campaignviews.route("/all/<int:page_number>")
@user_required()
def camp_info(page_number):
    instance = Campaigns
    order_by_column = "id"
    api_path = "campaigns/all"
    return paginator(page_number, instance, order_by_column, api_path)


@campaignviews.route("/info/<campaign_id>")
@user_required()
def camp_information(campaign_id):
    campaign_info = Campaigns.query.filter_by(
        id=campaign_id, organization_id=getOrg(get_jwt())
    ).one_or_none()

    # Return 404 when the given campaign is not found
    if not campaign_info:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = campaign_info.to_dict()
    return jsonify(data), 200


@campaignviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_campaign():
    campaign_id = request.args.get("id")
    try:
        db.session.query(Campaigns).filter_by(
            id=campaign_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {
            "message": f"ID: {campaign_id} was successfully deleted",
            "success": True,
        }
        return jsonify(data), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400


# create a transaction for a campaign
@campaignviews.route("/transaction/create/<campaign_id>", methods=["POST"])
@user_required()
def campaign_transaction(campaign_id):
    if request.method == "POST":
        campaign = Campaigns.query.filter_by(
            id=campaign_id, organization_id=getOrg(get_jwt())
        ).first()
        contact_id = request.form["transaction_by"]
        contact = ContactUsers.query.filter_by(
            id=contact_id, organization_id=getOrg(get_jwt())
        ).first()
        if not campaign or not contact:
            resp = DataResponse(False, "Campaign/Contact Does not Exist")
            return resp.status()
        try:

            transaction_details = {
                "dateReceived": datetime.now(),
                "transactionType": request.form["transactionType"],
                "totalAmount": request.form["totalAmount"],
                "billing_address": request.form["billing_address"],
                "transaction_by": request.form["transaction_by"],
                "transaction_from": request.form["transaction_from"],
                "transaction_for": request.form["transaction_for"],
            }
            transaction = Transactions(**transaction_details)
            campaign.transactions.append(transaction)

            db.session.flush()

            transaction.organization_id = getOrg(get_jwt())
            db.session.commit()
            resp = DataResponse(
                True, "Transaction created for Campaign {}".format(campaign_id)
            )
            return resp.status()
        except Exception as e:
            resp = DataResponse(False, str(e))
            return resp.status()
