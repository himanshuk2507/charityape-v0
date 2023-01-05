from operator import and_, or_
from typing import List

from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from sqlalchemy import desc
from numpy import median

from src.contacts.companies.models import AssociatedContact, ContactCompanies
from src.contacts.contact_users.models import ContactUsers
from src.contacts.households.models import Households
from src.contacts.interactions.models import ContactInteraction
from src.contacts.tags.models import ContactTags
from src.contacts.todos.models import ContactTodo
from src.contacts.volunteering.models import VolunteerActivity
from src.donations.pledges.models import Pledge
from src.donations.one_time_transactions.models import OneTimeTransaction
from src.donations.recurring_transactions.models import RecurringTransaction
from src.library.decorators.authentication_decorators import admin_required
from src.library.donation_summaries.smart_recommendations import smart_ask, time_of_year
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db
from src.mail_blasts.models import MailBlast


contacts_tab_endpoints = Blueprint('contacts_tab_endpoints', __name__)


'''
@route POST /contacts/users
@desc Create a new ContactUsers object
@access Admin
'''


@contacts_tab_endpoints.route('', methods=['POST'])
@admin_required()
def create_contact_user_route():
    body = request.json
    body['organization_id'] = get_jwt().get('org')

    try:
        result_bool, result_data = ContactUsers.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/users
@desc List Contact Users
@access Admin
'''


@contacts_tab_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_all_contact_users_route():
    try:
        organization_id = get_jwt().get('org')
        data = Paginator(
            model=ContactUsers,
            query=ContactUsers.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=organization_id
        ).result

        for contact in data['rows']:
            if not contact.get('tags'):
                contact['tags'] = []
            else:
                contact['tags'] = [
                    names[0] for names in
                    db.session.query(ContactTags.name).filter(
                        and_(
                            ContactTags.id.in_(contact['tags']),
                            ContactTags.organization_id == organization_id
                        )
                    ).all()
                ]

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/users/<uuid>
@desc Fetch Contact User by ID
@access Admin
'''


@contacts_tab_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_contact_user_by_id_route(id):
    try:
        user: ContactUsers = ContactUsers.fetch_by_id(
            id, get_jwt().get('org'))

        if not user:
            return Response(False, 'This Contact does not exist').respond()
        user = model_to_dict(user)
        user['company'] = model_to_dict(ContactCompanies.fetch_by_id(id=user.get(
            'company'), organization_id=user.get('organization_id'))) if user.get('company') is not None else None
        user['households'] = [
            model_to_dict(household) for household in
            Households.query.filter(
                and_(
                    Households.id.in_(user.get('households')),
                    Households.organization_id == user.get('organization_id')
                )
            ).all()
        ] if user.get('households') is not None else []
        user['tags'] = [
            model_to_dict(household) for household in
            ContactTags.query.filter(
                and_(
                    ContactTags.id.in_(user.get('tags')),
                    ContactTags.organization_id == user.get('organization_id')
                )
            ).all()
        ] if user.get('tags') is not None else []

        return Response(True, user).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /contacts/users/<uuid>
@desc Update Contact User by ID
@access Admin
'''


@contacts_tab_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_contact_user_by_id_route(id):
    try:
        body = request.json
        user: ContactUsers = ContactUsers.fetch_by_id(
            id, organization_id=get_jwt().get('org'))

        if not user:
            return Response(False, 'This Contact does not exist').respond()

        result_bool, result_data = user.update(body)
        if result_bool == False:
            return Response(False, result_data).respond()

        user = model_to_dict(result_data)
        user['company'] = model_to_dict(ContactCompanies.fetch_by_id(id=user.get(
            'company'), organization_id=user.get('organization_id'))) if user.get('company') is not None else None
        user['households'] = [
            model_to_dict(household) for household in
            Households.query.filter(
                and_(
                    Households.id.in_(user.get('households')),
                    Households.organization_id == user.get('organization_id')
                )
            ).all()
        ] if user.get('households') is not None else []
        user['tags'] = [
            model_to_dict(household) for household in
            ContactTags.query.filter(
                and_(
                    ContactTags.id.in_(user.get('tags')),
                    ContactTags.organization_id == user.get('organization_id')
                )
            ).all()
        ] if user.get('tags') is not None else []

        return Response(True, user).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DELETE /contacts/users
@desc Delete Contact Users by ID
@access Admin
'''


