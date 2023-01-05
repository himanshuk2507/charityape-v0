import datetime
from flask import request, Blueprint, jsonify
from sqlalchemy import func

from flask_jwt_extended import get_jwt
from skraggle.base_helpers.responser import DataResponse
from skraggle.base_helpers.updating_fields_fetch import get_fields

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator, paginator_search
from .models import TransactionDonation
from skraggle.contact.models import ContactUsers
from skraggle.config import db

transactions_donation = Blueprint(
    "transactions_donation", __name__, template_folder="templates"
)


@transactions_donation.route("/create", methods=["POST"])
@user_required()
def add_donation():
    contact_id = request.args.get("id")
    contact = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not contact:
        return DataResponse(False, 'No contact with this ID exists').status()

    body = request.json
    
    total_amount = body["total_amount"]
    payment_method = body["payment_method"]
    date_received = datetime.datetime.now()

    donations = TransactionDonation(
        total_amount=total_amount,
        payment_method=payment_method,
        date_received=date_received,
        organization_id=getOrg(get_jwt()),
        contact_id=contact_id
    )
    contact.transaction_donations.append(donations)
    if contact.total_donations is None:
        contact.total_donations = total_amount
    else:
        contact.total_donations += total_amount
        
    if contact.number_of_donations is None:
        contact.number_of_donations = 1
    else:
        contact.number_of_donations += 1

    db.session.flush()
    db.session.commit()
    
    return DataResponse(True, 'Transaction was recorded successfully').status()


@transactions_donation.route("/update", methods=["PATCH"])
@user_required()
def update_donation():
    transactionDonation_id = request.args.get("id")
    donation = TransactionDonation.query.filter_by(
        id=transactionDonation_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not donation:
        return DataResponse(False, 'No transaction with this ID exists').status()

    body = request.json
    
    donation_obj = dict.fromkeys(get_fields(TransactionDonation))

    try:
        for field in body:
            if field in donation_obj.keys():
                setattr(donation, field, body[field])
        db.session.commit()
        return DataResponse(True, 'Transaction updated successfully!').status()
    except Exception as e:
        return DataResponse(False, str(e)[:105]).status()


@transactions_donation.route("/all/<int:page_number>",methods=["GET"])
@user_required()
def all_donation(page_number):
    common_url = "transaction-donations/all"
    order_id = "id"
    return paginator(page_number, TransactionDonation, order_id, common_url)


@transactions_donation.route("/info/<transactionDonation_id>",methods=["GET"])
@user_required()
def donation_list(transactionDonation_id):
    transactionDonation = TransactionDonation.query.filter_by(
        id=transactionDonation_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not transactionDonation:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = transactionDonation.to_dict()
    return jsonify(data), 200


@transactions_donation.route("/delete", methods=["DELETE"])
@user_required()
def delete_donation():
    id = request.args.get("id")
    try:
        TransactionDonation.query.filter_by(
            id=id, organization_id=getOrg(get_jwt())
        ).delete()
        return DataResponse(True, "Transaction deleted successfully!").status()
    except Exception as e:
        return DataResponse(False, str(e)[:105]).status()



@transactions_donation.route("/search", methods=["GET"])
@user_required()
def search():
    param = request.args['query']
    page = request.args['page']
    order_by = 'date_received'
    filter_string = f'%{param}%'

    query = (
        TransactionDonation.query.filter(
        TransactionDonation.payment_method.ilike(filter_string) |
        TransactionDonation.transaction_type.ilike(filter_string)
    ).order_by(
        getattr(TransactionDonation, order_by))
    )
    path = "transaction-donation/search"
    return paginator_search(page, query, path)