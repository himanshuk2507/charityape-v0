import uuid

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt

from skraggle.config import db
from skraggle.decarotor import user_required
from skraggle.base_helpers.dict_responser import multi_dict_resp
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator
from .models import Forms, Responses
from skraggle.base_helpers.responser import DataResponse
from skraggle.campaigns.models import Campaigns
from datetime import datetime
import json

formview = Blueprint("formview", __name__)


@formview.route("/create", methods=["POST"])
@user_required()
def create_form():
    form_name = request.json.get("form_name")
    form = Forms.query.filter_by(form_name=form_name, organization_id=getOrg(get_jwt())).first()
    if form:
        return DataResponse(False, f"Form name {form_name} already exists").status()
    form_type = request.json.get("form_type")
    desc = request.json.get("desc")
    status = request.json.get("status")
    followers = request.json.get("followers")
    is_default_donation = request.json.get("is_default_donation")
    is_default_currency = request.json.get("is_default_currency")
    tags = request.json.get("tags")
    is_minimum_amount = request.json.get("is_minimum_amount")
    is_processing_fee = request.json.get("is_processing_fee")
    is_tribute = request.json.get("is_tribute")
    form = {
        "form_name": form_name,
        "form_type": form_type,
        "tags": tags,
        "desc": desc,
        "status": status,
        "followers": followers,
        "is_minimum_amount": is_minimum_amount,
        "is_default_donation": is_default_donation,
        "is_processing_fee": is_processing_fee,
        "is_tribute": is_tribute,
        "is_default_currency": is_default_currency,
        "created": datetime.now()
    }
    for keys in request.json:
        if keys in form.keys():
            if isinstance(request.json[keys], str):
                if request.json[keys].lower() == "true" or request.json[keys].lower() == "false":
                    form[keys] = json.loads(request.json[keys].lower())
            else:
                form[keys] = request.json[keys]
        else:
            form[keys] = request.json[keys]

    form = Forms(**form)
    if "campaign_id" in request.json:
        campaign = Campaigns.query.filter_by(
            id=int(request.json["campaign_id"]), organization_id=getOrg(get_jwt())
        ).first()
        if campaign:
            campaign.Forms.append(form)
            db.session.flush()
            form.organization_id = getOrg(get_jwt())
        else:
            return DataResponse(False, f"Compaign does not exist").status()
    else:
        db.session.add(form)
        db.session.flush()
        form.organization_id = getOrg(get_jwt())

    db.session.commit()
    return DataResponse(True, f"Form - {form_name} created successfully").status()


@formview.route("/all/<int:page_number>", methods=["GET"])
@user_required()
def view_forms(page_number):
    instance = Forms
    order_by_column = "form_id"
    api_path = "forms/all"
    return paginator(page_number, instance, order_by_column, api_path)


@formview.route("/delete", methods=["DELETE"])
@user_required()
def transaction_delete():
    resp = {"Status": None}
    if request.method == "POST":
        ids = list(map(str,  request.args.get("form_ids").split(",")))
        forms_list = (
            db.session.query(Forms)
            .filter(Forms.organization_id == getOrg(get_jwt()))
            .filter(Forms.form_id.in_(ids))
            .all()
        )

        if forms_list:
            for form in forms_list:

                if form.status.lower() == "published":
                    resp["Status"] = "Published Forms must be closed before deleting"
                else:
                    db.session.delete(form)
                    db.session.commit()
                    resp["Status"] = "Forms Deleted"
        else:
            resp["Status"] = "Specified Forms Does not Exist"
    return jsonify(resp)


@formview.route("/filter",methods=["GET"])
@user_required()
def filter_forms():
    data = {}
    type = request.args.get("filter_type")
    if type.lower() == "date":
        date1 = request.args.get("date1")
        date2 = request.args.get("date2")
        format_date = "%d %B, %Y"
        start_date = datetime.strptime(date1, format_date)
        end_date = datetime.strptime(date2, format_date)
        print(start_date, end_date)
        filtered_forms = (
            db.session.query(Forms)
            .filter(Forms.organization_id == getOrg(get_jwt()))
            .filter(Forms.created.between(start_date, end_date))
        )
        data = {
            "Forms": [
                {
                    "form_id": form.form_id,
                    "form_name": form.form_name,
                    "campaign_id": form.compaign,
                    "campaign_name": Campaigns.query.filter_by(
                        id=form.compaign, organization_id=getOrg(get_jwt())
                    )
                    .first()
                    .name
                    if form.compaign is not None
                    else "NA",
                    "form_type": form.form_type,
                    "description": form.followers,
                    "followers": form.followers,
                    "status": form.status,
                }
                for form in filtered_forms
            ]
        }
    elif type.lower == "tags":
        pass
    return jsonify(data)


@formview.route("/Responses/add/<int:form_id>", methods=["PATCH"])
def add_response(form_id):
    if request.method == "POST":
        fullname = request.form["fullname"]
        address = request.form["address"]
        optional_fields = {
            "minimum_amount": "is_minimum_amount",
            "default_currency": "is_default_currency",
        }
        resp = {
            "fullname": fullname,
            "address": address,
            "gender": "NA",
            "last_name": "NA",
            "payment_method": "NA",
            "payment_type": "NA",
            "minimum_amount": 0,
            "birth_date": "NA",
            "comments": "NA",
            "default_currency": "INR",
        }
        main_form = Forms.query.filter_by(
            form_id=form_id, organization_id=getOrg(get_jwt())
        ).first()
        for keys in request.form:
            if keys in resp.keys():
                if keys in optional_fields.keys():
                    check = optional_fields[keys]
                    print(main_form)

                else:
                    resp[keys] = request.form[keys]
        response = Responses(**resp)
        main_form.Responses.append(response)
        db.session.flush()
        response.organization_id = getOrg(get_jwt())
        db.session.commit()
        return "Response Added Succesfully"

    @formview.route("/show_responses/<int:form_id>",methods=["GET"])
    @user_required()
    def show_responses(form_id):
        main_form = Forms.query.filter_by(
            form_id=form_id, organization_id=getOrg(get_jwt())
        ).first()
        form_responses = main_form.Responses
        return jsonify(multi_dict_resp(form_responses)), 200
