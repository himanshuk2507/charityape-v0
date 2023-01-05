from datetime import datetime, timedelta
from operator import and_, mod
from typing import List
from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from src.campaigns.models import Campaign

from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction
from src.library.base_helpers.model_to_dict import model_to_dict
from src.library.decorators.authentication_decorators import admin_required
from src.library.donation_summaries.fundraising_activity import FundraisingActivitySummary
from src.library.donation_summaries.goals import DonationGoals, RevenueGoals
from src.library.donation_summaries.segments import TransactionSegments
from src.library.donation_summaries.tracker import DonationTracker, RevenueTracker, TimeOfYearTracker
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.p2p.models import P2P
from src.profile.models import Admin


reports_tab_endpoints = Blueprint('reports_tab_endpoints', __name__)


'''
@route GET /report/donations-by-contact
@desc List donations with donor information
@access Admin
'''
@reports_tab_endpoints.route('donations-by-contact', methods=['GET'])
@admin_required()
def fetch_donations_by_contacts_route():
    try:
        organization_id = get_jwt().get('org')
        donations = Paginator(
            model=OneTimeTransaction,
            query=OneTimeTransaction.query.filter_by(is_revenue=False),
            query_string=Paginator.get_query_string(request.url),
            organization_id=organization_id
        ).result

        for donation in donations['rows']:
            is_user = True
            if donation.get('company_id') is not None:
                is_user = False
            if is_user:
                contact = ContactUsers.fetch_by_id(
                    id=donation.get('contact_id'),
                    organization_id=organization_id
                )
            else:
                contact = ContactCompanies.fetch_by_id(
                    id=donation.get('company_id'),
                    organization_id=organization_id
                )
            donation['contact'] = model_to_dict(contact)

        return Response(True, donations).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /report/campaign-performance
@desc Fetch information about the performance of every campaign
@access Admin
'''
@reports_tab_endpoints.route('campaign-performance', methods=['GET'], defaults={'days': 30})
@reports_tab_endpoints.route('campaign-performance/<int:days>', methods=['GET'])
@admin_required()
def fetch_campaign_performance_route(days):
    try:
        try:
            days = int(days)
        except (TypeError, ValueError):
            days = 30

        organization_id = get_jwt().get('org')
        delta = timedelta(days=days)
        history = datetime.now() - delta

        campaigns: List[Campaign] = Campaign.query.filter_by(
            organization_id=organization_id
        ).all()
        campaign_ids = [campaign.id for campaign in campaigns]
        donations = OneTimeTransaction.query.filter(
            and_(
                OneTimeTransaction.organization_id == organization_id,
                and_(
                    OneTimeTransaction.campaign_id.in_(campaign_ids),
                    and_(
                        OneTimeTransaction.is_revenue == False,
                        OneTimeTransaction.created_at >= history
                    )
                )
            )
        ).all() + \
            RecurringTransaction.query.filter(
                and_(
                    RecurringTransaction.organization_id == organization_id,
                    and_(
                        RecurringTransaction.campaign_id.in_(campaign_ids),
                        and_(
                            RecurringTransaction.is_revenue == False,
                            RecurringTransaction.created_at >= history
                        )
                    )
                )
            ).all()
        revenue = OneTimeTransaction.query.filter(
            and_(
                OneTimeTransaction.organization_id == organization_id,
                and_(
                    OneTimeTransaction.campaign_id.in_(campaign_ids),
                    and_(
                        OneTimeTransaction.is_revenue == True,
                        OneTimeTransaction.created_at >= history
                    )
                )
            )
        ).all() + \
            RecurringTransaction.query.filter(
                and_(
                    RecurringTransaction.organization_id == organization_id,
                    and_(
                        RecurringTransaction.campaign_id.in_(campaign_ids),
                        and_(
                            RecurringTransaction.is_revenue == True,
                            RecurringTransaction.created_at >= history
                        )
                    )
                )
            ).all()

        data = dict(
            campaigns = [model_to_dict(campaign) for campaign in campaigns],
            total_campaigns = len(campaigns),
            total_donation = sum([transaction.amount for transaction in donations]),
            total_revenue = sum([transaction.amount for transaction in revenue])
        )

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /report/p2p-leaderboard
@desc List global P2P leaderboard
@access Admin
'''
@reports_tab_endpoints.route('p2p-leaderboard', methods=['GET'], defaults={'days': 30})
@reports_tab_endpoints.route('p2p-leaderboard/<int:days>', methods=['GET'])
@admin_required()
def fetch_p2p_leaderboard_route(days):
    try:
        organization_id = get_jwt().get('org')
        delta = timedelta(days=days)
        history = datetime.now() - delta
        
        p2ps: List[P2P] = P2P.query.filter(
            and_(
                P2P.organization_id == organization_id,
                P2P.created_at >= history
            )
        ).all()
        campaign_ids = [p2p.campaign_id for p2p in p2ps]

        one_time = OneTimeTransaction.query.filter(
                and_(
                    OneTimeTransaction.organization_id == organization_id,
                    OneTimeTransaction.campaign_id.in_(campaign_ids)
                )
            ).all()
        recurring = RecurringTransaction.query.filter(
                and_(
                    RecurringTransaction.organization_id == organization_id,
                    RecurringTransaction.campaign_id.in_(campaign_ids)
                )
            ).all()
        
        donations = [model_to_dict(d) for d in one_time+recurring]
        donations.sort(key=lambda d: d.get('amount'), reverse=True)

        for donation in donations:
            contact_id = donation.get('contact_id')
            company_id = donation.get('company_id')

            if contact_id:
                contact = ContactUsers.fetch_by_id(
                    id=contact_id,
                    organization_id=organization_id
                )
            elif company_id:
                contact = ContactCompanies.fetch_by_id(
                    id=contact_id,
                    organization_id=organization_id
                )
            
            donation['contact'] = model_to_dict(contact)
            campaign: Campaign = Campaign.fetch_by_id(
                id=donation.get('campaign_id'),
                organization_id=organization_id
            ) if donation.get('campaign_id') else None
            if campaign:
                donation['campaign'] = model_to_dict(campaign)

        return Response(True, donations).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()