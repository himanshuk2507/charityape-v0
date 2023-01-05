from flask import Blueprint, request
from flask_jwt_extended import get_jwt, jwt_required
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers

from src.donations.one_time_transactions.models import OneTimeTransaction, PayPalTransaction
from src.library.base_helpers.chunk_list import chunk_list
from src.payment.paypal.paypal_action import ProcessPayPal
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict


one_time_transactions_tab_endpoints = Blueprint(
    'one_time_transactions_tab_endpoints', __name__)


'''
@route GET /donations/one-time-transactions
@desc List One-time Transactions
@access Admin
'''


@one_time_transactions_tab_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_transactions_route():
    try:
        organization_id = get_jwt().get('org')
        data = Paginator(
            model=OneTimeTransaction,
            query=OneTimeTransaction.query,
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
@route POST /donations/one-time-transactions
@desc Create Transaction
@access Admin
'''


@one_time_transactions_tab_endpoints.route('', methods=['POST'])
@admin_required()
def create_transaction_route():
    try:
        body = request.json
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = OneTimeTransaction.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, str(result_data)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/one-time-transactions/<uuid>
@desc Fetch Transaction by ID
@access Admin
'''


@one_time_transactions_tab_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_transaction_by_id_route(id):
    try:
        transaction = OneTimeTransaction.fetch_by_id(
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
@route PATCH /donations/one-time-transactions/<uuid>
@desc Update Transaction by ID
@access Admin
'''


@one_time_transactions_tab_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_transaction_by_id_route(id):
    try:
        body = request.json
        transaction: OneTimeTransaction = OneTimeTransaction.fetch_by_id(
            id=id,
            organization_id=get_jwt().get('org')
        )

        if not transaction:
            return Response(False, 'No transaction with this ID exists').respond()

        result_bool, result_data = transaction.update(data=body)

        if not result_bool:
            return Response(False, result_data).respond()

        return Response(True, model_to_dict(transaction)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DLEETE /donations/one-time-transactions
@desc Delete Transactions
@access Admin
'''


@one_time_transactions_tab_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_transactions_by_id_route():
    try:
        body = request.json
        if not body or body.get('ids') is None:
            return Response(False, '`ids` is a required field`').respond()

        ids = body.get('ids', [])
        if len(ids) == 0:
            return Response(False, 'No transactions provided for DELETE operation').respond()

        OneTimeTransaction.delete_many_by_id(ids, get_jwt().get('org'))

        return Response(True, 'Transaction(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /donations/one-time-transactions/paypal
@desc Create PayPal Transaction Order
@access Admin
'''
@one_time_transactions_tab_endpoints.route('/paypal', methods=['POST'])
@admin_required()
def create_paypal_transaction_route():
    admin_id = get_jwt().get('id')
    organization_id = get_jwt().get('org')
    try:
        body = request.json 
        body['organization_id'] = organization_id
        result_bool, result_data = PayPalTransaction.register(body, admin_id)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, str(result_data)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
     

'''
@route GET /donations/one-time-transactions/paypal/success
@desc GET transaction refrence from paypal and process
'''
@one_time_transactions_tab_endpoints.route('/paypal/success', methods=['GET'])
@jwt_required(optional=True)
def paypal_success():
    try:
        id = request.args.get('token')
        process_bool, process_message = ProcessPayPal(token=id).update_paypal_transaction()
        if process_bool: 
            return Response(True, process_message).respond()
        return Response(False, "Something went wrong", 500).respond()
    except Exception as e:
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/one-time-transactions/paypal/<uuid>
@desc Fetch PayPal Transaction by ID
@access Admin
'''
@one_time_transactions_tab_endpoints.route('/paypal/<uuid:id>', methods=['GET'])
@admin_required()
def fetch_pending_paypal_transaction_by_id_route(id):
    try:
        paypal = PayPalTransaction.fetch_by_id(
            id = id,
            organization_id = get_jwt().get('org')
        )
        
        if not paypal:
            return Response(False, 'No transaction with this ID exists').respond()

        return Response(True, model_to_dict(paypal)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
    

'''
@route GET /donations/one-time-transactions/paypal
@desc List PayPal Pending Transactions
@access Admin
'''
@one_time_transactions_tab_endpoints.route('/paypal', methods=['GET'])
@admin_required()
def fetch_paypal_pending_transactions_route():
    try:
        data = Paginator(
            model=PayPalTransaction,
            query=PayPalTransaction.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
