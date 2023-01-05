from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt

from skraggle.contact.models import ContactUsers
from skraggle.decarotor import user_required
from skraggle.base_helpers.eblast_email_fetch import extract_email
from skraggle.base_helpers.eblast_sender import eblast_send
from skraggle.base_helpers.orgGen import getOrg
from skraggle.base_helpers.pagination_helper import paginator
from skraggle.base_helpers.responser import DataResponse
from skraggle.run import app

from skraggle.validators_logics.validators import (
    EblastValidator,
    UuidValidator,
    UuidListValidator,
    emails_filter,
)
from pydantic import ValidationError
from .models import Eblasts, EblastsContent
from skraggle.config import db


eblastsview = Blueprint("eblastsview", __name__)


# basedir = path.abspath(path.dirname(__file__))
# CLIENT_SECRET_FILE = path.join(basedir, "client_secret.json")
# API_NAME = "gmail"
# API_VERSION = "v1"
# SCOPES = ["https://mail.google.com/"]


"""
# Api to create a email blast 
@parameters : "eblast_name","campaign_id","category_id","assignee"
"""


@eblastsview.route("/create", methods=["POST"])
@user_required()
def create_eblast():
    if request.method == "POST":
        data = {
            "eblast_name": request.form["eblast_name"],
            "campaign_id": request.form.get("campaign_id"),
            "category_id": request.form.get("category_id"),
            "assignee": request.form.get("assignee"),
        }
        try:
            is_valid = EblastValidator(**data)
            if is_valid:
                try:
                    add_eblast = Eblasts(**data)
                    db.session.add(add_eblast)
                    db.session.flush()
                    add_eblast.organization_id = getOrg(get_jwt())
                    # creating a demo sample content template for each eblast creation
                    eblast_content = {
                        "eblast_users": "contacts",
                        "segment_id": None,
                        "tag_id": None,
                        "send_to": None,
                        "mail_from": "",
                        "subject": "",
                        "attachments": None,
                        "sender_name": "",
                        "reply_to": [],
                        "send_to_unknown": False,
                        "content": None,
                    }
                    current_eblast = Eblasts.query.filter_by(
                        eblast_id=add_eblast.eblast_id
                    ).first()
                    eblast_sample = EblastsContent(**eblast_content)
                    current_eblast.eblast_content.append(eblast_sample)
                    db.session.flush()
                    eblast_sample.organization_id = getOrg(get_jwt())

                    db.session.commit()
                    resp = DataResponse(True, "Eblast Created Successfully")
                    return resp.status()
                except Exception as e:
                    resp = DataResponse(False, str(e))
                    return resp.status()

        except ValidationError as e:
            return e.json()


"""
# Api to view a email blast 
@parameters : "eblast_id"
"""


@eblastsview.route("/view/<eblast_id>", methods=["GET"])
@user_required()
def view_eblast(eblast_id):

    try:
        is_valid = UuidValidator(uuid=eblast_id)
        if is_valid:
            eblast = Eblasts.query.filter_by(
                eblast_id=eblast_id, organization_id=getOrg(get_jwt())
            ).first()
            if not eblast:
                resp = DataResponse(False, f"Eblast with id {eblast_id} Does not exist")
                return resp.status()
            return eblast.to_dict(), 200
    except ValidationError as e:
        return e.json()


"""
# Api to view all email blasts
@parameters : "eblast_id"
"""


@eblastsview.route("/view/all/<int:page_number>", methods=["GET"])
@user_required()
def view_all_eblasts(page_number):
    instance = Eblasts
    order_by_column = "eblast_id"
    api_path = "eblasts/view/all"
    return paginator(page_number, instance, order_by_column, api_path)


"""
# Api to delete a email blast
@parameters : "eblast_id"
"""


@eblastsview.route("/delete", methods=["DELETE"])
@user_required()
def delete_eblast():

    eblast_id = request.args.get("eblast_id")
    try:
        is_valid = UuidValidator(uuid=eblast_id)
        if is_valid:
            eblast = Eblasts.query.filter_by(
                eblast_id=eblast_id, organization_id=getOrg(get_jwt())
            ).first()
            if not eblast:
                resp = DataResponse(False, f"Eblast with id {eblast_id} Does not exist")
                return resp.status()
            try:
                db.session.delete(eblast)
                db.session.commit()
                resp = DataResponse(
                    True, f"Eblast with id {eblast_id} Deleted Successfully"
                )
                return resp.status()
            except Exception as e:
                resp = DataResponse(False, str(e))
                return resp.status()

    except ValidationError as e:
        return e.json()


"""
Api to update Eblast 
@Parameters: "eblast_id" 
"""


@eblastsview.route("/update", methods=["PATCH"])
@user_required()
def update_badge():

    updating_fields = [
        "eblast_name",
        "category_id",
        "campaign_id",
        "assignee",
    ]
    if request.method == "PATCH":
        eblast_id = request.args.get("eblast_id")
        try:
            is_valid = UuidValidator(uuid=eblast_id)
            if is_valid:
                eblast = Eblasts.query.filter_by(
                    eblast_id=eblast_id, organization_id=getOrg(get_jwt())
                ).first()
                if not eblast:
                    resp = DataResponse(
                        False, f"Eblast with id {eblast_id} Does not exist"
                    )
                    return resp.status()
                try:
                    for fields in updating_fields:
                        setattr(
                            eblast,
                            fields,
                            None if not request.form[fields] else request.form[fields],
                        )
                    db.session.add(eblast)
                    db.session.commit()
                    resp = DataResponse(
                        True, f"Eblast with id {eblast_id} Updated successfully"
                    )
                    return resp.status()
                except Exception as e:
                    resp = DataResponse(False, str(e))
                    return resp.status()
        except ValidationError as e:
            return e.json()


