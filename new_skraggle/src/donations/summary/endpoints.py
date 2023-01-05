from flask import Blueprint
from flask_jwt_extended import get_jwt

from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction
from src.library.decorators.authentication_decorators import admin_required
from src.library.donation_summaries.fundraising_activity import FundraisingActivitySummary
from src.library.donation_summaries.goals import DonationGoals, RevenueGoals
from src.library.donation_summaries.segments import TransactionSegments
from src.library.donation_summaries.tracker import DonationTracker, RevenueTracker, TimeOfYearTracker
from src.library.utility_classes.request_response import Response
from src.profile.models import Admin


donation_summary_tab_endpoints = Blueprint('donation_summary_tab_endpoints', __name__)


'''
@route GET /donations/summary/fundraising-activity
@desc Fetch a Historical Summary of Fundraising Activity
@access Admin
'''
@donation_summary_tab_endpoints.route('fundraising-activity', methods=['GET'], defaults={'days': 30})
@donation_summary_tab_endpoints.route('fundraising-activity/<int:days>', methods=['GET'])
@admin_required()
def fetch_fundraising_activity(days):
    try:
        try:
            days = int(days)
        except (TypeError, ValueError):
            days = 30

        jwt_claims = get_jwt()
        organization_id = jwt_claims.get('org')

        contact_users = ContactUsers.query.filter_by(organization_id=organization_id).all()
        contact_companies = ContactCompanies.query.filter_by(organization_id=organization_id).all()
        one_time_transactions = OneTimeTransaction.query.filter_by(organization_id=organization_id).all()
        recurring_transactions = RecurringTransaction.query.filter_by(organization_id=organization_id).all()
        
        result = FundraisingActivitySummary(
            days = days,
            contact_companies=contact_companies,
            contact_users=contact_users,
            one_time_transactions=one_time_transactions,
            recurring_transactions=recurring_transactions,
        ).result()
        
        return Response(True, result).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

        
'''
@route GET /donations/summary/transactions/donation
@desc Fetch a Historical Summary of Donations
@access Admin
'''
@donation_summary_tab_endpoints.route('transactions/donation', methods=['GET'], defaults={'days': 30})
@donation_summary_tab_endpoints.route('transactions/donation/<int:days>', methods=['GET'])
@admin_required()
def fetch_donations_summary(days):
    try:
        try:
            days = int(days)
        except (TypeError, ValueError):
            days = 30

        organization_id = get_jwt().get('org')
        
        result = DonationTracker(
            days = days,
            organization_id = organization_id
        ).result
        
        return Response(True, result).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/summary/transactions/revenue
@desc Fetch a Historical Summary of Revenue
@access Admin
'''
@donation_summary_tab_endpoints.route('transactions/revenue', methods=['GET'], defaults={'days': 30})
@donation_summary_tab_endpoints.route('transactions/revenue/<int:days>', methods=['GET'])
@admin_required()
def fetch_revenue_summary(days):
    try:
        try:
            days = int(days)
        except (TypeError, ValueError):
            days = 30

        organization_id = get_jwt().get('org')
        
        result = RevenueTracker(
            days = days,
            organization_id = organization_id
        ).result
        
        return Response(True, result).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/summary/goal
@desc Fetch a Summary of Transaction Goals Progress
@access Admin
'''
@donation_summary_tab_endpoints.route('goal', methods=['GET'])
@admin_required()
def fetch_transaction_goal_progress_summary():
    try:
        jwt_claims = get_jwt()
        organization_id = jwt_claims.get('org')
        admin: Admin = Admin.fetch_by_id(
            id=jwt_claims.get('id'),
            organization_id=organization_id
        )
        result = dict(
            donations = DonationGoals(
                organization_id=organization_id,
                monthly_goal=admin.monthly_donation_goal,
                quarterly_goal=admin.quarterly_donation_goal,
                yearly_goal=admin.yearly_donation_goal,
            ).result,
            revenue = RevenueGoals(
                organization_id=organization_id,
                monthly_goal=admin.monthly_revenue_goal,
                quarterly_goal=admin.quarterly_revenue_goal,
                yearly_goal=admin.yearly_revenue_goal,
            ).result,
        )
        return Response(True, result).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/summary/segment
@desc Fetch a Summary of Transactions by Segment
@access Admin
'''
@donation_summary_tab_endpoints.route('segment', methods=['GET'], defaults={ 'days': 365 })
@donation_summary_tab_endpoints.route('segment/<int:days>', methods=['GET'])
@admin_required()
def fetch_transaction_segment_summary(days):
    try:
        try:
            days = int(days)
        except (TypeError, ValueError):
            days = 365

        organization_id = get_jwt().get('org')
        result = TransactionSegments(
            days=days,
            organization_id=organization_id
        ).result
        
        return Response(True, result).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/summary/time-of-year
@desc Fetch a Summary of Transactions by Time of Year
@access Admin
'''
@donation_summary_tab_endpoints.route('time-of-year', methods=['GET'], defaults={ 'days': 365 })
@donation_summary_tab_endpoints.route('time-of-year/<int:days>', methods=['GET'])
@admin_required()
def fetch_transaction_time_of_year_summary(days):
    try:
        try:
            days = int(days)
        except (TypeError, ValueError):
            days = 365

        organization_id = get_jwt().get('org')
        result = TimeOfYearTracker(
            days=days,
            organization_id=organization_id
        ).result()
        
        return Response(True, result).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /donations/summary/donor-scores
@desc Fetch a summary of donor scores, grouped by score and number of donors
@access Admin
'''
@donation_summary_tab_endpoints.route('donor-scores', methods=['GET'])
@admin_required()
def fetch_donor_score_summary():
    try:
        organization_id = get_jwt().get('org')
        donations = (
            OneTimeTransaction
                .query
                .filter_by(organization_id=organization_id, is_revenue=False)
                .all() +
            RecurringTransaction
                .query
                .filter_by(organization_id=organization_id, is_revenue=False)
                .all()
        )
        donor_scores = OneTimeTransaction.rank_by_donor_score(donations)
        
        donor_scores_by_count = {}
        # group by score->count
        for score in donor_scores.values():
            if score in donor_scores_by_count:
                donor_scores_by_count[score] += 1
            else:
                donor_scores_by_count[score] = 1

        return Response(True, donor_scores_by_count).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()