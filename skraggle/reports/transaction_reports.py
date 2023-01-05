from flask import request, Blueprint, jsonify
from skraggle.donation.models import (
    ScheduleRecurringRevenue,
    ScheduleRecurringDonation,
    TransactionDonation,
    TransactionsRevenue,
)
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.config import db
from skraggle.base_helpers.pagination_helper import get_paginated_list
from flask_jwt_extended import get_jwt
from skraggle.contact.models import ContactUsers
from skraggle.base_helpers.responser import DataResponse


transactionreportviews = Blueprint("transactionreportviews", __name__)


@transactionreportviews.route("/all_transaction",methods=["GET"])
def all_transaction():
    transaction_revenue = TransactionsRevenue.query.all()
    transaction_donation = TransactionDonation.query.all()
    return {
        "transaction_revenue_list": [str(x.id) for x in transaction_revenue],
        "transaction_donation_list": [str(x.id) for x in transaction_donation],
    }


@transactionreportviews.route("/all_transactions_broken_by_type",methods=["GET"])
def all_transactions_broken_by_type():
    transaction_type = request.form["transaction_type"]
    if transaction_type == "transaction_donation":
        transaction_donation = TransactionDonation.query.all()
        return {"transaction_donation_list": [str(x.id) for x in transaction_donation]}
    elif transaction_type == "transaction_revenue":
        transaction_revenue = TransactionsRevenue.query.all()
        return {
            "transaction_revenue_list": [str(x.id) for x in transaction_revenue],
        }
    else:
        data = "Wrong transaction type"
        return jsonify(data)


@transactionreportviews.route("/all_donations",methods=["GET"])
def all_donation():
    transaction_donation = TransactionDonation.query.all()
    return {"transaction_donation_list": [str(x.id) for x in transaction_donation]}

@transactionreportviews.route("/all_revenue",methods=["GET"])
def all_revenue():
    transaction_revenue = TransactionsRevenue.query.all()
    return {
        "transaction_revenue_list": [str(x.id) for x in transaction_revenue],
    }

@transactionreportviews.route("/receipts/<int:page_number>", methods=["GET"])
@user_required()
def reciepts(page_number):
    transaction = TransactionDonation.query.filter()
    
    all_reciept = []
    for trxn in transaction:
        contact = ContactUsers.query.filter_by(id=trxn.contact_id).one_or_none()
        datas = {
            "id": trxn.id,
            "contact": contact.fullname,
            "amount": trxn.total_amount,
            "paymentType": trxn.transaction_type,
            "paymentMethod": trxn.payment_method,
            "dateReceived": trxn.date_received
        }
        all_reciept.append(datas)
    api_path = "reports/transactions/receipts"
    return get_paginated_list(all_reciept, api_path, page_number)


@transactionreportviews.route("receipts/<uuid:id>", methods=["GET"])
@user_required()
def receipt_by_id(id):
    transaction = TransactionDonation.query.filter_by(id=id).one_or_none()
    if not transaction:
        return DataResponse(False, "Invalid transaction id").status()
    datas = {
        "id": transaction.id,
        "amount": transaction.total_amount,
        "paymentType": transaction.transaction_type,
        "paymentMethod": transaction.payment_method,
        "dateReceived": transaction.date_received
    }
    return DataResponse(True, datas).status()