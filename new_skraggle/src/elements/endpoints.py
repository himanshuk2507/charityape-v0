from operator import and_
from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db
from .models import Element


elements_tab_endpoints = Blueprint('elements_tab_endpoints', __name__)


'''
@route GET /elements
@desc List Elements
@access Admin
'''


@elements_tab_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_elements_route():
    try:
        data = Paginator(
            model=Element,
            query=Element.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /elements
@desc Create Element
@access Admin
'''


@elements_tab_endpoints.route('', methods=['POST'])
@admin_required()
def create_element_route():
    try:
        body = request.json
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = Element.register(body)

        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /elements/<uuid>
@desc Fetch Element by ID
@access Admin
'''


@elements_tab_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_element_by_id_route(id):
    try:
        element = Element.fetch_by_id(id, organization_id=get_jwt().get('org'))

        if not element:
            return Response(False, 'No element with this ID exists').respond()

        return Response(True, model_to_dict(element)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /elements/<uuid>
@desc Update Element by ID
@access Admin
'''


@elements_tab_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_element_by_id_route(id):
    try:
        body = request.json
        element: Element = Element.fetch_by_id(
            id=id, organization_id=get_jwt().get('org'))

        result_bool, result_data = element.update(body)

        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DLEETE /elements
@desc Delete Elements by ID
@access Admin
'''


@elements_tab_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_elements_by_id_route():
    try:
        body = request.json

        if not body or body.get('elements') is None:
            return Response(False, '`elements` is a required field').respond()

        elements = body.get('elements', [])
        if len(elements) == 0:
            return Response(False, 'No elements to perform DELETE operation on').respond()

        Element.delete_many_by_id(elements, get_jwt().get('org'))
        return Response(True, 'Element(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
