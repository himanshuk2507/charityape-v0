from datetime import datetime
from uuid import UUID

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from itsdangerous import json
from skraggle.base_helpers.updating_fields_fetch import get_fields

from skraggle.decarotor import user_required
from skraggle.base_helpers.dict_responser import dict_resp, multi_dict_resp
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator, paginator_search
from skraggle.base_helpers.responser import DataResponse
from .models import SegmentUsers, ContactUsers
from skraggle.config import db
from sqlalchemy import and_, or_
import time

segmentview = Blueprint("segmentview", __name__,)


@segmentview.route("/add", methods=["POST"])
@user_required()
def segment_create():
    body = request.json

    if not 'name' in body or not 'contacts' in body:
        return DataResponse(False, "`name` and `contacts` are required fields").status()

    name = body['name']
    date = datetime.now()
    contacts = body['contacts']
    description = body['description'] if 'description' in body else ''
    segment_user = SegmentUsers(
        name=name, created_on=date, contacts=contacts, description=description
    )
    db.session.add(segment_user)
    db.session.flush()
    segment_user.organization_id = getOrg(get_jwt())
    db.session.commit()

    return DataResponse(True, { "id": segment_user.segment_id }).status()



@segmentview.route("/all/<int:page_number>", methods=["GET"])
@user_required()
def segments_detail(page_number):
    instance = SegmentUsers
    order_by_column = "segment_id"
    api_path = "segments/all"
    return paginator(page_number, instance, order_by_column, api_path)

@segmentview.route("/segment/<segment_id>", methods=["GET"])
@user_required()
def segments_list(segment_id):
    segment = SegmentUsers.query.filter_by(
        segment_id=segment_id, organization_id=getOrg(get_jwt())
    ).first()
    if segment:
        return jsonify(dict_resp(segment)), 200
    else:
        return DataResponse(False, "No Segment was Found with given ID").status()


@segmentview.route("/update", methods=["PATCH"])
@user_required()
def segments_update():
    body = request.json

    if len(body) == 0:
        return DataResponse(False, "No fields were specified in request body").status()

    segment_id = request.args.get("segment_id")
    segment = SegmentUsers.query.filter_by(
        segment_id=segment_id, organization_id=getOrg(get_jwt())
    ).one_or_none()

    if segment is None:
        return DataResponse(False, "Segment does not exist").status()

    updatable_fields = { "name", "description", "name" }
    segment_obj = dict.fromkeys(get_fields(SegmentUsers))
    try:
        for field in body:
            if field in updatable_fields and field in segment_obj.keys():
                setattr(segment, field, body[field])
        db.session.commit()
        return DataResponse(True, "Segment updated successfully!").status()
    except Exception as e:
        return DataResponse(False, "An error occurred").status()


@segmentview.route("/delete", methods=["DELETE"])
@user_required()
def segments_delete():
    segment_id = request.args.get("segment_id")
    segment = SegmentUsers.query.filter_by(
        segment_id=segment_id, organization_id=getOrg(get_jwt())
    ).one_or_none()

    if segment is None:
        return DataResponse(False, "This segment does not exist").status()

    db.session.delete(segment)
    db.session.commit()
    return DataResponse(True, "Segment deleted successfully").status()


@segmentview.route("/segment/<segment_id>/contacts/delete", methods=["DELETE"])
@user_required()
def segments_contacts_delete(segment_id):
    segment = SegmentUsers.query.filter_by(
        segment_id=segment_id, organization_id=getOrg(get_jwt())
    ).one_or_none()

    if segment is None:
        return DataResponse(False, f"User with id {segment_id} does not exist").status()

    body = request.json

    contacts = body['contacts'] if 'contacts' in body.keys() else None

    if not contacts:
        return DataResponse(False, "Array `contacts` is required").status()

    for contact in contacts:
        if UUID(contact) in segment.contacts:
            try:
                segment.contacts.remove(UUID(contact))
            except Exception as e:
                return DataResponse(False, str(e)[:105]).status()

    db.session.commit()
    return DataResponse(True, "Contacts Deleted from Segment").status()


@segmentview.route("/segment/<segment_id>/contacts", methods=["GET"])
@user_required()
def segments_contacts_overview(segment_id):
    segment = SegmentUsers.query.filter_by(
        segment_id=segment_id, organization_id=getOrg(get_jwt())
    ).one_or_none()

    if not segment:
        return DataResponse(False, "This segment does not exist").status()

    contacts_list = list(segment.contacts)
    contacts = (
        ContactUsers
        .query
        .filter_by(organization_id = getOrg(get_jwt()))
        .filter(ContactUsers.id.in_(contacts_list))
        .all()
    )

    return DataResponse(True, multi_dict_resp(contacts)).status()


@segmentview.route("/search", methods=["GET"])
@user_required()
def search():
    search_string = request.args.get("search_string")
    page_number = request.args.get("page")
    order_by_column = "segment_id"
    instance = SegmentUsers.query.filter(or_(
        SegmentUsers.name.ilike(f'%{search_string}%'),
        SegmentUsers.description.ilike(f'%{search_string}%')
        )).order_by(getattr(SegmentUsers, order_by_column))
    api_path = "segments/search"
    return paginator_search(page_number, instance, api_path)