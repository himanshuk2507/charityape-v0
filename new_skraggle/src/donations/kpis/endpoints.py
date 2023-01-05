from flask import Blueprint
from flask_jwt_extended import get_jwt

from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.request_response import Response
from src.library.donation_kpis.donors import DonorKPIs, donor_kpis_schema
from src.library.donation_kpis.fundraising import FundraisingKPIs, fundraising_kpis_schema
from src.profile.models import Admin


donation_kpis_tab_endpoints = Blueprint('donation_kpis_tab_endpoints', __name__)


'''
@route GET /donations/kpi
@desc List KPI options
@access Admin
'''
@donation_kpis_tab_endpoints.route('', methods=['GET'])
@admin_required()
def list_kpi_options():
    try:
        data = dict(
            donor = donor_kpis_schema,
            fundraising = fundraising_kpis_schema,
            email_marketing = []
        )
        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/kpi/donor
@desc List Donor KPIs
@access Admin
'''
@donation_kpis_tab_endpoints.route('donor', methods=['GET'])
@admin_required()
def fetch_donor_kpis():
    try:
        jwt_claims = get_jwt()
        organization_id = jwt_claims.get('org')
        admin: Admin = Admin.fetch_by_id(
            id=jwt_claims.get('id'),
            organization_id=organization_id
        )
        
        contact_users = ContactUsers.query.filter_by(organization_id=organization_id).all()
        contact_companies = ContactCompanies.query.filter_by(organization_id=organization_id).all()
        one_time_transactions = OneTimeTransaction.query.filter_by(organization_id=organization_id).all()
        recurring_transactions = RecurringTransaction.query.filter_by(organization_id=organization_id).all()

        result = DonorKPIs(
            contact_companies=contact_companies,
            contact_users=contact_users,
            one_time_transactions=one_time_transactions,
            recurring_transactions=recurring_transactions,
            schema=admin.donor_kpis
        ).result()
        return Response(True, result).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /donations/kpi/fundraising
@desc List Fundraising KPIs
@access Admin
'''
@donation_kpis_tab_endpoints.route('fundraising', methods=['GET'])
@admin_required()
def fetch_fundraising_kpis():
    try:
        jwt_claims = get_jwt()
        organization_id = jwt_claims.get('org')
        admin: Admin = Admin.fetch_by_id(
            id=jwt_claims.get('id'),
            organization_id=organization_id
        )
        contact_users = ContactUsers.query.filter_by(organization_id=organization_id).all()
        contact_companies = ContactCompanies.query.filter_by(organization_id=organization_id).all()
        one_time_transactions = OneTimeTransaction.query.filter_by(organization_id=organization_id).all()
        recurring_transactions = RecurringTransaction.query.filter_by(organization_id=organization_id).all()

        result = FundraisingKPIs(
            contact_companies=contact_companies,
            contact_users=contact_users,
            one_time_transactions=one_time_transactions,
            recurring_transactions=recurring_transactions,
            schema=admin.fundraising_kpis
        ).result()
        return Response(True, result).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()