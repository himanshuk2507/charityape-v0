from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.events.models import Packages
from skraggle.config import db
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator_search
from skraggle.base_helpers.responser import DataResponse

packageviews = Blueprint("packageviews", __name__)


@packageviews.route("/create", methods=["POST"])
@user_required()
def add_package():
    name = request.json.get("name")
    description = request.json.get("description")
    price = request.json.get("price")
    direct_cost = request.json.get("direct_cost")
    number_of_packages_for_sale = request.json.get("number_of_packages_for_sale")
    qty_purchase_limit = request.json.get("qty_purchase_limit")
    early_bird_discount_enabled = request.json.get("early_bird_discount_enabled")
    early_bird_discount_amount = request.json.get("early_bird_discount_enabled")
    early_bird_discount_cutoff_time = request.json.get("early_bird_discount_enabled")
    early_bird_discount_type =request.json.get("early_bird_discount_enabled")

    packages = Packages(
        name=name,
        description=description,
        price=price,
        direct_cost=direct_cost,
        number_of_packages_for_sale=number_of_packages_for_sale,
        qty_purchase_limit=qty_purchase_limit,
        organization_id=getOrg(get_jwt()),
        is_enabled=True,
        early_bird_discount_enabled=early_bird_discount_enabled,
        early_bird_discount_amount=early_bird_discount_amount,
        early_bird_discount_cutoff_time=early_bird_discount_cutoff_time,
        early_bird_discount_type=early_bird_discount_type
    )
    db.session.add(packages)
    db.session.flush()
    packages.organization_id = getOrg(get_jwt())
    db.session.commit()
    return DataResponse(True, f" Package with name: {packages.name} was added successfully").status()


