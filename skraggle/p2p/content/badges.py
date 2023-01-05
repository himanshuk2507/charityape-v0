from flask_jwt_extended import get_jwt

from skraggle.decarotor import user_required
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import Participants, Badges, P2pTeams
from flask import request, Blueprint, jsonify
from skraggle.config import db
from uuid import UUID


p2pbadges = Blueprint("p2pbadges", __name__)


@p2pbadges.route("/create", methods=["POST"])
@user_required()
def create_badge():
    if request.method == "POST":
        badge_data = {
            "badge_name": request.form["badge_name"],
            "badge_color": request.form["badge_color"]
            if "badge_color" in request.form
            else "NA",
            "badge_icon": request.form["badge_icon"]
            if "badge_icon" in request.form
            else "NA",
            "badge_restriction": request.form["badge_restriction"],
            "badge_status": request.form["badge_status"],
            "badge_award": request.form["badge_award"],
            "achievement_reached_type": request.form["achievement_reached_type"],
            "achievement_reached": request.form["achievement_reached"],
            "manually_award": bool(request.form["manually_award"]),
            "uploaded_batch": request.form["uploaded_batch"]
            if "uploaded_batch" in request.form
            else "NA",
        }
        badge = Badges(**badge_data)
        db.session.add(badge)
        db.session.flush()
        badge.organization_id = getOrg(get_jwt())
        db.session.commit()
        return (
            jsonify({"status": True, "message": "Badge Created Successfully !!"}),
            200,
        )


@p2pbadges.route("/update", methods=["PATCH"])
@user_required()
def update_badge():
    updating_fields = [
        "badge_name",
        "badge_color",
        "badge_icon",
        "badge_restriction",
        "badge_status",
        "badge_award",
        "achievement_reached_type",
        "achievement_reached",
        "manually_award",
        "uploaded_batch",
    ]
    if request.method == "PATCH":
        badge_id = request.args.get("badge_id")
        badge = Badges.query.filter_by(
            badge_id=badge_id, organization_id=getOrg(get_jwt())
        ).one_or_none()
        if badge:
            for fields in updating_fields:
                if fields == "manually_award":
                    setattr(badge, fields, bool(request.form[fields]))
                else:
                    setattr(badge, fields, request.form[fields])
            db.session.add(badge)
            db.session.commit()
            return (
                jsonify(
                    {
                        "status": "True",
                        "message": f"Badge <{badge_id}> updated Successfully ",
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "status": "False",
                        "message": f"Badge <{badge_id}> does not exist",
                    }
                ),
                404,
            )


@p2pbadges.route("/delete", methods=["DELETE"])
@user_required()
def delete_badge():
    badge_id = request.args.get("badge_id")
    try:
        Badges.filter_by(badge_id=badge_id,organization_id = getOrg(get_jwt())).delete()
        db.session.commit()
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Team with ID: {badge_id} deleted successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 404


@p2pbadges.route("/list/all", methods=["GET"])
@user_required()
def view_badges():
    badges = Badges.query.all()
    participant_badges = (
        db.session.query(Badges)
        .filter(Badges.organization_id == getOrg(get_jwt()))
        .filter(Badges.badge_restriction == "any_participant")
        .all()
    )
    team_badges = (
        db.session.query(Badges)
        .filter(Badges.organization_id == getOrg(get_jwt()))
        .filter(Badges.badge_restriction != "any_participant")
        .all()
    )

    data = {
        "badges": [
            {
                "badge_id": badge.badge_id,
                "badge_name": badge.badge_name,
                "badge_color": badge.badge_color,
                "badge_icon": badge.badge_icon,
                "badge_restriction": badge.badge_restriction,
                "badge_status": badge.badge_status,
                "badge_award": badge.badge_award,
                "achievement_reached_type": badge.achievement_reached_type,
                "achievement_reached": badge.achievement_reached,
                "manually_award": badge.manually_award,
                "uploaded_batch": badge.uploaded_batch,
            }
            for badge in badges
        ],
        "participant_badges": [
            {
                "badge_id": badge.badge_id,
                "badge_name": badge.badge_name,
                "badge_color": badge.badge_color,
                "badge_icon": badge.badge_icon,
                "badge_restriction": badge.badge_restriction,
                "badge_status": badge.badge_status,
                "badge_award": badge.badge_award,
                "achievement_reached_type": badge.achievement_reached_type,
                "achievement_reached": badge.achievement_reached,
                "manually_award": badge.manually_award,
                "uploaded_batch": badge.uploaded_batch,
            }
            for badge in participant_badges
        ],
        "team_badges": [
            {
                "badge_id": badge.badge_id,
                "badge_name": badge.badge_name,
                "badge_color": badge.badge_color,
                "badge_icon": badge.badge_icon,
                "badge_restriction": badge.badge_restriction,
                "badge_status": badge.badge_status,
                "badge_award": badge.badge_award,
                "achievement_reached_type": badge.achievement_reached_type,
                "achievement_reached": badge.achievement_reached,
                "manually_award": badge.manually_award,
                "uploaded_batch": badge.uploaded_batch,
            }
            for badge in team_badges
        ],
    }
    return jsonify(data)


