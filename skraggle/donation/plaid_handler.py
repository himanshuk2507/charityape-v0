import json
from datetime import datetime
import time
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.payment_initiation_address import PaymentInitiationAddress
from plaid.model.payment_initiation_recipient_create_request import (
    PaymentInitiationRecipientCreateRequest,
)
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.sandbox_public_token_create_request import (
    SandboxPublicTokenCreateRequest,
)
from plaid.api import plaid_api
from flask import Blueprint

from flask import jsonify, request
import plaid
import os

from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

plaidhandler = Blueprint("plaidhandler", __name__)

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")
PLAID_PRODUCTS = os.getenv("PLAID_PRODUCTS", "transactions").split(",")
# PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# will be able to select institutions from.
PLAID_COUNTRY_CODES = os.getenv("PLAID_COUNTRY_CODES", "US").split(",")
INSTITUTION_ID = "ins_109508"


def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value


host = plaid.Environment.Sandbox

if PLAID_ENV == "sandbox":
    host = plaid.Environment.Sandbox

if PLAID_ENV == "development":
    host = plaid.Environment.Development

if PLAID_ENV == "production":
    host = plaid.Environment.Production
PLAID_REDIRECT_URI = empty_to_none("PLAID_REDIRECT_URI")

configuration = plaid.Configuration(
    host=host,
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "plaidVersion": "2020-09-14",
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))

payment_id = None
transfer_id = None
item_id = None
# access_token = "access-sandbox-1d675787-b0a8-466a-80ee-24b4f419aa76"
# @plaidhandler.route("/api/info", methods=["POST"])
# def info():
#     globalhelpers access_token
#     globalhelpers item_id
#     return jsonify(
#         {"item_id": item_id, "access_token": access_token, "products": PLAID_PRODUCTS}
#     )


# api to create a link token which is used for link initialisation


@plaidhandler.route("/api/create_link_token", methods=["POST"])
def create_link_token():
    try:
        request = LinkTokenCreateRequest(
            products=products,
            client_name="Plaid Quickstart",
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id=str(time.time())),
        )

        # create link token
        response = client.link_token_create(request)
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        return json.loads(e.body)


# Exchange token flow - exchange a Link public_token for
# an API access_token


@plaidhandler.route("/api/set_access_token", methods=["POST"])
def get_access_token():
    global access_token
    global item_id
    global transfer_id
    public_token = request.form["public_token"]
    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response["access_token"]
        item_id = exchange_response["item_id"]
        return jsonify(exchange_response.to_dict())
    except plaid.ApiException as e:
        return json.loads(e.body)


# Get Sandbox public token and exchange for access token
@plaidhandler.route("/api/get_public_access_token", methods=["POST"])
def get_public_access_token():
    global access_token
    pt_request = SandboxPublicTokenCreateRequest(
        institution_id=INSTITUTION_ID, initial_products=[Products("transactions")]
    )
    pt_response = client.sandbox_public_token_create(pt_request)
    exchange_request = ItemPublicTokenExchangeRequest(
        public_token=pt_response["public_token"]
    )
    exchange_response = client.item_public_token_exchange(exchange_request)
    access_token = exchange_response.to_dict()["access_token"]
    return jsonify(exchange_response.to_dict())


# Pull Item details for each account associated
@plaidhandler.route("/api/get_item_details", methods=["GET"])
def get_item_details():
    request = ItemGetRequest(access_token=access_token)
    response = client.item_get(request)
    item = response["item"]
    status = response["status"]
    return jsonify(item.to_dict())


# Pull Account details like accout number and account routing numnber  for each account associated
@plaidhandler.route("/api/get_account_details", methods=["GET"])
def get_account_details():
    request = AuthGetRequest(access_token=access_token)
    response = client.auth_get(request)
    numbers = response["numbers"]
    return jsonify(numbers.to_dict())


# Pull real-time balance information for each account associated
# with the Item
@plaidhandler.route("/api/get_account_balance", methods=["GET"])
def get_account_balance():
    request = AccountsBalanceGetRequest(access_token=access_token)
    response = client.accounts_balance_get(request)
    return jsonify(response.to_dict())


# Pull all the transactions
@plaidhandler.route("/api/get_transactions", methods=["GET"])
def get_account_transactions():
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=datetime.strptime("24052010", "%d%m%Y").date(),
        end_date=datetime.strptime("24052010", "%d%m%Y").date(),
        options=TransactionsGetRequestOptions(),
    )
    response = client.transactions_get(request)
    return jsonify(response.to_dict())


# Pull all the transactions
@plaidhandler.route("/api/create_payment_receipt", methods=["POST"])
def create_payment_receipt():
    request = PaymentInitiationRecipientCreateRequest(
        name="John Doe",
        iban="GB33BUKB20201555555555",
        address=PaymentInitiationAddress(
            street=["street name 999"], city="city", postal_code="99999", country="GB"
        ),
    )
    response = client.payment_initiation_recipient_create(request)
    recipient_id = response["recipient_id"]
    return jsonify(response.to_dict())


# plaid to generate bank account token for  stripe ach transfer
