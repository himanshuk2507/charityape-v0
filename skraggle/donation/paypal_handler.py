from flask import Blueprint, request, redirect
import os

from flask_jwt_extended import get_jwt

from skraggle.contact.Fundraising.models import Transactions
import ast

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.responser import DataResponse

paymenthandler = Blueprint("paymenthandler", __name__)
from skraggle.config import db

import paypalrestsdk
from paypalrestsdk import Payment

api = paypalrestsdk.configure(
    {
        "mode": "sandbox",
        "client_id": os.getenv("PAYPAL_CID"),
        "client_secret": os.getenv("PAYPAL_SKEY"),
    }
)


@paymenthandler.route("/paypal")
@user_required()
def paypal_handler():

    payment = Payment(
        {
            "intent": "sale",
            # Set payment method
            "payer": {"payment_method": "paypal"},
            # Set redirect URLs
            "redirect_urls": {
                "return_url": os.getenv("PAYPAL_RETURN_URL"),
                "cancel_url": "https://example.com/cancel",
            },
            # Set transaction object
            "transactions": [
                {
                    "amount": {"total": "10.00", "currency": "USD"},
                    "description": "payment description",
                }
            ],
        }
    )

    if payment.create():
        for link in payment.links:
            if link.method == "REDIRECT":
                redirect_url = link.href
                print("here")
                print("Redirect for approval: {}".format(redirect_url))
                return redirect(redirect_url)


@paymenthandler.route("/paypal/execute")
@user_required()
def paypal_execute():
    payer_id = request.args.get("PayerID")
    payment_id = request.args.get("paymentId")
    try:
        payment = Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            payment_data = str(payment)
            payment = ast.literal_eval(payment_data)
            payer_name = payment.get("payer").get("payer_info").get(
                "first_name"
            ) + payment.get("payer").get("payer_info").get("last_name")
            address = list(
                payment.get("transactions")[0]
                .get("item_list")
                .get("shipping_address")
                .values()
            )
            transaction_details = {
                "dateReceived": payment.get("create_time"),
                "transactionType": payment.get("payer").get("payment_method"),
                "totalAmount": payment.get("transactions")[0]
                .get("amount")
                .get("total"),
                "billing_address": "".join([str(elem) for elem in address]),
                "transaction_by": payer_name,
            }
            print(transaction_details)
            transaction_info = Transactions(**transaction_details)
            db.session.add(transaction_info)
            db.session.flush()
            curr_transaction = Transactions.query.filter_by(
                transaction_id=transaction_info.transaction_id
            ).first()
            curr_transaction.transaction_info = payment
            curr_transaction.status = "accepted"
            curr_transaction.organization_id = getOrg(get_jwt())
            db.session.commit()
            resp = DataResponse(True,"Transaction accepted Successfully")
            return resp.status()
    except paypalrestsdk.exceptions.ResourceNotFound as ex:
        resp = DataResponse(False, "Paypal resource not found: {}".format(ex))
        return resp.status()
