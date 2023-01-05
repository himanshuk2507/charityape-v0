from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from src.donations.sources.models import DonationSource

from src.library.base_helpers.chunk_list import chunk_list
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict


donation_sources_endpoints = Blueprint('donation_sources_endpoints', __name__)


'''
@route GET /donations/sources
@desc List Donation Sources
@access Admin
'''


@donation_sources_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_sources_route():
    try:
        data = Paginator(
            model=DonationSource,
            query=DonationSource.query.filter_by(
                organization_id=get_jwt().get('org')),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /donations/sources
@desc Create Donation Source
@access Admin
'''


@donation_sources_endpoints.route('', methods=['POST'])
@admin_required()
def create_source_route():
    try:
        body = request.json
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = DonationSource.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, str(result_data)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/sources/<uuid>
@desc Fetch Donation Source by ID
@access Admin
'''


@donation_sources_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_source_by_id_route(id):
    try:
        source = DonationSource.fetch_by_id(
            id=id, organization_id=get_jwt().get('org'))

        if not source:
            return Response(False, 'No source with this ID exists').respond()

        return Response(True, model_to_dict(source)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /donations/sources/<uuid>
@desc Update Donation Source by ID
@access Admin
'''


@donation_sources_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_source_by_id_route(id):
    try:
        body = request.json
        source = DonationSource.fetch_by_id(
            id=id, organization_id=get_jwt().get('org'))
        if not source:
            return Response(False, str('No source exists with this ID')).respond()

        result_bool, result_data = source.update(body)
        if not result_bool:
            return Response(False, str(result_data)).respond()
        return Response(True, model_to_dict(result_data)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DELETE /donations/sources
@desc Delete Donation Source by ID
@access Admin
'''


@donation_sources_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_sources_by_id_route():
    try:
        body = request.json

        if not body or body.get('ids') is None:
            return Response(False, '`ids` is a required field').respond()

        ids = body.get('ids', [])
        if len(ids) == 0:
            return Response(False, 'No sources provided for DELETE operation').respond()

        DonationSource.delete_many_by_id(ids, get_jwt().get('org'))
        return Response(True, 'Source(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
