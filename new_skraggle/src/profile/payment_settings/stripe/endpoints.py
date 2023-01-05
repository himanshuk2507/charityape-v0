from operator import and_
from os import getcwd
from pathlib import Path
from typing import List
import uuid
from flask import Blueprint, request
from flask_jwt_extended import get_jwt
import rsa

from src.library.base_helpers.chunk_list import chunk_list
from src.library.base_helpers.rsa_helpers import decrypt_rsa, private_key_from_string, public_key_from_string, stripe_secret_private_key
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db
from src.payment.stripe.models import StripeInformation
from src.payment.stripe.stripe import CreditCard, Stripe
from src.profile.models import Admin
from src.profile.payment_settings.stripe.models import StripeSettings


stripe_settings_endpoints = Blueprint('stripe_settings_endpoints', __name__)


'''
@route POST /payments-settings/stripe
@desc Set secrets for this Admin's Stripe account
@access Admin
'''
@stripe_settings_endpoints.route('stripe', methods=['POST'])
@admin_required()
def set_stripe_secrets_route():
    try:
        admin_id = get_jwt().get('id')
        organization_id = get_jwt().get('org')
        body = request.json

        stripe: StripeSettings = StripeSettings.query.filter_by(
            organization_id = organization_id,
            admin_id = admin_id
        ).one_or_none()
        
        if not stripe:
            body['admin_id'] = admin_id
            body['organization_id'] = organization_id

            result_bool, result_data = StripeSettings.register(body)
            
            if not result_bool:
                return Response(False, result_data).respond()
        else:
            result_bool, result_data = stripe.update(body)
            
            if not result_bool:
                return Response(False, result_data).respond()
        
        return Response(True, 'Settings updated successfully!').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /payments-settings/stripe
@desc Confirm whether this Admin's Stripe is configured
@access Admin
'''
@stripe_settings_endpoints.route('stripe', methods=['GET'])
@admin_required()
def confirm_stripe_configuration_route():
    try:
        admin_id = get_jwt().get('id')
        organization_id = get_jwt().get('org')

        stripe = StripeSettings.query.filter_by(
            admin_id = admin_id,
            organization_id = organization_id
        ).one_or_none()

        if not stripe:
            return Response(False, 'Stripe is not configured for this account').respond()

        return Response(True, 'Stripe has been configured for this account').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route GET /payments-settings/stripe/cards
@desc Fetch all cards for contact
@access Admin
'''
@stripe_settings_endpoints.route('stripe/cards/<uuid:id>', methods=['GET'])
@admin_required()
def fetch_all_cards_in_stripe_belonging_to_contact_route(id):
    try:
        organization_id = get_jwt().get('org')

        admin: Admin = Admin.fetch_by_id(
            id=get_jwt().get('id'),
            organization_id=organization_id
        )
        stripe_settings = admin.get_stripe_settings()

        stripe: Stripe = Stripe(
            api_key=stripe_settings.secret_key,
            contact_id=id,
            organization_id=organization_id
        )
        data = stripe.get_all_saved_cards_for_contact()

        if data == None or not isinstance(data, list):
            return Response(False, 'An error occurred', 500).respond()

        return Response(True, [model_to_dict(object) for object in data]).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route DELETE /payments-settings/stripe/cards
@desc Delete cards for contact
@access Admin
'''
@stripe_settings_endpoints.route('stripe/cards/<uuid:id>', methods=['DELETE'])
@admin_required()
def delete_card_for_contact_route(id):
    try:
        body = request.json 
        required_fields = ['card_id']
        for field in required_fields:
            if field not in body:
                return False, f'{field} is required!'

        organization_id = get_jwt().get('org')

        admin: Admin = Admin.fetch_by_id(
            id=get_jwt().get('id'),
            organization_id=organization_id
        )
        stripe_settings = admin.get_stripe_settings()

        stripe: Stripe = Stripe(
            api_key=stripe_settings.secret_key,
            contact_id=id,
            organization_id=organization_id
        )
        result_bool, result_data = stripe.remove_saved_card(id=body.get('card_id'))

        if not result_bool:
            return Response(False, str(result_data)).respond()
        return Response(True, 'Card deleted successfully!').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()

'''
@route POST /payments-settings/stripe/cards
@desc Add new card to Stripe
@access Admin
'''
@stripe_settings_endpoints.route('stripe/cards', methods=['POST'])
@admin_required()
def add_card_to_stripe_route():
    try:
        body = request.json 
        required_fields = ['contact_id', 'card_number', 'exp_month', 'exp_year', 'cvc']
        for field in required_fields:
            if field not in body:
                return False, f'{field} is required!'
        
        organization_id = get_jwt().get('org')

        admin: Admin = Admin.fetch_by_id(
            id=get_jwt().get('id'),
            organization_id=organization_id
        )
        stripe_settings = admin.get_stripe_settings()
        if not stripe_settings:
            return Response(False, 'Connect your Stripe account first to continue').respond()
        
        card: CreditCard = CreditCard(
            card_number=body.get('card_number'),
            cvc=body.get('cvc'),
            exp_month=body.get('exp_month'),
            exp_year=body.get('exp_year'),
        )

        private_key = stripe_secret_private_key(organization_id)
        if private_key is None:
            return Response(False, 'Connect your Stripe account first to continue').respond()

        stripe_secret = decrypt_rsa(
            stripe_settings.secret_key,
            private_key
        )
        if not stripe_secret:
            return Response(False, 'Connect your Stripe account first to continue').respond()

        stripe: Stripe = Stripe(
            api_key=stripe_secret,
            contact_id=body.get('contact_id'),
            organization_id=organization_id
        )

        result_bool, result_data = stripe.create_customer()
        if not result_bool:
            return Response(False, str(result_data)).respond()

        result_bool, result_data = stripe.add_card_payment_method(
            card=card,
            as_default=True
        )
        if not result_bool:
            return Response(False, str(result_data)).respond()

        return Response(True, model_to_dict(result_data)).respond()
    except Exception as e:
        raise e
        print(e)
        return Response(False, str(e), 500).respond()