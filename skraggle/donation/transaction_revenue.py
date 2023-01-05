import datetime
from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator
from .models import TransactionsRevenue
from skraggle.contact.models import ContactUsers
from skraggle.config import db

transaction_revenues = Blueprint(
    "transaction_revenues", __name__, template_folder="templates"
)


@transaction_revenues.route("/create", methods=["POST"])
@user_required()
def add_revenue():
    contact_id = request.args.get("id")
    contact = ContactUsers.query.filter_by(id=contact_id).one_or_none()
    if not contact:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )

    total_amount = request.form["total_amount"]
    payment_method = request.form["payment_method"]
    date_received = datetime.datetime.now()
    revenue = TransactionsRevenue(
        total_amount=total_amount,
        payment_method=payment_method,
        date_received=date_received,
    )
    contact.transaction_revenues.append(revenue)
    db.session.flush()
    revenue.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Donation with method: {revenue.payment_method} was added successfully",
        "success": True,
    }
    return jsonify(data), 200


@transaction_revenues.route("/update", methods=["PATCH"])
@user_required()
def update_revenue():
    transactionRevenue_id = request.args.get("id")
    revenue = TransactionsRevenue.query.filter_by(
        id=transactionRevenue_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not revenue:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    total_amount = request.form["total_amount"]
    payment_method = request.form["payment_method"]
    date_received = datetime.datetime.now()

    revenue.total_amount = total_amount
    revenue.payment_method = payment_method
    revenue.date_received = date_received
    TransactionsRevenue(
        total_amount=total_amount,
        payment_method=payment_method,
        date_received=date_received,
    )

    db.session.commit()
    data = {
        "message": f" Donation with method: {revenue.payment_method} was updated successfully",
        "success": True,
    }
    return jsonify(data), 200


@transaction_revenues.route("/all/<int:page_number>",methods=["GET"])
@user_required()
def all_revenue(page_number):
    common_url = "transaction-revenues/all"
    order_id = "id"
    return paginator(page_number, TransactionsRevenue, order_id, common_url)


@transaction_revenues.route("/info/<transactionRevenue_id>",methods=["GET"])
@user_required()
def revenue_list(transactionRevenue_id):
    transactionsRevenue = TransactionsRevenue.query.filter_by(
        id=transactionRevenue_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not transactionsRevenue:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = transactionsRevenue.to_dict()
    return jsonify(data), 200


@transaction_revenues.route("/delete", methods=["DELETE"])
@user_required()
def delete_revenue():
    transactionRevenue_id = request.args.get("id")
    try:
        TransactionsRevenue.query.filter_by(
            id=transactionRevenue_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {"message": f" ID: {transactionRevenue_id} was successfully deleted", "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
