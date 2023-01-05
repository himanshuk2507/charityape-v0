from datetime import datetime
from uuid import UUID

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy import and_

from skraggle.decarotor import user_required
from skraggle.base_helpers.dict_responser import dict_resp
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator, paginator_search
from skraggle.base_helpers.responser import DataResponse
from .models import HouseholdUsers
from skraggle.config import db
from sqlalchemy import and_, or_
import time

householdview = Blueprint("householdview", __name__)


@householdview.route("/add", methods=["POST"])
@user_required()
def households_create():
    name = request.json["name"]
    date = datetime.now()
    household_user = HouseholdUsers(name=name, contacts=None, created_on=date)
    db.session.add(household_user)
    db.session.flush()
    household_user.organization_id = getOrg(get_jwt())
    db.session.commit()
    resp = DataResponse(True, "Households created successfully")
    return resp.status()


@householdview.route("/<uuid:household_id>",methods=["GET"])
@user_required()
def households_list(household_id):
    household = HouseholdUsers.query.filter_by(
        household_id=household_id, organization_id=getOrg(get_jwt())
    ).first()
    if household:
        return jsonify(dict_resp(household)), 200
    else:
        return {"Error": "household does not exist"}


@householdview.route("/all/<int:page_number>",methods=["GET"])
@user_required()
def households_details(page_number):
    instance = HouseholdUsers
    order_by_column = "household_id"
    api_path = "households/all"
    return paginator(page_number, instance, order_by_column, api_path)


@householdview.route("/update", methods=["PATCH"])
@user_required()
def households_update():
    household_id = request.args.get("household_id")
    household = HouseholdUsers.query.filter_by(
        household_id=household_id, organization_id=getOrg(get_jwt())
    ).first()
    if household:
        name = request.form["name"]
        household.name = name
        db.session.commit()
        return f"household with id {household_id} Updated"
    return f"Employee with id = {household_id} Does not exist"


@householdview.route("/delete",methods=["DELETE"])
@user_required()
def households_delete():
    households = request.json.get("households")
    if not households:
        resp = DataResponse(False, "Empty Contacts List to Delete")
        return resp.status()

    try:
        db.session.query(HouseholdUsers).filter(
            and_(
                HouseholdUsers.organization_id == getOrg(get_jwt()),
                HouseholdUsers.household_id.in_(households),
            )
        ).delete(synchronize_session=False)
        db.session.commit()
        resp = DataResponse(
            True,
            f"{'Households' if len(households) > 1 else 'Household'} Deleted Successfully",
        )
        return resp.status()
    except Exception as e:
        resp = DataResponse(True, f"Error deleting Household :{str(e)[:105]}")
        return resp.status()


@householdview.route("/<household_id>/add-contact", methods=["PATCH"])
@user_required()
def add_Contact_to_household(household_id):
    household = HouseholdUsers.query.filter_by(
        household_id=household_id, organization_id=getOrg(get_jwt())
    ).first()
    if household:

        contacts = list(map(str, request.json.get("contacts", [])))
        print(contacts)
        for contact in contacts:
            print(">>>>", contact)
            print(household.contacts)
            if not household.contacts or contact not in household.contacts:

                try:
                    if household.contacts is None:
                        household.contacts = [contact]
                    else:
                        household.contacts.add(contact)

                except Exception as e:
                    resp = DataResponse(False, str(e)[:105])
                    return resp.status()
            else:
                resp = DataResponse(
                    False, f"Contact {contact} already exists in Tag > {household_id} ",
                )
                return resp.status()
        db.session.commit()
        resp = DataResponse(
            True, f"Contacts Added to Household with id  {household_id} "
        )
        return resp.status()

    else:
        resp = DataResponse(True, f"household with id {household_id} Does not exist")
        return resp.status()


@householdview.route("/<household_id>/delete-contact", methods=["DELETE"])
@user_required()
def delete_Contacts_from_household(household_id):
    household = HouseholdUsers.query.filter_by(
        household_id=household_id, organization_id=getOrg(get_jwt())
    ).first()
    if household:

        contacts = list(map(str, request.json.get("contacts", [])))
        for contact in contacts:

            if UUID(contact) in household.contacts:
                try:
                    household.contacts.remove(UUID(contact))
                except Exception as e:
                    resp = DataResponse(False, str(e)[:105])
                    return resp.status()
            else:
                resp = DataResponse(True, "Contact does not exist in household")
                return resp.status()

        db.session.commit()
        resp = DataResponse(True, "Contacts Deleted from Tags")
        return resp.status()
    else:
        resp = DataResponse(False, f"Tag with id {household_id} Does not exist")
        return resp.status()
    
    

@householdview.route("/search", methods=["GET"])
@user_required()
def search():
    search_string = request.args.get("search_string")
    page_number = request.args.get("page")
    order_by_column = "household_id"
    instance = HouseholdUsers.query.filter(or_(
        HouseholdUsers.name.ilike(f'%{search_string}%')
        )).order_by(getattr(HouseholdUsers, order_by_column))
    api_path = "households/search"
    return paginator_search(page_number, instance, api_path)