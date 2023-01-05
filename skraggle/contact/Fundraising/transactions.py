from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt

from skraggle.base_helpers.dict_responser import dict_resp, multi_dict_resp
from skraggle.base_helpers.pagination_helper import paginator
from skraggle.constants import DEFAULT_PAGE_SIZE, BASE_URL
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.paginator_util import paginated_response
from .models import Transactions, TransactionReceipts
from skraggle.config import db
from datetime import datetime
from skraggle.contact.models import ContactUsers
from skraggle.p2p.models import Donors
from skraggle.base_helpers.responser import DataResponse

transactiontab = Blueprint("transactiontab", __name__)


"""
Api to create transaction for Contact or Donors.

@Parameters: donor_id or contact_id
"""


@transactiontab.route("/create", methods=["POST"])
@user_required()
def add_transaction():
    if request.method == "POST":
        transaction_details = {
            "dateReceived": datetime.now(),
            "transactionType": request.form["transactionType"],
            "totalAmount": request.form["totalAmount"],
            "billing_address": request.form["billing_address"],
            "transaction_by": "NA",
            "transaction_from": request.form["transaction_from"],
            "transaction_for": request.form["transaction_for"],

        }
        if "donor_id" not in request.form and "contact_id" not in request.form:
            return (
                jsonify(
                    {"status": False, "message": "contact_id or donor_id required"}
                ),
                404,
            )
        if "donor_id" in request.form:
            donor_id = request.form["donor_id"]
            donor = Donors.query.filter_by(donor_id=donor_id).one_or_none()
            if donor:
                try:
                    transaction_details["transaction_by"] = "donor"
                    transaction = Transactions(**transaction_details)

                    donor.transactions.append(transaction)
                    db.session.flush()
                    transaction.organization_id = getOrg(get_jwt())
                    db.session.commit()

                    return (
                        jsonify(
                            {
                                "Status": True,
                                "message": "Transaction for Donor created successfully",
                            }
                        ),
                        200,
                    )

                except Exception as e:
                    return jsonify({"status": False, "message": str(e)[:105]}), 404
            else:
                return (
                    jsonify({"Status": True, "message": "donor does not exist"}),
                    404,
                )
        elif "contact_id" in request.form:
            contact_id = request.form["contact_id"]
            contact = ContactUsers.query.filter_by(id=contact_id).one_or_none()
            if contact:
                try:
                    transaction_details["transaction_by"] = "contact"
                    transaction = Transactions(**transaction_details)
                    contact.Transactions.append(transaction)
                    db.session.flush()
                    transaction.organization_id = getOrg(get_jwt())
                    db.session.commit()
                    return (
                        jsonify(
                            {
                                "Status": True,
                                "message": "Transaction for Contact created successfully",
                            }
                        ),
                        200,
                    )
                except Exception as e:
                    return jsonify({"status": False, "message": str(e)[:105]}), 404
            else:
                return (
                    jsonify({"Status": False, "message": "contact does not exist"}),
                    404,
                )
    else:
        return jsonify({"Error": "Method Not Allowed"}), 404


@transactiontab.route("/<uuid:id>", methods=["GET"])
@user_required()
def transactions_view(id):
    contact, donor = None, None
    transaction_by = request.args.get("transaction_by")
    if transaction_by == "contact":
        contact = ContactUsers.query.filter_by(id=id).one_or_none()
    elif transaction_by == "donor":
        donor = Donors.query.filter_by(donor_id=id).one_or_none()
    if contact or donor:
        trans = contact.Transactions if contact else donor.transactions
        trans = dict_resp(trans)
        trans["receipt"] = trans.receipt
        return jsonify(trans),200
    else:
        is_contact, is_donor = "Contact", "Donor"
        data = {
            "success": False,
            "message": f"{is_contact if contact else is_donor} does not exist",
        }
        return jsonify(data), 404


@transactiontab.route("/list/<uuid:transaction_id>", methods=["GET"])
@user_required()
def transaction_list(transaction_id):
    trans = Transactions.query.filter_by(transaction_id=transaction_id).first()
    if trans:
        trans_data = dict_resp(trans)
        trans_receipt = trans.receipts
        trans_data["receipt"] = dict_resp(trans_receipt[0])
        return jsonify(trans_data), 200
    else:
        resp = DataResponse(False, "Transaction does not exist")
        return resp.status()


@transactiontab.route("/all/<int:page_number>", methods=["GET"])
@user_required()
def get_all_transactions(page_number):
    instance = Transactions
    order_by_column = "transaction_id"
    api_path = "transactions/all"
    return paginator(page_number, instance, order_by_column, api_path)



