from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import P2pPromoCode, P2pCategories
from skraggle.config import db
import datetime

promocodeviews = Blueprint("promocodeviews", __name__, template_folder="templates")


@promocodeviews.route("/create", methods=["POST"])
@user_required()
def add_promocode():
    category_id = request.args.get("id")
    category = P2pCategories.query.filter_by(
        id=category_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not category:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    promo_code = request.form["promo_code"]
    description = request.form["description"]
    discount = request.form["discount"]
    max_user = request.form["max_user"]
    start_date = datetime.datetime.now()
    end_date = datetime.datetime.now()
    promo_code = P2pPromoCode(
        promo_code=promo_code,
        description=description,
        discount=discount,
        max_user=max_user,
        start_date=start_date,
        end_date=end_date
    )

    category.promocodes.append(promo_code)
    db.session.flush()
    promo_code.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Promocode with discount: {promo_code.discount} was added successfully",
        "success": True,
    }
    return jsonify(data), 200


@promocodeviews.route("/update", methods=["PATCH"])
@user_required()
def update_promocode():
    promocode_id = request.args.get("id")
    promocodes = P2pPromoCode.query.filter_by(
        id=promocode_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not promocodes:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    promo_code = request.form["promo_code"]
    description = request.form["description"]
    discount = request.form["discount"]
    max_user = request.form["max_user"]
    start_date = datetime.datetime.now()
    end_date = datetime.datetime.now()

    promocodes.promo_code = promo_code
    promocodes.description = description
    promocodes.discount = discount
    promocodes.max_user = max_user

    P2pPromoCode(
        promo_code=promo_code,
        description=description,
        discount=discount,
        max_user=max_user,
        start_date=start_date,
        end_date=end_date,
    )

    db.session.commit()

    data = {
        "message": f" Promocode with discount: {promocodes.discount} was updated successfully",
        "success": True,
    }
    return jsonify(data), 200


@promocodeviews.route("/all")
@user_required()
def all_promocode():
    promoCode = P2pPromoCode.query.all()
    return {"PromoCode_list": [str(x.id) for x in promoCode]}


@promocodeviews.route("/info/<promocode_id>")
@user_required()
def information_promocode(promocode_id):
    promoCode = P2pPromoCode.query.filter_by(
        id=promocode_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not promoCode:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = promoCode.to_dict()
    return jsonify(data), 200


@promocodeviews.route("/delete", methods=["DELETE"])
@user_required()
def information_promocode_delete():
    promocode_id = request.args.get("id")
    try:
        promocode = P2pPromoCode.query.filter_by(
            id=promocode_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {
            "message": f" ID: {promocode_id} was successfully deleted",
            "success": True,
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
