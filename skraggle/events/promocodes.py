from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.events.models import PromoCode, Packages
from skraggle.config import db
import datetime

from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator
from skraggle.base_helpers.responser import DataResponse

promocodeview = Blueprint("promocodeview", __name__)


@promocodeview.route("/create", methods=["POST"])
@user_required()
def add_promocode():
    package_id = request.args.get("package_id")
    packages = Packages.query.filter_by(
        id=package_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not packages:
        return DataResponse(False, "The given ID: {} doesn't exist".format(package_id)).status()
    
    json_data = request.json
    promo_code = json_data["promo_code"]
    description = json_data["description"]
    discount = json_data["discount"]
    max_user = json_data["max_user"]
    start_date = datetime.datetime.now()
    end_date = datetime.datetime.now()

    
    check = PromoCode.query.filter_by(promo_code=promo_code).one_or_none()
    if check:
        return DataResponse(False, "Promo Code {} already exist".format(promo_code)).status()
             
    promocodes = PromoCode(
        promo_code=promo_code,
        description=description,
        discount=discount,
        max_user=max_user,
        start_date=start_date,
        end_date=end_date,
        organization_id=getOrg(get_jwt())
    )

    packages.promocode.append(promocodes)
    db.session.flush()
    promocodes.organization_id = getOrg(get_jwt())
    db.session.commit()
    return DataResponse(
        True, 
        "Promo Code with promo: {} was added successfully".format(promocodes.promo_code)
        ).status()


@promocodeview.route("/update/<uuid:promocode_id>", methods=["PATCH"])
@user_required()
def update_promocode(promocode_id):
    promocodes = PromoCode.query.filter_by(
        id=promocode_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not promocodes:
        return DataResponse(False, "The given ID: {} doesn't exist".format(promocode_id)).status()
        
    json_data = request.json
    promo_code = json_data["promo_code"]
    description = json_data["description"]
    discount = json_data["discount"]
    max_user = json_data["max_user"]
    start_date = datetime.datetime.now()
    end_date = datetime.datetime.now()

    promocodes.promo_code = promo_code
    promocodes.description = description
    promocodes.discount = discount
    promocodes.max_user = max_user

    PromoCode(
        promo_code=promo_code,
        description=description,
        discount=discount,
        max_user=max_user,
        start_date=start_date,
        end_date=end_date,
    )

    db.session.commit()
    return DataResponse(True, "Promo Code with promo: {} was updated successfully".format(promocodes.promo_code)).status()


@promocodeview.route("/all/<int:page_number>",methods=["GET"])
@user_required()
def all_promocode(page_number):
    instance = PromoCode
    order_by_column = "id"
    api_path = "event-promocode/all"
    return paginator(page_number, instance, order_by_column, api_path)


@promocodeview.route("/info/<promocode_id>",methods=["GET"])
@user_required()
def info_promocode(promocode_id):
    promocode = PromoCode.query.filter_by(
        id=promocode_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not promocode:
        return DataResponse(False, "The given ID doesn't exist").status()
    

    data = promocode.to_dict()
    return DataResponse(True, data).status()


@promocodeview.route("/delete/<uuid:promocode_id>", methods=["DELETE"])
@user_required()
def information_promocode_delete(promocode_id):
    try:
        
        promo_code = PromoCode.query.filter_by(
            id=promocode_id, organization_id=getOrg(get_jwt())
        )
        if not promo_code.one_or_none():
            return DataResponse(False, "The ID: {} is Invalid".format(promocode_id)).status()
        
        promo_code.delete()
        db.session.commit()
        return DataResponse(True, "ID: {} was successfully deleted".format(promocode_id)).status()
    
    except Exception as e:
        return DataResponse(False, str(e)[:105]).status()
