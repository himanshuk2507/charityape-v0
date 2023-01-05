from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from src.contacts.todos.models import ContactTodo
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db


contacts_todos_endpoints = Blueprint('contacts_todos_endpoints', __name__)


'''
@route GET /contacts/todos
@desc List Contact Todos
@access Admin
'''
@contacts_todos_endpoints.route('', methods=['GET'])
@admin_required()
def fetch_all_contact_todos_route():
    try:
        data = Paginator(
            model=ContactTodo,
            query=ContactTodo.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route POST /contacts/todos
@desc Add Contact Todo
@access Admin
'''
@contacts_todos_endpoints.route('', methods=['POST'])
@admin_required()
def add_contact_todos_route():
    try:
        body = request.json 
        print(body)
        body['organization_id'] = get_jwt().get('org')

        result_bool, result_data = ContactTodo.register(body)

        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()

        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /contacts/todos/<uuid>
@desc Fetch Todo by ID
@access Admin
'''
@contacts_todos_endpoints.route('<uuid:id>', methods=['GET'])
@admin_required()
def fetch_contact_todo_by_id_route(id):
    try:
        todo = ContactTodo.fetch_by_id(id, organization_id=get_jwt().get('org'))
        
        if not todo:
            return Response(False, 'No to-do exists with this ID').respond()
        
        return Response(True, model_to_dict(todo)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route PATCH /contacts/todos/<uuid>
@desc Fetch Todo by ID
@access Admin
'''
@contacts_todos_endpoints.route('<uuid:id>', methods=['PATCH'])
@admin_required()
def update_contact_todo_by_id_route(id):
    try:
        todo = ContactTodo.fetch_by_id(id, organization_id=get_jwt().get('org'))
        
        if not todo:
            return Response(False, 'No to-do exists with this ID').respond()
        
        body = request.json 
        unallowed_fields = ['id', 'organization_id']
        for field in body.keys():
            if field not in unallowed_fields:
                setattr(todo, field, body.get(field))

        db.session.add(todo)
        db.session.commit()

        return Response(True, model_to_dict(todo)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()