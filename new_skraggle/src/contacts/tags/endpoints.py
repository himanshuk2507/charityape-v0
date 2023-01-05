from operator import and_
from typing import List
from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from sqlalchemy import not_
from src.contacts.contact_users.models import ContactUsers

from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db

from .models import ContactTags


contact_tags_tab_endpoints = Blueprint('contact_tags_tab_endpoints', __name__)


'''
@route GET /contacts/tags
@desc List tags
@access Admin
'''


@contact_tags_tab_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_all_tags_route():
    try:
        data = Paginator(
            model=ContactTags,
            query=ContactTags.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /contacts/tags
@desc Create tag
@access Admin
'''


@contact_tags_tab_endpoints.route('', methods=['POST'])
@admin_required()
def create_tag_route():
    body = request.json
    body['organization_id'] = get_jwt().get('org')

    try:
        result_bool, result_data = ContactTags.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DELETE /contacts/tags
@desc Delete ContactTags by ID
@access Admin
'''


@contact_tags_tab_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_tags_route():
    body = request.json
    tags = body.get('tags', [])

    if len(tags) == 0:
        return Response(False, 'No tags to perform DELETE operation on').respond()

    try:
        ContactTags.delete_many_by_id(tags, get_jwt().get('org'))

        return Response(True, 'Tag(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/tags/<uuid>
@desc Fetch ContactTag by ID
@access Admin
'''


@contact_tags_tab_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_tag_by_id_route(id):
    try:
        tag = ContactTags.fetch_by_id(id, organization_id=get_jwt().get('org'))
        data = model_to_dict(tag)
        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/tags/<uuid>/contacts
@desc Fetch tagged contacts
@access Admin
'''


@contact_tags_tab_endpoints.route('<uuid:id>/contacts', methods=['GET'])
@admin_required()
def fetch_tagged_contacts_route(id):
    try:
        # does tag exist?
        if not ContactTags.id_exists(id=id, organization_id=get_jwt().get('org')):
            return Response(False, 'This tag does not exist').respond()

        data = Paginator(
            model=ContactUsers,
            query=ContactUsers.query.filter(
                ContactUsers.tags.contains(f"{{{id}}}")),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /contacts/tags/<uuid>
@desc Update ContactTags by ID
@access Admin
'''


@contact_tags_tab_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_tag_by_id_route(id):
    try:
        body = request.json
        tag = ContactTags.fetch_by_id(id, organization_id=get_jwt().get('org'))

        # validations
        if not tag:
            return Response(False, 'This tag does not exist')

        allowed_fields = ['name']
        for field in body.keys():
            if field in allowed_fields:
                setattr(tag, field, body.get(field))

        db.session.add(tag)
        db.session.commit()

        return Response(True, model_to_dict(tag)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
