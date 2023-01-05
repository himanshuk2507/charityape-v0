from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import P2pCategories
from skraggle.config import db

categoryviews = Blueprint("categoryviews", __name__, template_folder="templates")


@categoryviews.route("/create", methods=["POST"])
@user_required()
def add_categories():
    name = request.form["name"]
    description = request.form["description"]
    category = P2pCategories(name=name, description=description)
    db.session.add(category)
    db.session.flush()
    category.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Category with name: {category.name} was added successfully",
        "success": True,
    }
    return jsonify(data), 200


@categoryviews.route("/update", methods=["PATCH"])
@user_required()
def update_category():
    category_id = request.args.get("id")
    categories = P2pCategories.query.filter_by(
        id=category_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not categories:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    name = request.form["name"]
    description = request.form["description"]
    categories.name = name
    categories.description = description
    P2pCategories(name=name, description=description)
    db.session.commit()
    data = {
        "message": f" Category with name: {categories.name} was updated successfully",
        "success": True,
    }
    return jsonify(data)


@categoryviews.route("/all")
@user_required()
def all_categories():
    categories = P2pCategories.query.all()
    return {"Categories_list": [str(x.id) for x in categories]}


@categoryviews.route("/info/<category_id>")
@user_required()
def info_categories(category_id):
    categories = P2pCategories.query.filter_by(
        id=category_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not categories:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = categories.to_dict()
    return jsonify(data), 200


@categoryviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_categories():
    category_id = request.args.get("id")
    try:
        P2pCategories.query.filter_by(
            id=category_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {
            "message": f" ID: {category_id} was successfully deleted",
            "success": True
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400
