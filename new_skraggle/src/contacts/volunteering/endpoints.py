from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from src.contacts.volunteering.models import VolunteerActivity
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db


contacts_volunteer_activity_endpoints = Blueprint('contacts_volunteer_activity_endpoints', __name__)


'''
@route GET /contacts/volunteer-activity
@desc List Volunteer Activities for this Admin
@access Admin
'''
@contacts_volunteer_activity_endpoints.route('', methods=['GET'])
@admin_required()
def list_volunteer_activity_route():
    try:
        data = Paginator(
            model=VolunteerActivity,
            query=VolunteerActivity.query.filter_by(organization_id = get_jwt().get('org')),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route POST /contacts/volunteer-activity
@desc Create Volunteer Activity
@access Admin
'''
@contacts_volunteer_activity_endpoints.route('', methods=['POST'])
@admin_required()
def create_volunteer_activity_route():
    try:
        body = request.json 
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = VolunteerActivity.regsiter(body)

        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()