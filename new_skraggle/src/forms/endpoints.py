from operator import and_

from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from sqlalchemy.orm.session import make_transient
from src.forms.models import Form
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db


forms_tab_endpoints = Blueprint('forms_tab_endpoints', __name__)


'''
@route POST /forms
@desc Create a new Form object
@access Admin
'''
@forms_tab_endpoints.route('', methods=['POST'])
@admin_required()
def create_form_route():
    body = request.json 
    body['organization_id'] = get_jwt().get('org')

    try:
        result_bool, result_data = Form.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /forms
@desc List Forms
@access Admin
'''
@forms_tab_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_all_forms_route():
    try:
        data = Paginator(
            model=Form,
            query=Form.query.filter(Form.archived == False),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /forms/<uuid>
@desc Fetch Form by ID
@access Admin
'''
@forms_tab_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_form_by_id_route(id):
    try:
        form = Form.fetch_by_id(id, organization_id=get_jwt().get('org'))
        
        if not form:
            return Response(False, 'No form exists with this ID').respond()

        return Response(True, model_to_dict(form)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route PATCH /forms/<uuid>
@desc Update Form by ID
@access Admin
'''
@forms_tab_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_form_by_id_route(id):
    try:
        body = request.json
        form = Form.fetch_by_id(id, organization_id=get_jwt().get('org'))

        # validations
        if not form:
            return Response(False, 'No form exists with this ID').respond()

        unallowed_fields = ['id', 'organization_id']
        for field in body.keys():
            if field not in unallowed_fields:
                setattr(form, field, body.get(field))

        db.session.add(form)
        db.session.commit()

        return Response(True, model_to_dict(form)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route DELETE /forms
@desc Delete Form by ID
@access Admin
'''
@forms_tab_endpoints.route('', methods=['DELETE'])
@admin_required()
def delete_form_by_id_route():
    try:
        body = request.json
        forms = body.get('forms', [])

        if len(forms) == 0:
            return Response(False, 'No forms to perform DELETE operation on').respond()

        db.session.query(Form)\
            .filter(
                and_(
                    Form.id.in_(forms),
                    Form.organization_id == get_jwt().get('org')
                )
            )\
            .delete()
        db.session.commit()

        return Response(True, 'Form(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route POST /forms/clone
@desc Clone Form by ID
@access Admin
'''
@forms_tab_endpoints.route('clone', methods=['POST'])
@admin_required()
def clone_form_by_id_route():
    try:
        body = request.json
        forms = body.get('forms', [])

        if len(forms) == 0:
            return Response(False, 'No forms to perform CLONE operation on').respond()

        forms = db.session.query(Form)\
            .filter(
                and_(
                    Form.id.in_(forms),
                    Form.organization_id == get_jwt().get('org')
                )
            )\
            .all()
        for form in forms:
            make_transient(form)
            form.id = None
            form.name += " (cloned)"
            db.session.add(form)
            db.session.commit()

        data = [model_to_dict(form) for form in forms]

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route POST /forms/archive
@desc Archive Form by ID
@access Admin
'''
@forms_tab_endpoints.route('archive', methods=['POST'])
@admin_required()
def archive_form_by_id_route():
    try:
        body = request.json
        forms = body.get('forms', [])

        if len(forms) == 0:
            return Response(False, 'No forms to perform ARCHIVE operation on').respond()

        forms = db.session.query(Form)\
            .filter(
                and_(
                    Form.id.in_(forms),
                    Form.organization_id == get_jwt().get('org')
                )
            )\
            .all()

        for form in forms:
            form.archived = True

        db.session.commit()

        archived_forms = [model_to_dict(form) for form in forms]
        return Response(True, archived_forms).respond()

    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /forms/archive
@desc Archive Form by ID
@access Admin
'''
@forms_tab_endpoints.route('archive', methods=['GET'])
@admin_required()
def get_archive_forms_route():
    try:
        data = Paginator(
            model=Form,
            query=Form.query.filter(Form.archived),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