@packageviews.route("/clone", methods=["POST"])
@user_required()
def clone_event():
    package_id = request.args.get("id")
    clone_package = Packages.query.filter_by(
        id=package_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not clone_package:
        return DataResponse(False, "The given ID doesn't exist").status()

    name = clone_package.name
    description = clone_package.description
    price = clone_package.price
    direct_cost = clone_package.direct_cost
    number_of_packages_for_sale = clone_package.number_of_packages_for_sale
    qty_purchase_limit = clone_package.qty_purchase_limit
    is_enabled = clone_package.is_enabled
    early_bird_discount_enabled = clone_package.early_bird_discount_enabled,
    early_bird_discount_amount = clone_package.early_bird_discount_amount,
    early_bird_discount_cutoff_time = clone_package.early_bird_discount_cutoff_time,
    early_bird_discount_type = clone_package.early_bird_discount_type
    package = Packages(
        name=name,
        description=description,
        price=price,
        direct_cost=direct_cost,
        number_of_packages_for_sale=number_of_packages_for_sale,
        qty_purchase_limit=qty_purchase_limit,
        organization_id=getOrg(get_jwt()),
        is_enabled=bool(is_enabled),
        early_bird_discount_enabled=bool(early_bird_discount_enabled),
        early_bird_discount_amount=early_bird_discount_amount,
        early_bird_discount_cutoff_time=early_bird_discount_cutoff_time,
        early_bird_discount_type=early_bird_discount_type or 'amount'
    )
    db.session.add(package)
    db.session.flush()
    package.organization_id = getOrg(get_jwt())
    db.session.commit()

    return DataResponse(True, f" Package with name: {package.name} was clone successfully from Package_ID {package_id}").status()


@packageviews.route("/update", methods=["PATCH"])
@user_required()
def update_package():
    package_id = request.args.get("id")
    packages = Packages.query.filter_by(
        id=package_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not packages:
        return DataResponse(False, "The given ID doesn't exist").status()
    name = request.json.get("name")
    description = request.json.get("description")
    price = request.json.get("price")
    direct_cost = request.json.get("direct_cost")
    number_of_packages_for_sale = request.json.get("number_of_packages_for_sale")
    qty_purchase_limit = request.json.get("qty_purchase_limit")
    is_enabled = request.json.get("is_enabled")
    early_bird_discount_enabled = request.json.get("early_bird_discount_enabled")
    early_bird_discount_amount = request.json.get("early_bird_discount_enabled")
    early_bird_discount_cutoff_time = request.json.get("early_bird_discount_enabled")
    early_bird_discount_type =request.json.get("early_bird_discount_enabled")
    packages.name = name or packages.name
    packages.description = description or packages.description
    packages.price = price or packages.price
    packages.direct_cost = direct_cost or packages.direct_cost
    packages.number_of_packages_for_sale = number_of_packages_for_sale or packages.number_of_packages_for_sale
    packages.qty_purchase_limit = qty_purchase_limit or packages.qty_purchase_limit
    packages.is_enabled = is_enabled or packages.is_enabled
    packages.early_bird_discount_enabled = early_bird_discount_enabled or packages.early_bird_discount_enabled
    packages.early_bird_discount_amount = early_bird_discount_amount or early_bird_discount_amount
    packages.early_bird_discount_cutoff_time = early_bird_discount_cutoff_time or early_bird_discount_cutoff_time
    packages.early_bird_discount_type = early_bird_discount_type or early_bird_discount_type

    db.session.commit()
    return DataResponse(True, f" Package with name: {packages.name} was updated successfully").status()


@packageviews.route("/all/<int:page_number>", methods=["GET"])
@user_required()
def all_packages(page_number):
    instance = Packages.query.filter_by(organization_id=getOrg(get_jwt())).order_by('id')
    api_path = "event-package/all"
    return paginator_search(page_number, instance, api_path)


@packageviews.route("/info/<package_id>", methods=["GET"])
@user_required()
def package_info(package_id):
    packages = Packages.query.filter_by(
        id=package_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not packages:
        return DataResponse(False, "The given ID doesn't exist").status()

    data = packages.to_dict()
    return DataResponse(True, data).status()


@packageviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_package():
    package_id = request.args.get("id")
    try:
        Packages.query.filter_by(
            id=package_id, organization_id=getOrg(get_jwt())
        ).delete()
        db.session.commit()
        return DataResponse(True, f" ID: {package_id} was successfully deleted").status()
    except Exception as e:
        return DataResponse(False, str(e)[:105], 400).status()


@packageviews.route("/toggle-is-enabled", methods=["PUT"])
@user_required()
def toggle_is_enabled():
    package_id = request.args.get("id")
    try:
        package = Packages.query.filter_by(
            id=package_id, organization_id=getOrg(get_jwt())
        ).first()
        package.is_enabled = not package.is_enabled
        db.session.commit()

        return DataResponse(True, f" ID: {package_id} was successfully {'enabled' if package.is_enabled else 'disabled'}").status()
    except Exception as e:
        return DataResponse(False, str(e)[:105], 400).status()


@packageviews.route("/add-participants", methods=["POST"])
@user_required()
def add_participants():
    participants = request.json.get("ids")
    package_id = request.args.get("id")
    try:
        package = Packages.query.filter_by(
            id=package_id, organization_id=getOrg(get_jwt())
        ).first()
        if package.participants:
            package.participants = package.participants.append(participants)
        else:
            package.participants = participants
        db.session.commit()

        return DataResponse(True, f"Participants added to Package: {package_id}").status()
    except Exception as e:
        return DataResponse(False, str(e)[:105], 400).status()


@packageviews.route("/remove-participants", methods=["DELETE"])
@user_required()
def remove_participants():
    participants = request.json.get("ids")
    package_id = request.args.get("id")
    try:
        package = Packages.query.filter_by(
            id=package_id, organization_id=getOrg(get_jwt())
        ).first()

        if package.participants:
            for participant in participants:
                package.participants.remove(participant)

        db.session.commit()

        return DataResponse(True, f"Participants removed from Package: {package_id}").status()
    except Exception as e:
        return DataResponse(False, str(e)[:105], 400).status()
