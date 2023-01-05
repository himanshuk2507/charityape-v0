from flask import Blueprint

socialsettings = Blueprint("socialsettings", __name__, template_folder="templates")


@socialsettings.route("", methods=["POST"])
def social_share():
    return "in progress"
