from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from src.library.base_helpers.chunk_list import chunk_list
from src.library.base_helpers.model_to_dict import model_to_dict
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.app_config import db

from .models import ImpactArea


impact_area_endpoints = Blueprint('impact_area_endpoints', __name__)


'''
@route GET /impact-area
@desc List Impact Areas
@access Admin
'''
@impact_area_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_all_impact_areas_route():
    try:
        data = Paginator(
            model=ImpactArea,
            query=ImpactArea.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route POST /impact-area
@desc Create Impact Area
@access Admin
'''
@impact_area_endpoints.route('', methods=['POST'])
@admin_required()
def create_impact_area_route():
    try:
        body = request.json
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = ImpactArea.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route PATCH /impact-area/<uuid>
@desc Update Impact Area
@access Admin
'''
@impact_area_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_impact_area_route(id):
    try:
        body = request.json
        impact_area: ImpactArea = ImpactArea.fetch_by_id(id=id, organization_id=get_jwt().get('org'))
        if not impact_area:
            return Response(False, 'No impact area exists with this ID').respond()

        result_bool, result_data = impact_area.update(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /impact-area/<uuid>
@desc Fetch Impact Area by ID
@access Admin
'''
@impact_area_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_impact_area_by_id_route(id):
    try:
        impact_area: ImpactArea = ImpactArea.fetch_by_id(id=id, organization_id=get_jwt().get('org'))
        if not impact_area:
            return Response(False, 'No impact_area exists with this ID').respond()

        return Response(True, model_to_dict(impact_area)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route DELETE /impact-area
@desc Delete Impact Area by ID
@access Admin
'''
@impact_area_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_impact_area_by_id_route():
    try:
        body = request.json

        if not body or body.get('ids') is None:
            return Response(False, '`ids` is a required field').respond()

        impact_areas = body.get('ids', [])
        organization_id = get_jwt().get('org')

        if len(impact_areas) == 0:
            return Response(False, 'No impact areas to perform DELETE operation on').respond()
            
        ImpactArea.delete_many_by_id(
            ids=impact_areas,
            organization_id=organization_id
        )
        return Response(True, 'Impact area(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()