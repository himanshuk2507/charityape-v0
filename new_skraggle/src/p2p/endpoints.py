from operator import and_

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from sqlalchemy.engine import Row

from src.campaigns.models import Campaign
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction
from src.library.decorators.authentication_decorators import admin_required
from src.library.donor_score import rank_by_donor_score_with_campaign
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db

from .models import P2P, P2PEmail


p2p_endpoints = Blueprint('p2p_endpoints', __name__)


'''
@route POST /p2p
@desc Create P2P
@access Admin
'''


@p2p_endpoints.route('', methods=['POST'])
@admin_required()
def create_p2p_route():
    try:
        body = request.json
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = P2P.register(body)

        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /p2p
@desc List P2Ps
@access Admin
'''


@p2p_endpoints.route('', methods=['GET'])
@admin_required()
def list_p2ps_route():
    try:
        organization_id = get_jwt().get('org')
        data = Paginator(
            model=P2P,
            query=P2P.query,
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
                p2p['campaign'] = p2p['campaign'][0] if p2p['campaign'] is not None and isinstance(
                    p2p['campaign'], Row) and len(p2p['campaign']) > 0 else None

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /p2p/<uuid>
@desc Fetch P2P by ID
@access Admin
'''


@p2p_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_p2p_by_id_route(id):
    try:
        p2p: P2P = P2P.fetch_by_id(id, organization_id=get_jwt().get('org'))
        if not p2p:
            return Response(False, "This p2p does not exist").respond()

        data = model_to_dict(p2p)
        data['sent_emails'] = [model_to_dict(
            email) for email in p2p.sent_emails or []]
        data['donations_count'] = p2p.donations_count
        data['raised'] = p2p.amount_raised()
        if not data.get('campaign_id'):
            data['campaign'] = None
        else:
            data['campaign'] = db.session.query(Campaign.name).filter(
                and_(
                    Campaign.id == p2p.campaign_id,
                    Campaign.organization_id == get_jwt().get('org')
                )
            ).one_or_none()
            data['campaign'] = data['campaign'][0] if data['campaign'] is not None and isinstance(
                data['campaign'], Row) and len(data['campaign']) > 0 else None

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /p2p/<uuid>
@desc Update P2P by ID
@access Admin
'''


@p2p_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_p2p_by_id_route(id):
    try:
        body = request.json

        p2p: P2P = P2P.fetch_by_id(id=id, organization_id=get_jwt().get('org'))

        result_bool, result_data = p2p.update(body)

        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DELETE /p2p
@desc Delete P2Ps
@access Admin
'''


@p2p_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_p2p_by_id_route():
    try:
        body = request.json
        if not body or body.get('ids') is None:
            return Response(False, '`ids` array is required in request body').respond()

        ids = body.get('ids', [])
        P2P.delete_many_by_id(ids, get_jwt().get('org'))

        return Response(True, 'P2P(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /p2p/<uuid>/donations
@desc Fetch Donations Associated with P2P
@access Admin
'''


@p2p_endpoints.route('<uuid:id>/donations', methods=['GET'])
@admin_required()
def fetch_associated_donations_route(id):
    try:
        organization_id = get_jwt().get('org')
        p2p: P2P = P2P.fetch_by_id(id)
        if not p2p:
            return Response(False, 'No P2P exists with this ID').respond()
        if not p2p.campaign_id:
            return Response(True, dict(
                has_next=False,
                has_previous=False,
                rows=[]
            )).respond()

        one_time = [
            model_to_dict(transaction) for transaction in OneTimeTransaction.query.filter(
                and_(
                    OneTimeTransaction.organization_id == organization_id,
                    and_(
                        OneTimeTransaction.campaign_id == p2p.campaign_id,
                        OneTimeTransaction.is_revenue == False
                    )
                )
            ).all()
        ]
        recurring = [
            model_to_dict(transaction) for transaction in RecurringTransaction.query.filter(
                and_(
                    RecurringTransaction.organization_id == organization_id,
                    and_(
                        RecurringTransaction.campaign_id == p2p.campaign_id,
                        RecurringTransaction.is_revenue == False
                    )
                )
            ).all()
        ]
        transactions = one_time + recurring
        for transaction in transactions:
            transaction['campaign'] = Campaign.fetch_by_id(
                id=transaction.get('campaign_id'),
                organization_id=organization_id
            ).name if transaction.get('campaign_id') else None

        return Response(True, dict(
            has_next=False,
            has_previous=False,
            rows=transactions
        )).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /p2p/<uuid>/ranked-participants
@desc Return List of Donors Ranked by Donor Score
@access Admin
'''


@p2p_endpoints.route('<uuid:id>/ranked-participants', methods=['GET'])
@admin_required()
def fetch_participants_by_rank_route(id):
    try:
        organization_id = get_jwt().get('org')
        p2p: P2P = P2P.fetch_by_id(id)
        if not p2p:
            return Response(False, 'No P2P exists with this ID').respond()
        if not p2p.campaign_id:
            return Response(True, dict(
                has_next=False,
                has_previous=False,
                rows=[]
            )).respond()

        one_time = OneTimeTransaction.query.filter(
            and_(
                OneTimeTransaction.organization_id == organization_id,
                and_(
                    OneTimeTransaction.campaign_id == p2p.campaign_id,
                    OneTimeTransaction.is_revenue == False
                )
            )
        ).all()
        recurring = RecurringTransaction.query.filter(
            and_(
                RecurringTransaction.organization_id == organization_id,
                and_(
                    RecurringTransaction.campaign_id == p2p.campaign_id,
                    RecurringTransaction.is_revenue == False
                )
            )
        ).all()

        donations = one_time + recurring

        scores = rank_by_donor_score_with_campaign(donations)
        result = []
        for contact_id in scores:
            contact = ContactUsers.fetch_by_id(
                contact_id) or ContactCompanies.fetch_by_id(contact_id)
            score_dict = scores[contact_id]
            contact = model_to_dict(contact)
            contact['donor_score'] = score_dict.get('score')
            contact['total_donations'] = sum([donation.amount for donation in donations if str(
                donation.contact_id) == contact_id or str(donation.company_id) == contact_id])
            contact['campaign'] = score_dict.get('campaign_name')
            result.append(contact)

        return Response(True, result).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
