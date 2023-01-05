
from operator import and_
from typing import List
from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.custom_validator import Validator
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from src.app_config import db
from sqlalchemy.orm.session import make_transient
from .models import Packages

packageviews = Blueprint("packageviews", __name__)


'''
@route POST /package/create
@desc Create Packages
@access Admin
'''


@packageviews.route('/create', methods=["POST"])
@admin_required()
def package():
    body = request.json
    body['organization_id'] = get_jwt().get('org')

    try:
        result_bool, result_data = Packages.register(body)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /package
@desc All Packages
@access Admin
'''


@packageviews.route('', methods=["GET"])
@admin_required()
def list_packages():
    try:
        data = Paginator(
            model=Packages,
            query=Packages.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /package/clone
@desc Clone Packages
@access Admin
'''


@packageviews.route("/clone", methods=["POST"])
@admin_required()
def clone_package():
    try:
        body = request.json
        packages = body.get('packages', [])

        if len(packages) == 0:
            return Response(False, 'No package to perform CLONE operation on').respond()

        packages = db.session.query(Packages)\
            .filter(
            and_(
                Packages.id.in_(packages),
                Packages.organization_id == get_jwt().get('org')
            )
        )\
            .all()
        for package in packages:
            make_transient(package)
            package.id = None
            package.name += " (cloned)"
            db.session.add(package)
            db.session.commit()

        data = Paginator(
            model=Packages,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route PATCH /package/<uuid>
@desc Update Packages by ID
@access Admin
'''


@packageviews.route("<uuid:id>", methods=["PATCH"])
@admin_required()
def update_package(id):
    try:
        body = request.json
        package = Packages.fetch_by_id(
            id, organization_id=get_jwt().get('org'))

        # validations
        if not package:
            return Response(False, 'This package does not exist').respond()
        unallowed_fields = ['id', 'organization_id']

        for field in body.keys():
            if field not in unallowed_fields:
                setattr(package, field, body.get(field))

        db.session.add(package)
        db.session.commit()

        return Response(True, model_to_dict(package)).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route GET /package/info/<uuid>
@desc Get Packages by ID
@access Admin
'''


@packageviews.route("/info/<uuid:id>", methods=["GET"])
@admin_required()
def package_info_by_id(id):
    package: Packages = Packages.fetch_by_id(
        id, organization_id=get_jwt().get('org'))
    if not package:
        return Response(False, f"This Package {id} does not exist").respond()

    return Response(True, model_to_dict(package)).respond()


@packageviews.route("", methods=["DELETE"])
@admin_required()
def delete_package():
    try:
        body = request.json
        if not body or body.get('packages') is None:
            return Response(False, '`packages` is a required field').respond()

        package_ids = body.get('packages', [])
        if len(package_ids) == 0:
            return Response(False, 'No Packages to perform DELETE operation on').respond()
        Packages.delete_many_by_id(package_ids, get_jwt().get('org'))

        return Response(True, 'Package(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
