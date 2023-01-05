from flask import Blueprint, request, session
from flask_jwt_extended import get_jwt
from sqlalchemy import and_
from skraggle.base_helpers.object_utility import ObjectHandler
from skraggle.base_helpers.updating_fields_fetch import get_fields
from skraggle.decarotor import admin_required, user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator, paginator_search
from .models import ContactUsers
from skraggle.config import db
from sqlalchemy.sql import func
from sqlalchemy import and_, or_
from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.base_helpers.responser import DataResponse

contactview = Blueprint("contactview", __name__)

def is_valid_contact_params(data):
    params = [
        'fullname',            
        'primary_phone',
        'primary_email',       
        'tags',
        'total_donations',     
        'donor_score',
        'donations_this_year', 
        'donations_last_year',
        'birth_date',          
        'company',
        'address',             
        'city',
        'state',               
        'postal_zip',
        'country',             
        'priority'
    ]
    
    for param in params:
        if param not in data.keys():
            return False
    return True
    
@contactview.route("/create", methods=["POST"])
@user_required()
def contacts_create():
    org = get_jwt()
    contact_obj = ObjectHandler("ContactUsers", org["org"])
    contact_data = contact_obj.make()
    try:
        for keys in request.json:
            if keys in contact_data.keys():
                contact_data[keys] = request.json[keys]
        contact_user = ContactUsers(**contact_data)
        db.session.add(contact_user)
        db.session.commit()
        resp = DataResponse(True, "Contact Created Successfully")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()

@contactview.route("/update/<uuid:contact_id>", methods=["PATCH"])
@user_required()
def contacts_update(contact_id):
    contact_id = request.args.get("contact_id")
    contact = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).first()
    if not contact:
        resp = DataResponse(
            False, f"Contact ID: {contact_id} doesn't correspond to a valid contact"
        )
        return resp.status()
    contact_obj = dict.fromkeys(get_fields(ContactUsers))
    try:
        for keys in request.json:
            if keys in contact_obj.keys():
                setattr(contact, keys, request.json[keys])
        db.session.commit()
        resp = DataResponse(True, f"Contact with id {contact_id} Updated")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:105])
        return resp.status()


@contactview.route("/<uuid:contact_id>", methods=["GET"])
@admin_required()
def contact_list(contact_id):
    def getSession():
        return session.get("key", "not set")

    print(getSession())
    contacts = ContactUsers.query.filter_by(
        id=contact_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not contacts:
        resp = DataResponse(False, f"Contact with id {contact_id} does not exist")
        return resp.status()
    return dict_resp(contacts), 200


@contactview.route("/all/<int:page_number>", methods=["GET"])
@user_required()
def contacts_details(page_number):
    instance = ContactUsers
    order_by_column = "id"
    api_path = "contacts/all"
    return paginator(page_number, instance, order_by_column, api_path)


@contactview.route("/delete", methods=["DELETE"])
@user_required()
def contacts_delete():
    contacts = request.json.get("contacts")
    if not contacts:
        resp = DataResponse(False, "Empty Contacts List to Delete")
        return resp.status()

    try:
        db.session.query(ContactUsers).filter(
            and_(
                ContactUsers.organization_id == getOrg(get_jwt()),
                ContactUsers.id.in_(contacts),
            )
        ).delete(synchronize_session=False)
        db.session.commit()
        resp = DataResponse(
            True,
            f"{'Contacts' if len(contacts) > 1 else 'Contact' } Deleted Successfully",
        )
        return resp.status()
    except Exception as e:
        resp = DataResponse(True, f"Error deleting Contact :{ str(e)[:105]}")
        return resp.status()   
        

@contactview.route("/search", methods=["GET"])
@user_required()
def search():
    search_string = request.args.get("search_string")
    page_number = request.args.get("page")
    order_by_column = "id"
    instance = ContactUsers.query.filter(or_(
        ContactUsers.fullname.ilike(f'%{search_string}%'),
        ContactUsers.primary_phone.ilike(f'%{search_string}%'),
        ContactUsers.primary_email.ilike(f'%{search_string}%'),
        ContactUsers.tags.ilike(f'%{search_string}%')
        )).order_by(getattr(ContactUsers, order_by_column))
    api_path = "contact/search"
    return paginator_search(page_number, instance, api_path)