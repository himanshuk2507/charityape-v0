from flask import Blueprint, request
from flask_jwt_extended import get_jwt, jwt_required
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers

from src.library.base_helpers.chunk_list import chunk_list
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.profile.models import Admin
from src.profile.payment_settings.stripe.models import StripeSettings

from .models import RecurringTransaction
from src.payment.paypal.paypal_action import ProcessPayPal
from .models import RecurringTransaction, PayPalRecurringTransaction


recurring_transactions_tab_endpoints = Blueprint(
    'recurring_transactions_tab_endpoints', __name__)


'''
@route GET /donations/recurring-transactions
@desc List Recurring Transactions
@access Admin
'''


@recurring_transactions_tab_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_transactions_route():
    try:
        organization_id = get_jwt().get('org')
        data = Paginator(
            model=RecurringTransaction,
            query_string=Paginator.get_query_string(request.url),
            organization_id=organization_id
        ).result
        for transaction in data['rows']:
            contact = transaction.get(
                'contact_id') or transaction.get('company_id')
            if contact is not None:
                contact = ContactUsers.fetch_by_id(
                    id=contact, organization_id=organization_id
                ) or ContactCompanies.fetch_by_id(
                    id=contact, organization_id=organization_id
                )
                transaction['contact'] = model_to_dict(contact)

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /donations/recurring-transactions
@desc Create Transaction
@access Admin
'''


@recurring_transactions_tab_endpoints.route('', methods=['POST'])
@admin_required()
def create_transaction_route():
    try:
        body = request.json
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = RecurringTransaction.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, str(result_data)).respond()
    except Exception as e:
        raise e
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/recurring-transactions/<uuid>
@desc Fetch Transaction by ID
@access Admin
'''


@recurring_transactions_tab_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_transaction_by_id_route(id):
    try:
        transaction = RecurringTransaction.fetch_by_id(
            id=id,
            organization_id=get_jwt().get('org')
        )

        if not transaction:
            return Response(False, 'No transaction with this ID exists').respond()

        return Response(True, model_to_dict(transaction)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /donations/recurring-transactions/<uuid>
@desc Update Transaction by ID
@access Admin
'''


@recurring_transactions_tab_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_transaction_by_id_route(id):
    try:
        body = request.json
        claims = get_jwt()
        organization_id = claims.get('org')
        admin_id = claims.get('id')
        transaction: RecurringTransaction = RecurringTransaction.fetch_by_id(
            id=id,
            organization_id=organization_id
        )

        if not transaction:
            return Response(False, 'No transaction with this ID exists').respond()

        stripe_settings: StripeSettings = Admin.fetch_by_id(
            id=admin_id, organization_id=organization_id).get_stripe_settings()

        result_bool, result_data = transaction.update(
            data=body,
            api_key=stripe_settings.secret_key if stripe_settings else None
        )

        if not result_bool:
            return Response(False, result_data).respond()

        return Response(True, model_to_dict(transaction)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DELETE /donations/recurring-transactions
@desc Delete Transactions
@access Admin
'''


@recurring_transactions_tab_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_transactions_by_id_route():
    try:
        body = request.json

        if not body or body.get('ids') is None:
            return Response(False, '`ids` is a required field`').respond()

        ids = body.get('ids', [])
        if len(ids) == 0:
            return Response(False, 'No transactions provided for DELETE operation').respond()

        organization_id = get_jwt().get('org')
        RecurringTransaction.delete_many_by_id(ids, organization_id)

        return Response(True, 'Transaction(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /donations/recurring-transactions/paypal
@desc Create Transaction
@access Admin
'''
@recurring_transactions_tab_endpoints.route('/paypal', methods=['POST'])
@admin_required()
def create_paypal_transaction_route():
    try:
        body = request.json 
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = PayPalRecurringTransaction.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, str(result_data)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
    
    


'''
@route GET /donations/recurring-transactions/paypal
@desc List PayPal Recurring Transactions
@access Admin
'''
@recurring_transactions_tab_endpoints.route('/paypal', methods=['GET'])
@admin_required()
def fetch_paypal_transactions_route():
    try:
        data = Paginator(
            model=PayPalRecurringTransaction,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
    
    

'''
@route GET /donations/recurring-transactions/paypal/<uuid>
@desc Fetch PayPal Transaction by ID
@access Admin
'''
@recurring_transactions_tab_endpoints.route('/paypal/<uuid:id>', methods=['GET'])
@admin_required()
def fetch_paypal_transaction_by_id_route(id):
    try:
        transaction = PayPalRecurringTransaction.fetch_by_id(
            id = id,
            organization_id = get_jwt().get('org')
        )
        
        if not transaction:
            return Response(False, 'No transaction with this ID exists').respond()

        return Response(True, model_to_dict(transaction)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
    
    

'''
@route GET /donations/one-time-transactions/paypal/subscription/success
@desc GET transaction refrence from paypal and process
'''
@recurring_transactions_tab_endpoints.route('/paypal/subscription/success', methods=['GET'])
@jwt_required(optional=True)
def paypal_recuring_success():
    subscription_id = request.args.get('subscription_id')
    ba_token = request.args.get('ba_token')
    process_bool, process_message = ProcessPayPal(token=subscription_id).update_paypal_subscription(ba_token)
    if process_bool: 
        return Response(True, process_message).respond()
    return Response(False, process_message, 500).respond()



'''
@route PATCH /donations/one-time-transactions/paypal/<subscription_id>/<action>
@desc PATCH transaction refrence from paypal and process
'''
@recurring_transactions_tab_endpoints.route('/paypal/<subscription_id>/<action>', methods=['PATCH'])
@admin_required()
def paypal_subscription_action(action, subscription_id):
    print(action)
    body = request.json
    match action:
        case "suspend":
            action_bool, action_data = ProcessPayPal(token=subscription_id, data=body).suspend_paypal_subscription()
            if action_bool:
                return Response(True, action_data).respond()
            return Response(False, action_data, 500).respond()
        case "activate":
            action_bool, action_data = ProcessPayPal(token=subscription_id, data=body).activate_paypal_subscription()
            if action_bool:
                return Response(True, action_data).respond()
            return Response(False, action_data, 500).respond()
        case "cancle":
            action_bool, action_data = ProcessPayPal(token=subscription_id, data=body).cancle_paypal_subscription()
            if action_bool:
                return Response(True, action_data).respond()
            return Response(False, action_data, 500).respond()
        case _:
            return Response(False, "action must be `suspend`, `activate` or `cancle`", 500).respond()