@transactiontab.route("/delete", methods=["DELETE"])
@user_required()
def transaction_delete():

    if request.method == "DELETE":
        id = request.args.get("transactions_id")
        ids = id.split(",")

        trans = (
            db.session.query(Transactions)
            .filter(Transactions.transaction_id.in_(ids))
            .all()
        )
        if trans:
            try:
                for tran in trans:
                    db.session.delete(tran)
                db.session.commit()
                resp = DataResponse(True, "Transaction(s) Deleted Successfully")
                return resp.status()
            except Exception as e:
                resp = DataResponse(False, str(e)[:105])
                return resp.status()
        else:
            resp = DataResponse(False, "Transaction(s) Does not Exist")
            return resp.status()


@transactiontab.route("/unreceipted-transactions", methods=["GET"])
@user_required()
def transaction_unreceipted():
    receipts = TransactionReceipts.query.all()
    ids = []
    for id in receipts:
        ids.append(id.transaction_id)

    transactions = (
        db.session.query(Transactions)
        .filter(~Transactions.transaction_id.in_(ids))
        .all()
    )

    data = {
        "unreceipted_transactions": [
            {
                "contact_id": trans.transaction_id,
                "contact": str(
                    ContactUsers.query.filter_by(id=trans.contact_id).first().fullname
                ),
                "date_received": trans.dateReceived,
                "total_amount": trans.totalAmount,
                "status": trans.status,
                "transaction_type": trans.transactionType,
            }
            for trans in transactions
        ]
    }

    return jsonify(data)


@transactiontab.route("/approved-transactions", methods=["GET"])
@user_required()
def transaction_approved():
    transactions = Transactions.query.filter_by(status="approved").all()

    data = {
        "unreceipted_transactions": [
            {
                "contact_id": trans.transaction_id,
                "contact": str(
                    ContactUsers.query.filter_by(id=trans.contact_id).first().fullname
                ),
                "date_received": trans.dateReceived,
                "total_amount": trans.totalAmount,
                "status": trans.status,
                "transaction_type": trans.transactionType,
            }
            for trans in transactions
        ]
    }

    return jsonify(data)


@transactiontab.route("/receipts/<int:transaction_id>", methods=["GET"])
@user_required()
def transaction_receipt(transaction_id):
    trans = Transactions.query.filter_by(transaction_id=transaction_id).first()
    data = None
    if trans:
        receipts = trans.receipts
        data = {
            "receipts": [
                {
                    "receipt_id": recp.receiptID,
                    "receipt_name": recp.receipt_name,
                    "full_address": recp.full_address,
                    "delivery_option": recp.delivery_option,
                    "email": recp.email,
                }
                for recp in receipts
            ]
        }

    else:
        data = {"Error": "Transaction does not exist"}
    return jsonify(data)


@transactiontab.route("/receipts/create", methods=["POST"])
@user_required()
def transaction_receipt_create():
    transaction_id = request.args.get("transaction_id")
    resp = {"Status": ""}
    trans = Transactions.query.filter_by(transaction_id=transaction_id).first()
    if request.method == "POST":
        if trans:
            receipt_name = request.form["receipt_name"]
            full_address = request.form["full_address"]
            delivery_option = request.form["delivery_option"]
            email = request.form["email"]
            receipt = TransactionReceipts(
                receipt_name=receipt_name,
                full_address=full_address,
                delivery_option=delivery_option,
                email=email,
            )
            trans.receipts.append(receipt)
            db.session.flush()
            receipt.organization_id = getOrg(get_jwt())
            db.session.commit()
            resp["Status"] = "Receipt Created"
        else:
            resp["Status"] = "Transaction Does not Exist"
    return jsonify(resp)


@transactiontab.route("/get_status/<uuid:transaction_id>", methods=["GET"])
@user_required()
def get_transaction_status(transaction_id):
    status = Transactions.query.filter_by(transaction_id=transaction_id).first()
    if status:
        return jsonify({"Status": status.status}), 200
    else:
        return jsonify({"Error": "Transaction Does not Exist"}), 404


@transactiontab.route("/set_status/<uuid:transaction_id>", methods=["PATCH"])
@user_required()
def set_transaction_status(transaction_id):
    status = Transactions.query.filter_by(transaction_id=transaction_id).first()
    if status:
        print(status)

        update_status = request.form.get("transaction_status")
        print(status.status)
        status.status = update_status
        db.session.commit()
        print(status.status)
        resp = DataResponse(
            True, f"Status Updated for Transaction ID : {status.transaction_id}"
        )
        return resp.status()
    else:
        resp = DataResponse(False, f"Transaction does not exist ")
        return resp.status()