"""
# Api to edit a email blast content
@parameters : "eblast_id"
"""


@eblastsview.route("/content/update", methods=["PATCH"])
@user_required()
def edit_eblast_content():

    eblast_id = request.args.get("eblast_id")
    if request.method == "PATCH":
        try:
            is_valid = UuidValidator(uuid=eblast_id)
            if is_valid:
                eblast_content = EblastsContent.query.filter_by(
                    eblast=eblast_id, organization_id=getOrg(get_jwt())
                ).first()
                if not eblast_content:
                    resp = DataResponse(
                        False, f"Eblast with id {eblast_id} Does not exist"
                    )
                    return resp.status()
                content_data = {
                    "eblast_users": "contacts",
                    "segment_id": None,
                    "tag_id": None,
                    "send_to": None,
                    "mail_from": "",
                    "subject": "",
                    "attachments": None,
                    "sender_name": "",
                    "reply_to": [],
                    "send_to_unknown": False,
                    "content": None,
                    "exclude": False,
                    "_exclude_emails": [],
                }

                try:
                    for field in content_data.keys():
                        if field in request.form:
                            if field == "_exclude_emails":
                                content_data[field] = list(
                                    map(str, request.form[field].split(","))
                                )
                                print(request.form[field])
                            else:
                                content_data[field] = (
                                    request.form[field]
                                    if field != "send_to_unknown" and field != "exclude"
                                    else bool(request.form[field])
                                )
                    db.session.query(EblastsContent).filter(
                        EblastsContent.eblast == eblast_id
                    ).update(content_data)
                    db.session.commit()
                    resp = DataResponse(True, "Eblast Updated Successfully")
                    return resp.status()
                except Exception as e:
                    resp = DataResponse(False, str(e))
                    return resp.status()
        except ValidationError as e:
            return e.json()


"""
# Api to mark a  multiple eblasts as sent,archive,draft 
@parameters: eblast_id,eblast_id2 ...
"""


@eblastsview.route("/mark_as", methods=["PATCH"])
@user_required()
def eblast_status():
    eblast_ids = request.json.get("eblasts")
    mark_as = request.form["mark_as"]
    try:
        is_valid = UuidListValidator(ids=eblast_ids)
        if is_valid and request.method == "PATCH":

            try:
                eblast_list = (
                    db.session.query(Eblasts)
                    .filter(Eblasts.organization_id == getOrg(get_jwt()))
                    .filter(Eblasts.eblast_id.in_(eblast_ids))
                    .all()
                )
                print(eblast_list)
                for eblast in eblast_list:
                    eblast.status = mark_as
                db.session.commit()
                resp = DataResponse(True, f"Eblasts Marked as {mark_as}")
                return resp.status()
            except Exception as e:
                resp = DataResponse(False, str(e))
                return resp.status()
    except ValidationError as e:
        return e.json()


"""
# Api to get all eblasts based on status ("sent",'archive","draft")
@parameters: eblast_id,eblast_status
"""


@eblastsview.route("/status/<status>", methods=["GET"])
@user_required()
def view_status_eblasts(status):
    try:
        eblasts = db.session.query(Eblasts).filter(Eblasts.status == status).all()
        return jsonify({"eblasts": [eblast.to_dict() for eblast in eblasts]}), 200
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()


"""
# Api to get statistics for a eblast
@parameters: eblast_id
"""


@eblastsview.route("/statistics", methods=["GET"])
@user_required()
def get_eblasts_stats():
    eblast_id = request.args.get("eblast_id")
    try:
        is_valid = UuidValidator(uuid=eblast_id)
        if is_valid:
            eblast = Eblasts.query.filter_by(
                eblast_id=eblast_id, organization_id=getOrg(get_jwt())
            ).first()
            return jsonify(eblast.eblast_stats()), 200
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()


"""
# Api to update statistics for a eblast
@parameters: eblast_id
"""


@eblastsview.route("/statistics/update", methods=["PATCH"])
@user_required()
def update_eblasts_stats():

    eblast_id = request.form["eblast_id"]
    try:
        is_valid = UuidValidator(uuid=eblast_id)
        if is_valid and request.method == "PATCH":
            stats = {
                "amount_raised": None,
                "clicked": None,
                "delivered": None,
                "opened": None,
                "rejected": None,
                "unopened": None,
                "unsubscribed": None,
            }
            for field in stats.keys():
                if field in request.form:
                    stats[field] = request.form[field]
            db.session.query(Eblasts).filter(Eblasts.eblast_id == eblast_id).filter(
                Eblasts.organization_id == getOrg(get_jwt())
            ).update({Eblasts.stats: stats})
            db.session.commit()
            resp = DataResponse(True, "Eblast Statistics Updated Successfully")
            return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e))
        return resp.status()


@eblastsview.route("/send/<eblast_id>", methods=["POST"])
@user_required()
def send_eblasts(eblast_id):
    eblast = Eblasts.query.filter_by(
        eblast_id=eblast_id, organization_id=getOrg(get_jwt())
    ).first()
    if eblast:
        _content = list(eblast.eblast_content)[0]
        _user_emails = extract_email(
            _content, exclude=bool(_content.exclude), org_id=getOrg(get_jwt())
        )
        recipients = emails_filter(_user_emails)
        eblast_send.delay(
            recipients=recipients,
            sender=_content.mail_from,
            subject=_content.subject,
            content=_content.content,
            attachments=_content.attachments,
            reply_to=_content.reply_to,
        )
        resp = DataResponse(True, "Eblast being sent in background")
        return resp.status()
