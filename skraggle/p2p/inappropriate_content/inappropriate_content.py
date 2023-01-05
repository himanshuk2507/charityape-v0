from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import InappropriateContent
from flask import request, Blueprint, jsonify
from skraggle.config import db

p2p_inappropriate_content = Blueprint("p2p_inappropriate_content", __name__)


@p2p_inappropriate_content.route("", methods=["GET"])
@user_required()
def view_inappropriate_urls():
    blocked_urls = (
        db.session.query(InappropriateContent)
        .filter(InappropriateContent.organization_id==getOrg(get_jwt()))
        .filter(InappropriateContent.url_status == "blocked")
        .all()
    )
    cleared_urls = (
        db.session.query(InappropriateContent)
        .filter(InappropriateContent.organization_id == getOrg(get_jwt()))
        .filter(InappropriateContent.url_status == "cleared")
        .all()
    )
    flagged_urls = (
        db.session.query(InappropriateContent)
        .filter(InappropriateContent.organization_id == getOrg(get_jwt()))
        .filter(InappropriateContent.url_status == "flagged")
        .all()
    )
    data = {
        "blocked_urls": [blocked_url.to_dict() for blocked_url in blocked_urls],
        "cleared_urls": [cleared_url.to_dict() for cleared_url in cleared_urls],
        "flagged_urls": [flagged_url.to_dict() for flagged_url in flagged_urls],
    }
    return jsonify(data)


@p2p_inappropriate_content.route("/mark_as", methods=["PATCH"])
@user_required()
def mark_urls():
    resp = {
        "status": None,
        "message": None,
    }
    if request.method == "PATCH":
        url_id = request.args.get("url_id")
        mark_as = request.args.get("mark_as")
        options = ["blocked", "flagged", "cleared"]
        url = InappropriateContent.query.filter_by(url_id=url_id,organization_id=getOrg(get_jwt())).one_or_none()
        if url:
            if mark_as in options:
                url.url_status = mark_as
                db.session.commit()
                resp["success"] = True
                resp["message"] = f"Urls marked as {mark_as}"
                return jsonify(resp), 200
            else:
                resp["success"] = False
                resp[
                    "message"
                ] = "Urls can be marked as only blocked,cleared or flagged"
                return jsonify(resp), 404
        else:
            resp["success"] = False
            resp["message"] = "Url does not exist"
            return jsonify(resp), 404


@p2p_inappropriate_content.route("/add", methods=["POST"])
@user_required()
def add_urls():
    resp = {
        "success": None,
        "message": None,
    }
    if request.method == "POST":
        url = request.args.get("url")
        mark_as = request.args.get("mark_as")
        existing_url = InappropriateContent.query.filter_by(url=url,organization_id=getOrg(get_jwt())).one_or_none()
        if existing_url is not None:
            resp["success"] = False
            resp[
                "message"
            ] = f"Url already exists and marked as {existing_url.url_status}"
            return jsonify(resp), 404
        else:
            try:
                add_url = InappropriateContent(url=url, url_status=mark_as)
                db.session.add(add_url)
                db.session.flush()
                add_url.organization_id = getOrg(get_jwt())
                db.session.commit()
                resp["success"] = True
                resp["message"] = f"Url added and marked as {mark_as}"
                return jsonify(resp), 200
            except Exception as e:
                resp["success"] = False
                resp["message"] = str(e)[:105]
                return jsonify(resp), 404




