from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from src.library.base_helpers.chunk_list import chunk_list
from src.library.base_helpers.model_to_dict import model_to_dict
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.app_config import db

from .models import Keyword


keyword_endpoints = Blueprint('keyword_endpoints', __name__)


'''
@route GET /keyword
@desc List Keywords
@access Admin
'''
@keyword_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_all_keywords_route():
    try:
        data = Paginator(
            model=Keyword,
            query=Keyword.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route POST /keyword
@desc Create Keyword
@access Admin
'''
@keyword_endpoints.route('', methods=['POST'])
@admin_required()
def create_keywords_route():
    try:
        body = request.json
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = Keyword.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route PATCH /keyword/<uuid>
@desc Update Keyword
@access Admin
'''
@keyword_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_keywords_route(id):
    try:
        body = request.json
        keyword: Keyword = Keyword.fetch_by_id(id=id, organization_id=get_jwt().get('org'))
        if not keyword:
            return Response(False, 'No keyword exists with this ID').respond()

        result_bool, result_data = keyword.update(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /keyword/<uuid>
@desc Fetch Keyword by ID
@access Admin
'''
@keyword_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_keyword_by_id_route(id):
    try:
        keyword: Keyword = Keyword.fetch_by_id(id=id, organization_id=get_jwt().get('org'))
        if not keyword:
            return Response(False, 'No keyword exists with this ID').respond()

        return Response(True, model_to_dict(keyword)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route DELETE /keyword
@desc Delete Keywords by ID
@access Admin
'''
@keyword_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_keywords_by_id_route():
    try:
        body = request.json

        if not body or body.get('ids') is None:
            return Response(False, '`ids` is a required field').respond()

        keywords = body.get('ids', [])
        organization_id = get_jwt().get('org')

        if len(keywords) == 0:
            return Response(False, 'No keywords to perform DELETE operation on').respond()

        Keyword.delete_many_by_id(
            ids=keywords,
            organization_id=organization_id
        )
        return Response(True, 'Keyword(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()