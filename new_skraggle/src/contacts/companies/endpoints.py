from operator import and_
from typing import List
from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from src.contacts.contact_users.models import ContactUsers
from src.contacts.interactions.models import ContactInteraction
from src.contacts.tags.models import ContactTags
from src.contacts.todos.models import ContactTodo
from src.contacts.volunteering.models import VolunteerActivity
from src.donations.pledges.models import Pledge
from src.donations.one_time_transactions.models import OneTimeTransaction

from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.custom_validator import Validator
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db
from src.mail_blasts.models import MailBlast

from .models import AssociatedContact, ContactCompanies


contact_companies_endpoints = Blueprint(
    'contact_companies_endpoints', __name__)


'''
@route POST /contacts/companies
@desc Create ContactCompany
@access Admin
'''


@contact_companies_endpoints.route('', methods=['POST'])
@admin_required()
def create_company_route():
    body = request.json
    body['organization_id'] = get_jwt().get('org')

    try:
        result_bool, result_data = ContactCompanies.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/companies
@desc List ContactCompanies
@access Admin
'''


@contact_companies_endpoints.route('', methods=['GET'])
@admin_required()
def list_companies_route():
    try:
        organization_id = get_jwt().get('org')
        data = Paginator(
            model=ContactCompanies,
            query=ContactCompanies.query,
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
@route GET /contacts/companies/<uuid>
@desc Fetch ContactCompany by ID
@access Admin
'''


@contact_companies_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_company_by_id_route(id):
    try:
        company: ContactCompanies = ContactCompanies.fetch_by_id(
            id, organization_id=get_jwt().get('org'))
        if not company:
            return Response(False, "This company does not exist").respond()
        company.load_tag_names()

        data = model_to_dict(company)
        data['primary_contact'] = model_to_dict(ContactUsers.fetch_by_id(
            company.primary_contact)) if company.primary_contact else None

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /contacts/companies/<uuid>
@desc Update ContactCompany by ID
@access Admin
'''


@contact_companies_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_company_by_id_route(id):
    try:
        body = request.json
        company = ContactCompanies.fetch_by_id(
            id, organization_id=get_jwt().get('org'))

        # validations
        if not company:
            return Response(False, 'This company does not exist').respond()
        unallowed_fields = ['id', 'organization_id']
        if body.get('email'):
            if not Validator.is_email(body.get('email')):
                return Response(False, "`email` is not a valid email address").respond()

        for field in body.keys():
            if field not in unallowed_fields:
                setattr(company, field, body.get(field))
        if body.get('assignee'):
            contact = ContactUsers.fetch_by_id(body.get('assignee'))
            if not contact:
                return Response(False, '`assignee` is not a valid contact').respond()

        db.session.add(company)
        db.session.commit()

        return Response(True, model_to_dict(company)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DELETE /contacts/companies
@desc Delete Companies by ID
@access Admin
'''


@contact_companies_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_companies_route():
    body = request.json
    companies = body.get('companies', [])

    if len(companies) == 0:
        return Response(False, 'No companies to perform DELETE operation on').respond()

    try:
        ContactCompanies.delete_many_by_id(companies, get_jwt().get('org'))

        return Response(True, 'Company(-ies) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/companies/<uuid>/contacts
@desc Fetch Associated Contacts
@access Admin
'''


@contact_companies_endpoints.route('<uuid:id>/contacts', methods=['GET'])
@admin_required()
def fetch_associated_contacts_route(id):
    try:
        company: ContactCompanies = ContactCompanies.query.filter_by(
            id=id, organization_id=get_jwt().get('org')).one_or_none()

        associated_contacts_zip = [{'position': associated_contact.position,
                                    'contact_id': associated_contact.contact_id} for associated_contact in company.associated_contacts]

        associated_contacts = [
            contact.contact_id for contact in company.associated_contacts]
        associated_contacts: List[ContactUsers] = ContactUsers.query.filter(
            ContactUsers.id.in_(associated_contacts)).all()
        associated_contacts = [model_to_dict(
            contact) for contact in associated_contacts]

        for contact in associated_contacts:
            meta_data = [obj for obj in associated_contacts_zip if str(
                obj['contact_id']) == str(contact['id'])]
            contact['position'] = meta_data[0]['position'] if len(
                meta_data) > 0 else None

        return Response(True, associated_contacts).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /contacts/companies/<uuid>/contacts
@desc Add Associated Contact
@access Admin
'''


@contact_companies_endpoints.route('<uuid:id>/contacts', methods=['POST'])
@admin_required()
def add_associated_contacts_route(id):
    body = request.json
    if not body.get('contacts'):
        return Response(False, "`contacts` is a required field").respond()

    try:
        company: ContactCompanies = db.session.query(ContactCompanies).filter_by(
            id=id, organization_id=get_jwt().get('org')).one_or_none()
        if not company:
            return Response(False, "This company does not exist").respond()

        contacts = body.get('contacts')

        for contact_obj in contacts:
            contact_obj['company_id'] = id
            associated_contact = AssociatedContact(**contact_obj)
            company.associated_contacts.append(associated_contact)

            contact: ContactUsers = db.session.query(ContactUsers).filter_by(
                id=contact_obj.get('contact_id')).one_or_none()
            if contact:
                contact.associated_contacts.append(associated_contact)

            db.session.add_all([associated_contact, contact, company])
            db.session.flush()

        db.session.commit()

        return Response(True, "Contact(s) added successfully").respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route DELETE /contacts/companies/<uuid>/contacts
@desc Delete Associated Contacts
@access Admin
'''


@contact_companies_endpoints.route('<uuid:id>/contacts', methods=['DELETE'])
@admin_required()
def delete_associated_contacts(id):
    try:
        body = request.json
        associated_contact_ids: List[AssociatedContact] = body.get('contacts')
        if not associated_contact_ids or len(associated_contact_ids) == 0:
            return Response(False, "No Associated Contacts provided for DELETE operation").respond()

        company: ContactCompanies = db.session.query(ContactCompanies).filter_by(
            id=id, organization_id=get_jwt().get('org')).one_or_none()
        if not company:
            return Response(False, "This company does exist").respond()

        for associated_contact in company.associated_contacts:
            company.associated_contacts.remove(associated_contact)

            contact: ContactUsers = db.session.query(ContactUsers).filter_by(
                id=associated_contact.contact_id).one_or_none()
            if contact:
                contact.associated_contacts.remove(associated_contact)
                db.session.add(contact)

        db.session.add(company)
        db.session.commit()

        return Response(True, "Associated contact(s) removed successfully").respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/companies/<uuid>/interactions
@desc List Interactions For This Company
@access Admin
'''


@contact_companies_endpoints.route('<uuid:id>/interactions', methods=['GET'])
@admin_required()
def list_interactions_route(id):
    try:
        # find all interactions where organization_id = get_jwt().get('org')
        # AND company_id == id
        data = Paginator(
            model=ContactInteraction,
            query=ContactInteraction.query.filter_by(company_id=id),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /contacts/companies/<uuid>/todos
@desc List Todos For This User
@access Admin
'''


@contact_companies_endpoints.route('<uuid:id>/todos', methods=['GET'])
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
