from operator import and_
from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from src.contacts.contact_users.models import ContactUsers

from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db

from .models import Households


households_tab_endpoints = Blueprint('households_tab_endpoints', __name__)


'''
@route GET /contacts/households
@desc List households
@access Admin
'''


@households_tab_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_all_households_route():
    try:
        data = Paginator(
            model=Households,
            query=Households.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /contacts/households
@desc Create household
@access Admin
'''


@households_tab_endpoints.route('', methods=['POST'])
@admin_required()
def create_household_route():
    body = request.json
    body['organization_id'] = get_jwt().get('org')

    try:
        result_bool, result_data = Households.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DELETE /contacts/households
@desc Delete Households by ID
@access Admin
'''


@households_tab_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_households_route():
    body = request.json
    households = body.get('households', [])

    if len(households) == 0:
        return Response(False, 'No households to perform DELETE operation on').respond()

    try:
        Households.delete_many_by_id(households, get_jwt().get('org'))
        
        return Response(True, 'Household(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/households/<uuid>
@desc Fetch Household by ID
@access Admin
'''


@households_tab_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_household_by_id_route(id):
    try:
        household = Households.fetch_by_id(
            id, organization_id=get_jwt().get('org'))
        return Response(True, model_to_dict(household)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /contacts/households/<uuid>
@desc Update Household by ID
@access Admin
'''


@households_tab_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_household_by_id_route(id):
    try:
        body = request.json
        household = Households.fetch_by_id(
            id, organization_id=get_jwt().get('org'))

        # validations
        if not household:
            return Response(False, 'This household does not exist').respond()

        allowed_fields = ['name']
        for field in body.keys():
            if field in allowed_fields:
                setattr(household, field, body.get(field))

        db.session.add(household)
        db.session.commit()

        return Response(True, model_to_dict(household)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/households/<uuid>/members
@desc Fetch Household members
@access Admin
'''


@households_tab_endpoints.route('<uuid:id>/members', methods=['GET'])
@admin_required()
def fetch_household_members_route(id):
    try:
        data = Paginator(
            model=ContactUsers,
            query=ContactUsers.query.filter(
                ContactUsers.households.contains([id])),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