@p2pbadges.route("/list/<badge_id>", methods=["GET"])
@user_required()
def view_one_badge(badge_id):
    badge = Badges.query.filter_by(badge_id=badge_id,organization_id=getOrg(get_jwt())).one_or_none()
    if badge:
        data = {
            "badge_id": badge.badge_id,
            "badge_name": badge.badge_name,
            "badge_color": badge.badge_color,
            "badge_icon": badge.badge_icon,
            "badge_restriction": badge.badge_restriction,
            "badge_status": badge.badge_status,
            "badge_award": badge.badge_award,
            "achievement_reached_type": badge.achievement_reached_type,
            "achievement_reached": badge.achievement_reached,
            "manually_award": badge.manually_award,
            "uploaded_batch": badge.uploaded_batch,
        }
        return jsonify(data), 200
    else:
        return jsonify({"Error": f"Badge with id {badge_id} does not exist"})


@p2pbadges.route("/award", methods=["PATCH"])
@user_required()
def award_badge():
    badge_id = request.args.get("badge_id")
    badge = Badges.query.filter_by(badge_id=badge_id,organization_id = getOrg(get_jwt())).one_or_none()
    badge_restriction = badge.badge_restriction
    if badge:
        if badge_restriction == "team":
            team_id = request.args.get("team_id")
            team = P2pTeams.query.filter_by(team_id=team_id,organization_id=getOrg(get_jwt())).one_or_none()
            if team:
                if team.badges is None:
                    team.badges = [badge_id]
                else:
                    team.badges.award(badge_id)
                db.session.commit()
                return jsonify(
                    {"status": True, "message": "Badge awarded to team "}, 200
                )
            else:
                return jsonify(
                    {
                        "status": False,
                        "message": "Team does not exist or check badge restriction",
                    },
                    404,
                )
        else:
            participant_id = request.args.get("participant_id")
            participant = Participants.query.filter_by(
                participant_id=participant_id,organization_id=getOrg(get_jwt())
            ).one_or_none()
            badge_type = {
                "team_captain": "Team Captain",
                "team_members": "Team Member",
                "any_participant": "Participant",
            }
            if badge.badge_restriction in badge_type.keys():
                if participant:
                    if badge.badge_restriction == "team_captain":
                        if not participant.is_team_captain:
                            return jsonify(
                                {
                                    "status": False,
                                    "message": "Badge can only awarded to Team Captains",
                                },
                                404,
                            )
                    elif badge.badge_restriction == "in_team":
                        if not participant.is_team:
                            return jsonify(
                                {
                                    "status": False,
                                    "message": "Badge can only awarded to Team Members",
                                },
                                404,
                            )
                    if participant.badges_list is None:
                        participant.badges_list = [badge_id]
                    else:
                        participant.badges_list.award(badge_id)
                    db.session.commit()
                    return jsonify(
                        {
                            "status": True,
                            "message": f"Badge assigned to {badge_type[badge.badge_restriction]}",
                        },
                        200,
                    )
                else:
                    return jsonify(
                        {"status": False, "message": f"Participant does not exist",},
                        404,
                    )


@p2pbadges.route("/revoke", methods=["PATCH"])
@user_required()
def revoke_badge():
    badge_id = request.args.get("badge_id")
    badge = Badges.query.filter_by(badge_id=badge_id,organization_id=getOrg(get_jwt())).one_or_none()
    if badge:
        badge_type = {
            "team_captain": "Team Captain",
            "team_members": "Team Member",
            "any_participant": "Participant",
        }
        if badge.badge_restriction == "team":
            team_id = request.args.get("team_id")
            team = P2pTeams.query.filter_by(team_id=team_id,organization_id=getOrg(get_jwt())).one_or_none()
            if team:
                if UUID(badge_id) in team.badges:
                    team.badges.revoke(badge_id)
                    db.session.commit()
                return (
                    jsonify(
                        {
                            "status": True,
                            "message": f"Badge revoked for team <{team_id}>",
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"status": False, "message": "Team does not exist"}), 404
        elif badge.badge_restriction in badge_type.keys():
            print("here")
            participant_id = request.args.get("participant_id")
            participant = Participants.query.filter_by(
                participant_id=participant_id,organization_id=getOrg(get_jwt())
            ).one_or_none()
            if participant:

                if UUID(badge_id) in participant.badges_list:
                    participant.badges_list.revoke(UUID(badge_id))
                    db.session.commit()
                    return (
                        jsonify(
                            {
                                "status": True,
                                "message": f"Badge revoked from {badge_type[badge.badge_restriction]}",
                            }
                        ),
                        200,
                    )
            else:
                return (
                    jsonify(
                        {
                            "status": False,
                            "message": f"{badge_type[badge.badge_restriction]} does not exist",
                        }
                    ),
                    404,
                )
    return jsonify({"status": False, "message": "Badge does not exist"}), 404
