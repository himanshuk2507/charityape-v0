import json
import os
from datetime import datetime

from flask_jwt_extended import get_jwt

from skraggle.base_helpers.orgGen import getOrg
from skraggle.contact.Fundraising.models import Transactions
import stripe
from flask import Blueprint, jsonify, request, redirect, url_for
from skraggle.base_helpers.responser import DataResponse
from skraggle.config import db
from skraggle.contact.models import ContactUsers
from skraggle.decarotor import user_required
from skraggle.donation.models import ScheduleRecurringDonation

stripe_keys = {
    "secret_key": os.getenv("STRIPE_SECRET_KEY"),
    "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY"),
}

stripehandler = Blueprint("stripehandler", __name__, template_folder="templates")
stripe.api_key = stripe_keys["secret_key"]


@stripehandler.route("/stripe/<mode>/<id>", methods=["GET"])
def index(id, mode):
    amount, description = 0, "NA"
    print(stripe.Account.retrieve())
    if "amount" and "description" in request.args:
        amount = request.args.get("amount")
        description = request.args.get("description")
    return redirect(
        url_for(
            "stripehandler.create_checkout_session",
            amount=amount,
            description=description,
            id=id,
            mode=mode,
        )
    )


@stripehandler.route(
    "<id>/stripe/create-checkout-session/<mode>/<amount>/<description>"
)
def create_checkout_session(id, amount, description, mode):
    domain_url = str(request.host_url)
    stripe.api_key = stripe_keys["secret_key"]
    contact = ContactUsers.query.filter_by(id=id).first()

    try:
        if mode == "payment":
            stripe_customer_id = stripe.Customer.list(
                email=contact.primary_email, limit=1
            )["data"][0]["id"]
            try:
                if stripe_customer_id:

                    checkout_session = stripe.checkout.Session.create(
                        success_url=domain_url
                        + "payments/success?session_id={CHECKOUT_SESSION_ID}",
                        cancel_url=domain_url + "cancelled",
                        payment_method_types=["card"],
                        mode="payment",
                        customer=stripe_customer_id,
                        payment_intent_data={"setup_future_usage": "off_session",},
                        line_items=[
                            {
                                "name": "Donation",
                                "description": description,
                                "quantity": 1,
                                "currency": "INR",
                                "amount": amount,
                            }
                        ],
                    )
                    return redirect(checkout_session.url, code=303)
            except Exception as e:
                return jsonify(error=str(e)), 403
        elif mode == "recurring":
            recurring_plan = ScheduleRecurringDonation.query.filter_by(id=id).first()
            try:
                if recurring_plan:
                    checkout_session = stripe.checkout.Session.create(
                        success_url=domain_url
                        + "payments/success?session_id={CHECKOUT_SESSION_ID}",
                        cancel_url=domain_url + "cancelled",
                        payment_method_types=["card"],
                        mode="subscription",
                        customer=recurring_plan.customer_id,
                        line_items=[{"price": recurring_plan.plan_id, "quantity": 1,},],
                    )
                    return redirect(checkout_session.url, code=303)
            except Exception as e:
                return jsonify(error=str(e)), 403
    except Exception as e:
        return jsonify(error=str(e)), 403


@stripehandler.route("/success")
def success():
    stripe.api_key = stripe_keys["secret_key"]
    payment = stripe.checkout.Session.retrieve(request.args.get("session_id"))
    payment_data = str(payment)
    payment_data = json.loads(payment_data)
    print(payment_data)
    amount, transaction_by, address, payment_method = (
        payment_data.get("amount_total"),
        payment_data.get("customer_details").get("email"),
        payment_data.get("billing_address_collection"),
        payment_data.get("mode"),
    )
    transaction_details = {
        "dateReceived": datetime.now(),
        "transactionType": payment_method,
        "totalAmount": amount,
        "billing_address": "".join(
            [str(elem) for elem in address] if address else "NA"
        ),
        "transaction_by": list(
            db.session.query(ContactUsers.id)
            .filter_by(primary_email=transaction_by)
            .first()
        )[0],
        "transaction_for": "donation",
        "transaction_from": "from_contact",
    }

    transaction_info = Transactions(**transaction_details)
    db.session.add(transaction_info)
    db.session.flush()
    curr_transaction = Transactions.query.filter_by(
        transaction_id=transaction_info.transaction_id
    ).first()
    curr_transaction.transaction_info = payment_data
    curr_transaction.status = "accepted"
    db.session.commit()
    resp = DataResponse(True, "Transaction successful")
    return resp.status()


