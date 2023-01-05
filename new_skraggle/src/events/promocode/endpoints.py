from operator import and_
from typing import List
from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.custom_validator import Validator
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db
from .models import PromoCode

promocode = Blueprint("promocode", __name__)



'''
@route POST /promocode/create
@desc Create Promocode
@access Admin
'''
@promocode.route('/create', methods=["POST"])
@admin_required()
def create_code():
     body = request.json 
     body['organization_id'] = get_jwt().get('org')

     try:
          result_bool, result_data = PromoCode.register(body)
          if result_bool:
               return Response(True, model_to_dict(result_data)).respond()
          return Response(False, result_data).respond()
     except Exception as e:
          print(e)
          return Response(False, str(e), 500).respond()
     
     


'''
@route GET /promocode
@desc All Promocode
@access Admin
'''
@promocode.route('', methods=["GET"])
@admin_required()
def list_promocode():
    try:
        data = Paginator(
            model=PromoCode,
            query=PromoCode.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
   
   

'''
@route PATCH /promocode/<uuid>
@desc Update Promo Code by ID
@access Admin
'''
@promocode.route("<uuid:id>", methods=["PATCH"])
@admin_required()
def update_promocode(id):
     try:
          body = request.json 
          promo_code = PromoCode.fetch_by_id(id, organization_id=get_jwt().get('org'))

          # validations
          if not promo_code:
               return Response(False, 'This Promo does not exist').respond()
          unallowed_fields = ['id', 'organization_id']

          for field in body.keys():
               if field not in unallowed_fields:
                    setattr(promo_code, field, body.get(field))

          db.session.add(promo_code)
          db.session.commit()

          return Response(True, model_to_dict(promo_code)).respond()
     except Exception as e:
          print(e)
          return Response(False, str(e), 500).respond()
     
     

'''
@route GET /promocode/info/<uuid>
@desc Get Promo Code by ID
@access Admin
'''
@promocode.route("/info/<uuid:id>", methods=["GET"])
@admin_required()
def promocode_info_by_id(id):
     promo_code: PromoCode = PromoCode.fetch_by_id(id, organization_id=get_jwt().get('org'))
     if not promo_code:
          return Response(False, "This PromoCode does not exist").respond()
     
     return Response(True, model_to_dict(promo_code)).respond()
     
   

'''
@route DELETE /promocode
@desc Delete Promo Code by ID
@access Admin
'''
@promocode.route("", methods=["DELETE"])
@admin_required()
def delete_promocode():
     try:
          body = request.json
          if not body or body.get('promocodes') is None:
               return Response(False, '`promocodes` is a required field').respond()

          promocode_ids = body.get('promocodes', [])
          if len(promocode_ids) == 0:
               return Response(False, 'No PromoCode to perform DELETE operation on').respond()
               
          PromoCode.delete_many_by_id(promocode_ids, get_jwt().get('org'))
          return Response(True, 'PromoCode(s) deleted successfully').respond()
     except Exception as e:
          print(e)
          return Response(False, str(e), 500).respond()
