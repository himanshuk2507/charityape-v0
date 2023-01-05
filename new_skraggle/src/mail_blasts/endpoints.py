from operator import and_
from typing import List
from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from src.campaigns.models import Campaign
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.contacts.tags.models import ContactTags
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction

from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db
from .models import MailBlast


mailblast_tab_endpoints = Blueprint('mailblast_tab_endpoints', __name__)


'''
@route GET /mailblasts
@desc List Mail blasts
@access Admin
'''
@mailblast_tab_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_mailblasts_route():
    try:
        query = MailBlast.query
        if 'archived' in request.url:
            query = query.filter_by(archived = True)
        else:
            query = query.filter_by(archived = False)
        data = Paginator(
            model=MailBlast,
            query=query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        for mailblast in data['rows']:
            mailblast['assignee'] = model_to_dict(
                MailBlast.fetch_by_id(
                    id=mailblast['id'],
                    organization_id=mailblast['organization_id']
                ).assignee
            )

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route POST /mailblasts
@desc Create Mailblast
@access Admin
'''
@mailblast_tab_endpoints.route('', methods=['POST'])
@admin_required()
def create_mailblast_route():
    try:
        body = request.json 
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = MailBlast.register(body)

        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /mailblasts/subscription
@desc Fetch a List of Contacts That are Subscribed to MailBlasts
@access Admin
'''
@mailblast_tab_endpoints.route('subscription', methods=['GET'])
@admin_required()
def fetch_mailblast_subscriptions_route():
    try:
        organization_id = get_jwt().get('org')
        filter_params = {
            'organization_id': organization_id,
            'is_subscribed_to_mailblasts': True
        }
        users: List[ContactUsers] = ContactUsers.query.filter_by(**filter_params).all() + ContactCompanies.query.filter_by(**filter_params).all()
        users = [model_to_dict(user) for user in users]
        for user in users:
            user['tags'] = [
                model_to_dict(tag) for tag in ContactTags.query.filter(
                    and_(
                        ContactTags.id.in_(user.get('tags', [])),
                        ContactTags.organization_id == user.get('organisation_id')
                    )
                ).all()
            ]
        
        return Response(True, users).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /mailblasts/<uuid>
@desc Fetch Mailblast by ID
@access Admin
'''
@mailblast_tab_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_mailblast_by_id_route(id):
    try:
        organization_id = get_jwt().get('org')
        mailblast = MailBlast.fetch_by_id(id, organization_id)
        
        if not mailblast:
            return Response(False, 'No mailblast with this ID exists').respond()
        mailblast = model_to_dict(mailblast)
        campaign_id = mailblast.get('campaign_id')
        if campaign_id:
            campaign: Campaign = Campaign.fetch_by_id(campaign_id)
            mailblast['raised_amount'] = campaign.amount_raised
            mailblast['target_amount'] = campaign.fundraising_goal
            mailblast['campaign'] = model_to_dict(campaign)

        return Response(True, mailblast).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route PATCH /mailblasts/<uuid>
@desc Update Mailblast by ID
@access Admin
'''
@mailblast_tab_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_mailblast_by_id_route(id):
    try:
        body = request.json 
        mailblast: MailBlast = MailBlast.fetch_by_id(id=id, organization_id=get_jwt().get('org'))
        
        result_bool, result_data = mailblast.update(body)
        
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route DELETE /mailblasts
@desc Delete Mailblasts by ID
@access Admin
'''
@mailblast_tab_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_mailblasts_by_id_route():
    try:
        body = request.json
        if not body or body.get('mailblasts') is None:
            return Response(False, '`mailblasts` is a required field').respond()

        mailblasts = body.get('mailblasts', [])
        if len(mailblasts) == 0:
            return Response(False, 'No mailblasts to perform DELETE operation on').respond()
        
        MailBlast.delete_many_by_id(mailblasts, get_jwt().get('org'))
        return Response(True, 'MailBlast(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /mailblasts/<uuid>/mailing-list
@desc Retrieve mailing list
@access Admin
'''
@mailblast_tab_endpoints.route('<uuid:id>/mailing-list', methods=['GET'])
@admin_required()
def fetch_mailing_list_route(id):
    try:
        organization_id = get_jwt().get('org')
        mailblast: MailBlast = MailBlast.fetch_by_id(
            id=id,
            organization_id=organization_id
        )
        mailing_list = [
            model_to_dict(recipient) for recipient in mailblast.get_mailing_list()
        ]
        
        return Response(True, mailing_list).respond()

    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
