from operator import and_
from typing import List
from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from src.contacts.contact_users.models import ContactUsers

from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.custom_validator import Validator
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db

from .models import ContactInteraction


contact_interactions_endpoints = Blueprint('contact_interactions_endpoints', __name__)


'''
@route POST /contacts/interactions
@desc Create Interaction
@access Admin
'''
@contact_interactions_endpoints.route('', methods=['POST'])
@admin_required()
def create_interaction_route():
    try:
        body = request.json 
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = ContactInteraction.register(body)

        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /contacts/interactions
@desc List Contact & Company Interactions
@access Admin
'''
@contact_interactions_endpoints.route('', methods=['GET'])
@admin_required()
def list_interaction_route():
    try:
        # find all interactions where organization_id = get_jwt().get('org')
        data = Paginator(
            model=ContactInteraction,
            query=ContactInteraction.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()