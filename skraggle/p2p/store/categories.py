from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import StoreCategories, StoreProduct
from skraggle.config import db

storecategoryviews = Blueprint(
    "storecategoryviews", __name__, template_folder="templates"
)


@storecategoryviews.route("/create", methods=["POST"])
@user_required()
def add_categories():
    name = request.form["name"]
    category = StoreCategories(name=name)
    db.session.add(category)
    db.session.flush()
    category.organization_id=getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Category with name: {category.name} was added successfully",
        "success": True}
    return jsonify(data), 200


@storecategoryviews.route("/update", methods=["PATCH"])
@user_required()
def update_categories():
    category_id = request.args.get('id')
    categories = StoreCategories.query.filter_by(id=category_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not categories:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    name = request.form["name"]
    categories.name = name
    StoreCategories(name=name)
    db.session.commit()
    data = {
        "message": f" Category with name: {categories.name} was added successfully",
        "success": True}
    return jsonify(data), 200


@storecategoryviews.route("/all")
@user_required()
def all_categories():
    categories = StoreCategories.query.all()
    return {"Category_list": [str(x.id) for x in categories]}


@storecategoryviews.route("/info/<category_id>")
@user_required()
def info_categories(category_id):
    category = StoreCategories.query.filter_by(id=category_id,organization_id=getOrg(get_jwt())).one_or_none()
    if not category:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = category.to_dict()
    return jsonify(data), 200


@storecategoryviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_categories():
    category_id = request.args.get("id ")
    try:
        category = StoreCategories.query.filter_by(id=category_id ,organization_id=getOrg(get_jwt())).delete()
        db.session.commit()
        data = {"message": f" ID: {category_id} was successfully deleted",
                "success": True}
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
