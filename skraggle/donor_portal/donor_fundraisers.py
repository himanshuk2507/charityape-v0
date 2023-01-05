from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy import desc

from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse
from skraggle.campaigns.models import Campaigns
from skraggle.config import db
from skraggle.contact.Fundraising.models import Transactions
from skraggle.decarotor import user_required

donorportalfund = Blueprint("donorportalfund", __name__)


@donorportalfund.route("/recent_donations/<campaign_id>", methods=["GET"])
@user_required()
def portal_recent_donations(campaign_id):
    try:
        recent_transactions = (
            db.session.query(Transactions)
            .filter_by(campaign_id=campaign_id, organization_id=getOrg(get_jwt()))
            .order_by(Transactions.dateReceived)[-10:][::-1]
        )
        print(recent_transactions)
        transactions = {}
        for idx, transaction in enumerate(recent_transactions):
            transactions[f"Transaction-{idx + 1}"] = dict_resp(transaction)
            trans_receipt = transaction.receipts if transaction.receipts else ""
            transactions[f"Transaction-{idx + 1}"]["receipt"] = (
                dict_resp(trans_receipt[0]) if trans_receipt != "" else "No Receipt"
            )
        return jsonify(transactions), 200

    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@donorportalfund.route("/top_participants/<campaign_id>", methods=["GET"])
@user_required()
def portal_top_participants(campaign_id):
    try:
        campaign = Campaigns.query.filter_by(
            id=campaign_id, organization_id=getOrg(get_jwt())
        ).first()
        if campaign:
            all_transactions = campaign.transactions
            all_transactions.sort(key=lambda x: x.totalAmount, reverse=True)
            top_ten_trans = all_transactions[:10]
            top_participants = {}
            for idx, transaction in enumerate(top_ten_trans):
                top_participants[f"{idx}"] = dict(
                    name=transaction.transaction_from,
                    amount=transaction.totalAmount,
                    date=transaction.dateReceived,
                )
            print(top_participants)
            return top_participants, 200
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@donorportalfund.route("/stats/<campaign_id>", methods=["GET"])
@user_required()
def portal_stats(campaign_id):
    try:
        campaign = Campaigns.query.filter_by(
            id=campaign_id, organization_id=getOrg(get_jwt())
        ).first()
        if campaign:

            camp_trnasactions = campaign.transactions
            total_donations = len(camp_trnasactions)
            raised_amount = sum([getattr(x, "totalAmount") for x in camp_trnasactions])
            amount_left = float(campaign.fundraising_goal) - raised_amount
            donation_goal = int(campaign.fundraising_goal)
            percent_reached = int(raised_amount) * 100.0 / int(donation_goal)
            stats = {
                "campaign_name":campaign.name,
                "raised_amount": raised_amount,
                "total_donations": total_donations,
                "amount_left": amount_left,
                "donation_goal": donation_goal,
                "percent_reached": f"{percent_reached} %",

            }

            return jsonify(stats), 200
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()
