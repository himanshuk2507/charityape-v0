from random import choice
import string
from flask import Blueprint, request, redirect, jsonify
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from .models import UrlShortener
from datetime import datetime
from skraggle.config import db


urlshortiew = Blueprint("urlshortview", __name__)


def gen_short_id(id_len):
    "Generating short id for url shortener if no custom id is specified"
    return "".join(
        choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
        for _ in range(id_len)
    )


@urlshortiew.route("/shorten-url", methods=["POST"])
@user_required()
def shorten_url():
    if request.method == "POST":
        original_url = request.form["original_url"]
        custom_id = (
            request.form["custom_id"]
            if "custom_id" in request.form
            else str(gen_short_id(12))
        )
        if (
            custom_id
            and UrlShortener.query.filter_by(
                custom_id=custom_id, organization_id=getOrg(get_jwt())
            ).first()
            is not None
        ):
            return jsonify({"Error": "Custom ID existed,try other"}), 404
        if not original_url:
            return jsonify({"Error": "Original URL required"}), 404
        generated_links = UrlShortener(
            original_url=original_url, custom_id=custom_id, created_at=datetime.now()
        )
        db.session.add(generated_links)
        db.session.flush()
        generated_links.organization_id = getOrg(get_jwt())
        db.session.commit()
        print(original_url, custom_id)
        return jsonify({"Shorten_url": f"{request.host_url}form-view/{custom_id}"}), 200


@urlshortiew.route("/form-view/<custom_id>")
@user_required()
def redirect_original_url(custom_id):
    actual_url = (
        UrlShortener.query.filter_by(
            custom_id=custom_id, organization_id=getOrg(get_jwt())
        )
        .first()
        .original_url
    )
    if actual_url:
        return redirect(actual_url), 200
    else:
        return jsonify({"Error": "Invalid Url"}), 404
