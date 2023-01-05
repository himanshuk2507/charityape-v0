from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from src.library.decorators.authentication_decorators import admin_required
from src.library.base_helpers.rsa_helpers import decrypt_rsa
from src.profile.payment_settings.paypal.models import PayPalSettings
# from src.payment.paypal.models import PayPalProducts
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.profile.models import Admin


paypal_settings_endpoints = Blueprint('paypal_settings_endpoints', __name__)


'''
@route POST /payments-settings/paypal
@desc Set secrets for this Admin's PayPal account
@access Admin
'''
@paypal_settings_endpoints.route('paypal', methods=['POST'])
@admin_required()
def set_paypal_secrets_route():
     try:
          admin_id = get_jwt().get('id')
          organization_id = get_jwt().get('org')
          # print(organization_id)
          body = request.json

          paypal: PayPalSettings = PayPalSettings.query.filter_by(
               organization_id = organization_id,
               admin_id = admin_id
          ).one_or_none()
          
          if not paypal:
               body['admin_id'] = admin_id
               body['organization_id'] = organization_id

               result_bool, result_data = PayPalSettings.register(body)
               
               if not result_bool:
                    return Response(False, result_data).respond()
          else:
               result_bool, result_data = paypal.update(body)
               
               if not result_bool:
                    return Response(False, result_data).respond()
          
          return Response(True, 'Settings updated successfully!').respond()
     except Exception as e:
          print(e)
          return Response(False, str(e), 500).respond()
     
     
'''
@route GET /payments-settings/paypal
@desc Confirm whether this Admin's PayPal is configured
@access Admin
'''
@paypal_settings_endpoints.route('paypal', methods=['GET'])
@admin_required()
def confirm_paypal_configuration_route():
    try:
        admin_id = get_jwt().get('id')
        organization_id = get_jwt().get('org')

        paypal = PayPalSettings.query.filter_by(
            admin_id = admin_id,
            organization_id = organization_id
        ).one_or_none()

        if not paypal:
            return Response(False, 'PayPal is not configured for this account').respond()

        return Response(True, 'PayPal has been configured for this account').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()