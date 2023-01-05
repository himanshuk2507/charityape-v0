from flask_jwt_extended import get_jwt
from skraggle.decarotor import user_required
from skraggle.base_helpers.dict_responser import multi_dict_resp
from skraggle.base_helpers.orgGen import getOrg
from skraggle.p2p.models import Participants, P2pTeams
from flask import request, Blueprint, jsonify
from skraggle.config import db

p2pteams = Blueprint("p2pteams", __name__)


@p2pteams.route("/add", methods=["POST"])
@user_required()
def add_team():
    if request.method == "POST":
        team_data = {
            "team_name": request.form["team_name"],
            "captain": request.form["captain"] if "captain" in request.form else None,
            "verified_amount": request.form["verified_amount"],
            "unverified_amount": request.form["unverified_amount"],
            "amount_raised": request.form["amount_raised"],
            "team_avatar": request.form["team_avatar"],
        }
        team = P2pTeams(**team_data)
        db.session.add(team)
        db.session.flush()
        team.organization_id = getOrg(get_jwt())
        db.session.commit()
        return (
            jsonify(
                {
                    "Status": "Team -- {} Created Successfully".format(
                        team_data["team_name"]
                    )
                }
            ),
            200,
        )
    return (
        jsonify({"Status": "Unable to Create Team"}),
        404,
    )


# API to update a single team. Takes parameter: fields in updating_fields list
@p2pteams.route("/update_team", methods=["PATCH"])
@user_required()
def update_team():
    team_id = request.form["team_id"]
    team_to_update = P2pTeams.filter_by(
        team_id=team_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if not team_to_update:

        return (
            jsonify({"success": False, "message": "The given team doesn't exist"}),
            404,
        )
    updating_fields = [
        "team_name",
        "amount_raised",
        "verified_amount",
        "unverified_amount",
        "captain",
        "team_avatar",
    ]
    try:
        for column in updating_fields:
            if column == "captain":
                setattr(
                    team_to_update,
                    column,
                    request.form["captain"] if "captain" in request.form else None,
                )
            else:
                setattr(team_to_update, column, request.form[column]) or None

        db.session.add(team_to_update)
        db.session.commit()
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Team corresponding to ID: {team_id} updated successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]})


@p2pteams.route("/add_to_team", methods=["GET"])
@user_required()
def add_to_team():
    team_id = request.args.get("team_id")
    participant_id = request.args.get("participant_id")
    team = P2pTeams.query.filter_by(
        team_id=team_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    participant = Participants.query.filter_by(
        participant_id=participant_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if team:
        if participant:
            team.team_members.append(participant)
            participant.in_team = True
            participant.organization_id = getOrg(get_jwt())
            db.session.commit()
            return (
                jsonify(
                    {
                        "Status": f"Participant -- {participant.full_name} -- added to the team {team.team_name}"
                    }
                ),
                200,
            )
        else:
            return (
                jsonify({"Status": "Participant does not Exist"}),
                404,
            )
    else:
        return (
            jsonify({"Status": "Team does not Exist"}),
            404,
        )


@p2pteams.route("/team/<uuid:team_id>", methods=["GET"])
@user_required()
def get_team_details(team_id):
    team = P2pTeams.query.filter_by(
        team_id=team_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if team:
        return jsonify(team.to_dict()), 200
    else:
        return jsonify({"Error": "Specified team does not exist"}), 404


@p2pteams.route("/team/<uuid:team_id>/members", methods=["GET"])
@user_required()
def get_team_members(team_id):
    team = P2pTeams.query.filter_by(
        team_id=team_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if team:
        team_info = team.team_members
        data = {
            "team_name": team.team_name,
            "team_size": f"{len([x for x in team_info])}",
            "members": [
                {"id": team_member.participant_id, "full_name": team_member.full_name}
                for team_member in team_info
            ],
        }
        return jsonify(data), 200
    else:
        return jsonify({"Error": "Specified team does not exist"}), 404


@p2pteams.route("/alter_captain_role", methods=["PATCH"])
@user_required()
def alter_captain():
    participant_id = request.args.get("participant_id")
    team_id = request.args.get("team_id")
    captain_role = request.args.get("captain_status")
    captain_member = Participants.filter_by(
        participant_id=participant_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    team = P2pTeams.filter_by(
        team_id=team_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if captain_member and team:
        if captain_role == "promote":
            captain_member.is_team_captain = True
            team.captain = participant_id
            db.session.commit()
            return jsonify({captain_member.full_name: "Promoted as Captain"})
        elif captain_role == "demote":
            captain_member.is_team_captain = False
            team.captain = None
            db.session.commit()
            return jsonify({captain_member.full_name: "Demoted as Captain"})


# API to remove member from the team he is assigned to. Takes parameter: member_id
@p2pteams.route("/remove_member/<participant_id>", methods=["PATCH"])
@user_required()
def remove_member_from_team(participant_id):
    if participant_id is None:
        return (
            jsonify(
                {"success": False, "message": "Member ID is required for this method"}
            ),
            400,
        )
    member = Participants.filter_by(
        participant_id=participant_id, organization_id=getOrg(get_jwt())
    ).one_or_none()
    if member is None:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Couldn't find a member with ID: {participant_id}",
                }
            ),
            404,
        )
    team_id = member.team
    print(team_id)
    team = db.session.query(P2pTeams).filter_by(participants=team_id).one_or_none()
    team.team_members.remove(member)
    member.in_team = False
    db.session.commit()
    return (
        jsonify(
            {
                "success": True,
                "message": f"Member with ID : {participant_id} successfully removed from Team with ID: {team_id}",
            }
        ),
        200,
    )


# API to delete a team. Takes parameter: team_id
@p2pteams.route("/delete", methods=["DELETE"])
@user_required()
def delete_team():
    team_id = request.form["team_id"]
    try:
        team_to_delete = P2pTeams.filter_by(
            team_id=team_id, organization_id=getOrg(get_jwt())
        ).first()
        participants = team_to_delete.team_members
        for participant in participants:
            team_to_delete.team_members.remove(participant)
        db.session.delete(team_to_delete)
        db.session.commit()
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Team with ID: {team_id} deleted successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)[:105]}), 400


# API to list all teams. Takes no parameter
@p2pteams.route("/show_all_teams", methods=["GET"])
@user_required()
def show_team_list():
    all_teams = P2pTeams.query.all()
    teams_dict = multi_dict_resp(all_teams)
    return jsonify(teams_dict), 200