@stripehandler.route("/cancelled")
def cancelled():
    stripe.api_key = stripe_keys["secret_key"]
    resp = DataResponse(True, "Transaction Cancelled")
    return resp.status()


@stripehandler.route("/<contact_id>/add_payment_method", methods=["POST"])
@user_required()
def add_payment_method(contact_id):
    stripe.api_key = stripe_keys["secret_key"]
    contact = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).first()
    if contact:

        stripe_customer_id = stripe.Customer.list(email=contact.primary_email, limit=1)[
            "data"
        ][0]["id"]
        try:
            if stripe_customer_id:
                payment_method = stripe.PaymentMethod.create(
                    type="card",
                    card={
                        "number": request.form["card_number"],
                        "exp_month": request.form["exp_month"],
                        "exp_year": request.form["exp_year"],
                        "cvc": request.form["cvc"],
                    },
                )

                payment_id = payment_method.id
                stripe.PaymentMethod.attach(
                    payment_id, customer=stripe_customer_id,
                )
                resp = DataResponse(True, "Added Payment method")
                return resp.status()
        except Exception as e:
            return str(e)[:105]


@stripehandler.route("/<contact_id>/change_payment_method", methods=["PATCH"])
@user_required()
def change_payment_method(contact_id):
    stripe.api_key = stripe_keys["secret_key"]
    contact = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).first()
    if contact:
        stripe_customer_id = stripe.Customer.list(email=contact.primary_email, limit=1)[
            "data"
        ][0]["id"]
        try:

            token = stripe.Token.create(
                card={
                    "number": request.form["card_number"],
                    "exp_month": request.form["exp_month"],
                    "exp_year": request.form["exp_year"],
                    "cvc": request.form["cvc"],
                },
            )

            token_id = token["id"]
            source = stripe.Customer.create_source(stripe_customer_id, source=token_id,)
            stripe.Customer.modify(
                stripe_customer_id,
                default_source=source["id"],
                invoice_settings={"default_payment_method": source["id"]},
            )

            resp = DataResponse(True, "Changed Payment method")
            return resp.status()
        except Exception as e:
            return str(e)[:400]


@stripehandler.route("/<contact_id>/view_payment_method", methods=["GET"])
@user_required()
def view_payment_method(contact_id):
    stripe.api_key = stripe_keys["secret_key"]
    contact = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).first()
    if contact:
        stripe_customer_id = stripe.Customer.list(email=contact.primary_email, limit=1)[
            "data"
        ][0]["id"]
        try:

            payment_methods = stripe.PaymentIntent.list(
                customer=stripe_customer_id, limit=1
            )

            return jsonify(payment_methods), 200
        except Exception as e:
            return str(e)[:105]


@stripehandler.route("/stripe/recurring/update_payment/<recurring_plan_id>", methods=["PATCH"])
@user_required()
def update_payment_method(recurring_plan_id):
    try:
        recurring_plan = ScheduleRecurringDonation.query.filter_by(
            id=recurring_plan_id
        ).first()
        stripe_customer_id = recurring_plan.customer_id
        token = stripe.Token.create(
            card={
                "number": request.form["card_number"],
                "exp_month": request.form["exp_month"],
                "exp_year": request.form["exp_year"],
                "cvc": request.form["cvc"],
            },
        )
        token_id = token["id"]
        source = stripe.Customer.create_source(stripe_customer_id, source=token_id,)
        stripe.Customer.modify(
            stripe_customer_id,
            default_source=source["id"],
            invoice_settings={"default_payment_method": source["id"]},
        )
        resp = DataResponse(True,"PaymentMethod Details are updated ")
        return resp.status()
    except Exception as e:
        return str(e)[:105]
