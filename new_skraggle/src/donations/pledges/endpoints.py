from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from src.campaigns.models import Campaign
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.donations.pledges.models import Pledge, PledgeInstallment
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.library.base_helpers.chunk_list import chunk_list
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db


pledges_tab_endpoints = Blueprint('pledges_tab_endpoints', __name__)


'''
@route GET /donations/pledges
@desc List Pledges
@access Admin
'''


@pledges_tab_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_pledges_route():
    try:
        data = Paginator(
            model=Pledge,
            query=Pledge.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /donations/pledges
@desc Create Pledge
@access Admin
'''


@pledges_tab_endpoints.route('', methods=['POST'])
@admin_required()
def create_pledges_route():
    try:
        body = request.json
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = Pledge.register(body)

        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/pledges/<uuid>
@desc Fetch Pledge by ID
@access Admin
'''


@pledges_tab_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_pledge_by_id_route(id):
    try:
        organization_id = get_jwt().get('org')

        pledge: Pledge = Pledge.fetch_by_id(
            id=id, organization_id=organization_id)

        if not pledge:
            return Response(False, 'No pledge exists with this ID').respond()

        data = model_to_dict(pledge)

        if pledge.contact_id:
            data['contact'] = ContactUsers.fetch_by_id(
                pledge.contact_id, organization_id=organization_id)
        elif pledge.company_id:
            data['contact'] = ContactCompanies.fetch_by_id(
                pledge.campaign_id, organization_id=organization_id)
        data['contact'] = model_to_dict(data.get('contact'))

        if pledge.campaign_id:
            campaign = Campaign.fetch_by_id(
                pledge.campaign_id, organization_id=organization_id)
            if campaign:
                data['campaign'] = model_to_dict(campaign)

        installments = [model_to_dict(installment)
                        for installment in pledge.installments]
        if len(installments) > 0:
            data['installments'] = installments

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /donations/pledges/<uuid>
@desc Update Pledge by ID
@access Admin
'''


@pledges_tab_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_pledge_by_id_route(id):
    try:
        body = request.json
        pledge: Pledge = Pledge.fetch_by_id(
            id=id, organization_id=get_jwt().get('org'))
        result_bool, result_data = pledge.update(data=body)

        if not result_bool:
            return Response(False, str(result_data), 500).respond()

        return Response(True, model_to_dict(result_data)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DELETE /donations/pledges
@desc Delete Pledges by ID
@access Admin
'''


@pledges_tab_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_pledges_by_id_route():
    try:
        body = request.json
        if not body or not body.get('ids'):
            raise Exception('`ids` is a required field')

        Pledge.delete_many_by_id(ids=body.get(
            'ids'), organization_id=get_jwt().get('org'))

        return Response(True, 'Pledge(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
