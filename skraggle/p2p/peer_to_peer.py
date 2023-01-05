from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt
from skraggle.base_helpers.object_utility import ObjectHandler
from skraggle.base_helpers.updating_fields_fetch import get_fields
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import P2PFundraiser
from skraggle.config import db
import datetime
import os
from skraggle.base_helpers.pagination_helper import paginator
from skraggle.base_helpers.responser import DataResponse
from skraggle.base_helpers.dict_responser import dict_resp
import random, string, secrets


peertopeer = Blueprint("peertopeer", __name__, template_folder="templates")



def is_valid_p2p_params(data):
     params = [
        'campaign',            
        'designation',
        'display_name',       
        'first_name',
        'last_name',     
        'email',
        'goal', 
        'currency',
        'offline_amount',          
        'offline_donation',
        'goal_date',             
        'supporter',
        'personal_message',               
        'profile_photo'
     ]
    
     for param in params:
          if param not in data.keys():
               return param
     return True

# Generate P2p ID #
def get_p2p_id():
     res = ''.join(random.choices(string.ascii_uppercase, k=8))
     code = str(res)
     return code

@peertopeer.route('/create_p2p', methods=["POST"])
@user_required()
def create_p2p():
     
     
     data = request.json
     if is_valid_p2p_params(data) == True:
          campaign = data['campaign']
          designation = data['designation']
          display_name = data['display_name']
          first_name = data['first_name']
          last_name = data['last_name']
          email = data['email']
          goal = data['goal']
          currency = data['currency']
          offline_amount = data['offline_amount']
          offline_donation = data['offline_donation']
          goal_date = data['goal_date']
          supporter = data['supporter']
          personal_message = data['personal_message']
          profile_photo = data['profile_photo']
          
          if P2PFundraiser.query.filter_by(email=email).first():
               resp = DataResponse(False, "Email already taken")
               return resp.status()
          else:
               p2p = P2PFundraiser(
                    p2p_id=get_p2p_id(),
                    campaign=campaign,
                    designation=designation,
                    display_name=display_name,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    goal=goal,
                    currency=currency,
                    offline_amount=offline_amount,
                    offline_donation=offline_donation,
                    goal_date=goal_date,
                    supporter=supporter,
                    personal_message=personal_message,
                    profile_photo=profile_photo,
                    organization_id=getOrg(get_jwt())
               )
               db.session.add(p2p)
               db.session.commit()
               db.session.flush()
               p2p.organization_id = getOrg(get_jwt())
               db.session.commit()
               resp = DataResponse(True, "P2P Created Successfully")
               return resp.status()
     
     resp = DataResponse(False, "{} field missing".format(is_valid_p2p_params(data)))
     return resp.status()
     


@peertopeer.route("/all/<int:page_number>", methods=["GET"])
@user_required()
def p2p_details(page_number):
    instance = P2PFundraiser
    order_by_column = "id"
    api_path = "p2p/all"
    return paginator(page_number, instance, order_by_column, api_path)



@peertopeer.route("/<uuid:p2p_id>", methods=["GET"])
@user_required()
def p2p_list(p2p_id):
     p2p = P2PFundraiser.query.filter_by(
        id=p2p_id, organization_id=getOrg(get_jwt())
     ).one_or_none()
     if not p2p:
          resp = DataResponse(False, "P2P with id {} does not exist".format(p2p_id))
          return resp.status()
     return dict_resp(p2p), 200


@peertopeer.route("/<uuid:p2p_id>", methods=["DELETE"])
@user_required()
def delete_p2p(p2p_id):
     p2p = P2PFundraiser.query.filter_by(
        id=p2p_id, organization_id=getOrg(get_jwt())
     ).one_or_none()

     if p2p is None:
        return DataResponse(False, "This P2P does not exist").status()

     db.session.delete(p2p)
     db.session.commit()
     return DataResponse(True, "P2P deleted successfully").status()



@peertopeer.route("/<uuid:p2p_id>", methods=["PATCH"])
def update_p2p(p2p_id):
     body = request.json     
     
     p2p = P2PFundraiser.query.filter_by(id=p2p_id).one_or_none()
     if not p2p:
          return DataResponse(False, "This P2P does not exist").status() 
     
     p2p_object = dict.fromkeys(get_fields(P2PFundraiser))

     try:
          for field in body:
               if field in p2p_object.keys():
                    setattr(p2p, field, body[field])
          db.session.commit()
          return DataResponse(True, "P2P Update successfully").status()
     except Exception as e:
          return DataResponse(False, str(e)[:105]).status()
     