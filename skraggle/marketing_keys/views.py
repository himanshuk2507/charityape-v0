from flask import request, Blueprint, jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy.exc import NoResultFound
from skraggle.config import db
from skraggle.decarotor import user_admin_required, user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.marketing_keys.models import MarketingKeys
from skraggle.marketing_keys.response_helpers import (
    no_result_found_response,
    generic_exception_response,
)

marketingviews = Blueprint("marketingviews", __name__)


@marketingviews.route("/create", methods=["POST"])
@user_admin_required()
def create_marketing_keys():
    json_data = request.json
    try:
        admin_id = json_data["admin_id"]
        google_analytics = json_data.get("google_analytics")
        facebook_pixel = json_data.get("facebook_pixel")
        facebook_conversion = json_data.get("facebook_conversion")
        new_marketing_key = MarketingKeys(
            admin_id=admin_id,
            google_analytics=google_analytics,
            facebook_pixel=facebook_pixel,
            facebook_conversion=facebook_conversion,
        )
        db.session.add(new_marketing_key)
        db.session.flush()
        keys_id = new_marketing_key.id
        new_marketing_key.organization_id = getOrg(get_jwt())
        db.session.commit()
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Keys with id: {keys_id} for admin_id: {admin_id} added successfully",
                }
            ),
            200,
        )
    except KeyError:
        return (
            jsonify({"success": False, "message": "Admin ID is required to add keys"}),
            400,
        )
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": f"Following error happened while adding keys: {e}",
            }
        )


@marketingviews.route("/update/<keys_id>", methods=["PATCH"])
@user_required()
def update_marketing_keys(keys_id):
    json_data = request.json
    key_type = json_data["key_type"]
    update_keys = json_data["keys"]
    try:
        marketing_key = MarketingKeys.filter_by(
            id=keys_id, organization_id=getOrg(get_jwt())
        ).one()
        existing_keys = getattr(marketing_key, key_type)
        for key in update_keys:
            existing_keys[key] = update_keys[key]
        db.session.add(marketing_key)
        db.session.commit()
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"{key_type} Keys ID: {keys_id} updated successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return generic_exception_response(e)


@marketingviews.route("/view/<key_id>", methods=["GET"])
@user_required()
def get_specific_key(key_id):
    json_data = request.json
    try:
        key_type = json_data["key_type"]
        db_keys = MarketingKeys.query.filter_by(
            id=key_id, organization_id=getOrg(get_jwt())
        ).one()
        return (
            jsonify(
                {"success": False, "message": f"key_type: {getattr(db_keys, key_type)}"}
            ),
            200,
        )
    except KeyError:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Please define the key type you want to fetch",
                }
            ),
            400,
        )

    except NoResultFound:
        return no_result_found_response(key_id)

    except AttributeError:
        return (
            jsonify(
                {"success": False, "message": f"{key_type} is not a valid key_type"}
            ),
            400,
        )

    except Exception as e:
        return generic_exception_response(e)


@marketingviews.route("/delete/<key_type>", methods=["DELETE"])
@user_required()
def delete_specific_key(key_type):
    json_data = request.json
    key_id = json_data.get("key_id")
    if key_id is None:
        return (
            jsonify(
                {"success": False, "message": "Key ID is required for this method"}
            ),
            400,
        )
    try:
        db_keys = MarketingKeys.filter_by(
            id=key_id, organization_id=getOrg(get_jwt())
        ).one()
        setattr(db_keys, key_type, None)
        db.session.add(db_keys)
        db.session.commit()
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"{key_type} key has been successfully deleted from the record with Key ID: {key_id}",
                }
            ),
            200,
        )
    except NoResultFound:
        return no_result_found_response(key_id)
    except Exception as e:
        return generic_exception_response(e)


@marketingviews.route("/view_all/<key_id>", methods=["GET"])
@user_required()
def get_all_keys(key_id):
    try:
        db_keys = MarketingKeys.filter_by(
            id=key_id, organization_id=getOrg(get_jwt())
        ).one()
        keys = {
            "google_analytics": db_keys.google_analytics,
            "facebook_pixel": db_keys.facebook_pixel,
            "facebook_conversion": db_keys.facebook_conversion,
        }
        return jsonify({"message": keys, "success": True})

    except NoResultFound:
        return no_result_found_response(key_id)

    except Exception as e:
        return generic_exception_response(e)