@contacts_tab_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_contact_user_by_id_route():
    try:
        body = request.json
        contacts = body.get('contacts', [])

        if len(contacts) == 0:
            return Response(False, 'No contacts to perform DELETE operation on').respond()

        ContactUsers.delete_many_by_id(contacts, get_jwt().get('org'))

        return Response(True, 'Contact(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/users/<uuid>/interactions
@desc List Interactions For This User
@access Admin
'''


@contacts_tab_endpoints.route('<uuid:id>/interactions', methods=['GET'])
@admin_required()
def list_interactions_route(id):
    try:
        data = Paginator(
            model=ContactInteraction,
            query=ContactInteraction.query.filter_by(contact_id=id),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/users/<uuid>/todos
@desc List Todos For This User
@access Admin
'''


@contacts_tab_endpoints.route('<uuid:id>/todos', methods=['GET'])
@admin_required()
def list_todos_route(id):
    try:
        data = Paginator(
            model=ContactTodo,
            query=ContactTodo.get_query_for_contact(contact_id=id),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/users/<uuid>/volunteer-activity
@desc List Volunteer Activity For This User
@access Admin
'''


@contacts_tab_endpoints.route('<uuid:id>/volunteer-activity', methods=['GET'])
@admin_required()
def list_volunteer_activity_route(id):
    try:
        data = Paginator(
            model=VolunteerActivity,
            query=VolunteerActivity.query.filter_by(contact_id=id),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/users/<uuid>/one-time-transactions
@desc List One-Time Transactions For This User
@access Admin
'''


@contacts_tab_endpoints.route('<uuid:id>/one-time-transactions', methods=['GET'])
@admin_required()
def list_one_time_transactions_route(id):
    try:
        organization_id = get_jwt().get('org')
        data = Paginator(
            model=OneTimeTransaction,
            query=OneTimeTransaction.query.filter(
                and_(
                    OneTimeTransaction.organization_id == organization_id,
                    or_(
                        OneTimeTransaction.contact_id == id,
                        OneTimeTransaction.company_id == id
                    )
                )
            ),
            query_string=Paginator.get_query_string(request.url),
            organization_id=organization_id
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/users/<uuid>/recurring-transactions
@desc List Recurring Transactions For This User
@access Admin
'''


@contacts_tab_endpoints.route('<uuid:id>/recurring-transactions', methods=['GET'])
@admin_required()
def list_recurring_transactions_route(id):
    try:
        organization_id = get_jwt().get('org')
        data = Paginator(
            model=RecurringTransaction,
            query=RecurringTransaction.query.filter(
                and_(
                    RecurringTransaction.organization_id == organization_id,
                    or_(
                        RecurringTransaction.contact_id == id,
                        RecurringTransaction.company_id == id
                    )
                )
            ),
            query_string=Paginator.get_query_string(request.url),
            organization_id=organization_id
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/users/<uuid>/smart-recommendations
@desc Get SmartRecommendations
@access Admin
'''


@contacts_tab_endpoints.route('<uuid:id>/smart-recommendations', methods=['GET'])
@admin_required()
def fetch_smart_recommendations_route(id):
    try:
        organization_id = get_jwt().get('org')
        transactions = db.session.query(OneTimeTransaction).filter(
            OneTimeTransaction.organization_id == organization_id
        ).all() + \
            db.session.query(RecurringTransaction).filter(
                RecurringTransaction.organization_id == organization_id
        ).all()

        return Response(True, dict(
            smart_ask=smart_ask(transactions, id),
            time_of_year=time_of_year(transactions, id),
            best_way_to_reach_out='mail'
        )).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
