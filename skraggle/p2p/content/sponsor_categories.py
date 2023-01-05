from flask import request, Blueprint
from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import SponsorCategories
from skraggle.config import db

sponsorcategoriesviews = Blueprint(
    "sponsorcategoriesviews", __name__, template_folder="templates"
)


@sponsorcategoriesviews.route("/create", methods=["GET", "POST"])
@user_required()
def add_sponsorcategories():
    if request.method == "POST":
        name = request.form["name"]
        sponsorcategories = SponsorCategories(category_name=name)
        db.session.add(sponsorcategories)
        db.session.flush()
        sponsorcategories.organization_id = getOrg(get_jwt())
        db.session.commit()
    return "Successfully Added"


@sponsorcategoriesviews.route("/update", methods=["PATCH"])
@user_required()
def update_sponsorcategories():
    id = request.args.get("id")
    sponsorcategory = SponsorCategories.query.filter_by(
        id=id, organization_id=getOrg(get_jwt())
    )
    name = request.form["name"]
    sponsorcategory.category_name = name
    SponsorCategories(category_name=name)
    db.session.commit()
    return "Updated Successfully"


@sponsorcategoriesviews.route("/all")
@user_required()
def all_sponsorcategories():
    info = SponsorCategories.query.all()
    return "All data available"


@sponsorcategoriesviews.route("/info/<id>")
@user_required()
def info_sponsorcategories(id):
    info = SponsorCategories.query.filter_by(id=id, organization_id=getOrg(get_jwt()))
    return "Data Available"


@sponsorcategoriesviews.route("/delete", methods=["DELETE"])
@user_required()
def delete_sponsorcategories():
    id = request.args.get("id")
    delete = SponsorCategories.query.filter_by(
        id=id, organization_id=getOrg(get_jwt())
    ).delete()
    db.session.commit()
    return "Data Deleted "
