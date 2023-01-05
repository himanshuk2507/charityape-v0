from operator import and_
from typing import List
from flask import Blueprint, request
from src.app_config import db
from flask_jwt_extended import get_jwt
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.custom_validator import Validator
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from .models import Fields

fieldviews = Blueprint("fieldviews", __name__)

'''
@route POST /field/create
@desc Create Fields
@access Admin
'''


@fieldviews.route('/create', methods=["POST"])
@admin_required()
def create_fields():
    body = request.json
    body['organization_id'] = get_jwt().get('org')

    try:
        result_bool, result_data = Fields.register(body)
        print(result_bool)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /field
@desc All Fields
@access Admin
'''


@fieldviews.route('', methods=["GET"])
@admin_required()
def list_fields():
    try:
        data = Paginator(
            model=Fields,
            query=Fields.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /field/<uuid>
@desc Update Fields by ID
@access Admin
'''


@fieldviews.route("<uuid:id>", methods=["PATCH"])
@admin_required()
def update_fields(id):
    try:
        body = request.json
        fields = Fields.fetch_by_id(id, organization_id=get_jwt().get('org'))

        # validations
        if not fields:
            return Response(False, 'This Fields does not exist').respond()
        unallowed_fields = ['id', 'organization_id']

        for field in body.keys():
            if field not in unallowed_fields:
                setattr(fields, field, body.get(field))

        db.session.add(fields)
        db.session.commit()

        return Response(True, model_to_dict(fields)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /field/info/<uuid>
@desc Get Field by ID
@access Admin
'''


@fieldviews.route("/info/<uuid:id>", methods=["GET"])
@admin_required()
def field_info_by_id(id):
    field: Fields = Fields.fetch_by_id(id, organization_id=get_jwt().get('org'))
    if not field:
        return Response(False, "This Fields does not exist").respond()

    return Response(True, model_to_dict(field)).respond()


'''
@route DELETE /field/<uuid>
@desc Delete field by ID
@access Admin
'''


@fieldviews.route("", methods=["DELETE"])
@admin_required()
def delete_field():
    try:
        body = request.json
        if not body or body.get('ids') is None:
            return Response(False, '`ids` is a required field').respond()
        
        field_ids = body.get('ids', [])
        if len(field_ids) == 0:
            return Response(False, 'No fields to perform DELETE operation on').respond()
        
        Fields.delete_many_by_id(field_ids, get_jwt().get('org'))
        return Response(True, 'Field(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
