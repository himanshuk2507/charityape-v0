from flask import request, Blueprint
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.config import db
from skraggle.base_helpers.pagination_helper import paginator, get_paginated_list
from flask_jwt_extended import get_jwt
from skraggle.contact.models import ContactUsers
from skraggle.base_helpers.responser import DataResponse
from skraggle.donation.models import AdminDonations


adminview = Blueprint("adminview", __name__, template_folder="templates")



def is_valid_fields(data):
     params = [
        'name',            
        'description',
        'contact_id'
     ]
    
     for param in params:
        if param not in data.keys():
            return param
     return True

def is_valid_update_fields(data):
     params = [
        'name',            
        'description'
     ]
    
     for param in params:
        if param not in data.keys():
            return param
     return True

@adminview.route("/create-admin", methods=["POST"])
@user_required()
def create_admin():
     json_data = request.json
     check_fields = is_valid_fields(json_data)
     match check_fields:
          case True:
               name = json_data["name"]
               description = json_data["description"]
               contact_id = json_data["contact_id"]
               organization_id = getOrg(get_jwt())
               contact = ContactUsers.query.filter_by(
                    id=contact_id, organization_id=getOrg(get_jwt())
               ).one_or_none()
               if not contact:
                    return DataResponse(False, 'No contact with this ID exists').status()
               
               new_admin = AdminDonations(
                    organization_id=organization_id,
                    contact=contact_id,
                    name=name,
                    description=description
               )
               db.session.add(new_admin)
               db.session.commit()
               return DataResponse(True, "Donation's Admin Created").status()
          
          case _:
               return DataResponse(False, "{} fields missing in the request body".format(check_fields)).status()
          
        
@adminview.route("/all-admin/<int:page_number>", methods=["GET"])
@user_required()
def admin_details(page_number):
     instance = []
     admin_data = AdminDonations.query.filter()
     for data in admin_data:
          contact = ContactUsers.query.filter_by(
                    id=data.contact, organization_id=getOrg(get_jwt())
               ).one_or_none()
          
          model_dict = {
               "id": data.id,
               "name": data.name,
               "description": data.description,
               "organization_id": data.organization_id,
               "status": data.status,
               "date_created": data.date_created,
               "assignee": [
                    {
                         "contact_id": data.contact,
                         "name": contact.fullname
                    }
               ]
          }
          instance.append(model_dict)
     api_path = "donations/all_admin"
     return get_paginated_list(
          instance, 
          api_path,
          page_number
          )
     
     

@adminview.route('/update-admin/<uuid:admin_id>', methods=['PATCH'])
@user_required()
def update_admin(admin_id):
    json_body = request.json
    
    check_fields = is_valid_update_fields(json_body)
    match check_fields:
         case True:
               name = json_body['name']
               description = json_body['description']
               admin = AdminDonations.query.filter_by(id=admin_id).one_or_none()
               if not admin:
                   return DataResponse(False, "Invalid admin ID").status()
               admin.name = name
               admin.description = description
               db.session.commit()
               return DataResponse(True, "Admin record updated").status()
         case _:
              return DataResponse(False, "{} fields missing in the request body".format(check_fields)).status()
         
         

@adminview.route('/delete-admin/<uuid:admin_id>', methods=['DELETE'])
@user_required()
def delete_admin(admin_id):
     admin = AdminDonations.query.filter_by(id=admin_id).one_or_none()
     match admin:
          case None:
               return DataResponse(False, "Invalid admin ID").status()
          case _:
               db.session.delete(admin)
               db.session.commit()
               return DataResponse(True, "Admin record deleted").status()