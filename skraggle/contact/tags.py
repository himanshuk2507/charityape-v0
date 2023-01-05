from datetime import datetime
from uuid import UUID

from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy import and_

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator, paginator_search
from skraggle.base_helpers.responser import DataResponse
from .models import TagUsers
from skraggle.config import db
import time

tagview = Blueprint("tagview", __name__)


@tagview.route("/add", methods=["POST"])
@user_required()
def add_tag():
    tag_name = request.json.get("tag_name")
    tag = TagUsers.query.filter_by(
        tag_name=tag_name, organization_id=getOrg(get_jwt())
    ).first()
    if tag:
        resp = DataResponse(True, "Tag Name already exists")
        return resp.status()

    created_on = datetime.now()
    tags = TagUsers(tag_name=tag_name, created=created_on)
    db.session.add(tags)
    db.session.flush()
    tags.organization_id = getOrg(get_jwt())
    db.session.commit()
    resp = DataResponse(True, "Tag Created Successfully")
    return resp.status()


@tagview.route("/update", methods=["PATCH"])
@user_required()
def update_tag():
    tag_name = request.json.get("tag_name")
    tag = TagUsers.query.filter_by(
        tag_name=tag_name, organization_id=getOrg(get_jwt())
    ).first()
    if tag:
        resp = DataResponse(False, "Tag Name already exists")
        return resp.status()

    tag_id = request.args.get("tag_id")
    tag = TagUsers.query.filter_by(
        tag_id=tag_id, organization_id=getOrg(get_jwt())
    ).first()
    if tag:
        created_on = time.strftime("%dth %b,%Y")
        tag.tag_name = tag_name
        tag.created = created_on
        db.session.commit()
        return DataResponse(True, f"Tag with id {tag_id} Updated").status()
    return DataResponse(True, f"Tag with id {tag_id} Does not exist").status()


@tagview.route("/details/<int:page_number>", methods=["GET"])
@user_required()
def get_tag_info(page_number):
    instance = TagUsers.query.filter_by(organization_id=getOrg(get_jwt())).order_by('tag_id')
    api_path = "tags/details"
    return paginator_search(page_number, instance, api_path)


@tagview.route("/<uuid:tag_id>", methods=["GET"])
@user_required()
def get_tag_information(tag_id):
    tags = TagUsers.query.filter_by(
        tag_id=tag_id, organization_id=getOrg(get_jwt())
    ).first()
    if tags:
        data = {
            "tag_name": tags.tag_name,
            "tag_id": tags.tag_id,
            "created_on": tags.created_on
        }
        return DataResponse(True, data).status()
    else:
        return DataResponse(True, "<h1>Tag Does Not Exist With Given ID</h1>").status()


@tagview.route("/delete", methods=["DELETE"])
@user_required()
def delete_tag():
    tags = request.json.get("tags")
    if not tags:
        resp = DataResponse(False, "Empty Tag List to Delete")
        return resp.status()

    try:
        db.session.query(TagUsers).filter(
            and_(
                TagUsers.organization_id == getOrg(get_jwt()),
                TagUsers.tag_id.in_(tags),
            )
        ).delete(synchronize_session="fetch")
        db.session.commit()
        resp = DataResponse(
            True,
            f"{'Tags' if len(tags) > 1 else 'Tag'} Deleted Successfully",
        )
        return resp.status()
    except Exception as e:
        resp = DataResponse(True, f"Error deleting tag :{str(e)[:105]}")
        return resp.status()


@tagview.route("/<tag_id>/add-contact", methods=["PATCH"])
@user_required()
def add_Contact_to_tag(tag_id):
    tag = TagUsers.query.filter_by(
        tag_id=tag_id, organization_id=getOrg(get_jwt())
    ).first()
    if tag:
        contacts = list(map(str, request.json.get("contacts", [])))
        for contact in contacts:

            if not tag.contacts or contact not in tag.contacts:
                try:
                    if tag.contacts is None:
                        tag.contacts = [contact]
                    else:
                        tag.contacts.add(contact)
                except Exception as e:
                    resp = DataResponse(False, str(e)[:105])
                    return resp.status()
            else:
                resp = DataResponse(
                    False, f"Contact {UUID(contact)} already exists in Tag > {tag_id} "
                )
                return resp.status()
        db.session.commit()
        resp = DataResponse(
            True, f"Contacts Added to Tags with id  {tag_id} "
        )
        return resp.status()
    else:
        resp = DataResponse(True, f"Tag with id {tag_id} Does not exist")
        return resp.status()


@tagview.route("/<tag_id>/delete-contact", methods=["DELETE"])
@user_required()
def delete_Contacts_from_tag(tag_id):
    tag = TagUsers.query.filter_by(
        tag_id=tag_id, organization_id=getOrg(get_jwt())
    ).first()
    if tag:
        contacts = list(map(str, request.json.get("contacts", [])))
        for contact in contacts:

            if tag.contacts or UUID(contact) in tag.contacts:
                try:
                    tag.contacts.remove(UUID(contact))
                except Exception as e:
                    resp = DataResponse(False, str(e)[:105])
                    return resp.status()
            else:
                resp = DataResponse(True, "Contact is not associated with this Tag")
                return resp.status()
        db.session.commit()
        resp = DataResponse(True, "Contacts Deleted from Tags")
        return resp.status()
    else:
        resp = DataResponse(False, f"Tag with id {tag_id} Does not exist")
        return resp.status()


@tagview.route("/search", methods=["GET"])
@user_required()
def search():
    search_string = request.args.get("search_string")
    page_number = request.args.get("page")
    order_by_column = "tag_name"
    instance = TagUsers.query.filter(TagUsers.tag_name.ilike(f'%{search_string}%')).order_by(
        getattr(TagUsers, order_by_column))
    api_path = "tags/search"
    return paginator_search(page_number, instance, api_path)
