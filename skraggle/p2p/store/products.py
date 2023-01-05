from flask_jwt_extended import get_jwt
from flask import Blueprint, request, jsonify
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import StoreCategories, StoreProduct
from skraggle.config import db

storeproductsviews = Blueprint(
    "storeproductsviews", __name__, template_folder="templates"
)


@storeproductsviews.route("/create", methods=["POST"])
@user_required()
def add_product():
    category_id = request.args.get("id")
    category = StoreCategories.query.filter_by(
        id=category_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not category:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    name = request.form["name"]
    description = request.form["description"]
    product = StoreProduct(name=name, description=description)
    category.store_product.append(product)
    db.session.flush()
    product.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Product with name: {product.name} is added successfully",
        "success": True}
    return jsonify(data), 200


@storeproductsviews.route("/update", methods=["PATCH"])
@user_required()
def update_product():
    id = request.args.get("id")
    product = StoreProduct.query.filter_by(id=id,organization_id = getOrg(get_jwt())).one_or_none()
    name = request.form["name"]
    description = request.form["description"]
    product.name = name
    product.description = description
    StoreProduct(name=name, description=description)
    db.session.commit()
    data = {
        "message": f" Product with name: {product.name} was updated successfully",
        "success": True}
    return jsonify(data), 200


@storeproductsviews.route("/all")
@user_required()
def all_product():
    product = StoreProduct.query.all()
    data = {
        "message": f" Products_list: {[str(x.id) for x in product]}",
        "success": True
    }
    return jsonify(data), 200


@storeproductsviews.route("/info/<product_id>")
@user_required()
def info_product(product_id):
    product = StoreProduct.query.filter_by(id=product_id).one_or_none()
    if not product:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = product.to_dict()
    return jsonify(data), 200


@storeproductsviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_product():
    product_id = request.args.get('id')
    try:
        data = {"message": f" ID: {product_id} was successfully deleted",
                "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400