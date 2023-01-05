from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.campaigns.models import Campaigns
from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator
from skraggle.landing_page.models import Elements
from skraggle.config import db

elementsviews = Blueprint("elementsviews", __name__)


@elementsviews.route("/create", methods=["POST"])
@user_required()
def add_elements():
    campaign_id = request.args.get("id")
    campaign = Campaigns.query.filter_by(
        id=campaign_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not campaign:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    name = request.form["name"]
    type = request.form["type"]
    elements = Elements(name=name, type=type)
    campaign.element.append(elements)
    db.session.flush()
    elements.organization_id = getOrg(get_jwt())
    db.session.commit()
    data = {
        "message": f" Element with name: {elements.name} was added successfully with Campaign ID{campaign.id}",
        "success": True,
    }
    return jsonify(data), 200


@elementsviews.route("/update", methods=["PATCH"])
@user_required()
def update_elements():
    element_id = request.args.get("id")
    elements = Elements.query.filter_by(
        id=element_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not elements:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    name = request.form["name"]
    type = request.form["type"]
    elements.name = name
    elements.type = type
    Elements(name=name, type=type)
    db.session.commit()
    data = {
        "message": f" Element with name: {elements.name} was updated successfully",
        "success": True,
    }
    return jsonify(data), 200


@elementsviews.route("/clone", methods=["POST"])
@user_required()
def clone_elements():
    element_id = request.args.get("id")
    clone_element = Elements.query.filter_by(
        id=element_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not clone_element:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    name = clone_element.name
    type = clone_element.type
    campaign_id = clone_element.campaign_id
    internal = clone_element.internal
    external = clone_element.external
    source_code = clone_element.source_code
    disabled = clone_element.disabled
    archive = clone_element.archive
    elements = Elements(
        name=name,
        type=type,
        campaign_id=campaign_id,
        internal=internal,
        external=external,
        source_code=source_code,
        disabled=disabled,
        archive=archive,
    )
    db.session.add(elements)
    db.session.flush()
    elements.organization_id = getOrg(get_jwt())
    db.session.commit()

    data = {
        "message": f" Element with name: {elements.name} was clone successfully from Element ID {element_id}",
        "success": True,
    }
    return jsonify(data), 200


@elementsviews.route("/all/<int:page_number>",methods=["GET"])
@user_required()
def all_elements(page_number):
    instance = Elements
    order_by_column = "id"
    api_path = "element/all"
    return paginator(page_number, instance, order_by_column, api_path)


@elementsviews.route("/info/<element_id>",methods=["GET"])
@user_required()
def info_elements(element_id):
    element = Elements.query.filter_by(
        id=element_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not element:
        return (
            jsonify({"success": False, "message": "The given ID doesn't exist"}),
            404,
        )
    data = element.todict()
    return jsonify(data), 200


@elementsviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_elements():
    element_id = request.args.get("id")
    try:
        Elements.query.filter_by(
            id=element_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        data = {
            "message": f" ID: {element_id} was successfully deleted",
            "success": True,
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400


@elementsviews.route("/type_update", methods=["POST"])
@user_required()
def type_update():
    element_id = request.args.get("id")
    element = Elements.query.filter_by(
        id=element_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not element:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"The Landing page with ID: {element_id} doesn't exist",
                }
            ),
            404,
        )
    type = request.form["type"]
    source_code = request.form["source_code"]
    element.source_code = source_code
    internal_count = element.internal
    external_count = element.external
    if type == "internal" and element.type == "internal":
        element.internal = internal_count + 1
    elif type == "external" and element.type == "external":
        element.external = external_count + 1
    db.session.commit()

    data = {
        "message": f" No of {type} usage updated, new {type} count : {element.internal} ",
        "success": True,
    }
    return jsonify(data), 200
