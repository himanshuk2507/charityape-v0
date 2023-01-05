from operator import and_

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from sqlalchemy.engine import Row

from src.campaigns.models import Campaign
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.library.base_helpers.chunk_list import chunk_list
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db
from src.mail_blasts.models import MailBlast
from src.p2p.models import P2P
from src.forms.models import Form
from src.elements.models import Element
from src.events.event.models import EventsInformation


campaign_tab_endpoints = Blueprint('campaign_tab_endpoints', __name__)


'''
@route GET /campaigns
@desc List Campaigns
@access Admin
'''
@campaign_tab_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_all_campaigns_route():
    try:
        data = Paginator(
            model=Campaign,
            query=Campaign.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route POST /campaigns
@desc Create Campaign
@access Admin
'''
@campaign_tab_endpoints.route('', methods=['POST'])
@admin_required()
def create_campaign_route():
    try:
        body = request.json 
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = Campaign.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route PATCH /campaigns/<uuid>
@desc Update Campaign by ID
@access Admin
'''
@campaign_tab_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_campaign_route(id):
    try:
        body = request.json 
        campaign: Campaign = Campaign.fetch_by_id(id=id, organization_id=get_jwt().get('org'))
        if not campaign:
            return Response(False, 'No campaign exists with this ID').respond()
        
        result_bool, result_data = campaign.update(body)
        
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route DELETE /campaigns/<uuid>
@desc Delete Campaign by ID
@access Admin
'''
@campaign_tab_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_campaign_route():
    try:
        body = request.json
        camapigns = body.get('campaigns', [])
        organization_id = get_jwt().get('org')

        if len(camapigns) == 0:
            return Response(False, 'No campaigns to perform DELETE operation on').respond()
            
        Campaign.delete_many_by_id(camapigns, organization_id)

        return Response(True, 'Campaign(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /campaigns/<uuid>
@desc Fetch Campaign by ID
@access Admin
'''
@campaign_tab_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_campaign_by_id_route(id):
    try:
        campaign: Campaign = Campaign.fetch_by_id(id, organization_id=get_jwt().get('org'))
        
        if not campaign:
            return Response(False, 'No campaign with this ID exists').respond()

        data = model_to_dict(campaign)
        data['amount_raised'] = campaign.amount_raised
        data['donations_amount'] = campaign.donations_amount
        data['revenue_amount'] = campaign.revenue_amount
        data['volunteer_hours'] = campaign.volunteer_hours

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /campaigns/<uuid>/p2p
@desc Fetch P2Ps associated with this Campaign
@access Admin
'''
@campaign_tab_endpoints.route('<uuid:id>/p2p', methods=['GET'])
@admin_required()
def fetch_campaign_p2ps_route(id):
    try:
        organization_id=get_jwt().get('org')
        data = Paginator(
            model=P2P,
            query=P2P.query.filter_by(campaign_id = id),
            query_string=Paginator.get_query_string(request.url),
            organization_id=organization_id
        ).result

        for p2p in data['rows']:
            p2p['raised'] = P2P.fetch_by_id(
                id=p2p['id'],
                organization_id=p2p['organization_id']
            ).amount_raised()
            if not p2p.get('campaign_id'):
                p2p['campaign'] = None
            else:
                p2p['campaign'] = db.session.query(Campaign.name).filter(
                        and_(
                            Campaign.id == p2p['campaign_id'],
                            Campaign.organization_id == organization_id
                        )
                    ).one_or_none()
                p2p['campaign'] = p2p['campaign'][0] if p2p['campaign'] is not None and isinstance(p2p['campaign'], Row) and len(p2p['campaign']) > 0 else None

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /campaigns/<uuid>/forms
@desc Fetch Forms associated with this Campaign
@access Admin
'''
@campaign_tab_endpoints.route('<uuid:id>/forms', methods=['GET'])
@admin_required()
def fetch_campaign_forms_route(id):
    try:
        data = Paginator(
            model=Form,
            query=Form.query.filter_by(campaign_id = id),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /campaigns/<uuid>/elements
@desc Fetch Elements associated with this Campaign
@access Admin
'''
@campaign_tab_endpoints.route('<uuid:id>/elements', methods=['GET'])
@admin_required()
def fetch_campaign_elements_route(id):
    try:
        data = Paginator(
            model=Element,
            query=Element.query.filter_by(campaign_id = id),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /campaigns/<uuid>/mailblasts
@desc Fetch Mailblasts associated with this Campaign
@access Admin
'''
@campaign_tab_endpoints.route('<uuid:id>/mailblasts', methods=['GET'])
@admin_required()
def fetch_campaign_mailblasts_route(id):
    try:
        data = Paginator(
            model=MailBlast,
            query=MailBlast.query.filter_by(campaign_id = id),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /campaigns/<uuid>/events
@desc Fetch Events associated with this Campaign
@access Admin
'''
@campaign_tab_endpoints.route('<uuid:id>/events', methods=['GET'])
@admin_required()
def fetch_campaign_events_route(id):
    try:
        data = Paginator(
            model=EventsInformation,
            query=EventsInformation.query.filter_by(campaign_id = id),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()