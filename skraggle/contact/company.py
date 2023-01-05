from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import and_, or_

from skraggle.base_helpers.responser import DataResponse
from skraggle.contact.models import CompanyUsers
from skraggle.config import db
from skraggle.decarotor import user_required
from sqlalchemy.sql import func

from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator, paginator_search

companyview = Blueprint("companyview", __name__)


@companyview.route("/add", methods=["POST"])
@user_required()
def add_company():
    if request.method == "POST":
        company_name = request.json.get("company_name")
        primary_phone = request.json.get("primary_phone")
        tag = request.json.get("tag")
        created_on = func.now()
        company = CompanyUsers(
            company_name=company_name,
            primary_phone=primary_phone,
            tag=tag,
            created_on=created_on,
        )
        db.session.add(company)
        db.session.flush()
        company.organization_id = getOrg(get_jwt())
        db.session.commit()
        return f"Company - {company_name} created successfully"


@companyview.route("/update", methods=['PATCH'])
def update_company_info():
    company_id = request.args.get("id")
    company = CompanyUsers.query.filter_by(company_id=company_id).first()
    if company:
        company_name = request.json.get("company_name")
        primary_phone = request.json.get("primary_phone")
        tag = request.json.get("tag")
        company.company_name = company_name
        company.primary_phone = primary_phone
        company.tag = tag
        company.created_on = func.now()
        db.session.commit()
        return f"company with id {company_id} Updated"
    return f"Employee with id  {company_id} Does not exist"


@companyview.route("/all/<int:page_number>", methods=["GET"])
@user_required()
def get_info(page_number):
    instance = CompanyUsers
    order_by_column = "company_id"
    api_path = "company/all"
    return paginator(page_number, instance, order_by_column, api_path)


@companyview.route("/<string:company_id>", methods=["GET"])
@user_required()
def get_information(company_id):
    company = CompanyUsers.query.filter_by(
        company_id=company_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not company:
        return jsonify({"error": "Company does not exist"}), 404
    if company:
        data = {
            "Company": {
                "company_id": company.company_id,
                "Company_name": company.company_name,
                "primary_phone": company.primary_phone,
                "tags": company.tag,
                "created_on": company.created_on,
            }
        }
        return jsonify(data), 200


@companyview.route("/delete", methods=["DELETE"])
@user_required()
def delete_company():
    companies = request.json.get("companies")
    if not companies:
        resp = DataResponse(False, "Empty Contacts List to Delete")
        return resp.status()

    try:
        db.session.query(CompanyUsers).filter(
            and_(
                CompanyUsers.organization_id == getOrg(get_jwt()),
                CompanyUsers.company_id.in_(companies),
            )
        ).delete(synchronize_session=False)
        db.session.commit()
        resp = DataResponse(
            True,
            f"{'Companies' if len(companies) > 1 else 'Company'} Deleted Successfully",
        )
        return resp.status()
    except Exception as e:
        resp = DataResponse(True, f"Error deleting Company :{str(e)[:105]}")
        return resp.status()


@companyview.route("/search", methods=["GET"])
@user_required()
def search():
    search_string = request.args.get("search_string")
    page_number = request.args.get("page")
    order_by_column = "company_id"
    instance = CompanyUsers.query.filter(or_(CompanyUsers.company_name.ilike(f'%{search_string}%'),
                                                 CompanyUsers.tag.ilike(f'%{search_string}%'),
                                                 CompanyUsers.primary_phone.ilike(f'%{search_string}%'))).order_by(getattr(CompanyUsers, order_by_column))
    api_path = "company/search"
    return paginator_search(page_number, instance, api_path)
